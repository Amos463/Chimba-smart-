# Owner actions

The following require owner or external action:

1. Provision PostgreSQL/PostGIS and Redis in production.
2. Set unique `JWT_SECRET`, database password, Redis password/TLS and CORS origins.
3. Provide email/SMS integration for password reset delivery.
4. Approve a deployed worker configuration and retry/recovery policy.
5. Configure GitHub Environment `commercial-release`, protect it with owner approval, and provide Android signing secrets (`ANDROID_KEYSTORE_BASE64`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`, `ANDROID_STORE_PASSWORD`).
6. Provide macOS/Xcode and Apple signing credentials for iOS.
7. Resolve PyGSLIB: request a supported Linux/Python build and native dependency recipe from OpenGeoStat; review MIT/GPL source boundaries with counsel before commercial service use.
8. Review GemPy EUPL-1.2, PostGIS/QGIS GPL, psycopg LGPL and full transitive notices with counsel.
9. Perform supervised field pilot and geological/professional review.
10. Approve public HTTPS deployment and disaster-recovery schedule.
11. Configure GitHub repository variables/secrets, branch protection, required status checks and `COMMERCIAL_RELEASE_GATES_PASSED` only after external gates have evidence.
