# Release readiness

Baseline date: 2026-11-24.

## Gate summary

| Area | Status | Evidence |
|---|---|---|
| Backend/API tests | PASS | 32 passed, 1 PostGIS skipped in default suite |
| Live PostgreSQL/PostGIS | PASS | Disposable PostGIS 16-3.4 migration test passed |
| Alembic | PASS | 0001-0007 SQLite upgrade and metadata parity |
| Redis/RQ | PARTIAL | Dependencies, worker service and Redis connectivity implemented; worker crash/retry end-to-end test pending |
| RBAC | PASS | Six configurable role names plus legacy/owner roles |
| Conflict resolution | PASS | Server API list and resolution tested |
| Backup/restore | PASS | Disposable PostgreSQL dump/restore marker verified |
| PWA | PARTIAL | IndexedDB, push/pull, photos and conflict archive; browser smoke test pending |
| Flutter | FAIL | Skeleton only; no complete local schema/API workflow/build |
| Heavy engines | BLOCKED | Libraries absent; truthful unavailable adapters remain |
| Android APK/AAB | BLOCKED | Flutter SDK unavailable |
| Web build | BLOCKED | Flutter SDK unavailable |
| iOS | BLOCKED | macOS/Xcode/signing unavailable |
| Commercial ready | FAIL | Security and native field integrations are incomplete |

## Engine matrix

- trend2d: adapter ready; runtime tested.
- orientation: adapter ready; runtime tested.
- idw: adapter ready; runtime tested.
- downhole_composite: adapter ready; runtime tested.
- pykrige: adapter ready and library installed; runtime tested.
- gempy: adapter unavailable; library not installed.
- loopstructural: adapter unavailable; library not installed.
- pygslib: adapter unavailable; library not installed.
- pygimli: adapter unavailable; library not installed.
