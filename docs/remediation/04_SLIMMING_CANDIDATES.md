# Roamio Slimming Candidates

Updated: 2026-05-04

This file records content that can be deleted, frozen, or merged during the cleanup. The rule is simple: delete only when there is clear evidence; keep risky business modules on a candidate list until their runtime usage is known.

## Done: Round 1 Safe Slimming

Deleted full duplicate directory:
- `roamio-master/`

Deleted duplicate utility files from `backend/utils/` root:
- `backend/utils/email_service.py`
- `backend/utils/qq_oauth.py`
- `backend/utils/rate_limit.py`
- `backend/utils/tencent_cos.py`
- `backend/utils/file_upload_handler.py`
- `backend/utils/avatar_downloader.py`
- `backend/utils/trip_utils.py`

Kept canonical utility packages:
- `backend/utils/auth/`
- `backend/utils/external/`
- `backend/utils/storage/`
- `backend/utils/helpers/`
- `backend/utils/ai/`

Deleted old Vuex store:
- `frontend/web/src/store/index.js`

Reason:
- Current frontend uses Pinia in `frontend/web/src/stores/`.
- No live import of `@/store` was found.

## Done: Round 2 Security Document Slimming

Deleted tracked high-risk documents:
- `docs/AI_INTEGRATION_MILESTONE.md`
- `docs/SECURITY_CHECKLIST.md`
- `docs/ecosystem/ROAMIO_DATABASE_INFO_FOR_RALENDAR.md`
- `docs/ecosystem/ROAMIO_INTEGRATION_REPORT.md`
- `docs/ecosystem/INTEGRATION_CHECKLIST.md`
- `docs/summaries/DAILY_SUMMARY_20251113.md`

Deleted local untracked private deployment materials:
- `cloud_settings/`

Reason:
- These files contained real or real-looking secrets, server addresses, database hosts, database passwords, OAuth keys, email authorization codes, or migration records.
- They were historical operational notes, not current source-of-truth engineering docs.

Security cleanup record:
- `docs/remediation/05_SECURITY_CLEANUP.md`

## Done: Round 3 Documentation Slimming

Deleted outdated planning/status documents:
- `docs/AI_DEPLOYMENT_CHECKLIST.md`
- `docs/AI_MVP_DEPLOYMENT.md`
- `docs/AI_MVP_SUMMARY.md`
- `docs/AI_PHASE2_RAG_PLAN.md`
- `docs/AI_ROADMAP.md`
- `docs/AI_TRIP_PLANNER.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/summaries/PROJECT_STATUS.md`
- `docs/guides/TENCENT_COS_SETUP.md`

Replaced `docs/README.md` with a small current index.
Replaced root `README.md` with a small remediation-focused project entry.
Replaced root `.env.example` with a pure placeholder template.

Reason:
- These files mixed historical planning, aspirational roadmap content, stale project state, and implementation notes that no longer match the codebase.
- Active cleanup documentation now lives under `docs/remediation/`.

## Candidate: Complex or Unfinished Features

These modules may need to be frozen or removed, but should not be deleted blindly because models and migrations may affect existing databases.

Candidates:
- Billing/subscription: `backend/models/payment.py`, `backend/models/subscription.py`
- Deep Ralendar integration: `backend/api/viewsets/ralendar_*`, `backend/api/views/ralendar_events.py`
- Temporary redirect page: `frontend/web/src/views/RedirectPage.vue` and `/2025_review`
- Legacy compatibility views/urls: `backend/views/`, `backend/urls/`

Recommendation:
- Freeze route entry points first.
- Remove frontend entry points next.
- Only then consider model and migration cleanup.
