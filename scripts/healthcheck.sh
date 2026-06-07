#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"
BASE_URL="${BASE_URL:-http://127.0.0.1:${PORT}}"

check_head() {
  local path="$1"
  local url="${BASE_URL}${path}"

  curl -fsSI "${url}" >/dev/null
  echo "PASS HEAD ${url}"
}

check_status() {
  local path="$1"
  local url="${BASE_URL}${path}"
  local status

  status="$(curl -sS -o /dev/null -w "%{http_code}" "${url}")"
  case "${status}" in
    200|301|302|401|403)
      echo "PASS GET ${url} -> ${status}"
      ;;
    *)
      echo "FAIL GET ${url} -> ${status}" >&2
      exit 1
      ;;
  esac
}

check_qq_login_url() {
  local url="${BASE_URL}/api/v1/auth/qq_login_url/"
  local body

  body="$(curl -fsS "${url}")"
  if [[ "${body}" != *"authorize_url"* ]]; then
    echo "FAIL GET ${url}: missing authorize_url" >&2
    exit 1
  fi
  echo "PASS GET ${url} -> authorize_url present"
}

check_head "/"
check_status "/api/v1/auth/me/"
check_qq_login_url
