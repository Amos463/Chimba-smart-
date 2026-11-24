# Commercial audit

Audit baseline: repository commit `2f6fd9c`, 2026-11-24.

## Verification summary

- 27 backend tests pass; 1 PostGIS test is skipped when PostgreSQL is unavailable.
- Fresh SQLite migration chain 0001-0007 passes; `alembic check` reports no new upgrade operations.
- Python bytecode compilation passes.
- JavaScript syntax checks pass.
- Flutter toolchain is unavailable in this Codespaces environment.
- PyKrige requirement conflict is resolved at `PyKrige==1.7.3`.
- The baseline Codespaces script can select the repository virtual environment instead of the host Python 3.14 interpreter.

## Critical

- Production authorization has no durable Redis-backed throttling or queueing.
- FastAPI `BackgroundTasks` is process-local and does not survive worker or application restarts.
- Refresh/logout sessions and password reset workflows are now modelled, but delivery, Redis reuse controls and account-management UI are not complete.
- Live PostgreSQL/PostGIS migration and backup/restore validation has not been executed here.
- Cross-platform production builds cannot be verified without their native toolchains.

## High

- Project roles are only owner/member/administrator; the requested six configurable roles are not fully implemented server-side.
- Sync creates conflicts but has no server-approved conflict resolution endpoint.
- No record update payload is implemented for existing non-attachment entities.
- Attachment storage is local filesystem only; object-storage compatibility is not implemented.
- CORS is configurable, but production origins must be explicitly set.
- Password reset delivery is intentionally not wired to email/SMS.

## Medium

- The PWA and Flutter clients are offline-first foundations, not complete field applications.
- Flutter uses SQLite but is only a local skeleton.
- Offline basemaps, Bluetooth instruments and 3D visualization are not implemented.
- PostGIS geometry is limited to generated WGS84 point columns; projected CRS transformations are advisory/processing scope.
- No Redis worker metrics or worker health endpoint exists.

## Low

- Several docs and changelogs still contain pre-release wording.
- The API is mostly flat rather than versioned under `/api/v1`.
- There is no formal OpenAPI/exported version policy.
