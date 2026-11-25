# Mobile acceptance report

Status date: 2026-11-25
Overall status: **PARTIAL** — the PWA remains the primary field client. Flutter is not an accepted replacement.

## Acceptance matrix

| Requirement | Status | Evidence / gap |
|---|---|---|
| SQLite persistence and migrations | PARTIAL | SQLite schema v2 has records, sync state and attachment metadata. Migration/reopen tests across restart have not been run. |
| Project selection | BLOCKED | Project listing primitive exists; a complete selection workflow is not integrated into field capture. |
| GPS sample capture | PARTIAL | GPS permission/helper and local form exist. Device GPS behavior, coordinate/CRS validation and persistence are not field-tested. |
| Assay capture | PARTIAL | Form code exists, but field-specific contract acceptance and server round trip are not proven. |
| Collar, survey and intervals | PARTIAL | Preliminary local forms exist; full survey contract, validations and synchronization are incomplete. |
| Geological orientation | PARTIAL | Preliminary form exists; no acceptance on a supported device. |
| Camera and durable photo storage | BLOCKED | Camera workflow, durable file storage, upload recovery and attachment relationship acceptance are incomplete. |
| Offline app restart | NOT RUN | No app restart persistence test or Android device execution. |
| Push and pull synchronization | PARTIAL | Foreground push and project/pull methods exist; end-to-end cursor/restart behavior is not established. |
| Conflict resolution | BLOCKED | Server conflict API exists; Flutter conflict presentation and resolution workflow are absent. |
| Token refresh and logout | BLOCKED | Basic token storage/login exists; refresh rotation and logout/session invalidation are not integrated in Flutter. |
| Network loss and recovery | NOT RUN | No device-level interruption/recovery test. |
| Reports and export | BLOCKED | Not integrated in the Flutter client. |
| Android build | PARTIAL | First hosted build failed at SDK package setup. Corrected hosted build is pending in [run 45558488726](https://github.com/Amos463/Chimba-smart-/actions/runs/45558488726). |
| Physical device acceptance | NOT RUN | No installation, GPS, camera, offline, sync or processing acceptance on a real device. |

## Verified implementation and tests

- SQLite schema v2 and a basic capture form for sample, assay, collar, interval and orientation records.
- Project listing, pull and push primitives in `mobile/lib/src/services/sync_service.dart`.
- Previous Flutter analyze and widget tests passed; the hosted web workflow also passed Flutter analyze/tests.
- No test currently proves durable record/photo persistence across process death or network recovery.

## Release gate

Do not mark Flutter as field-ready until persistence/migration, project selection, all required record contracts, camera storage, offline restart, token lifecycle, conflict resolution and recovery are tested on supported Android devices.
