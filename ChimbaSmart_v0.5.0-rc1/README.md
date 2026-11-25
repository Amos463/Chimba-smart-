# ChimbaSmart v0.5.0-rc1

ChimbaSmart is an offline-oriented geological field-data platform under active engineering. This repository is an engineering release candidate, **not a commercially certified geological/resource-estimation product**.

## Current components

- `backend/`: FastAPI, SQLAlchemy, Alembic migrations through 0007, PostgreSQL/PostGIS support, SQLite development/test mode, Redis/RQ processing, project permissions, synchronization, attachments and PDF reporting.
- `frontend/`: JavaScript PWA with IndexedDB-backed offline queue and server synchronization. Browser restart, interrupted upload, and multi-device conflict E2E tests remain outstanding.
- `mobile/`: Flutter foundation with SQLite, login/push primitives, GPS helper and Android/web scaffolding. It is not yet a complete field client and does not replace the PWA.
- `docker-compose.yml`: PostgreSQL/PostGIS, Redis, API, standard worker and optional-engine worker services. A production deployment has not been certified.

## Verification

Run the local verification script:

```bash
./scripts/codespaces_verify.sh
```

Core backend tests:

```bash
cd backend
../.venv/bin/python -m pytest -q
```

Latest local validation: backend with disposable Redis, 35 passed and 1 skipped; optional-engine suite, 4 passed; Flutter analyze/test passed. The verification script reaches the SQLite migration/drift check but cannot complete JavaScript checks because Node.js is unavailable here. GitHub Actions workflows have not yet run.

## Engine status

- PASS on synthetic runtime cases: Trend 2D, orientation, IDW, downhole compositing, PyKrige, GemPy 2026.0.3, LoopStructural 1.12.0.
- PARTIAL: pyGIMLi 1.6.1 ERT forward modeling; inversion and measured field validation are not complete.
- BLOCKED: PyGSLIB. The official repository and Conda distribution were located, but the available Linux build could not import with a reproducible current native stack; its source build does not support the current Python 3.12 toolchain. See `docs/SERVER_ENGINE_DEPLOYMENT_REPORT.md`.
- PARTIAL: PyProj/PROJ and PostGIS are present. GDAL/QGIS processing services are not integrated.

All geological outputs are exploratory and require professional review. They are not certified mineral resources or reserves.

## Local API and deployment

Use environment variables from `.env.example` and never use development secrets in shared/production environments. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md), [docs/BACKUP_RESTORE.md](docs/BACKUP_RESTORE.md), and [docs/SECURITY.md](docs/SECURITY.md).

## Readiness

The project is **not commercially ready**. Open items include Flutter workflows, browser E2E, worker crash/retry recovery, complete attachment backup/restore, PyGSLIB, pyGIMLi inversion, production signing, legal dependency clearance, and Tanzania field validation.

Read [docs/RELEASE_READINESS.md](docs/RELEASE_READINESS.md), [docs/FINAL_REPOSITORY_AUDIT.md](docs/FINAL_REPOSITORY_AUDIT.md), and [docs/OWNER_ACTIONS.md](docs/OWNER_ACTIONS.md) for evidence and owner actions.
