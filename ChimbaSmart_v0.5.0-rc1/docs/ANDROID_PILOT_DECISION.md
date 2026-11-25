# Android pilot client decision

**Decision: choose option B — package the tested PWA in a Capacitor Android shell.**

The hosted Playwright field scenario passed in [Backend CI run 45648096883](https://github.com/Amos463/Chimba-smart-/actions/runs/45648096883), and the web/PWA checks passed in [run 45648096960](https://github.com/Amos463/Chimba-smart-/actions/runs/45648096960). The PWA remains the primary field client; interrupted attachment uploads, restore behavior, and real-device operation are still unverified. The existing Flutter client remains PARTIAL and must not be presented as a pilot-ready alternative.

## Options

| Option | Effort estimate | Offline behavior | Main risks |
|---|---:|---|---|
| A — bring Flutter to pilot parity | Approximately 3–5 engineering weeks, then device/field validation | SQLite schema and capture primitives exist, but durable camera uploads, complete project selection/pull, refresh/logout, conflict resolution, reports and restart/network-loss acceptance still need implementation. | Reimplements workflows already present in the PWA; risks divergent validation and sync behavior; current Flutter coverage does not demonstrate persistence or device acceptance. |
| B — Capacitor shell around the PWA | Approximately 3–5 engineering days for shell/configuration/CI, excluding owner server setup and real-device acceptance | Bundled PWA assets plus IndexedDB/Service Worker preserve the existing offline queue; API access requires a configurable HTTPS server URL. Android WebView storage, service-worker behavior and permission handling must be verified. | WebView geolocation/camera permissions, server URL/CORS configuration, attachment durability, and Android WebView version differences require real-device checks. |

## Rationale and limits

The repository's [`FLUTTER_MOBILE_STATUS.md`](FLUTTER_MOBILE_STATUS.md) records that Flutter is an incremental foundation: several required workflows are not integrated and persistence/restart/network-loss tests are absent. By contrast, the PWA has an established IndexedDB queue and is receiving the pilot sample, assay, QA/QC, conflict, and analysis workflows. Sharing that implementation is the lower-risk path for a small pilot.

This decision does **not** make the Android app complete or accepted. Before calling the shell pilot-ready:

1. Keep the PWA browser flow as the acceptance source of truth.
2. Package its assets locally and support a configurable HTTPS API URL; do not hard-code a production domain.
3. Verify GPS, camera/file chooser, offline restart, upload recovery, token refresh, sync and PDF behavior on a physical Android device.
4. Build APK/AAB only with GitHub Actions. Use testing signing until owner signing secrets are configured.
5. Keep Flutter marked PARTIAL and do not claim client parity until its separate acceptance gates pass.

Production server URL, Android signing, and real-device checks remain owner/external actions.
