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
- `docs/DEPLOYMENT.md`（生产部署手册）
- `docs/guides/FRONTEND_THEME_SPEC.md`（前端主题规范）
- `docs/guides/NGINX_GUNICORN_PROXY.md`（Nginx + Gunicorn HTTP 代理）

Do not treat old planning or integration documents as source of truth until audited.

## Stack

- Backend: Django, Django REST Framework, Simple JWT
- Frontend: Vue 3, Vue Router, Pinia, Bootstrap
- Optional integrations: DeepSeek AI, Tencent COS, QQ OAuth, Ralendar

## Main Entry Points

- Backend settings: `roamio/settings/`
- Backend routes: `roamio/urls.py`
- Backend command entry: `cd backend && python manage.py ...`
- Root command shim: `python manage.py ...` remains as transition compatibility only.
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

The root `manage.py` is a thin compatibility shim. Prefer the `backend/` workspace for new local, CI, and deployment commands.

AI trip generation uses DeepSeek's OpenAI-compatible Chat Completions API. To enable it, put these values in the runtime `.env` file on the machine that runs Django:

```bash
AI_GENERATION_ENABLED=True
DEEPSEEK_API_KEY=replace-with-your-real-key
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_API_TIMEOUT=45
AI_MAX_TOKENS=5000
```

Do not commit the real key. `deepseek-v4-flash` is the recommended production model for faster structured JSON generation; `deepseek-v4-pro` can be used for slower, deeper generation if the timeout and token budget are increased. The old `QWEN_API_KEY` and `QWEN_MODEL` variables are no longer used.

Map SDK pickers and geocoding are currently disabled. Location UI falls back to copying the place name and opening provider search pages without embedded SDK keys. Weather/IP location is also disabled by default in production (`frontend/web/.env.production` sets `VITE_WEATHER_ENABLED=false`); only set it to `true` and provide `AMAP_API_KEY` if the weather feature is reopened.

Linux production deploys should install:

```bash
pip install -r requirements-prod.txt
```

Production app serving defaults to Gunicorn over local HTTP on `127.0.0.1:8000`. Nginx must proxy to that endpoint with `proxy_pass http://127.0.0.1:8000;`. Keep the uWSGI config only as the rollback path.

```bash
ROAMIO_SETTINGS=dev bash scripts/start_gunicorn.sh
bash scripts/healthcheck.sh
bash scripts/stop_gunicorn.sh
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

For production deployment, prefer the checked Gunicorn script over manual command sequences:

```bash
cd /home/acs/roamio
ROAMIO_SETTINGS=prod bash scripts/deploy_gunicorn.sh
```

The deploy script aborts when the working tree is dirty. To temporarily stash and restore local server changes:

```bash
ROAMIO_SETTINGS=prod AUTO_STASH=1 bash scripts/deploy_gunicorn.sh
```

The script pulls the configured branch, runs `cd backend && python manage.py check`, builds the Vite bundle, stops uWSGI, starts Gunicorn on local HTTP `127.0.0.1:8000`, and runs local health checks:

```text
/
/api/v1/auth/me/
/api/v1/auth/qq_login_url/
```

During the maintenance window, Nginx must be changed from `uwsgi_pass 127.0.0.1:8000` to `proxy_pass http://127.0.0.1:8000` and reloaded. Public HTTPS may return 502 between stopping uWSGI and reloading Nginx; this is expected until the proxy protocol switch is complete. See `docs/guides/NGINX_GUNICORN_PROXY.md`.

### Common Production Issues

- `413 Payload Too Large`: the upload was rejected before Django handled it. Check Nginx `client_max_body_size`, then retry with a smaller image/video. Frontend upload errors should surface this as a file-too-large message.
- `401 Unauthorized`: check whether the refresh cookie is present and whether `/api/v1/auth/refresh/` succeeds. For OAuth-related failures, verify Redis/cache and `QQ_REDIRECT_URI`.
- Upload API returns field errors: inspect the JSON `detail` or field key such as `avatar`; frontend upload screens prioritize these messages.

### Rollback

Rollback keeps the old uWSGI path available. Restore the Nginx `uwsgi_pass` block, reload Nginx, then return to a known-good revision and run the uWSGI deploy script:

```bash
cd /home/acs/roamio
git log --oneline -5
git checkout <known-good-commit>
ROAMIO_SETTINGS=prod bash scripts/deploy_uwsgi.sh
```

If only the Gunicorn process is unhealthy and code is unchanged, restart it directly:

```bash
bash scripts/stop_gunicorn.sh
ROAMIO_SETTINGS=prod bash scripts/start_gunicorn.sh
BASE_URL=http://127.0.0.1:8000 bash scripts/healthcheck.sh
```

If rolling back to uWSGI, restart uWSGI directly after restoring Nginx:

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
