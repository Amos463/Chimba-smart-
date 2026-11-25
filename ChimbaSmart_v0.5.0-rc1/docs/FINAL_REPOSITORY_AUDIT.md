# Final repository audit

Audit date: 2026-11-25. This audit records the initial tree at `17a126c` plus targeted changes and tests in the current working tree. A PASS denotes runtime evidence, not commercial certification.

## Status key

- **PASS**: directly tested and passed.
- **PARTIAL**: code or limited runtime evidence exists, but requirements are incomplete.
- **BLOCKED**: an external/technical blocker prevents valid implementation or test.
- **NOT RUN**: no execution evidence was obtained.

## Repository surface

- Backend: FastAPI, SQLAlchemy, seven Alembic revisions, authentication, project roles, sync/conflicts, attachments, reports, and RQ queue routing.
- Processing: trend2d, orientation, IDW, downhole compositing, PyKrige, GemPy, LoopStructural, pyGIMLi ERT forward adapter, and unavailable PyGSLIB adapter.
- Field clients: JavaScript PWA with IndexedDB queue; Flutter code contains a minimal home screen, SQLite record table, GPS primitive, login and push primitive.
- Infrastructure: PostgreSQL/PostGIS, Redis, core worker and heavy-engine worker services. Backup scripts cover PostgreSQL dump/restore, but complete project plus attachment restoration is not verified.
- CI: no `.github/workflows` existed at audit start.

## Requirement findings

| Area | Status | Evidence / limitation |
|---|---|---|
| Core API regression tests | PASS | Full suite with disposable Redis: 35 passed, 1 skipped. |
| PostGIS migration tests | NOT RUN | Previous checkpoint records one disposable migration pass; not rerun in this audit turn. |
| SQLite migration history 0001-0007 | PARTIAL | Previously verified; no fresh migration run in this audit. |
| Auth and project isolation | PARTIAL | API tests exist and pass; production deployment and concurrency are not fully tested. |
| Redis/RQ job processing | PARTIAL | RQ and worker routing exist; crash, retry, Redis recovery and API-to-container job persistence are not exercised end-to-end. |
| PWA offline/restart/conflict | PARTIAL | IndexedDB code exists; no automated browser suite or app-restart test exists. |
| Flutter client | PARTIAL | Source has one home screen, a v1 local record table, GPS helper, login and pending push only; required full workflows are absent. |
| Flutter CI/build | PARTIAL | Local `flutter analyze` and `flutter test` passed; workflow YAML parses, but GitHub Actions has not run. |
| PyKrige | PASS | Ordinary kriging synthetic adapter test passed. |
| GemPy | PASS | GemPy 2026.0.3 real implicit model synthetic test passed. |
| LoopStructural | PASS | LoopStructural 1.12.0 Claudius synthetic foliation returned finite values. |
| pyGIMLi | PARTIAL | pyGIMLi 1.6.1 synthetic ERT forward model passes; measured-data inversion is not implemented. |
| PyGSLIB | BLOCKED | Official source/Conda artifact identified; Python 3.12 build and available Linux Conda runtime failures recorded in `ENGINE_INTEGRATION_REPORT.md`. Licensing is mixed MIT/GPL and requires counsel review. |
| QGIS/GDAL | PARTIAL | Not integrated as application processing services; PostGIS and PyProj are present. |
| Full backup/restore | NOT RUN | Only PostgreSQL marker restore was previously verified; application plus attachments not validated. |
| Commercial licensing | BLOCKED | EUPL/GPL and PyGSLIB mixed licensing need owner/legal review; transitive SBOM incomplete. |
| Production Android | BLOCKED | APK/AAB previously built with Android debug certificate; owner signing keys and device field acceptance are absent. |
| Commercial release | BLOCKED | Native/PWA E2E, worker recovery, complete restore, field validation and legal clearance remain open. |

## Stale or contradictory documentation found

- README described Flutter as a skeleton and 30-day access tokens, both stale against the current commit.
- `docs/STATUS.md` contained old release-era claims, including unavailable Flutter and Redis/RQ infrastructure.
- `docs/ENGINE_CONTRACT.md` retained an obsolete section claiming GemPy/LoopStructural/pyGIMLi were not installed and their adapters were unavailable.
- `mobile/README.md` correctly admitted the Flutter client is not production-ready but still describes all screens as a foundation.
- `mobile/docs/data-contract-v1.md` says the contract is proposed; it is not proven to be the Flutter/PWA/backend shared runtime contract.
- `docs/RELEASE_READINESS.md` and prior audit documents have metrics from earlier checkpoints. They are historical evidence, not the current full-suite result.

## Duplicate/unused/integration risks

- `backend/requirements-geostatistics.txt` repeats core requirements via `-r requirements.txt` and pins PyKrige; no comprehensive generated lock/SBOM is committed.
- Flutter has no platform background-sync implementation, conflict UI, attachment persistence or meaningful project repository.
- Heavy engine queue names and Docker services exist, but no live queue-to-specialized-worker acceptance test was found.
- PyGSLIB's official package imports VTK eagerly. The official Linux conda artifact tested here is not a usable runtime with the resolved current native dependencies.

## Current-turn validation

- `backend/.venv/bin/python -m pytest -q` with disposable Redis on port 56379: **35 passed, 1 skipped, 1 warning**.
- `backend/.venv/bin/python -m pytest -q tests/test_optional_engines.py`: **4 passed, 1 warning**.
- Python `compileall`: **PASS**.
- Docker Compose config: **PASS** with disposable non-production env values.
- Flutter `analyze`: **PASS**, no issues; Flutter `test`: **PASS**, 1 widget smoke test.
- Android Gradle `help` configuration: **PASS** using Java 17.
- Fresh SQLite Alembic upgrade through `0007_security_sessions` and `alembic check`: **PASS**, no drift.
- Workflow YAML parsing: **PASS**, all five workflow files parse and define jobs; GitHub Actions execution **NOT RUN**.
- JavaScript syntax check: **NOT RUN**, Node.js and alternate JS runtimes are unavailable in this environment.
- `scripts/codespaces_verify.sh`: reached backend suite and fresh migration/drift check successfully; stopped at step 5 because `node` is not installed. Its initial migration implementation used a global `alembic` executable and removed a fixed repository-local DB path; it was corrected to use the selected Python interpreter and a disposable `/tmp` database.
- Browser E2E, worker recovery, full restore and PostGIS: **NOT RUN in this audit turn**.
- PyGSLIB source build on Python 3.12: **BLOCKED**, `ModuleNotFoundError: No module named 'numpy.distutils'`.
- Official Linux Conda PyGSLIB 0.0.0.6.0.0/Python 3.8: installed in an isolated temp environment, import failed on native VTK/netCDF ABI (`undefined symbol: H5Pset_fapl_ros3`) after matching legacy `libgfortran4`.

No production keys, databases or user data were modified.
