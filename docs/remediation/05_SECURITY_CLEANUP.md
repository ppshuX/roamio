# Security Cleanup Record

Updated: 2026-05-04

## Rule

Any credential, password, server address, database host, API key, OAuth secret, or shared signing key that appeared in this repository must be treated as exposed. Removing files from the working tree reduces future leakage, but it does not make previously exposed secrets safe again.

## Deleted High-Risk Tracked Documents

- `docs/AI_INTEGRATION_MILESTONE.md`
- `docs/SECURITY_CHECKLIST.md`
- `docs/ecosystem/ROAMIO_DATABASE_INFO_FOR_RALENDAR.md`
- `docs/ecosystem/ROAMIO_INTEGRATION_REPORT.md`
- `docs/ecosystem/INTEGRATION_CHECKLIST.md`
- `docs/summaries/DAILY_SUMMARY_20251113.md`

## Deleted Local Private Deployment Materials

- `cloud_settings/`

This directory was not tracked by Git and contained historical deployment, domain migration, database migration, certificate, and environment configuration materials. It also contained real or real-looking credentials and therefore should not stay in the project workspace.

## Credentials To Rotate

Rotate these if any were ever real:
- Django `SECRET_KEY`
- Database users and passwords
- Redis password
- SMTP/email authorization codes
- QQ OAuth app key
- Tencent COS SecretId and SecretKey
- Qwen/DashScope API key, if it was ever real in historical deployments
- DeepSeek API key
- Baidu Map and AMap keys
- Ralendar OAuth client secret

## Follow-Up

1. Keep only one public environment template: root `.env.example`.
2. Ensure `.env.example` contains placeholders only.
3. Add pre-commit or CI secret scanning.
4. Run historical secret scanning before treating the repository as public-safe.
5. Decide separately whether to rewrite Git history. That is a disruptive operation and should not be mixed into normal code cleanup.
