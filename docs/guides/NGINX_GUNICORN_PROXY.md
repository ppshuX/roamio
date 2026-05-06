# Nginx Proxy to Gunicorn

This guide shows the minimal Nginx change for the production app-server switch:

- old: Nginx `uwsgi_pass` to uWSGI protocol on `127.0.0.1:8000`
- new: Nginx `proxy_pass` to Gunicorn HTTP on `127.0.0.1:8000`

## Maintenance Window Warning

When uWSGI has been stopped and Gunicorn is listening on `127.0.0.1:8000`, the public site will return **502** until Nginx is reloaded from `uwsgi_pass` to `proxy_pass`.

Run the process switch and Nginx reload in the same maintenance window:

```bash
ROAMIO_SETTINGS=prod bash scripts/deploy_gunicorn.sh
sudo nginx -t
sudo nginx -s reload
```

After reload, verify public HTTPS separately:

```bash
curl -I https://roamio.cn/
curl -I https://roamio.cn/api/v1/auth/me/
curl -sS https://roamio.cn/api/v1/auth/qq_login_url/
```

`scripts/deploy_gunicorn.sh` intentionally checks only local Gunicorn HTTP (`http://127.0.0.1:8000`) so it does not fail while Nginx is still using the old uWSGI protocol.

## Minimal Proxy Block

Use this shape for app routes that should reach Django:

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_read_timeout 300;
    proxy_connect_timeout 60;
    proxy_send_timeout 300;
}
```

For API-only blocks, keep the same proxy headers:

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_read_timeout 300;
}
```

Confirm Django settings trust the reverse proxy before relying on forwarded scheme/host behavior. In particular, verify `SECURE_PROXY_SSL_HEADER`, `ALLOWED_HOSTS`, CSRF trusted origins, and cookie security settings match the deployed Nginx/TLS topology.

## Rollback Reference

Keep the old uWSGI block commented for fast rollback:

```nginx
# location / {
#     include uwsgi_params;
#     uwsgi_pass 127.0.0.1:8000;
#     uwsgi_read_timeout 300;
#
#     uwsgi_param Host $host;
#     uwsgi_param HTTP_X_FORWARDED_FOR $proxy_add_x_forwarded_for;
#     uwsgi_param HTTP_X_REAL_IP $remote_addr;
#     uwsgi_param HTTP_X_FORWARDED_PROTO $scheme;
# }
```

Rollback order:

1. Stop Gunicorn: `bash scripts/stop_gunicorn.sh`
2. Restore the Nginx `uwsgi_pass` block and comment out `proxy_pass`.
3. Run `sudo nginx -t && sudo nginx -s reload`.
4. Restart uWSGI: `ROAMIO_SETTINGS=prod bash scripts/deploy_uwsgi.sh`.
