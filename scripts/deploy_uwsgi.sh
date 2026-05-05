#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/home/acs/roamio}"
REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-master}"
BACKEND_DIR="${BACKEND_DIR:-${APP_ROOT}/backend}"
FRONTEND_DIR="${FRONTEND_DIR:-${APP_ROOT}/frontend/web}"
UWSGI_INI="${UWSGI_INI:-${APP_ROOT}/scripts/uwsgi.ini}"
UWSGI_PROCESSES="${UWSGI_PROCESSES:-2}"
UWSGI_LOG="${UWSGI_LOG:-/tmp/uwsgi.log}"
ROAMIO_SETTINGS="${ROAMIO_SETTINGS:-dev}"
# Ubuntu 常无 `python`；若有环境变量 PYTHON_BIN=python 但路径上不存在，则回退到 python3/python。
_resolve_python_bin() {
  local pick="${PYTHON_BIN:-}"
  if [[ -n "${pick}" ]] && command -v "${pick}" >/dev/null 2>&1; then
    PYTHON_BIN="${pick}"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
    return 0
  fi
  echo "[deploy] No Python found. Install python3 or set PYTHON_BIN to the venv interpreter (e.g. ${APP_ROOT}/.venv/bin/python)." >&2
  exit 1
}
_resolve_python_bin
RUN_NPM_CI="${RUN_NPM_CI:-0}"
RUN_DJANGO_CHECK="${RUN_DJANGO_CHECK:-1}"
AUTO_STASH="${AUTO_STASH:-0}"
HEALTHCHECK_BASE_URL="${HEALTHCHECK_BASE_URL:-https://roamio.cn}"

stash_created=0

log() {
  echo "[deploy] $*"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing command: $1" >&2
    exit 1
  fi
}

check_http() {
  local path="$1"
  local url="${HEALTHCHECK_BASE_URL}${path}"
  local code
  code="$(curl -sS -o /dev/null -w "%{http_code}" "${url}")"
  case "${code}" in
    200|301|302|401|403)
      log "PASS ${url} -> ${code}"
      ;;
    *)
      echo "[deploy] FAIL ${url} -> ${code}" >&2
      return 1
      ;;
  esac
}

check_json_contains() {
  local path="$1"
  local expected="$2"
  local url="${HEALTHCHECK_BASE_URL}${path}"
  local body
  body="$(curl -fsS "${url}")"
  if [[ "${body}" != *"${expected}"* ]]; then
    echo "[deploy] FAIL ${url} missing ${expected}" >&2
    return 1
  fi
  log "PASS ${url} contains ${expected}"
}

restore_stash() {
  if [[ "${stash_created}" -eq 1 ]]; then
    log "Restoring stashed local changes"
    if ! git stash pop; then
      echo "[deploy] git stash pop reported conflicts; resolve manually." >&2
      exit 1
    fi
  fi
}

trap restore_stash EXIT

require_cmd git
require_cmd npm
require_cmd curl
require_cmd uwsgi
require_cmd "${PYTHON_BIN}"

log "Using PYTHON_BIN=${PYTHON_BIN}"

cd "${APP_ROOT}"

log "Checking git workspace"
if [[ -n "$(git status --porcelain)" ]]; then
  if [[ "${AUTO_STASH}" == "1" ]]; then
    log "Workspace dirty, creating temporary stash"
    git stash push -u -m "deploy-uwsgi-temp-$(date +%Y%m%d-%H%M%S)"
    stash_created=1
  else
    echo "[deploy] Working tree is not clean. Commit/stash first, or set AUTO_STASH=1." >&2
    exit 1
  fi
fi

log "Pulling latest code from ${REMOTE}/${BRANCH}"
git pull --ff-only "${REMOTE}" "${BRANCH}"

