# M4 Route Boundary Freeze Matrix

Updated: 2026-05-04

## Scope

This document is the M4 baseline for route governance after PR-A/PR-B/PR-C.
It focuses on:

1. Which route surfaces are active mainline.
2. Which legacy surfaces are compatibility-only.
3. What can be frozen now.
4. What can be removed only after production usage confirmation.

---

## Route Surfaces

### A. Mainline (continue evolving)

- Prefix: `/api/v1/`
- Source: `backend/api/urls.py`
- Backed by DRF routers/viewsets and explicit API views.
- Frontend request base: `frontend/web/src/api/request.js` (`/api/v1`)

Mainline groups:

- `/api/v1/users/`
- `/api/v1/comments/`
- `/api/v1/trips/` (legacy SiteStat compatibility API, still used by frontend)
- `/api/v1/trip-plans/` (new Trip editing/publish mainline)
- `/api/v1/auth/`
- `/api/v1/ralendar/trips/`
- `/api/v1/ralendar-oauth/`
- `/api/v1/ai/`
- `/api/v1/trip-plans/{trip}/events/`
- `/api/v1/token/`, `/api/v1/token/refresh/`
- `/api/v1/weather/`, `/api/v1/location/`
- `/api/v1/ralendar/events/{event_id}/`

### B. Compatibility Layer (freeze now)

Mounted in `roamio/urls.py`:

- `/trips/` -> `backend.urls` (legacy page routes)
- `/cetapp/` -> `backend.urls` (legacy alias)
- `/accounts/login/`, `/accounts/logout/` (legacy account routes)

Decision:

- These endpoints are compatibility-only.
- No new feature work under `backend/views/*` or `backend/urls/*`.
- All net-new backend behavior must be added under `/api/v1/*`.

---

## Frontend Usage Findings

### API wrapper usage (good)

Frontend API modules exist and are active under:

- `frontend/web/src/api/auth.js`
- `frontend/web/src/api/user.js`
- `frontend/web/src/api/trip.js`
- `frontend/web/src/api/tripPlan.js`
- `frontend/web/src/api/comment.js`
- `frontend/web/src/api/ai.js`
- `frontend/web/src/api/events.js`
- `frontend/web/src/api/ralendar.js`
- `frontend/web/src/api/ralendarOAuth.js`

### Direct fetch usage (needs consolidation)

Still found in component layer:

- `frontend/web/src/components/events/GlobalSidebar.vue`
  - `/api/v1/ralendar/trips/events/`
  - `/api/v1/ralendar/trips/events/create/`
  - `/api/v1/ralendar/events/{id}/`
- `frontend/web/src/components/WeatherWidget.vue`
  - `/api/v1/location/`
  - `/api/v1/weather/?location=...`

Action:

- Move these calls into `frontend/web/src/api/*` wrappers.
- Keep component layer free of raw endpoint strings.

---

## Freeze Matrix

### Keep and iterate

- `/api/v1/trip-plans/*` (authoring mainline)
- `/api/v1/auth/*`
- `/api/v1/users/*`
- `/api/v1/comments/*`
- `/api/v1/ai/*`
- `/api/v1/ralendar-*`

### Keep but mark compatibility

- `/api/v1/trips/*` (SiteStat tree compatibility)

Rule:

- Do not add new product capability here unless explicitly approved as compatibility debt.

### Freeze and deprecate (no new logic)

- `/trips/*`
- `/cetapp/*`
- `/accounts/login/`
- `/accounts/logout/`
- legacy handlers under `backend/views/*` and `backend/urls/*`

---

## Removal Gates (must satisfy before deleting legacy mounts)

All gates must pass:

1. **Frontend gate**: no active references to legacy mounts in `frontend/web/src`.
2. **Ops gate**: Nginx/access logs confirm no meaningful production traffic for a full observation window.
3. **Docs gate**: user-facing docs and bookmarks are migrated to `/` + `/api/v1/*`.
4. **Rollback gate**: rollback path documented (re-enable include paths quickly).

Only after all gates pass:

- Remove `/trips/` and `/cetapp/` includes from `roamio/urls.py`.
- Remove unused legacy handlers in `backend/views/*`.

---

## Immediate M4 Tasks

1. Add a small deprecation note block in `roamio/urls.py` for legacy includes (frozen status + removal gates).
2. Refactor direct `fetch` usage in `GlobalSidebar.vue` and `WeatherWidget.vue` into API wrapper modules.
3. Keep `/api/v1/trips/*` as compatibility API and document that new features go to `/api/v1/trip-plans/*`.

