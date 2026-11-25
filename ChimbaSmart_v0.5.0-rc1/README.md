# ChimbaSmart v0.5.0-rc1

ChimbaSmart is an offline-oriented geological field-data pilot. It is an engineering release candidate, **not a commercially certified geological or resource-estimation product**. Treat all analysis as exploratory and have a qualified geologist review field data and interpretations.

## Components

- `backend/`: FastAPI API, SQLite development mode, PostgreSQL/PostGIS, Redis/RQ jobs, synchronization, attachments and PDF reports.
- `frontend/`: installable JavaScript PWA with an IndexedDB-backed offline queue.
- `mobile/`: Flutter foundation; it is not yet at field-workflow parity and does not replace the PWA for pilot use.
- `docker-compose.yml`: PostgreSQL/PostGIS, Redis, API and workers. Production deployment still needs owner configuration and review.

## Quickstart: local SQLite

Requires Python 3.12 and the native Pango libraries used for PDF reports.

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r ChimbaSmart_v0.5.0-rc1/backend/requirements.txt
cd ChimbaSmart_v0.5.0-rc1/backend
export DATABASE_URL=sqlite:///./chimbasmart_dev.db
export AUTO_CREATE_TABLES=1
python -m app.cli create-user juma '<password>' --role admin
uvicorn app.main:app --reload
```

Replace `<password>` with a unique local password of at least 8 characters; do not reuse it in production. In another terminal, run the tests:

```bash
cd ChimbaSmart_v0.5.0-rc1/backend
python -m pytest -q
```

The test suite creates its database and attachment files under a temporary directory, not in the repository.

## Quickstart: PostgreSQL/PostGIS and Redis with Compose

From `ChimbaSmart_v0.5.0-rc1/`, create a local `.env` using unique development-only values (it is ignored by Git), then start the core services:

```bash
cp .env.example .env
# Edit POSTGRES_PASSWORD and JWT_SECRET in .env before starting services.
docker compose up -d db redis api worker
```

This command intentionally omits the optional engine-worker image. Compose is a local pilot/development convenience, not a production security setup. Follow [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) before exposing any service.

## Verification

From the project directory:

```bash
./scripts/codespaces_verify.sh
```

Latest release evidence, workflow URLs, known limitations and the pilot readiness decision are recorded in [docs/STATUS.md](docs/STATUS.md) and [docs/FINAL_MARKET_READINESS_REPORT.md](docs/FINAL_MARKET_READINESS_REPORT.md).

## Scientific scope

Trend, IDW, kriging and other outputs are exploratory; they are not JORC/NI 43-101 estimates, mineral resources or reserves. See [docs/SCIENCE_POLICIES.md](docs/SCIENCE_POLICIES.md) for initial pilot policies and geologist-review requirements.

No license has been selected for the project. See [docs/OWNER_ACTIONS.md](docs/OWNER_ACTIONS.md); the owner must decide the project license and complete `LICENSE.md`.
