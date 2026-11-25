# Security and license clearance

Status date: 2026-11-25
Overall status: **BLOCKED** for commercial clearance.

## Security status

| Control | Status | Evidence / remaining work |
|---|---|---|
| Authentication and session revocation | PARTIAL | Security review confirmed bcrypt's 72-byte truncation and access-token survival after logout/reset. Fixes use SHA-256-prehashed bcrypt for new hashes, reject legacy bcrypt passwords of 72+ bytes, bind access tokens to refresh sessions, and invalidate tokens by user auth version on password reset. Local backend suite: 38 passed, 5 skipped, 1 warning; fresh and existing-user migrations plus metadata parity through 0008 passed. Accounts with legacy passwords of 72+ bytes must reset; hosted CI for these changes and production configuration remain unverified. |
| Attachment authorization | PASS | Upload now requires project `update` permission; read-only denial test was added and passed. |
| API exposure default | PASS (local Compose only) | Compose binds API to `127.0.0.1`; production HTTPS proxy and deployment review remain required. |
| Mutable Flutter action in release workflow | PASS | Flutter action uses a verified immutable commit. Android SDK setup was also pinned when fixing CI. |
| Secret handling | PARTIAL | Workflow tests use test-only values. Production database, Redis, JWT, SMTP, signing secrets and repository environment approvals require owner configuration. |
| Full production security review | PARTIAL | A read-only code review was completed and its two confirmed authentication findings were fixed with regression tests. No deployed production configuration, HTTPS scan, monitoring validation or external penetration test was available. |
| Dependency vulnerability audit | PASS | Hosted [run 45560541803](https://github.com/Amos463/Chimba-smart-/actions/runs/45560541803) reports `No known vulnerabilities found`. The prior scan found 127 advisories across PyJWT 2.10.1, pytest 8.3.5, python-multipart 0.0.20, Pillow 11.2.1 and Starlette 0.46.2. Updated pins are PyJWT 2.15.1, pytest 9.0.3, python-multipart 0.0.34, Pillow 13.0.0 and FastAPI 0.165.0 (resolving Starlette 1.10.0). Local audit and tests also pass. |

## License and SBOM status

| Requirement | Status | Evidence / remaining work |
|---|---|---|
| Direct dependency inventory | PARTIAL | `THIRD_PARTY_LICENSE_AUDIT.md` records selected direct dependencies and known license flags. |
| Reproducible direct/transitive SBOM | PARTIAL | [`DEPENDENCY_SBOM_PYTHON.cdx.json`](./DEPENDENCY_SBOM_PYTHON.cdx.json) is a reproducible CycloneDX 1.6 snapshot generated with cyclonedx-bom 9.0.0; it has 58 resolved Python components, license identifiers and dependency entries. The Flutter lock resolves 118 package roots; 115 non-root/non-SDK packages have license/notice files, but there is no consolidated Dart SBOM or checked-in license-text archive. Python `numpy`, `pyproj`, `weasyprint` and transitive dependencies are not version-locked in the requirements manifest. |
| EUPL/GPL review | BLOCKED | GemPy EUPL-1.2, PostGIS/QGIS GPL components and PyGSLIB mixed MIT/GPL files require owner/counsel review for intended deployment/distribution. |
| Legal approval | NOT RUN | No counsel or owner approval is recorded. |

## Known legal flags

- GemPy and gempy-engine are recorded as EUPL-1.2 in the existing inventory.
- PostGIS/QGIS GPL obligations and psycopg LGPL notices need distribution-model review.
- PyGSLIB source contains mixed license provenance and has no reproducible supported runtime.
- The Python SBOM has license identifiers for its 58 components, but embeds license text for only 4. Dart package license files have not been normalized into the SBOM; native/system dependency notices remain unaudited.

This document is an engineering status record, not legal advice. Do not mark commercial distribution or SaaS licensing as cleared until a reproducible SBOM/notices inventory and written owner/legal approval exist.
