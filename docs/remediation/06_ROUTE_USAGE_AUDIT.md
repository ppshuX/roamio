# Route And API Usage Audit

Updated: 2026-05-04

## Current Frontend API Base

The frontend request wrapper uses:

- default base URL: `/api/v1`
- file: `frontend/web/src/api/request.js`

This means the current frontend mainline is the DRF API under `backend/api/urls.py`.

## Frontend API Modules In Use

Current API wrappers:
- `frontend/web/src/api/auth.js`
- `frontend/web/src/api/user.js`
- `frontend/web/src/api/trip.js`
- `frontend/web/src/api/tripPlan.js`
- `frontend/web/src/api/comment.js`
- `frontend/web/src/api/ai.js`
- `frontend/web/src/api/events.js`
- `frontend/web/src/api/ralendar.js`
- `frontend/web/src/api/ralendarOAuth.js`

Direct `fetch` calls still exist in:
- `frontend/web/src/components/events/GlobalSidebar.vue`
- `frontend/web/src/components/WeatherWidget.vue`

These should eventually be moved into API wrapper modules.

## Active DRF Route Groups

Registered in `backend/api/urls.py`:
- `/api/v1/users/`
- `/api/v1/comments/`
- `/api/v1/trips/`
- `/api/v1/trip-plans/`
- `/api/v1/auth/`
- `/api/v1/ralendar/trips/`
- `/api/v1/ralendar-oauth/`
- `/api/v1/ai/`
- `/api/v1/trip-plans/{trip}/events/`
- `/api/v1/weather/`
- `/api/v1/location/`
- `/api/v1/ralendar/events/{event_id}/`

## Legacy Compatibility Routes

Mounted in `roamio/urls.py`:
- `/trips/`
- `/cetapp/`
- `/accounts/login/`
- `/accounts/logout/`

These route into `backend.urls` and `backend.views`.

## Freeze Decision

The legacy route layer is frozen.

Rules:
- Do not add new functionality under `backend/views/` or `backend/urls/`.
- New backend behavior must go under `/api/v1/`.
- Legacy routes may remain temporarily for compatibility, but should be removed after confirming they are not used in production.
- Any frontend code that needs data should call `frontend/web/src/api/*`, not direct legacy endpoints.

## Cleanup Candidates From This Audit

Safe next steps:
- Move direct `fetch` calls in `GlobalSidebar.vue` and `WeatherWidget.vue` into API modules.
- Add a short deprecation comment around legacy route includes in `roamio/urls.py`.

Needs confirmation before deletion:
- Removing `/trips/` and `/cetapp/` compatibility mounts.
- Removing `backend/views/` old page handlers.
- Removing old `SiteStat` compatibility endpoints under `/api/v1/trips/`.
