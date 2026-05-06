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
- [11_M4_ROUTE_BOUNDARY_FREEZE.md](11_M4_ROUTE_BOUNDARY_FREEZE.md) - M4 route governance matrix: mainline `/api/v1`, compatibility freeze scope, and legacy removal gates.
- [12_FRONTEND_SCRIPT_SETUP_STANDARD.md](12_FRONTEND_SCRIPT_SETUP_STANDARD.md) - Frontend Vue 3 `<script setup>` coding standard, migration batches, and PR quality gates.
- [15_GUNICORN_MIGRATION_REMEDIATION.md](15_GUNICORN_MIGRATION_REMEDIATION.md) - **部署栈主线规格**：`Nginx+uWSGI` → `Nginx+Gunicorn`（批次 / 验收 / 回滚）。
- [18_CODEX_RUNBOOK_GUNICORN_MIGRATION.md](18_CODEX_RUNBOOK_GUNICORN_MIGRATION.md) - **推荐给 Codex 的部署主线入口**（Batch A PR、人肉 B/C、`15` 与 `16` 排期说明、Prompt）。
- [16_CODEX_RUNBOOK_BATCH_SECURITY_BACKUP_CI.md](16_CODEX_RUNBOOK_BATCH_SECURITY_BACKUP_CI.md) - **整改小包**（模板 / 密钥扫描 / SQLite 备份脚本占位 / CI smoke）；**不改变**「Gunicorn 优先」。

## 当前整改排期共识（部署 vs 细水长流）

| 优先级 | 主题 | 入口 |
|--------|------|------|
| **高（部署栈大迁移）** | uWSGI → Gunicorn，切 Nginx upstream、可回滚 | **[15](15_GUNICORN_MIGRATION_REMEDIATION.md)**，Codex 用 **[18](18_CODEX_RUNBOOK_GUNICORN_MIGRATION.md)** |
| **中（仓库卫生）** | 模板、扫描脚本、`backend.tests` 薄片 | [16](16_CODEX_RUNBOOK_BATCH_SECURITY_BACKUP_CI.md) |
| **视产品** | Vite / M4 路由冻结 | [10](10_RESTRUCTURE_VITE_CODEX_SPEC.md)、[11](11_M4_ROUTE_BOUNDARY_FREEZE.md) |

说明：**SQLite / `.env` 顺序**等是云库不可用时的**止血**，**不顶替** Gunicorn 这条部署主线。

## Working Rules

1. Confirm facts before changing code.
2. Stop the bleeding before refactoring.
3. Restore runnable, verifiable, deployable behavior before pursuing architecture polish.
4. Tie each cleanup change to a clear problem and a verification result.
5. Avoid mixing security, architecture, product behavior, and styling changes in the same cleanup slice.

## Current Direction

The first remediation pass is not a rewrite. The immediate target is to make the project safe to inspect, runnable locally, and easier to verify. Larger business-boundary refactors should happen only after the core startup path, settings boundary, and route surface are stable.
