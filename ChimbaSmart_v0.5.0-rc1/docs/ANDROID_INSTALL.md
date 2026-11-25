# Android pilot installation

The pilot Android client is a Capacitor wrapper around the PWA. It bundles the
web assets locally; account, project, synchronization, attachment, and report
requests go to the server URL configured on the login screen.

## Build and download

Android builds run only in GitHub Actions. The verified build for commit
`0cc9c97` is [run 45651643751](https://github.com/Amos463/Chimba-smart-/actions/runs/45651643751).
Download the
[`chimbasmart-capacitor-testing-signed-4` artifact](https://github.com/Amos463/Chimba-smart-/actions/runs/45651643751/artifacts/15040127397)
from that run. It contains a debug APK, a testing-signed release APK, a
testing-signed AAB, and `SHA256SUMS`. These testing artifacts are not
production-signed. The artifact expires on 2026-12-09.

Before installing, extract the artifact and verify its files:

```sh
sha256sum -c SHA256SUMS
adb install -r chimbasmart-testing-signed.apk
```

Verified SHA-256 values:

```text
4f1f39245ed1513cd7e9105682e6b2011139dfd2503e1d171a26d3616e1046e1  chimbasmart-debug.apk
7c914bd64d651b806799ded6ae9be1c4cf0e7a61f5bf5e394707e52596cbe0d9  chimbasmart-testing-signed.apk
03391230c711c3d6510c988f74446055d02639a3946eaad4af1abb3417ae91b4  chimbasmart-testing-signed.aab
```

Allow installation from the file manager or browser used to download the APK.
The AAB is for store/test distribution tooling and is not installed directly
with `adb`.

## First login and server URL

1. Deploy the API behind HTTPS and ensure its CORS configuration allows the
   Capacitor Android origin `https://localhost`.
2. Open ChimbaSmart and enter the full HTTPS API base URL on the login screen,
   for example `https://pilot.example.org`.
3. Save the URL, then enter the username and password provisioned by the
   project administrator.
4. Select the correct project before capturing data.

HTTP is rejected except for localhost development. The server URL is stored in
the app's local WebView storage. Do not configure production credentials or
personal data on a shared test device.

## Device acceptance checklist

These device checks are **NOT RUN** until a pilot owner installs the Actions
artifact on a physical Android device and records the model, Android version,
artifact run, and results.

- [ ] Install the APK and complete first login.
- [ ] Load and select a project.
- [ ] Capture a sample with GPS coordinates.
- [ ] Capture and durably retain a sample photo.
- [ ] Go offline, capture a sample, force-close/restart the app, and verify it remains.
- [ ] Restore network access and verify sample and photo synchronization.
- [ ] Add a laboratory result to an existing sample.
- [ ] Run analysis and download a report.
- [ ] Verify token refresh and logout.

Flutter remains a separate, incomplete client and is not the selected pilot app.
