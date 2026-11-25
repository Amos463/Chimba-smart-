# Deployment status

The repository includes Docker Compose services for PostgreSQL/PostGIS, Redis, FastAPI, the standard RQ worker and isolated optional-engine worker. This configuration is an engineering deployment baseline, not a production deployment certification.

## Required environment

- `ENV=prod`
- `DATABASE_URL`
- `JWT_SECRET`
- `POSTGRES_PASSWORD`
- `CORS_ORIGINS`
- `ATTACHMENTS_DIR`
- `REDIS_URL`
- `ACCESS_TOKEN_MINUTES`
- `REFRESH_TOKEN_DAYS`
- `MAX_REQUEST_BYTES`

## HTTPS

Run behind an HTTPS reverse proxy. Forward the original client address and request ID. Restrict database and Redis ports to private networks.

## Database

Run `alembic upgrade head` during a controlled migration step before starting the new API generation. Create a verified backup before every migration.

## Workers

- Standard jobs use RQ queue `chimbasmart`.
- Heavy optional jobs (GemPy, LoopStructural, pyGIMLi, PyKrige) route to `chimbasmart-engines`, run by the separate `engine-worker` image.
- Redis queue routing is configured, but worker crash/retry/restart and API-to-worker-to-database acceptance have NOT RUN in a live deployment.
- PyGSLIB is not enabled; its official binary failed import validation and its source build is not compatible with Python 3.12. See `SERVER_ENGINE_DEPLOYMENT_REPORT.md`.

## Engine container

Build locally with `docker build -f backend/Dockerfile.engines -t chimbasmart-engine-worker .`. The image build itself must be verified by GitHub Actions before release; no Actions run is recorded yet.

## Operational requirements

- Terminate TLS at a maintained HTTPS reverse proxy and enforce secure forwarded headers.
- Keep PostgreSQL and Redis on private networks; apply authentication, ACLs, TLS and firewall rules.
- Configure persistent, encrypted attachment storage and tested database/attachment backups.
- Configure monitoring for API health, worker queue depth, failed jobs, storage, database and Redis.
- Run migrations from a controlled deployment job after a verified backup.
- Do not use the development SQLite database for production.

Production secrets, domain, TLS certificate, monitoring, retention and restore objectives require owner configuration.
