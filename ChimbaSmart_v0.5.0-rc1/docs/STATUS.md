# ChimbaSmart repository status

Status date: 2026-11-25. Pilot work is in progress on `market-pilot`; only results linked to commands or hosted runs below are treated as verified.

## Market-pilot phase log

| Phase | Status | Files/work | Evidence / remaining risk |
|---|---|---|---|
| 0 — cleanup and baseline | PASS | Moved `.devcontainer` to repository root and made it Python-only; untracked backend attachments without deleting local files; ignored runtime data/build outputs; isolated test attachments in a temporary directory; pinned NumPy/PyProj/WeasyPrint; added quickstart and owner license action; fixed Compose runtime Redis URL expansion. | Local `pytest -q`: 38 passed, 5 skipped, 1 warning. Fresh SQLite Alembic upgrade through 0008 and `alembic check`: passed. Compose config: passed. Hosted [Backend CI run 45605231625](https://github.com/Amos463/Chimba-smart-/actions/runs/45605231625) and [Engine CI run 45605231429](https://github.com/Amos463/Chimba-smart-/actions/runs/45605231429): both passed, including JavaScript syntax, PostGIS/Redis tests, dependency audit and isolated worker-image build. Local Node.js syntax checks: NOT RUN (Node.js unavailable). At Phase 0 completion, `df -h /workspaces`: `/dev/loop4 32G 24G 5.8G 81%`. |
| 1 — backend and PWA field workflow | PASS for the implemented workflow scope | Added sample list API, project isolation, latest assay/QA/sync metadata, QA waiver migration and audited owner/admin routes, initial below-detection and batch-QA processing policy, PWA project selector, searchable sample list, later assay/QA entry, conflict controls and analysis-job UI. | Local `compileall` and backend tests: 43 passed, 5 skipped, 1 warning. Fresh SQLite migration 0001–0009 and `alembic check` passed; upgrade from 0008 preserved an existing user and created `qa_waivers`. Hosted Backend CI run [45648096883](https://github.com/Amos463/Chimba-smart-/actions/runs/45648096883) passed, including PWA Playwright acceptance; web/PWA checks [45648096960](https://github.com/Amos463/Chimba-smart-/actions/runs/45648096960) passed. Browser scenario covered offline capture/reload, sync recovery, later assays, below-detection entry, map/analysis/PDF, token refresh, second-device pull and conflict resolution. Interrupted attachment upload and restoration are not covered by this scenario. Initial geoscience policies need geologist review. |

## Components and current state

| Area | Status | Evidence / gap |
|---|---|---|
| FastAPI backend | PARTIAL | Auth, project roles, sample/assay/drillhole records, sync, conflicts, attachments, reports and engine jobs exist; production-scale API E2E is incomplete. |
| Authentication | PARTIAL | Session-bound access tokens, logout/reset invalidation and versioned bcrypt hashing are covered by local regression tests; legacy accounts and production reset delivery need owner action. |
| PostgreSQL/PostGIS | PARTIAL | Migrations through 0008 and spatial columns/indexes exist; live PostGIS 16-3.4 migration test passed before 0008; full restore remains incomplete. |
| SQLite | PASS | Local/development and API test path works. |
| Redis/RQ | PARTIAL | Live API-to-Redis-to-RQ-worker persistence and worker restart passed; isolated engine worker and retry recovery remain incomplete. |
| PWA | PARTIAL | Hosted Playwright acceptance passed in [Backend CI run 45648096883](https://github.com/Amos463/Chimba-smart-/actions/runs/45648096883): offline capture/reload, network recovery, later assay, below-detection assay, map/analysis/PDF, token refresh, second-device pull and conflict resolution. Interrupted attachment upload, browser/server restoration, and real field-device behavior remain unverified. |
| Flutter | PARTIAL | SQLite schema v2, local field-capture form, project/pull/push primitives and GPS helper exist; photos, durable uploads, conflicts and restart/device acceptance remain incomplete. |
| Backup/restore | PARTIAL | PostgreSQL marker dump/restore passed previously; full project plus photos/application restore not tested. |
| Android | PARTIAL | Hosted debug APK, testing release APK and AAB built and uploaded in run 45558488726; production signing and real-device acceptance are missing. |
| CI | PARTIAL | On commit `01d2ea2`, Backend CI [45648096883](https://github.com/Amos463/Chimba-smart-/actions/runs/45648096883) and web/PWA checks [45648096960](https://github.com/Amos463/Chimba-smart-/actions/runs/45648096960) passed. Engine, Android and release workflows have not been rerun on this commit; manual dispatch previously returned HTTP 403. |

## Geological processing

| Engine | Status | Runtime scope |
|---|---|---|
| Trend 2D | PASS | Existing synthetic/backend tests; surface samples only. |
| Orientation | PASS | Existing synthetic/backend tests; phone measurements remain lower confidence. |
| IDW | PASS | Existing grid test; exploratory interpolation only. |
| Downhole composite | PASS | Length-weighted intervals; no desurvey/domain estimation. |
| PyKrige 1.7.3 | PASS | Ordinary Kriging synthetic adapter test. |
| GemPy 2026.0.3 | PASS | Explicit-contact implicit model synthetic execution. |
| LoopStructural 1.12.0 | PASS | Claudius synthetic foliation evaluation. |
| pyGIMLi 1.6.1 | PARTIAL | ERT forward modeling passed; inversion not implemented/validated. |
| PyGSLIB | BLOCKED | Official Linux Conda build is Python 3.8-era and import fails against currently resolved VTK/HDF5/GFortran stack; official source build fails on Python 3.12 due `numpy.distutils` removal. License review is unresolved. |
| PyProj/PROJ | PARTIAL | PyProj installed and used by CRS transformations; full CRS/data-contract validation incomplete. |
| GDAL | NOT RUN | Not installed/integrated. |
| QGIS | NOT RUN | No QGIS processing service; PostGIS remains the server spatial datastore. |

## Tests

Latest recorded current-turn runs:

- Backend hosted integration/PostGIS/Redis suite and migration checks on commit `01d2ea2`: passed; hosted PWA Playwright acceptance passed in the same [Backend CI run 45648096883](https://github.com/Amos463/Chimba-smart-/actions/runs/45648096883). Web/PWA checks passed in [run 45648096960](https://github.com/Amos463/Chimba-smart-/actions/runs/45648096960).
- Local backend suite after auth fixes on 2026-11-25: 38 passed, 5 skipped, 1 Starlette deprecation warning. Local `pip-audit -r backend/requirements.txt`: no known vulnerabilities.
- Backend API-only suite on SQLite: 26 passed, 1 skipped, 1 warning; local Redis service was unavailable.
- Focused engine suite: 4 passed, 1 warning.
- Python compileall: passed.
- Flutter analyze: passed with no issues; Flutter test: passed (one widget smoke test).
- Fresh SQLite migrations through 0008 and Alembic metadata check: passed. Upgrade from 0007 preserved a user row and initialized `auth_version` to 0.
- Android Gradle project configuration: passed with Java 17.
- Workflow YAML syntax: all five workflows parsed. Latest Backend CI and web/PWA results are linked above. Latest successful engine, Android and release validation runs predate commit `01d2ea2`; manual dispatch previously returned HTTP 403.
- Docker Compose syntax: passed with disposable test-only secret values.
- Live PostGIS migration test: 1 passed.
- Live API login/project/sync push/pull and duplicate push: passed.
- Live RQ trend2d execution and worker restart: passed; one invalid RQ 2.4 enqueue argument was found and fixed.
- JavaScript syntax: NOT RUN locally; Node.js is unavailable.
- Browser PWA E2E: PASS for the hosted scenario in [Backend CI run 45648096883](https://github.com/Amos463/Chimba-smart-/actions/runs/45648096883); interrupted attachment upload and restore scenarios remain NOT RUN.
- Live Redis suite: passed with disposable Redis.
- Worker crash/restart: queue persistence plus restart execution passed for a job that was rejected by scientific validation.
- Full backup/restore: PostgreSQL logical restore passed for project, record, jobs and audit counts; separate attachment marker restore passed. Complete application/PWA/Flutter attachment restore remains PARTIAL.

## Commercial release decision

**BLOCKED.** The current repository is an engineering RC, not a market-ready product. Read `RELEASE_READINESS.md`, `FINAL_REPOSITORY_AUDIT.md`, `FINAL_IMPLEMENTATION_PLAN.md`, and `OWNER_ACTIONS.md`.

Geological outputs are exploratory; qualified professionals must review inputs, assumptions and interpretations. No resource/reserve certification is claimed.
