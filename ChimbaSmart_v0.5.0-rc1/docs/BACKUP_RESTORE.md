# Backup and restore

## PostgreSQL

Use a consistently permissioned PostgreSQL backup tool in a scheduled container or host cron job:

```bash
pg_dump --format=custom --no-owner "$DATABASE_URL" > /secure/backups/chimbasmart-$(date -u +%F-%H%M%SZ).dump
pg_restore --list /secure/backups/BACKUP_FILE.dump
```

## Attachments

Back up `ATTACHMENTS_DIR` or the future object-storage bucket separately. Match attachment backup retention to database backup retention.

## Restore rules

Do not restore into a live database. Restore to an isolated PostgreSQL/PostGIS instance, run migrations, verify row counts and spatial extension status, then obtain owner approval before cutover.

## Verification

Every restore test must restore a disposable database and a disposable attachment copy, execute `alembic upgrade head`, run health/readiness and selected API tests, verify foreign-key and spatial checks, and record the verification result.
