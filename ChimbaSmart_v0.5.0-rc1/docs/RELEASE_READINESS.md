# Release readiness

Baseline date: 2026-11-24.

## Gate summary

| Area | Status | Evidence |
|---|---|---|
| Backend/API tests | PASS | 32 passed, 1 PostGIS skipped in default suite |
| Live PostgreSQL/PostGIS | PASS | Disposable PostGIS 16-3.4 migration test passed |
| Alembic | PASS | 0001-0007 SQLite upgrade and metadata parity |
| Redis/RQ | PARTIAL | Dependencies, worker service and Redis connectivity implemented; worker crash/retry end-to-end test pending |
| RBAC | PASS | Six configurable role names plus legacy/owner roles |
| Conflict resolution | PASS | Server API list and resolution tested |
| Backup/restore | PASS | Disposable PostgreSQL dump/restore marker verified |
| PWA | PARTIAL | IndexedDB, push/pull, photos and conflict archive; browser smoke test pending |
| Flutter | PARTIAL | Flutter 3.38.5 analyzes and tests successfully; native local schema/API workflows remain incomplete |
| Heavy engines | PARTIAL | GemPy, LoopStructural and pyGIMLi execute real synthetic tests; PyGSLIB blocked; full production geological validation pending |
| Android APK/AAB | PARTIAL | Release APK/AAB built successfully; artifacts use the Android debug certificate until production signing is configured |
| Web build | PASS | Release web build completed under `mobile/build/web/` |
| iOS | BLOCKED | macOS/Xcode/signing unavailable |
| Commercial ready | FAIL | Security and native field integrations are incomplete |

## Engine matrix

- trend2d: adapter ready; runtime tested.
- orientation: adapter ready; runtime tested.
- idw: adapter ready; runtime tested.
- downhole_composite: adapter ready; runtime tested.
- pykrige: adapter ready and library installed; runtime tested.
- gempy: adapter ready for explicit-contact 3D models; GemPy 2026.0.3 runtime tested.
- loopstructural: adapter ready for implicit foliation; LoopStructural 1.12.0 runtime tested on Claudius data.
- pygslib: blocked; no installable PyPI/source distribution established.
- pygimli: adapter ready for ERT forward modelling; pyGIMLi 1.6.1 runtime tested. Inversion remains pending.

## Independent final audit 2026-11-24

The independent audit result is: **NOT COMMERCIALLY READY**.

Exact verification:

- Backend normal suite: 31 passed, 2 skipped.
- Backend live-Redis suite: 32 passed, 1 skipped.
- PostgreSQL/PostGIS migration: 1 passed.
- Alembic 0001-0007 and metadata parity: passed.
- Python compileall and PWA JavaScript syntax: passed.
- Docker Compose validation: passed.
- Open-source engine synthetic suite: 4 passed.
- GemPy: real 2026.0.3 implicit model compute passed.
- LoopStructural: real Claudius synthetic model returned finite values.
- pyGIMLi: real synthetic ERT forward model returned 3 positive values.
- PyGSLIB: blocked because no package/source distribution is available.
- Disposable PostgreSQL dump/restore: passed for a marker row.
- Flutter analyze: passed with no issues.
- Flutter test: passed.
- Flutter web release build: passed; output under `mobile/build/web/`.
- Flutter debug APK: built at `mobile/build/app/outputs/flutter-apk/app-debug.apk`.
- Flutter release APK: built successfully and signed with the Android debug certificate.
- Flutter release AAB: built successfully and signed with the Android debug certificate.
- Production owner signing key and Play Console deployment credentials are still required.
- Flutter, PWA browser restart, RQ worker crash/recovery and heavy optional engines remain PARTIAL or BLOCKED.

Tanzania field validation is intentionally separate and remains blocked.

## Artifact verification

- Debug APK SHA-256: `1cc00d2e9b6bb39e4c85f4a70067756863879c908d73da5df3366bb526bdc7d9`
- Release APK SHA-256: `4fbde7d56453e2b66b69c4d50d7e4d2506120be752a5859c4be4eeb2c088e02e`
- Release AAB SHA-256: `03d8a30740a40f4438d42c273aaeb3ea9a1ed41249c774a7ab6a36f1343c2c9a`
- Web release directory: `mobile/build/web/`
- Release APK/AAB are not production-certified artifacts until owner-provided signing configuration is available.
