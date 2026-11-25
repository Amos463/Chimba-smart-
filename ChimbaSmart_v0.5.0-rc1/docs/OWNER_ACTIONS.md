# Owner actions

The following require owner or external action:

1. Choose the project license and replace the `LICENSE.md` placeholder with the owner-approved license text.
2. Provision PostgreSQL/PostGIS and Redis in production.
3. Set unique `JWT_SECRET`, database password, Redis password/TLS and CORS origins.
4. Configure email/SMS reset-token delivery and securely reset any legacy account whose password was at least 72 UTF-8 bytes; those unversioned bcrypt hashes are now rejected because their original suffix cannot be verified.
5. Approve a deployed worker configuration and retry/recovery policy.
6. Configure GitHub Environment `commercial-release`, protect it with owner approval, and provide Android signing secrets (`ANDROID_KEYSTORE_BASE64`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`, `ANDROID_STORE_PASSWORD`).
7. Provide macOS/Xcode and Apple signing credentials for iOS.
8. Resolve PyGSLIB: request a supported Linux/Python build and native dependency recipe from OpenGeoStat; review MIT/GPL source boundaries with counsel before commercial service use.
9. Review GemPy EUPL-1.2, PostGIS/QGIS GPL, psycopg LGPL and full transitive notices with counsel.
10. Perform supervised field pilot and geological/professional review.
11. Approve public HTTPS deployment and disaster-recovery schedule.
12. Configure GitHub repository variables/secrets, branch protection, required status checks and `COMMERCIAL_RELEASE_GATES_PASSED` only after external gates have evidence.
13. Push-triggered Actions are active. Grant the operator token Actions read/write scope only if manual workflow dispatch or repository Actions settings inspection is required; the current integration token receives HTTP 403 for those operations.
14. Provide HTTPS reverse proxy/domain configuration, external monitoring and alerting. The Compose API now binds only to localhost.
15. Approve an attachment write-role policy and confirm whether project members with `create` but not `update` should be permitted to upload photos; current route requires `update`.
16. Choose the pilot HTTPS API URL, configure the deployment CORS allowlist for the Android Capacitor origin `https://localhost`, and arrange physical-device acceptance; GPS, camera, restart, and sync checks remain NOT RUN.
