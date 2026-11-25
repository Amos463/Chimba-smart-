# GitHub Actions build and storage policy

Workflows use ephemeral GitHub-hosted runners. CI artifacts are transient (7-day retention); APK/AAB/web distributions are not committed to Git. No self-hosted runner or SDK cache is configured.

## Workflows

- `backend-ci.yml`: Python 3.12, PostgreSQL/PostGIS and Redis tests, SQLite migration, JavaScript syntax, pip-audit.
- `engine-ci.yml`: separate heavy-engine installation/synthetic adapter tests and Docker build; manual, scheduled and engine-change triggers.
- `android-build.yml`: pinned Flutter, Java 17, analyze/test, debug APK, release APK and AAB testing builds; outputs are not production-signed.
- `web-build.yml`: Flutter web release build plus JavaScript syntax check; browser PWA E2E remains separately NOT RUN.
- `release.yml`: tag/manual workflow with production Environment approval and signing-secret checks; publishing is fail-closed until owner configures secrets and environment protection.

## Owner setup

1. Configure GitHub Environment `commercial-release` with required reviewers.
2. Add `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`, and `ANDROID_STORE_PASSWORD` as Environment secrets before production release.
3. Verify branch protection and required checks; workflows do not bypass protections or push to branches.
4. Review dependency/security alerts and accepted audit exceptions.

GitHub Actions has not yet been executed for this commit. Workflow file presence is not CI evidence.
