# Roamio Production Deployment

This is the current production runbook for the Django + Vue deployment on the
Ubuntu server.

## Current Topology

- App root: `/home/acs/roamio`
- Django settings mode: `ROAMIO_SETTINGS=prod`
- Database mode on the current server: `ROAMIO_USE_SQLITE=1`
- Gunicorn HTTP bind: `127.0.0.1:8000`
- Nginx public HTTPS: `https://roamio.cn` and `https://www.roamio.cn`
- Frontend build output: `backend/web_dist/`
- Gunicorn access log: `/tmp/gunicorn.access.log`
- Gunicorn error log: `/tmp/gunicorn.error.log`
- Django application error log: `/home/acs/roamio/django_errors.log`

Nginx must proxy HTTP to Gunicorn with `proxy_pass http://127.0.0.1:8000;`.
Do not use `uwsgi_pass` when Gunicorn is running.

## One-Time Server Setup

Install Python and production dependencies:

```bash
cd ~/roamio
python3 -m pip install --user -r requirements-prod.txt
python3 -m pip install --user gunicorn
```

If `gunicorn` is installed under `~/.local/bin`, keep that path available when
starting the app:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Install frontend dependencies from the frontend workspace:

```bash
cd ~/roamio/frontend/web
npm install
```

## Required `.env`

The server runtime environment is read from `~/roamio/.env`.

Minimum production values:

```bash
DEBUG=False
ALLOWED_HOSTS=roamio.cn,www.roamio.cn,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://roamio.cn,https://www.roamio.cn
ROAMIO_USE_SQLITE=1

AI_GENERATION_ENABLED=True
DEEPSEEK_API_KEY=replace-with-real-key
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_API_TIMEOUT=45
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.7

VUE_APP_BAIDU_MAP_KEY=
VUE_APP_AMAP_KEY=
AMAP_API_KEY=
```

Do not commit real keys. Do not paste real keys into issues, PRs, or chat logs.

`deepseek-v4-flash` is the recommended production model. It is faster and more
reliable for structured JSON trip generation. `deepseek-v4-pro` can time out or
return truncated JSON for this workload unless timeout and token budget are
raised.

Map SDKs and geocoding are intentionally disabled. Weather and IP location are
also disabled by default unless `frontend/web/.env.production` is changed to
`VITE_WEATHER_ENABLED=true` and `AMAP_API_KEY` is configured.

## Standard Deploy

Use this after code has been pushed to the branch deployed on the server:

```bash
cd ~/roamio
git pull

cd frontend/web
npm run build
sudo nginx -t
sudo nginx -s reload

cd ~/roamio
bash scripts/stop_gunicorn.sh
PATH="$HOME/.local/bin:$PATH" ROAMIO_SETTINGS=prod ROAMIO_USE_SQLITE=1 bash scripts/start_gunicorn.sh
```

Run the health checks:

```bash
cd ~/roamio
bash scripts/healthcheck.sh

curl -I https://roamio.cn/
curl -i --max-time 15 https://roamio.cn/api/v1/trips/
```

If only backend Python code changed, `npm run build` is not required.

## Scripted Deploy Option

The deploy script can pull, check Django, build frontend assets, stop uWSGI,
start Gunicorn, and run local health checks:

```bash
cd ~/roamio
PATH="$HOME/.local/bin:$PATH" BRANCH="$(git branch --show-current)" ROAMIO_SETTINGS=prod ROAMIO_USE_SQLITE=1 bash scripts/deploy_gunicorn.sh
```

Use the manual deploy path when debugging Nginx, environment variables, or
Gunicorn process ownership.

## Nginx Shape

The public server block should serve static frontend files and proxy API/admin
requests to Gunicorn HTTP. The exact SSL certificate paths are server-specific,
but app routing should follow this shape:

```nginx
root /home/acs/roamio/backend/web_dist;
index index.html;

location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_connect_timeout 60;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
}

location /admin/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_connect_timeout 60;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
}

location /assets/ {
    alias /home/acs/roamio/backend/web_dist/assets/;
    expires 7d;
    add_header Cache-Control "public, immutable";
}

location / {
    try_files $uri $uri/ /index.html;
}
```

The root for the SPA must point at `backend/web_dist`.

