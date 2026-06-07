#!/usr/bin/env sh
set -eu

# Lightweight repository secret scan.
#
# Allowlist format:
# - Optional file: scripts/secret_scan_allowlist.txt
# - Blank lines and lines starting with "#" are ignored.
# - Each remaining line is treated as a literal substring matched against the
#   full finding line: "path:line:content". Matching findings are suppressed.
# - Use this only for reviewed placeholders or known false positives; do not
#   allowlist real secrets.

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
ALLOWLIST_FILE="${ALLOWLIST_FILE:-${ROOT_DIR}/scripts/secret_scan_allowlist.txt}"

PATTERN='(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{35}|(SECRET_KEY|DB_PASSWORD|EMAIL_HOST_PASSWORD|QQ_APP_KEY|TENCENT_COS_SECRET_ID|TENCENT_COS_SECRET_KEY|DEEPSEEK_API_KEY|QWEN_API_KEY|AMAP[_A-Z]*KEY|PINGPP_(API_KEY|TEST_API_KEY|APP_ID)|RALENDAR_OAUTH_CLIENT_SECRET|client_secret|api_key|APP_KEY|SecretId|SecretKey)[[:space:]]*[:=][[:space:]]*[^[:space:]#]+)'
PLACEHOLDER_FILTER='replace-with-|placeholder|example\.com|localhost|127\.0\.0\.1|YOUR_|your-|same-as-|dummy|fake|changeme|change-me|leave-empty|noreply@example\.com'
PATH_FILTER='(^|/)(\.git|node_modules|backend/web_dist|frontend/web/dist|dist|build|staticfiles)(/|$)|(^|/)db\.sqlite3$|(^|/)[^/]*(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|.*\.lock)$'

cd "${ROOT_DIR}"

search_with_rg() {
  rg --hidden --line-number --no-heading --color never \
    --glob '!**/.git/**' \
    --glob '!**/node_modules/**' \
    --glob '!backend/web_dist/**' \
    --glob '!frontend/web/dist/**' \
    --glob '!dist/**' \
    --glob '!build/**' \
    --glob '!staticfiles/**' \
    --glob '!**/*.lock' \
    --glob '!**/package-lock.json' \
    --glob '!**/yarn.lock' \
    --glob '!**/pnpm-lock.yaml' \
    --glob '!**/db.sqlite3' \
    --glob '!scripts/secret_scan_allowlist.txt' \
    -e "${PATTERN}" .
}

search_with_git_grep() {
  git grep -n -I -E "${PATTERN}" -- . \
    ':(exclude).git/**' \
    ':(exclude)node_modules/**' \
    ':(exclude)backend/web_dist/**' \
    ':(exclude)frontend/web/dist/**' \
    ':(exclude)dist/**' \
    ':(exclude)build/**' \
    ':(exclude)staticfiles/**' \
    ':(exclude)*.lock' \
    ':(exclude)package-lock.json' \
    ':(exclude)yarn.lock' \
    ':(exclude)pnpm-lock.yaml' \
    ':(exclude)scripts/secret_scan_allowlist.txt' \
    ':(exclude)db.sqlite3'
}

search_with_grep() {
  grep -RInE "${PATTERN}" . \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=backend/web_dist \
    --exclude-dir=dist \
    --exclude-dir=build \
    --exclude-dir=staticfiles \
    --exclude='*.lock' \
    --exclude='package-lock.json' \
    --exclude='yarn.lock' \
    --exclude='pnpm-lock.yaml' \
    --exclude='secret_scan_allowlist.txt' \
    --exclude='db.sqlite3'
}

run_search() {
  if command -v rg >/dev/null 2>&1; then
    search_with_rg
  elif git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    search_with_git_grep
  else
    search_with_grep
  fi
}

findings="$(
  run_search 2>/dev/null \
    | grep -Ev "${PATH_FILTER}" \
    | grep -Eiv "${PLACEHOLDER_FILTER}" \
    | grep -Fv "scripts/scan_repo_secrets.sh:" \
    | grep -Fv "scripts/secret_scan_allowlist.txt:" || true
)"

if [ -n "${findings}" ] && [ -f "${ALLOWLIST_FILE}" ]; then
  allowlist="$(grep -Ev '^[[:space:]]*(#|$)' "${ALLOWLIST_FILE}" || true)"
  if [ -n "${allowlist}" ]; then
    tmp_allowlist="${TMPDIR:-/tmp}/roamio-secret-allowlist.$$"
    printf '%s\n' "${allowlist}" > "${tmp_allowlist}"
    findings="$(printf '%s\n' "${findings}" | grep -vFf "${tmp_allowlist}" || true)"
    rm -f "${tmp_allowlist}"
  fi
fi

if [ -n "${findings}" ]; then
  printf '%s\n' "[secret-scan] Potential secrets found:" >&2
  printf '%s\n' "${findings}" >&2
  printf '%s\n' "[secret-scan] Review findings. Use ${ALLOWLIST_FILE} only for confirmed false positives." >&2
  exit 1
fi

printf '%s\n' "[secret-scan] No obvious secrets found."
