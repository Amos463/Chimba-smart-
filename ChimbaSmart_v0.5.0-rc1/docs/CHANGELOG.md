# Changelog

## 2026-11-25 — Authentication hardening

- Addressed two confirmed authentication findings: bcrypt now hashes the full password through SHA-256 before bcrypt, and access tokens are bound to refresh sessions and invalidated on logout/password reset.
- Added migration 0008 for per-user auth versions, preserving existing users with a default version. Legacy bcrypt hashes for passwords of 72 or more UTF-8 bytes are rejected because their original suffix cannot be verified; affected accounts require a secure password reset.
- Added regression tests; local backend suite: 38 passed, 5 skipped, 1 warning. Hosted CI and production deployment validation remain pending.

## 2026-11-25 — Hosted workflow and dependency audit follow-up

- Fixed backend Redis integration test to use the workflow-provided `REDIS_URL`.
- Fixed Android SDK provisioning by pinning setup-android and explicitly installing platform-tools, Android 36 and build-tools 36.0.0.
- Added main-branch release validation that cannot enter the signing/publishing job; the hosted validation run passed with publish skipped.
- Built and uploaded debug APK, testing APK and AAB; recorded workflow artifact URL and SHA-256 checksums in `ANDROID_RELEASE_REPORT.md`.
- `pip-audit` initially found 127 advisories in five stale dependency versions. Updated FastAPI/Starlette, PyJWT, pytest, python-multipart and Pillow pins; local tests and the hosted backend audit pass with no known vulnerabilities.
- Added the requested mobile, PWA, worker, restore, Android, security/license and market-readiness reports. Commercial release remains blocked.

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
