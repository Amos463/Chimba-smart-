# ChimbaSmart cross-platform UI foundation — v0.1

This archive is a **Flutter UI foundation/prototype**, not a production app and not a completed ChimbaSmart rebuild. It establishes an adaptive interface direction for Android, iOS, Windows, macOS, Linux and Web using Flutter's supported platform targets.

## Included
- Adaptive navigation: bottom navigation on narrow/mobile layouts and navigation rail on wide/desktop layouts.
- Kiswahili screens for dashboard, field capture categories, map workspace, engine processing centre and data management.
- Engine-specific input hints based on official documentation patterns.
- Proposed shared data contract in `docs/data-contract-v1.md`.

## Not included / not yet implemented
- SQLite/Drift local persistence, offline attachment storage, background sync or conflict resolution.
- GPS, camera, compass/magnetometer, file picker or external Bluetooth instrument integrations.
- Live maps, offline map packages, API authentication, PostgreSQL/PostGIS or object storage.
- GemPy, LoopStructural, PyGSLIB, PyKrige, pyGIMLi or QGIS adapters.
- Security hardening, automated tests, app signing, store deployment or production validation.

## Run
Install Flutter, then from this folder:

```bash
flutter pub get
flutter analyze
flutter run -d chrome
```

Build Android on a configured Android SDK environment:

```bash
flutter build apk --release
```

Flutter iOS builds require macOS with Xcode. Windows/macOS/Linux desktop builds require their respective platform toolchains. A Linux Codespace can prepare/test common Dart code and build Android/web if configured, but cannot produce signed iOS App Store binaries without macOS/Xcode.

## Important
The current `chimbasmart.zip` PWA has not been migrated here. This is a new UI foundation intended to be reviewed before it replaces the PWA. Do not treat demo counters or statuses as live data.
