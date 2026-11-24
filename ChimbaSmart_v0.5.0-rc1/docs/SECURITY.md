# Security

## Implemented controls

- bcrypt password hashing.
- 15-minute access tokens by default.
- Opaque refresh tokens stored only as SHA-256 hashes.
- Refresh token rotation and reuse revocation.
- Password-reset one-time tokens; confirming reset revokes active refresh sessions.
- Logout revokes the supplied refresh session.
- Audit events for login, refresh, logout and password-reset actions.
- Request size limit based on `MAX_REQUEST_BYTES` and `Content-Length`.
- Restricted CORS origins from `CORS_ORIGINS`.
- No-store, nosniff, frame-deny and referrer security headers.
- Correlation ID response header.
- Image MIME/content verification, EXIF re-encoding, pixel limits and hash deduplication.
- Project membership enforcement on protected project operations.

## Authentication status

Access tokens do not yet carry revoked-session state. Logout revokes refresh capability but an already-issued access token remains usable until expiry. Revocation infrastructure and Redis-backed token/session checks are required for immediate session invalidation.

## Redis and queues

`REDIS_URL` is reserved for deployment configuration. Login throttling remains in-process and the processing queue remains `FastAPI.BackgroundTasks`; neither is yet suitable for multiple API/worker processes.

## Secrets

Set `JWT_SECRET`, `POSTGRES_PASSWORD`, `DATABASE_URL`, `ATTACHMENTS_DIR`, `CORS_ORIGINS` and Redis settings through environment variables. Never commit generated secrets or signing keys.
