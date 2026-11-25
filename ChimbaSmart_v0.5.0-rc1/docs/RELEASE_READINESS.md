# Release readiness

Baseline summary incorporates 2026-11-24 evidence; current-turn evidence is appended below.

## Gate summary

| Area | Status | Evidence |
|---|---|---|
| Backend/API tests | PASS | Hosted backend integration/PostGIS/Redis suite: 34 passed, 3 skipped, 5 warnings. SQLite migration/metadata, JS syntax and `pip-audit` all passed on run 45560541803. |
| Live PostgreSQL/PostGIS | PASS | Disposable PostGIS 16-3.4 migration test passed |
| Alembic | PASS | 0001-0008 fresh SQLite upgrade and metadata parity; PostGIS-specific validation predates 0008 |
| Redis/RQ | PARTIAL | Disposable live queue execution and stopped-worker restart passed; retry policy and isolated engine worker remain incomplete |
| RBAC | PASS | Six configurable role names plus legacy/owner roles |
| Conflict resolution | PASS | Server API list and resolution tested |
| Backup/restore | PARTIAL | PostgreSQL project/record/job/audit restore verified in a clean DB and attachment marker restored in a clean volume; complete application restoration remains pending |
| PWA | PARTIAL | IndexedDB, push/pull, photos and conflict archive; browser smoke test pending |
| Flutter | PARTIAL | Flutter 3.38.5 analyze and test passed on 2026-11-25; native local schema/API workflows remain incomplete |
| GitHub Actions | PASS | All five workflows are discovered and have successful runs. The integration token still cannot read Actions settings or dispatch manually; push-triggered execution works. |
| Heavy engines | PARTIAL | GemPy, LoopStructural and pyGIMLi execute real synthetic tests; PyGSLIB blocked; full production geological validation pending |
| Android APK/AAB | PARTIAL | Hosted run 45558488726 built and uploaded debug APK, testing APK and AAB; hashes are recorded in `ANDROID_RELEASE_REPORT.md`. Production signing and device acceptance remain outstanding. |
| Authentication security | PARTIAL | Two confirmed findings were fixed locally; 38 backend tests passed with 5 skipped and 1 warning. Fresh and existing-user migrations passed. Hosted CI for this patch is pending; legacy bcrypt hashes for 72+-byte passwords require secure reset. |
| Web build | PASS | Release web build completed under `mobile/build/web/` |
| iOS | BLOCKED | macOS/Xcode/signing unavailable |
| Commercial ready | BLOCKED | Security, native field integrations, worker recovery, complete restore and field validation remain incomplete |

## Engine matrix

- trend2d: adapter ready; runtime tested.
- orientation: adapter ready; runtime tested.
- idw: adapter ready; runtime tested.
- downhole_composite: adapter ready; runtime tested.
- pykrige: adapter ready and library installed; runtime tested.
- gempy: adapter ready for explicit-contact 3D models; GemPy 2026.0.3 runtime tested.
- loopstructural: adapter ready for implicit foliation; LoopStructural 1.12.0 runtime tested on Claudius data.
- pygslib: BLOCKED; official OpenGeoStat Conda/source found, but current Linux binary and Python 3.12 source build failed runtime/build validation. See `SERVER_ENGINE_DEPLOYMENT_REPORT.md`.
- pygimli: adapter ready for ERT forward modelling; pyGIMLi 1.6.1 runtime tested. Inversion remains pending.

## Independent final audit 2026-11-24

The independent audit result is: **NOT COMMERCIALLY READY**.

Exact verification:

- Backend normal suite: 31 passed, 2 skipped.
- Backend live-Redis suite: 32 passed, 1 skipped.
- PostgreSQL/PostGIS migration: 1 passed.
- Alembic 0001-0007 and metadata parity: passed in the 2026-11-24 audit.
- Python compileall and PWA JavaScript syntax: passed.
- Docker Compose validation: passed.
- Open-source engine synthetic suite: 4 passed.
- GemPy: real 2026.0.3 implicit model compute passed.
- LoopStructural: real Claudius synthetic model returned finite values.
- pyGIMLi: real synthetic ERT forward model returned 3 positive values.
- PyGSLIB: official GitHub source and OpenGeoStat Conda distribution identified; neither produced a usable runtime in tested configurations.
- PyGSLIB official source build (Python 3.12): blocked at `numpy.distutils` import.
- PyGSLIB official Linux Conda binary (Python 3.8): blocked at VTK/netCDF ABI after legacy GFortran runtime pin.
- Historical status at the time of the 2026-11-24 audit: workflows had not yet run. This was superseded by the successful hosted runs listed below.
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

## Current PyGSLIB and repository audit 2026-11-25

- Official OpenGeoStat source and Conda distribution were identified.
- PyGSLIB is retained in the engine roadmap but remains BLOCKED until importable runtime and component-level license clearance.
- Python 3.12 source build error: `ModuleNotFoundError: No module named 'numpy.distutils'`.
- Official Linux CPython 3.8 Conda package import error after legacy GFortran pin: `undefined symbol: H5Pset_fapl_ros3`.
- CI workflows are discovered. Backend run 45560541803 passed integration/migration/JS checks and reports no known dependency vulnerabilities; engine run 45560541814 passed the synthetic engine and image build; release validation run 45560541798 passed with publishing skipped on `main`.
- Android run 45558488726 passed and uploaded testing artifacts; release validation run 45560541798 passed with publishing skipped on `main`.
- Current-turn code/test evidence and requirement matrix: `FINAL_REPOSITORY_AUDIT.md`.
- Actionable remaining work: `FINAL_IMPLEMENTATION_PLAN.md`.

## Historical local artifact hashes

The following are historical local-build hashes, not the current hosted workflow artifacts. Current hosted artifact hashes are recorded in `ANDROID_RELEASE_REPORT.md`.

- Debug APK SHA-256: `1cc00d2e9b6bb39e4c85f4a70067756863879c908d73da5df3366bb526bdc7d9`
- Release APK SHA-256: `4fbde7d56453e2b66b69c4d50d7e4d2506120be752a5859c4be4eeb2c088e02e`
- Release AAB SHA-256: `03d8a30740a40f4438d42c273aaeb3ea9a1ed41249c774a7ab6a36f1343c2c9a`
- Web release directory: `mobile/build/web/`
- Release APK/AAB are not production-certified artifacts until owner-provided signing configuration is available.
