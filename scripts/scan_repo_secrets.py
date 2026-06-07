#!/usr/bin/env python3
"""Cross-platform lightweight repository secret scan."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_FILE = Path(os.environ.get("ALLOWLIST_FILE", ROOT / "scripts" / "secret_scan_allowlist.txt"))

SECRET_RE = re.compile(
    r"("
    r"AKIA[0-9A-Z]{16}|"
    r"sk-[A-Za-z0-9_-]{20,}|"
    r"AIza[0-9A-Za-z_-]{35}|"
    r"(?:SECRET_KEY|DB_PASSWORD|EMAIL_HOST_PASSWORD|QQ_APP_KEY|"
    r"TENCENT_COS_SECRET_ID|TENCENT_COS_SECRET_KEY|DEEPSEEK_API_KEY|QWEN_API_KEY|"
    r"AMAP[_A-Z]*KEY|BAIDU[_A-Z]*AK|VITE_[A-Z_]*(?:KEY|AK|CODE)|"
    r"PINGPP_(?:API_KEY|TEST_API_KEY|APP_ID)|RALENDAR_OAUTH_CLIENT_SECRET|"
    r"client_secret|api_key|APP_KEY|SecretId|SecretKey|securityJsCode)"
    r"\s*[:=]\s*['\"]?[^'\"\s#<>]+"
    r")"
)

PLACEHOLDER_RE = re.compile(
    r"replace-with-|placeholder|example\.com|localhost|127\.0\.0\.1|"
    r"YOUR_|your-|same-[a-z0-9-]+|dummy|fake|changeme|change-me|leave-empty|"
    r"noreply@example\.com|你的生产密钥|%VITE_[A-Z_]+%|_get_[A-Za-z0-9_]+\(",
    re.IGNORECASE,
)

REFERENCE_RE = re.compile(
    r"os\.getenv\(|require_env\(|settings\.[A-Z0-9_]+|models\.CharField|"
    r"self\.[a-z_]*api_key|api_key\s*=\s*self\.[a-z_]*api_key|"
    r"[A-Z0-9_]*(?:SECRET|KEY|PASSWORD|TOKEN|ID|AK):(?:\s|$)|looks\s+like|看起来像",
    re.IGNORECASE,
)

EXCLUDED_PARTS = {
    ".git",
    "node_modules",
    "backend/web_dist",
    "frontend/web/dist",
    "dist",
    "build",
    "staticfiles",
}

EXCLUDED_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "db.sqlite3",
    "scan_repo_secrets.py",
    "scan_repo_secrets.sh",
    "secret_scan_allowlist.txt",
}


def git_files() -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return [p for p in ROOT.rglob("*") if p.is_file()]
    return [ROOT / line for line in output.splitlines() if line]


def is_excluded(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if path.name in EXCLUDED_NAMES or path.suffix == ".lock":
        return True
    return any(rel == part or rel.startswith(f"{part}/") for part in EXCLUDED_PARTS)


def load_allowlist() -> list[str]:
    if not ALLOWLIST_FILE.exists():
        return []
    entries = []
    for raw in ALLOWLIST_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            entries.append(line)
    return entries


def is_allowed(finding: str, allowlist: list[str]) -> bool:
    return (
        PLACEHOLDER_RE.search(finding) is not None
        or REFERENCE_RE.search(finding) is not None
        or any(item in finding for item in allowlist)
    )


def main() -> int:
    allowlist = load_allowlist()
    findings = []

    for path in git_files():
        if not path.exists() or is_excluded(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, 1):
            if SECRET_RE.search(line):
                finding = f"{rel}:{lineno}:{line.strip()}"
                if not is_allowed(finding, allowlist):
                    findings.append(finding)

    if findings:
        print("[secret-scan] Potential secrets found:", file=sys.stderr)
        for finding in findings:
            print(finding, file=sys.stderr)
        print(f"[secret-scan] Review findings. Allowlist only false positives: {ALLOWLIST_FILE}", file=sys.stderr)
        return 1

    print("[secret-scan] No obvious secrets found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
