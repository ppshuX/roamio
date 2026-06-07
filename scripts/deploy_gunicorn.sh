#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/home/acs/roamio}"
REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-master}"
BACKEND_DIR="${BACKEND_DIR:-${APP_ROOT}/backend}"
FRONTEND_DIR="${FRONTEND_DIR:-${APP_ROOT}/frontend/web}"
ROAMIO_SETTINGS="${ROAMIO_SETTINGS:-dev}"
RUN_NPM_CI="${RUN_NPM_CI:-0}"
RUN_DJANGO_CHECK="${RUN_DJANGO_CHECK:-1}"
AUTO_STASH="${AUTO_STASH:-0}"
HEALTHCHECK_BASE_URL="${HEALTHCHECK_BASE_URL:-https://roamio.cn}"
GUNICORN_HOST="${GUNICORN_HOST:-127.0.0.1}"
GUNICORN_PORT="${GUNICORN_PORT:-8000}"

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
  echo "[deploy] No Python found. Install python3 or set PYTHON_BIN to the venv interpreter, for example ${APP_ROOT}/.venv/bin/python." >&2
  exit 1
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

_sniff_env_path_to_source() {
  if [[ -n "${ENV_FILE:-}" && -f "${ENV_FILE}" ]]; then
    printf '%s' "${ENV_FILE}"
    return 0
  fi
  if [[ -f "${APP_ROOT}/.env.prod" ]]; then
    printf '%s' "${APP_ROOT}/.env.prod"
    return 0
  fi
  if [[ -f "${APP_ROOT}/.env" ]]; then
    printf '%s' "${APP_ROOT}/.env"
    return 0
  fi
  return 1
}

_sniff_roamio_sqlite_flag() {
  local envfile
  if ! envfile="$(_sniff_env_path_to_source)"; then
    return 0
  fi
  if grep -Eq '^[[:space:]]*ROAMIO_USE_SQLITE[[:space:]]*=[[:space:]]*(1|true|yes|on)([[:space:]]|$)' "${envfile}" 2>/dev/null; then
    export ROAMIO_USE_SQLITE=1
    log "Detected ROAMIO_USE_SQLITE in ${envfile}; Django and Gunicorn will use the SQLite path."
  fi
}

_dotenv_export() {
  local envfile="$1"
  local line
  while IFS= read -r line; do
    [[ -z "${line}" ]] && continue
    eval "${line}"
  done < <(DEPLOY_DOTENV_TARGET="${envfile}" "${PYTHON_BIN}" <<'PY'
import os
import re

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
        value = rest.rstrip("\r\n")
        if not key_ok.match(key):
            continue
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        elif len(value) >= 2 and value[0] == "'" and value[-1] == "'":
            value = value[1:-1]
        print(f"export {key}={bash_single_quote(value)}")
PY
)
}

_load_dotenv_prod() {
  [[ "${ROAMIO_SETTINGS:-}" != "prod" ]] && return 0

  local envfile=""
  if [[ -n "${ENV_FILE:-}" ]]; then
    if [[ ! -f "${ENV_FILE}" ]]; then
      echo "[deploy] ENV_FILE does not exist: ${ENV_FILE}" >&2
      exit 1
    fi
    envfile="${ENV_FILE}"
  elif [[ -f "${APP_ROOT}/.env.prod" ]]; then
    envfile="${APP_ROOT}/.env.prod"
  elif [[ -f "${APP_ROOT}/.env" ]]; then
    envfile="${APP_ROOT}/.env"
    log "No .env.prod found; using existing .env."
  else
    cat <<EOF >&2
[deploy] ROAMIO_SETTINGS=prod requires ${APP_ROOT}/.env, ${APP_ROOT}/.env.prod, or ENV_FILE with ALLOWED_HOSTS, SECRET_KEY, database settings, and related production values.
EOF
    exit 1
  fi

  log "Loading production environment from ${envfile}"
  _dotenv_export "${envfile}"
}

stop_uwsgi() {
  local uwsgi_pids=""

  # Avoid full command-line matching for uWSGI; it can match this deploy script command line.
  if command -v pgrep >/dev/null 2>&1; then
    uwsgi_pids="$(pgrep -x uwsgi 2>/dev/null || true)"
    if [[ -n "${uwsgi_pids}" ]]; then
      # shellcheck disable=SC2086
      kill -9 ${uwsgi_pids} 2>/dev/null || true
      return 0
    fi
  fi

  if command -v killall >/dev/null 2>&1; then
    killall -9 uwsgi 2>/dev/null || true
    return 0
  fi

  echo "[deploy] WARN: pgrep/killall not found; uWSGI may still be running." >&2
}

trap restore_stash EXIT

_resolve_python_bin

require_cmd git
require_cmd npm
require_cmd curl
require_cmd gunicorn
require_cmd "${PYTHON_BIN}"

log "Using PYTHON_BIN=${PYTHON_BIN}"

cd "${APP_ROOT}"
_sniff_roamio_sqlite_flag

log "Checking git workspace"
if [[ -n "$(git status --porcelain)" ]]; then
  if [[ "${AUTO_STASH}" == "1" ]]; then
    log "Workspace dirty, creating temporary stash"
    git stash push -u -m "deploy-gunicorn-temp-$(date +%Y%m%d-%H%M%S)"
    stash_created=1
  else
    echo "[deploy] Working tree is not clean. Commit/stash first, or set AUTO_STASH=1." >&2
    exit 1
  fi
fi

log "Pulling latest code from ${REMOTE}/${BRANCH}"
git pull --ff-only "${REMOTE}" "${BRANCH}"

_load_dotenv_prod
export ROAMIO_SETTINGS
export ROAMIO_USE_SQLITE="${ROAMIO_USE_SQLITE:-}"

if [[ "${RUN_DJANGO_CHECK}" == "1" ]]; then
  log "Running Django system check"
  cd "${BACKEND_DIR}"
  ROAMIO_SETTINGS="${ROAMIO_SETTINGS}" ROAMIO_USE_SQLITE="${ROAMIO_USE_SQLITE:-}" "${PYTHON_BIN}" manage.py check
fi

log "Building frontend assets"
cd "${FRONTEND_DIR}"
if [[ "${RUN_NPM_CI}" == "1" ]]; then
  npm ci
fi
npm run build

cd "${APP_ROOT}"
log "Stopping uWSGI before starting Gunicorn"
stop_uwsgi
sleep 1

log "Stopping any existing Gunicorn on the target pidfile/port"
HOST="${GUNICORN_HOST}" PORT="${GUNICORN_PORT}" bash "${APP_ROOT}/scripts/stop_gunicorn.sh" || true

log "Starting Gunicorn on local HTTP ${GUNICORN_HOST}:${GUNICORN_PORT}"
HOST="${GUNICORN_HOST}" PORT="${GUNICORN_PORT}" bash "${APP_ROOT}/scripts/start_gunicorn.sh"
sleep 2

log "Running local Gunicorn HTTP health checks"
BASE_URL="http://${GUNICORN_HOST}:${GUNICORN_PORT}" bash "${APP_ROOT}/scripts/healthcheck.sh"

log "Local Gunicorn deployment completed."
log "Nginx must be switched in the same maintenance window: run nginx -t, reload, then verify public HTTPS via HEALTHCHECK_BASE_URL=${HEALTHCHECK_BASE_URL}."
