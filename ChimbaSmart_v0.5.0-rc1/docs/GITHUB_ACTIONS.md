# GitHub Actions build and storage policy

Workflows must live under the Git repository root at `.github/workflows/`. The project is in `ChimbaSmart_v0.5.0-rc1/`, so workflow commands and path filters include that prefix. Runners are ephemeral GitHub-hosted runners. CI artifacts are transient (7-day retention); APK/AAB/web distributions are not committed to Git. No self-hosted runner or SDK cache is configured.

## Workflows

- `.github/workflows/backend-ci.yml`: Python 3.12, PostgreSQL/PostGIS and Redis tests, SQLite migration, JavaScript syntax, pip-audit.
- `engine-ci.yml`: separate heavy-engine installation/synthetic adapter tests and Docker build; manual, scheduled and engine-change triggers.
- `android-build.yml`: pinned Flutter, Java 17, Android SDK 36, analyze/test, debug APK, release APK and AAB testing builds; outputs are not production-signed.
- `web-build.yml`: Flutter web release build plus JavaScript syntax check; browser PWA E2E remains separately NOT RUN.
- `release.yml`: main-branch pushes run validation only. Tag pushes or an explicit manual publish request require the owner release gate, production Environment approval, and signing secrets before building or publishing.

## Owner setup

1. Configure GitHub Environment `commercial-release` with required reviewers.
2. Add `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`, and `ANDROID_STORE_PASSWORD` as Environment secrets before production release.
3. Verify branch protection and required checks; workflows do not bypass protections or push to branches.
4. Review dependency/security alerts and accepted audit exceptions.

An earlier checkpoint incorrectly placed workflow files under `ChimbaSmart_v0.5.0-rc1/.github/workflows`; GitHub does not discover nested workflow folders. The five root-level workflows are now discovered and active. A main-branch release workflow run is validation-only; release tags and explicit publish requests remain owner-gated.
