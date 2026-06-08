# Roamio Docs

Updated: 2026-05-04

This directory is being slimmed down as part of the Roamio remediation work. Historical planning, deployment notes, private migration notes, and promotional summaries are no longer treated as source-of-truth documentation.

## Current Source Of Truth

- `docs/remediation/README.md` - cleanup workspace and active remediation index.
- `docs/remediation/01_PROBLEM_INVENTORY.md` - current problem inventory.
- `docs/remediation/02_REMEDIATION_PLAN.md` - remediation strategy.
- `docs/remediation/03_ROADMAP.md` - execution roadmap.
- `docs/remediation/04_SLIMMING_CANDIDATES.md` - deleted content and remaining candidates.
- `docs/remediation/05_SECURITY_CLEANUP.md` - security cleanup record.
- `docs/remediation/06_ROUTE_USAGE_AUDIT.md` - current API and route usage audit.
- `docs/remediation/07_SETTINGS_SPLIT.md` - Django settings split and environment boundary.
- `docs/remediation/08_DEPENDENCY_TRIM.md` - dependency slimming notes.
- `docs/remediation/09_SECOND_DOC_CLEANUP.md` - second sensitive/stale documentation cleanup pass.
- `docs/DEPLOYMENT.md` - current production deployment runbook.

## Reference Docs Still Kept

- `docs/api/ECOSYSTEM_API_DOCUMENTATION.md`
- `docs/guides/`
- `docs/integration/`
- `docs/ecosystem/`

These reference docs are not guaranteed to be fully current. Treat them as background material until each one is audited.

## Documentation Rules Going Forward

1. Do not add secrets, server IPs, database hosts, credentials, or real tokens.
2. Prefer short current documents over long historical summaries.
3. Put cleanup and migration decisions under `docs/remediation/`.
4. Delete obsolete docs instead of preserving them as active documentation.
5. Use Git history for historical context.
