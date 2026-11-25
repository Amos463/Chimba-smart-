# Flutter mobile status

Status date: 2026-11-25

## Current implementation

The Flutter code is an incremental field foundation, not a finished field application:

- SQLite `records`, `sync_state` and `attachments` tables, schema migration version 2.
- Local UUID records and pending/retry/synced/conflict/rejected sync states.
- Basic token storage and login; pending push to `/sync/push`.
- GPS permission/request helper.
- A home screen, generic GPS local observation action and Kiswahili field-capture form for sample, assay, collar, interval and orientation records.
- Project listing and server-pull methods exist in `SyncService`; foreground push is implemented.
- Camera, durable attachment store, project selection/retrieval, pull cursor, token refresh/logout, conflict-resolution UI, CSV, drillhole, assay, QA/QC, map and reports are not fully integrated.
- Test coverage includes analyze and a home-widget test; no persistence, restart, attachment, or network-loss acceptance tests exist.

## Verified from prior checkpoint

- Flutter analyze and widget test passed.
- Flutter web, Android debug APK, release APK and AAB were built locally. The release APK/AAB use the Android debug certificate and are not production-signed.
- No GitHub Actions workflow had been present at audit start.

## Release gate

Status is **PARTIAL**. Do not replace the PWA or describe the Flutter client as an offline-first production field tool until local schema migration, API pull/push, attachments, conflict resolution and device restart tests pass.

## Owner actions

- Supply production Android keystore through GitHub Actions secrets.
- Install APK on supported Android devices and approve permission/GPS/camera workflows.
- Provide macOS/Xcode and Apple signing configuration if iOS distribution is required.
