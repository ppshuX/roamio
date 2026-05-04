# Django Settings Split

## Goal

Separate local development and production settings so remediation work can be verified locally without depending on production-only services or credentials.

## Changes

- Moved the old monolithic `roamio/settings.py` into `roamio/settings/base.py`.
- Added `roamio/settings/dev.py` for local development:
  - SQLite database.
  - local memory cache.
  - file-based email backend.
  - localhost-only hosts and CSRF origins.
  - permissive CORS for local frontend debugging.
- Added `roamio/settings/prod.py` for deployment:
  - required `SECRET_KEY`.
  - required `ALLOWED_HOSTS`.
  - required database connection variables.
  - secure cookie and HTTPS defaults.
- Added `roamio/settings/__init__.py` so the existing `DJANGO_SETTINGS_MODULE=roamio.settings` entrypoint keeps working.
- Removed import-time `print()` diagnostics from settings. Django settings should be quiet and deterministic.

## Selection Rule

The default is local development settings.

```powershell
python manage.py check
```

Production settings can be selected explicitly:

```powershell
$env:ROAMIO_SETTINGS='prod'
python manage.py check
```

## Verification

- `python -m py_compile` passed for the settings package and Django entrypoints.
- `python manage.py check` passed with no issues.

## Remaining Work

- Clean up garbled comments in `base.py` when the next settings pass happens.
- Move provider-specific settings into smaller sections only if they are still needed after route and feature cleanup.
- Decide whether COS upload, QQ OAuth, and Ralendar integration stay in the core product or move behind explicit optional modules.
