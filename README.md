# Roamio

Roamio is a Django + Vue travel planning and sharing project. The project is currently in remediation mode: security cleanup, structure slimming, route boundary clarification, and local development recovery are the priority before adding new features.

## Current Status

Active cleanup docs live in:

- `docs/remediation/README.md`
- `docs/remediation/01_PROBLEM_INVENTORY.md`
- `docs/remediation/02_REMEDIATION_PLAN.md`
- `docs/remediation/03_ROADMAP.md`
- `docs/remediation/04_SLIMMING_CANDIDATES.md`
- `docs/remediation/05_SECURITY_CLEANUP.md`
- `docs/remediation/06_ROUTE_USAGE_AUDIT.md`
- `docs/remediation/07_SETTINGS_SPLIT.md`

Do not treat old planning or integration documents as source of truth until audited.

## Stack

- Backend: Django, Django REST Framework, Simple JWT
- Frontend: Vue 3, Vue Router, Pinia, Bootstrap
- Optional integrations: Qwen/DashScope AI, Tencent COS, QQ OAuth, Ralendar

## Main Entry Points

- Backend settings: `roamio/settings/`
- Backend routes: `roamio/urls.py`
- API routes: `backend/api/urls.py`
- Frontend app: `frontend/web/src/main.js`
- Frontend routes: `frontend/web/src/router/index.js`
- Frontend API wrappers: `frontend/web/src/api/`
- Frontend build output: `backend/web_dist/`

## Local Development

Backend:

```bash
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Linux production deploys that still use uWSGI should install:

```bash
pip install -r requirements-prod.txt
```

Frontend:

```bash
cd frontend/web
npm install
npm run serve
```

Build frontend:

```bash
cd frontend/web
npm run build
```

The Vite build writes the SPA bundle to `backend/web_dist/`, which is the directory Django and deployment configs should serve.

## Security

Never commit real credentials. Any secret that appeared in this repository should be considered exposed and rotated.

Use `.env.example` only as a placeholder template. Real local values belong in `.env`, which must not be committed.

## Cleanup Rules

- New backend behavior should go under `/api/v1/`.
- Legacy `backend/views/` and `backend/urls/` routes are frozen.
- Do not add new historical summary docs.
- Prefer small current docs under `docs/remediation/`.
