# Commercial audit

Audit date: 2026-11-25. This audit reflects the implementation and verification documented in `FINAL_REPOSITORY_AUDIT.md`; it is not a certification.

## Critical

- **BLOCKED:** ChimbaSmart is not commercially ready. Flutter is a foundation, not a complete field app; PWA browser restart/offline acceptance, worker crash/retry recovery, complete project-and-attachment restoration, production signing, and field-pilot evidence are missing.
- **BLOCKED:** Commercial distribution/service licensing requires owner and counsel review of GemPy EUPL-1.2, GPL components and transitive dependencies. PyGSLIB's mixed MIT/GPL source needs file-level analysis.

## High

- **BLOCKED:** PyGSLIB has no verified usable runtime in this environment. Python 3.12 source build fails on missing `numpy.distutils`; the official Linux CPython 3.8 Conda package fails importing with `undefined symbol: H5Pset_fapl_ros3` after pinning its legacy GFortran runtime.
- **PARTIAL:** API-to-Redis-to-RQ persistence and ordinary worker restart were verified. Isolated-worker execution, forced crash recovery and retry behavior remain unverified.
- **PARTIAL:** Backup evidence is limited to a PostgreSQL marker-row restore; a full PostGIS project with attachments has not been restored and checked.
- **PARTIAL:** Flutter has SQLite, login/push primitives, GPS helper and a smoke test, but not the required field data capture, durable attachment, conflict, pull, device restart and background synchronization workflows.

## Medium

- **PARTIAL:** pyGIMLi has a real synthetic ERT forward-model adapter; inversion and recovered-model validation are not implemented.
- **PARTIAL:** PWA IndexedDB sync and attachment code exists, but browser end-to-end/restart coverage and client parity with the normative contract are incomplete.
- **PARTIAL:** PostGIS migration was validated in a prior checkpoint; this audit turn freshly exercised SQLite migrations 0001-0007 and Alembic metadata parity only.
- **PARTIAL:** GitHub Actions discovered and ran all five workflows. Engine, web, Android testing build and main-branch release validation passed. Backend integration/migration/JS checks passed but `pip-audit` found 127 advisories in five packages; patched dependency pins pass local audit and await hosted rerun.

## Low

- **PARTIAL:** `scripts/codespaces_verify.sh` now uses the selected Python interpreter and a disposable SQLite database, but local verification stops at JavaScript syntax checks because Node.js is unavailable in this environment.
- **PARTIAL:** QGIS/GDAL are not integrated processing services; PostGIS and PyProj are available.

## Verified local evidence

- Backend suite with disposable Redis: **35 passed, 1 skipped, 1 warning**.
- Optional engine tests: **4 passed, 1 warning**.
- Python compileall, Flutter analyze/test, Android Gradle configuration with Java 17, Docker Compose validation, all workflow YAML parsing, fresh SQLite migration and `alembic check`: **PASS**.
- PyKrige, GemPy, LoopStructural and pyGIMLi synthetic engine tests pass; these do not constitute geological or resource certification.
- Hosted Android artifact 14997580735 includes debug APK, testing release APK and AAB; exact hashes are in `ANDROID_RELEASE_REPORT.md`.

See `FINAL_REPOSITORY_AUDIT.md`, `RELEASE_READINESS.md` and `OWNER_ACTIONS.md` for test scope and remaining actions.
