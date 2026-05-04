# Second Documentation Cleanup

## Goal

Remove remaining historical integration notes that either expose credentials or direct maintainers toward obsolete deployment/configuration paths.

## Deleted

- `docs/integration/RALENDAR_OAUTH_CONFIGURATION.md`
  - Contained a real OAuth client secret.
  - Referred to deleted `cloud_settings/` configuration.
- `docs/integration/OAUTH_IMPLEMENTATION_SUMMARY.md`
  - Contained the same OAuth client secret.
  - Mixed implementation history with deployment instructions.
- `docs/features/RALENDAR_INTEGRATION.md`
  - Historical feature note with stale `cloud_settings` and uWSGI deployment commands.
- `docs/features/CORS_AND_API_PROXY.md`
  - Historical CORS workaround note tied to an external app host rather than current route boundaries.
- `docs/integration/OAUTH_IMPLEMENTATION_PROGRESS.md`
  - Historical progress tracker with stale settings paths and secret-like placeholder values.
- `docs/integration/OAUTH_SETUP_GUIDE.md`
  - Old setup flow tied to deleted `cloud_settings/`.
- `docs/integration/OAUTH_TEST_PLAN.md`
  - Old manual test checklist tied to deleted `cloud_settings/`.
- `docs/integration/ENV_CONFIG_CHECKLIST.md`
  - Old environment checklist tied to deleted `cloud_settings/`.

## Required Security Action

Rotate the exposed Ralendar OAuth client credentials. Deleting the files only prevents future accidental reuse; it does not make previously committed credentials safe.

## Verification

- Re-ran sensitive keyword scan after deletion.
- The remaining matches are placeholders, code references to environment variables, or remediation notes that intentionally document the cleanup risk.
