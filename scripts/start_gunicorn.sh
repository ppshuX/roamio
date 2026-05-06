#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/home/acs/roamio}"
BACKEND_DIR="${BACKEND_DIR:-${APP_ROOT}/backend}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8001}"
WORKERS="${WORKERS:-3}"
THREADS="${THREADS:-2}"
TIMEOUT="${TIMEOUT:-120}"
PIDFILE="${PIDFILE:-/tmp/roamio-gunicorn-${PORT}.pid}"
ACCESS_LOG="${ACCESS_LOG:-/tmp/gunicorn.access.log}"
ERROR_LOG="${ERROR_LOG:-/tmp/gunicorn.error.log}"

export ROAMIO_SETTINGS="${ROAMIO_SETTINGS:-dev}"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-roamio.settings}"
export PYTHONPATH="${APP_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

if [[ ! -d "${BACKEND_DIR}" ]]; then
  echo "Backend directory not found: ${BACKEND_DIR}" >&2
  exit 1
fi

if [[ -f "${PIDFILE}" ]]; then
  existing_pid="$(cat "${PIDFILE}")"
  if [[ -n "${existing_pid}" ]] && kill -0 "${existing_pid}" 2>/dev/null; then
    echo "Gunicorn already running on ${HOST}:${PORT} with PID ${existing_pid}"
    exit 0
  fi
  rm -f "${PIDFILE}"
fi

mkdir -p "$(dirname "${ACCESS_LOG}")" "$(dirname "${ERROR_LOG}")"

gunicorn roamio.wsgi:application \
  --chdir "${BACKEND_DIR}" \
  --bind "${HOST}:${PORT}" \
  --workers "${WORKERS}" \
  --threads "${THREADS}" \
  --timeout "${TIMEOUT}" \
  --pid "${PIDFILE}" \
  --access-logfile "${ACCESS_LOG}" \
  --error-logfile "${ERROR_LOG}" \
  --capture-output \
  --daemon

echo "Gunicorn started on ${HOST}:${PORT}"
echo "PID file: ${PIDFILE}"
echo "Access log: ${ACCESS_LOG}"
echo "Error log: ${ERROR_LOG}"
