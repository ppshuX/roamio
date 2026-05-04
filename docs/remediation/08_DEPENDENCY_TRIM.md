# Dependency Trim

## Goal

Keep install paths aligned with how the project is actually used during remediation.

## Changes

- Kept `requirements.txt` cross-platform so local checks work on Windows and Linux.
- Moved `uwsgi` to `requirements-prod.txt` because it is a Linux deployment dependency and blocks Windows installs.
- Moved `ipython` to `requirements-dev.txt` because it is a developer convenience, not runtime behavior.
- Removed `moviepy` from active requirements because no current code imports it.
- Removed direct frontend dependencies on `jquery` and `@vue/cli-plugin-vuex`; the current app uses Pinia and Bootstrap does not require jQuery.
- `@vue/cli-plugin-vuex` remains transitive through `@vue/cli-service`, so it is not fully gone from `package-lock.json` yet.

## Verification

- Backend dependency check was validated by installing the runtime packages needed for Django startup.
- `python manage.py check` passes after the dependency trim and settings split.
- `npm uninstall jquery @vue/cli-plugin-vuex` completed and updated `frontend/web/package.json` / `frontend/web/package-lock.json`.

## Follow-up

- Re-add media processing packages only when a retained feature imports and verifies them.
- Keep deployment-only packages out of the default local setup path.
- Plan a separate frontend tooling upgrade; current Vue CLI dependencies warn under Node 24.
