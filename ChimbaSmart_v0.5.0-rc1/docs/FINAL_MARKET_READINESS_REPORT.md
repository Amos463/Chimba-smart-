# Final market-readiness report

Status date: 2026-11-25
Hosted CI evidence checkpoint: `962e079a76247e5186bb071ca3bbd7935da5f943` (the authentication hardening described below was added afterward and still requires hosted validation).

## Decision

**BLOCKED — not approved for commercial release or production deployment.** All five hosted workflows now pass, and the backend audit reports no known vulnerabilities for the resolved requirements. The current evidence still supports an engineering release candidate only; it does not establish field, scientific, disaster-recovery, complete SBOM/license, production security, or legal readiness.

## Gate summary

| Priority | Status | Evidence and remaining blocker |
|---|---|---|
| GitHub Actions | PASS | Five root workflows are discovered. Backend, engine, Android, web and main-branch release validation have successful hosted runs. Publishing stayed skipped and no release was created. |
| Flutter field acceptance | PARTIAL | SQLite v2 and preliminary capture/sync code exist. Project selection, durable camera uploads, restart, conflict resolution, complete auth lifecycle and device acceptance are not verified. |
| PWA acceptance | PARTIAL | Web build and JS syntax checks passed. Browser offline/restart/upload recovery and multi-device E2E were not run. |
| Engine worker | PARTIAL | API-to-Redis-to-RQ persistence and ordinary worker restart were exercised. Isolated engine-worker execution, crash recovery and retry behavior remain unverified. PyGSLIB is blocked; pyGIMLi inversion is not implemented. |
| Backup/restore | PARTIAL | A logical restore recovered 1 project, 1 record, 3 jobs and 12 audit events; a separate attachment-volume marker was checksum-verified. A complete application and attachment restore plus API verification was not performed. |
| Android release | PARTIAL | Corrected hosted build completed and uploaded APK/AAB testing artifacts with SHA-256 values. No physical-device install or field workflow test is evidenced. Production signing is not configured. |
| Security and licensing | BLOCKED | Two confirmed authentication findings were fixed and tested locally; hosted CI for these changes is pending. Production HTTPS/monitoring, a complete transitive SBOM/notices inventory and legal approval remain outstanding. Legacy bcrypt hashes for passwords of 72+ bytes require secure reset. |
| Commercial/field approval | BLOCKED | Qualified geologist review, supervised field pilot, owner approvals, production infrastructure, legal clearance and real-device acceptance are required. |

## GitHub Actions evidence

| Workflow | Run | Result |
|---|---|---|
| Backend CI | [Run 45560541803](https://github.com/Amos463/Chimba-smart-/actions/runs/45560541803) | PASS: 34 passed, 3 skipped, 5 warnings; SQLite migration/metadata, JS syntax and `pip-audit` passed (`No known vulnerabilities found`). |
| Engine CI | [Run 45560541814](https://github.com/Amos463/Chimba-smart-/actions/runs/45560541814) | PASS. Synthetic runtime tests, registry check and isolated engine-worker image build passed. |
| Android testing builds | [Run 45557089303](https://github.com/Amos463/Chimba-smart-/actions/runs/45557089303) | Failed because deprecated SDK `tools` was requested. Fixed by pinning the setup action and requesting platform-tools, Android 36 and build-tools 36.0.0. [Rerun 45558488726](https://github.com/Amos463/Chimba-smart-/actions/runs/45558488726) succeeded and uploaded [artifact 14997580735](https://github.com/Amos463/Chimba-smart-/actions/runs/45558488726/artifacts/14997580735). Checksums are in `ANDROID_RELEASE_REPORT.md`. |
| Web/PWA checks | [Run 45557089165](https://github.com/Amos463/Chimba-smart-/actions/runs/45557089165) | PASS: JavaScript syntax, Flutter analyze/tests, web build and artifact upload. This is not browser E2E evidence. [Web artifact](https://github.com/Amos463/Chimba-smart-/actions/runs/45557089165/artifacts/14996162524). |
| Release validation | [Run 45560541798](https://github.com/Amos463/Chimba-smart-/actions/runs/45560541798) | PASS: backend and Flutter release gates passed on `main`; owner gate and publish job were skipped as intended. No release was published. |

The root-workflow discovery issue is resolved. The GitHub API integration still returns HTTP 403 for repository Actions settings and manual dispatch, but push-triggered workflows work. No tag was created and no release was published.

## Tests and operational checks

- Local backend suite on updated dependencies: **32 passed, 5 skipped, 1 warning**. The API-only suite was **26 passed, 1 skipped, 1 warning**; local Redis/Docker was unavailable.
- After the authentication changes: **38 passed, 5 skipped, 1 warning**; fresh SQLite migrations through 0008, existing-user upgrade and Alembic metadata check passed. These changes have not yet been run in hosted CI.
- Hosted backend suite: **34 passed, 3 skipped, 5 warnings**; the live workflow also passed migrations, JS syntax and dependency audit.
- Python backend `compileall`: **PASS**.
- All five root workflow YAML files parsed locally: **PASS**.
- Updated backend dependency pins were audited locally and in hosted CI: **No known vulnerabilities found**.
- PostGIS, RQ, restore and engine evidence is summarized in the linked acceptance reports; their limitations remain material.
- Physical Android acceptance, browser E2E, full restore/API test and field validation: **NOT RUN**.

## Required owner actions

1. Provide production secrets, HTTPS endpoint, monitoring and production database/Redis/object-storage configuration.
2. Configure required reviewers and approve commercial release gates only after independent evidence review.
3. Provide a production signing keystore; until then, builds are testing artifacts only.
4. Arrange Android device acceptance and supervised field pilot with qualified geological review.
5. Obtain legal review of EUPL/GPL and unresolved transitive dependency licenses.
6. Require complete attachment-inclusive restore test and production-like worker recovery test.

See [OWNER_ACTIONS.md](./OWNER_ACTIONS.md), [MOBILE_ACCEPTANCE_REPORT.md](./MOBILE_ACCEPTANCE_REPORT.md), [PWA_ACCEPTANCE_REPORT.md](./PWA_ACCEPTANCE_REPORT.md), [ENGINE_WORKER_ACCEPTANCE_REPORT.md](./ENGINE_WORKER_ACCEPTANCE_REPORT.md), [FULL_BACKUP_RESTORE_REPORT.md](./FULL_BACKUP_RESTORE_REPORT.md), [ANDROID_RELEASE_REPORT.md](./ANDROID_RELEASE_REPORT.md), and [SECURITY_AND_LICENSE_CLEARANCE.md](./SECURITY_AND_LICENSE_CLEARANCE.md).
