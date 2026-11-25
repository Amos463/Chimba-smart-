# ChimbaSmart repository status

Status date: 2026-11-25. This describes the current code and verified evidence, not the historical v0.4/v0.5 handoff.

## Components and current state

| Area | Status | Evidence / gap |
|---|---|---|
| FastAPI backend | PARTIAL | Auth, project roles, sample/assay/drillhole records, sync, conflicts, attachments, reports and engine jobs exist; production-scale API E2E is incomplete. |
| PostgreSQL/PostGIS | PARTIAL | Migrations through 0007 and spatial columns/indexes exist; live PostGIS 16-3.4 migration test passed; full restore remains incomplete. |
| SQLite | PASS | Local/development and API test path works. |
| Redis/RQ | PARTIAL | Live API-to-Redis-to-RQ-worker persistence and worker restart passed; isolated engine worker and retry recovery remain incomplete. |
| PWA | PARTIAL | IndexedDB queue, push/pull, attachment and conflict storage exist; browser interruption/restart and multi-device E2E have not run. |
| Flutter | PARTIAL | SQLite schema v2, local field-capture form, project/pull/push primitives and GPS helper exist; photos, durable uploads, conflicts and restart/device acceptance remain incomplete. |
| Backup/restore | PARTIAL | PostgreSQL marker dump/restore passed previously; full project plus photos/application restore not tested. |
| Android | PARTIAL | APK/AAB previously built locally with debug signing; production signing and real-device acceptance are missing. |
| CI | BLOCKED | Workflows are pushed, but GitHub Actions API reports zero discovered workflows and workflow dispatch is not available with the current token. |

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

- Backend suite with disposable Redis: 35 passed, 1 skipped, 1 third-party deprecation warning.
- Focused engine suite: 4 passed, 1 warning.
- Python compileall: passed.
- Flutter analyze: passed with no issues; Flutter test: passed (one widget smoke test).
- Fresh SQLite migrations through 0007 and Alembic metadata check: passed.
- Android Gradle project configuration: passed with Java 17.
- Workflow YAML syntax: all five workflows parsed; GitHub Actions: NOT RUN.
- Docker Compose syntax: passed with disposable test-only secret values.
- Live PostGIS migration test: 1 passed.
- Live API login/project/sync push/pull and duplicate push: passed.
- Live RQ trend2d execution and worker restart: passed; one invalid RQ 2.4 enqueue argument was found and fixed.
- JavaScript syntax: NOT RUN locally; Node.js is unavailable.
- Browser PWA E2E: NOT RUN.
- Live Redis suite: passed with disposable Redis.
- Worker crash/restart: queue persistence plus restart execution passed for a job that was rejected by scientific validation.
- Full backup/restore: PostgreSQL logical restore passed for project, record, jobs and audit counts; separate attachment marker restore passed. Complete application/PWA/Flutter attachment restore remains PARTIAL.

## Commercial release decision

**BLOCKED.** The current repository is an engineering RC, not a market-ready product. Read `RELEASE_READINESS.md`, `FINAL_REPOSITORY_AUDIT.md`, `FINAL_IMPLEMENTATION_PLAN.md`, and `OWNER_ACTIONS.md`.

Geological outputs are exploratory; qualified professionals must review inputs, assumptions and interpretations. No resource/reserve certification is claimed.
