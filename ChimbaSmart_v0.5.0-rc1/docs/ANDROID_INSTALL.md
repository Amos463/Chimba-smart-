# Android pilot installation

The pilot Android client is a Capacitor wrapper around the PWA. It bundles the
web assets locally; account, project, synchronization, attachment, and report
requests go to the server URL configured on the login screen.

## Build and download

Android builds run only in GitHub Actions. Open the successful
[`Android testing builds`](https://github.com/Amos463/Chimba-smart-/actions/workflows/android-build.yml)
run for the `market-pilot` branch and download its
`chimbasmart-capacitor-testing-signed-*` artifact. The artifact includes a debug
APK, a testing-signed release APK, a testing-signed AAB, and `SHA256SUMS`.
These testing artifacts are not production-signed.

Before installing, extract the artifact and verify its files:

```sh
sha256sum -c SHA256SUMS
adb install -r chimbasmart-testing-signed.apk
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
