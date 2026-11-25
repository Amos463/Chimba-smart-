# Security and license clearance

Status date: 2026-11-25
Overall status: **BLOCKED** for commercial clearance.

## Security status

| Control | Status | Evidence / remaining work |
|---|---|---|
| Attachment authorization | PASS | Upload now requires project `update` permission; read-only denial test was added and passed. |
| API exposure default | PASS (local Compose only) | Compose binds API to `127.0.0.1`; production HTTPS proxy and deployment review remain required. |
| Mutable Flutter action in release workflow | PASS | Flutter action uses a verified immutable commit. Android SDK setup was also pinned when fixing CI. |
| Secret handling | PARTIAL | Workflow tests use test-only values. Production database, Redis, JWT, SMTP, signing secrets and repository environment approvals require owner configuration. |
| Full production security review | NOT RUN | No deployed production configuration, HTTPS scan, monitoring validation or external penetration test. |
| Dependency vulnerability audit | PARTIAL | Hosted run [45558488839](https://github.com/Amos463/Chimba-smart-/actions/runs/45558488839) found 127 advisories across five packages: PyJWT 2.10.1, pytest 8.3.5, python-multipart 0.0.20, Pillow 11.2.1 and Starlette 0.46.2. Direct pins were updated to PyJWT 2.15.1, pytest 9.0.3, python-multipart 0.0.34, Pillow 13.0.0 and FastAPI 0.165.0 (which resolves Starlette 1.10.0). Local `pip-audit -r backend/requirements.txt` now reports no known vulnerabilities; hosted verification of the updated pins is pending. |

## License and SBOM status

| Requirement | Status | Evidence / remaining work |
|---|---|---|
| Direct dependency inventory | PARTIAL | `THIRD_PARTY_LICENSE_AUDIT.md` records selected direct dependencies and known license flags. |
| Reproducible direct/transitive SBOM | BLOCKED | No complete checked-in lock for all Python dependencies and no consolidated cross-ecosystem SBOM with license/notices was produced. Python requirements include unpinned dependencies. |
| EUPL/GPL review | BLOCKED | GemPy EUPL-1.2, PostGIS/QGIS GPL components and PyGSLIB mixed MIT/GPL files require owner/counsel review for intended deployment/distribution. |
| Legal approval | NOT RUN | No counsel or owner approval is recorded. |

## Known legal flags

- GemPy and gempy-engine are recorded as EUPL-1.2 in the existing inventory.
- PostGIS/QGIS GPL obligations and psycopg LGPL notices need distribution-model review.
- PyGSLIB source contains mixed license provenance and has no reproducible supported runtime.
- Transitive Python, Dart/Flutter and native/system dependency notices are not yet fully enumerated.

This document is an engineering status record, not legal advice. Do not mark commercial distribution or SaaS licensing as cleared until a reproducible SBOM/notices inventory and written owner/legal approval exist.
