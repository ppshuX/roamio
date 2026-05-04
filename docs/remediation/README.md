# Roamio Remediation

This folder is the working record for the Roamio cleanup. It keeps problem discovery, decisions, slimming notes, and verification separate from product docs.

## Index

- [01_PROBLEM_INVENTORY.md](01_PROBLEM_INVENTORY.md) - Current problem inventory grouped by risk and module.
- [02_REMEDIATION_PLAN.md](02_REMEDIATION_PLAN.md) - Cleanup goals, principles, and phased plan.
- [03_ROADMAP.md](03_ROADMAP.md) - Execution roadmap, milestones, and acceptance criteria.
- [04_SLIMMING_CANDIDATES.md](04_SLIMMING_CANDIDATES.md) - Deletion candidates, removed content, and modules pending confirmation.
- [05_SECURITY_CLEANUP.md](05_SECURITY_CLEANUP.md) - Security cleanup notes and credential rotation checklist.
- [06_ROUTE_USAGE_AUDIT.md](06_ROUTE_USAGE_AUDIT.md) - Frontend API usage and backend route boundary audit.
- [07_SETTINGS_SPLIT.md](07_SETTINGS_SPLIT.md) - Django settings split, environment boundary, and verification notes.
- [08_DEPENDENCY_TRIM.md](08_DEPENDENCY_TRIM.md) - Python dependency slimming and install-path notes.
- [09_SECOND_DOC_CLEANUP.md](09_SECOND_DOC_CLEANUP.md) - Second sensitive/stale documentation cleanup pass.
- [10_RESTRUCTURE_VITE_CODEX_SPEC.md](10_RESTRUCTURE_VITE_CODEX_SPEC.md) - **Single spec**: repo layout (`backend/` + `frontend/`), Vite migration, PR order, optional Django app rename, Codex handoff (中文).

## Working Rules

1. Confirm facts before changing code.
2. Stop the bleeding before refactoring.
3. Restore runnable, verifiable, deployable behavior before pursuing architecture polish.
4. Tie each cleanup change to a clear problem and a verification result.
5. Avoid mixing security, architecture, product behavior, and styling changes in the same cleanup slice.

## Current Direction

The first remediation pass is not a rewrite. The immediate target is to make the project safe to inspect, runnable locally, and easier to verify. Larger business-boundary refactors should happen only after the core startup path, settings boundary, and route surface are stable.
