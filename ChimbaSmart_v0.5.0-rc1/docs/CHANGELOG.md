# Changelog

## 2026-11-25 — Engineering audit and release-readiness checkpoint

- Reconciled README, status, engine, deployment, license, mobile and release documentation with the verified implementation.
- Recorded PyGSLIB official source/Conda investigation and kept the engine BLOCKED because tested builds did not yield an importable runtime; no unsupported adapter was added.
- Added GitHub-hosted backend, engine, Android, web and approved-release workflows. YAML was validated locally; GitHub execution remains NOT RUN.
- Added environment-driven Android production signing configuration; release workflow refuses to publish without owner signing secrets and release-gate approval.
- Hardened `scripts/codespaces_verify.sh` to use the selected Python interpreter and an isolated temporary SQLite database; fresh migrations and Alembic parity pass.
- Corrected the engine-worker Redis command so environment variables expand at runtime.
- Commercial release remains BLOCKED pending Flutter/PWA end-to-end work, worker recovery, full restore, licensing, production signing and field validation.

## 2026-11-25 — Worker, PostGIS and Flutter checkpoint

- Added a second Flutter field-capture foundation: SQLite schema v2, a Kiswahili sample/assay/collar/interval/orientation form, project/pull/push primitives and attachment metadata.
- Fixed RQ 2.4 enqueue compatibility by removing `retries=0` from `queue.enqueue`, which RQ was passing to the worker function as a keyword.
- Verified live PostGIS migration and API auth/project/sync push/pull/duplicate operations.
- Verified API-to-Redis-to-RQ-worker-database execution and a worker stopped/restarted during queued job execution.
- Verified PostgreSQL logical restore into a clean database and a separate clean attachment volume marker.
