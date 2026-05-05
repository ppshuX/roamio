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
PYTHON_BIN="${PYTHON_BIN:-python}"
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
pkill -9 -f uwsgi || true
sleep 1
uwsgi --env "ROAMIO_SETTINGS=${ROAMIO_SETTINGS}" --ini "${UWSGI_INI}" --processes "${UWSGI_PROCESSES}" --daemonize "${UWSGI_LOG}"
sleep 2

log "Running health checks"
check_http "/"
check_http "/api/v1/trips/"
check_json_contains "/api/v1/auth/qq_login_url/" "authorize_url"

log "Deployment completed"