# 用 Python 解析 .env 并 export：`source .env` 会把 SECRET_KEY 里的 # ( ) $ 等当成 bash 语法而报错。
_dotenv_export() {
  local envfile="$1"
  local _line
  while IFS= read -r _line; do
    [[ -z "${_line}" ]] && continue
    eval "${_line}"
  done < <(DEPLOY_DOTENV_TARGET="${envfile}" "${PYTHON_BIN}" <<'PY'
import os, re

path = os.environ["DEPLOY_DOTENV_TARGET"]


def bash_single_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


key_ok = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

with open(path, encoding="utf-8", errors="replace") as fp:
    for raw in fp:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, _, rest = line.partition("=")
        key = key.strip()
        val = rest.rstrip("\r\n")
        if not key_ok.match(key):
            continue
        if len(val) >= 2 and val[0] == '"' and val[-1] == '"':
            val = val[1:-1]
        elif len(val) >= 2 and val[0] == "'" and val[-1] == "'":
            val = val[1:-1]
        print(f"export {key}={bash_single_quote(val)}")
PY
)
}

# prod：自动加载环境变量（与 manage.py / 同 shell 里启动的 uwsgi 共享）
_load_dotenv_prod() {
  [[ "${ROAMIO_SETTINGS:-}" != "prod" ]] && return 0
  local eff=""
  if [[ -n "${ENV_FILE:-}" ]]; then
    if [[ ! -f "${ENV_FILE}" ]]; then
      echo "[deploy] ENV_FILE 指向的文件不存在: ${ENV_FILE}" >&2
      exit 1
    fi
    eff="${ENV_FILE}"
  elif [[ -f "${APP_ROOT}/.env.prod" ]]; then
    eff="${APP_ROOT}/.env.prod"
  elif [[ -f "${APP_ROOT}/.env" ]]; then
    eff="${APP_ROOT}/.env"
    log "未找到 .env.prod，使用已有的 .env（不用再复制一份配置）"
  else
    cat <<EOF >&2
[deploy] ROAMIO_SETTINGS=prod：请在 ${APP_ROOT}/.env 中配置 ALLOWED_HOSTS、SECRET_KEY、数据库等（或通过 ENV_FILE / .env.prod 指定文件）。
EOF
    exit 1
  fi
  log "Loading production environment from ${eff}"
  _dotenv_export "${eff}"
}
_load_dotenv_prod

if [[ "${RUN_DJANGO_CHECK}" == "1" ]]; then
  log "Running Django system check"
  cd "${BACKEND_DIR}"
  ROAMIO_SETTINGS="${ROAMIO_SETTINGS}" "${PYTHON_BIN}" manage.py check
fi

log "Building frontend assets"
cd "${FRONTEND_DIR}"
if [[ "${RUN_NPM_CI}" == "1" ]]; then
  npm ci
fi
npm run build

cd "${APP_ROOT}"
log "Restarting uWSGI"
# 禁止使用 pkill -f uwsgi：会误匹配 bash 命令行里的 scripts/deploy_uwsgi.sh
if command -v pgrep >/dev/null 2>&1; then
  _uwsgi_pids="$(pgrep -x uwsgi 2>/dev/null || true)"
  if [[ -n "${_uwsgi_pids}" ]]; then
    # shellcheck disable=SC2086
    kill -9 ${_uwsgi_pids} 2>/dev/null || true
  fi
elif command -v killall >/dev/null 2>&1; then
  killall -9 uwsgi 2>/dev/null || true
else
  echo "[deploy] WARN: pgrep/killall not found; uwsgi restart may spawn duplicates" >&2
fi
sleep 1
uwsgi --env "ROAMIO_SETTINGS=${ROAMIO_SETTINGS}" --ini "${UWSGI_INI}" --processes "${UWSGI_PROCESSES}" --daemonize "${UWSGI_LOG}"
sleep 2

log "Running health checks"
check_http "/"
# /trips 会扫库 + 聚合统计，易受数据或序列化问题影响返回 500；探活改用需鉴权但未传 token 即 401 的轻接口。
check_http "/api/v1/auth/me/"
check_json_contains "/api/v1/auth/qq_login_url/" "authorize_url"

log "Deployment completed"
