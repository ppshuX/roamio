#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8001}"
PIDFILE="${PIDFILE:-/tmp/roamio-gunicorn-${PORT}.pid}"
STOP_TIMEOUT="${STOP_TIMEOUT:-10}"

stop_pid() {
  local pid="$1"
  local command_line

  command_line="$(ps -p "${pid}" -o args= 2>/dev/null || true)"
  if [[ "${command_line}" != *"gunicorn"* || "${command_line}" != *"roamio.wsgi:application"* ]]; then
    echo "Refusing to stop PID ${pid}; it does not look like Roamio Gunicorn." >&2
    exit 1
  fi

  kill "${pid}"
  for _ in $(seq 1 "${STOP_TIMEOUT}"); do
    if ! kill -0 "${pid}" 2>/dev/null; then
      return 0
    fi
    sleep 1
  done

  echo "Gunicorn PID ${pid} did not stop after ${STOP_TIMEOUT}s; sending SIGKILL." >&2
  kill -9 "${pid}" 2>/dev/null || true
}

if [[ -f "${PIDFILE}" ]]; then
  pid="$(cat "${PIDFILE}")"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    stop_pid "${pid}"
    rm -f "${PIDFILE}"
    echo "Gunicorn stopped from PID file ${PIDFILE}"
    exit 0
  fi
  rm -f "${PIDFILE}"
fi

if pkill -f "gunicorn.*roamio.wsgi:application.*${HOST}:${PORT}" 2>/dev/null; then
  echo "Gunicorn stopped by process pattern on ${HOST}:${PORT}"
else
  echo "No Gunicorn process found for ${HOST}:${PORT}"
fi