For the full proxy migration notes, see `docs/guides/NGINX_GUNICORN_PROXY.md`.

## Verification Checklist

Check local Gunicorn:

```bash
ss -ltnp | grep ':8000' || echo "8000 is not listening"
ps aux | grep -E 'gunicorn|uwsgi|manage.py|127.0.0.1:8000|:8000' | grep -v grep
curl -i --max-time 15 http://127.0.0.1:8000/api/v1/trips/ -H "Host: roamio.cn" -H "X-Forwarded-Proto: https"
```

Check public HTTPS:

```bash
curl -I https://roamio.cn/
curl -i --max-time 15 https://roamio.cn/api/v1/trips/
curl -s https://roamio.cn/ | grep -E "api.map.baidu.com|webapi.amap.com|i8UmOot|91443|53b6" || echo "public html clean"
```

Check AI connectivity without exposing the key:

```bash
cd ~/roamio
set -a
source .env
set +a

curl -sS --max-time 20 https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$DEEPSEEK_MODEL"'",
    "messages": [{"role":"user","content":"Reply only OK"}],
    "max_tokens": 20
  }'
```

Expected result: JSON containing `choices`. A plain `401` or
`invalid_api_key` means the key is invalid or not loaded.

## Common Issues

### `Missing command: gunicorn`

Install Gunicorn and make sure `~/.local/bin` is on `PATH`:

```bash
python3 -m pip install --user gunicorn
PATH="$HOME/.local/bin:$PATH" python3 -m gunicorn --version
```

### `curl: (52) Empty reply from server`

Usually Nginx is still using `uwsgi_pass` while Gunicorn is serving HTTP, or
the old uWSGI process still owns `127.0.0.1:8000`.

Check the port owner:

```bash
ss -ltnp | grep ':8000'
```

If old uWSGI is still present:

```bash
pkill -f 'uwsgi --env ROAMIO_SETTINGS=prod' || true
```

If one old master remains, stop it by PID after confirming it is uWSGI:

```bash
ps aux | grep uwsgi | grep -v grep
kill <pid>
```

### `400 Bad Request` from local health check

Check `ALLOWED_HOSTS` and use the expected host header:

```bash
grep '^ALLOWED_HOSTS=' ~/roamio/.env
curl -i http://127.0.0.1:8000/api/v1/trips/ -H "Host: roamio.cn" -H "X-Forwarded-Proto: https"
```

### Public API times out but local Gunicorn works

Nginx is probably not proxying HTTP to Gunicorn correctly. Recheck:

```bash
sudo nginx -t
sudo nginx -s reload
sudo tail -n 80 /var/log/nginx/roamio_error.log
tail -n 40 /tmp/gunicorn.access.log
```

### AI generation returns 400

DeepSeek returned JSON that could not be parsed, often because the output was
truncated. Keep the production model on `deepseek-v4-flash` and keep
`AI_MAX_TOKENS` near `4000` to reduce this risk.

Inspect:

```bash
tail -n 160 ~/roamio/django_errors.log
```

### AI generation returns 500 or 504

Check the Django log first:

```bash
tail -n 160 ~/roamio/django_errors.log
```

Typical causes:

- `Read timed out`: DeepSeek was slow. Retry or keep using `deepseek-v4-flash`.
- `invalid_api_key` or `401`: the key is wrong or not loaded.
- `model not found`: `DEEPSEEK_MODEL` is wrong for the account.

### Weather or location returns disabled

This is expected while map/weather services are downgraded. The frontend should
not automatically call weather endpoints in production unless
`VITE_WEATHER_ENABLED=true`.

## Rollback

For application rollback:

```bash
cd ~/roamio
git log --oneline -10
git checkout <known-good-commit>

bash scripts/stop_gunicorn.sh
PATH="$HOME/.local/bin:$PATH" ROAMIO_SETTINGS=prod ROAMIO_USE_SQLITE=1 bash scripts/start_gunicorn.sh
```

If frontend files changed in the rollback target:

```bash
cd ~/roamio/frontend/web
npm run build
sudo nginx -s reload
```

The legacy uWSGI path should only be used as an emergency rollback. If using it,
restore the Nginx `uwsgi_pass` block first, then run the uWSGI scripts.
