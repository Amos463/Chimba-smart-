# Android release report

Status date: 2026-11-25
Overall status: **PARTIAL**

## Hosted build evidence

| Check | Status | Evidence |
|---|---|---|
| Android SDK setup | PASS on corrected rerun | The failed run showed `sdkmanager` error `Failed to find package 'tools'`. Workflow now pins `android-actions/setup-android` and explicitly installs platform-tools, Android 36 and build-tools 36.0.0. |
| Debug APK, release APK and AAB | PASS | Corrected [run 45558488726](https://github.com/Amos463/Chimba-smart-/actions/runs/45558488726) built all three testing artifacts and verified non-empty files. |
| Artifact upload | PASS | [Artifact 14997580735](https://github.com/Amos463/Chimba-smart-/actions/runs/45558488726/artifacts/14997580735), `chimbasmart-android-testing-2`, uploaded successfully (154,874,370 bytes). |
| Production signing | BLOCKED | Owner production keystore and secrets are not configured. Testing builds must not be presented as production-signed. |
| APK install on real device | NOT RUN | No device installation evidence. |
| Login/project loading/offline restart/GPS/camera/sync | NOT RUN | No real-device acceptance evidence. |
| Processing result on device | NOT RUN | No device-triggered processing job returning a validated result. |

## Hosted artifact checksums

| Artifact | SHA-256 |
|---|---|
| Debug APK | `9f052503c67c2cee7d63ad1e1cb6befc9037ea0a7b94676071a31fc4062bd7fc` |
| Testing release APK | `141c156453b894861613cde9ae7ed1e701a8ed6bd17e47e39daf6d013db32ea7` |
| Testing release AAB | `0f8699d360ce7b88d48f91036b16192315233ac9172c0d3b72aeb12dd0ce2c58` |

The previous Android workflow run [45557089303](https://github.com/Amos463/Chimba-smart-/actions/runs/45557089303) failed before Flutter setup/build. It produced no workflow APK/AAB artifacts. Historical local-build hashes in older readiness notes are not checksums for artifacts from the corrected hosted workflow.

## Release gate

Hosted artifacts are testing-signed only. Their existence and hashes do not prove installation or field acceptance. Test installation and required workflows on an actual supported Android device. Production signing and Play distribution require owner credentials and approval.
