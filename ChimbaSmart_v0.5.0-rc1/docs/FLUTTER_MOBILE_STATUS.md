# Flutter mobile status

Status date: 2026-11-25

## Current implementation

The Flutter code is a small working foundation, not a finished field application:

- SQLite `records` and `sync_state` tables, schema version 1.
- Local UUID records and pending/retry/synced/conflict/rejected sync states.
- Basic token storage and login; pending push to `/sync/push`.
- GPS permission/request helper.
- One home screen with a generic local observation action.
- Camera, durable attachment store, project selection/retrieval, pull cursor, token refresh/logout, conflict-resolution UI, CSV, drillhole, assay, QA/QC, map and reports are not fully integrated.
- Test coverage currently consists of a home-widget test; no device/restart/network-loss acceptance tests exist.

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
