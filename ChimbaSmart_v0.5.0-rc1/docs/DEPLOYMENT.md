# Deployment status

The repository includes a Docker Compose PostgreSQL/PostGIS and API baseline. It is not a production deployment certification.

## Required environment

- `ENV=prod`
- `DATABASE_URL`
- `JWT_SECRET`
- `POSTGRES_PASSWORD`
- `CORS_ORIGINS`
- `ATTACHMENTS_DIR`
- `REDIS_URL` once Redis-backed controls are enabled
- `ACCESS_TOKEN_MINUTES`
- `REFRESH_TOKEN_DAYS`
- `MAX_REQUEST_BYTES`

## HTTPS

Run behind an HTTPS reverse proxy. Forward the original client address and request ID. Restrict database and Redis ports to private networks.

## Database

Run `alembic upgrade head` during a controlled migration step before starting the new API generation. Create a verified backup before every migration.

## Workers

Do not scale the current `FastAPI.BackgroundTasks` implementation as a durable processor. Deploy a Redis-backed worker system (RQ or Celery) before production job workloads.
