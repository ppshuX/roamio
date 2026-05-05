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
- Backend command entry: `backend/manage.py`
- Root command shim: `manage.py` forwards to `backend/manage.py` during the transition.
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
cd backend
python manage.py migrate
python manage.py runserver
```

Linux production deploys should install:

```bash
pip install -r requirements-prod.txt
```

Gunicorn migration Batch A is preparation only. It starts Gunicorn on a temporary local port and does not switch Nginx traffic away from the current uWSGI upstream.

```bash
PORT=8001 ROAMIO_SETTINGS=dev bash scripts/start_gunicorn.sh
PORT=8001 bash scripts/healthcheck.sh
PORT=8001 bash scripts/stop_gunicorn.sh
```

Gunicorn writes access logs to `/tmp/gunicorn.access.log` and error logs to `/tmp/gunicorn.error.log` by default.

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

## Production Deploy

For the current uWSGI deployment path, prefer the checked script over manual command sequences:

```bash
cd /home/acs/roamio
ROAMIO_SETTINGS=prod bash scripts/deploy_uwsgi.sh
```

The deploy script aborts when the working tree is dirty. To temporarily stash and restore local server changes:

```bash
ROAMIO_SETTINGS=prod AUTO_STASH=1 bash scripts/deploy_uwsgi.sh
```

The script pulls the configured branch, runs `backend/manage.py check`, builds the Vite bundle, restarts uWSGI, and checks:

```text
/
/api/v1/auth/me/
/api/v1/auth/qq_login_url/
```

### Common Production Issues

- `413 Payload Too Large`: the upload was rejected before Django handled it. Check Nginx `client_max_body_size`, then retry with a smaller image/video. Frontend upload errors should surface this as a file-too-large message.
- `401 Unauthorized`: check whether the refresh cookie is present and whether `/api/v1/auth/refresh/` succeeds. For OAuth-related failures, verify Redis/cache and `QQ_REDIRECT_URI`.
- Upload API returns field errors: inspect the JSON `detail` or field key such as `avatar`; frontend upload screens prioritize these messages.

### Rollback

Minimal uWSGI rollback is to return to the previous Git revision and rerun the same deploy script:

```bash
cd /home/acs/roamio
git log --oneline -5
git checkout <known-good-commit>
ROAMIO_SETTINGS=prod bash scripts/deploy_uwsgi.sh
```

If only the process is unhealthy and code is unchanged, restart uWSGI directly:

```bash
bash scripts/start_uwsgi.sh
```

## Security

Never commit real credentials. Any secret that appeared in this repository should be considered exposed and rotated.

Use `.env.example` only as a placeholder template. Real local values belong in `.env`, which must not be committed.

## Cleanup Rules

- New backend behavior should go under `/api/v1/`.
- Legacy `backend/views/` and `backend/urls/` routes are frozen.
- Do not add new historical summary docs.
- Prefer small current docs under `docs/remediation/`.
