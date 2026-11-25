# Final market-readiness report

Status date: 2026-11-25
Evidence checkpoint: `b8340717e202a239c8df849d79b046db46abec21`

## Decision

**BLOCKED — not approved for commercial release or production deployment.** The current evidence supports an engineering release candidate only. A successful build or unit suite does not establish field, scientific, disaster-recovery, security, or legal readiness.

## Gate summary

| Priority | Status | Evidence and remaining blocker |
|---|---|---|
| GitHub Actions | PARTIAL | Five root workflows are discovered. Engine CI and web build passed; Android build and main-branch release validation passed. Backend integration/migration/JS checks passed, but the audit found 127 advisories. Patched pins are locally audited; hosted verification is pending. |
| Flutter field acceptance | PARTIAL | SQLite v2 and preliminary capture/sync code exist. Project selection, durable camera uploads, restart, conflict resolution, complete auth lifecycle and device acceptance are not verified. |
| PWA acceptance | PARTIAL | Web build and JS syntax checks passed. Browser offline/restart/upload recovery and multi-device E2E were not run. |
| Engine worker | PARTIAL | API-to-Redis-to-RQ persistence and ordinary worker restart were exercised. Isolated engine-worker execution, crash recovery and retry behavior remain unverified. PyGSLIB is blocked; pyGIMLi inversion is not implemented. |
| Backup/restore | PARTIAL | A logical restore recovered 1 project, 1 record, 3 jobs and 12 audit events; a separate attachment-volume marker was checksum-verified. A complete application and attachment restore plus API verification was not performed. |
| Android release | PARTIAL | Corrected hosted build completed and uploaded APK/AAB testing artifacts with SHA-256 values. No physical-device install or field workflow test is evidenced. Production signing is not configured. |
| Security and licensing | BLOCKED | Three previously identified code/configuration findings were fixed. The hosted dependency audit found 127 advisories across five packages; direct pins are patched and local `pip-audit` reports none, with hosted rerun pending. Production HTTPS/monitoring, full transitive SBOM/notices, owner security configuration and legal approval remain outstanding. |
| Commercial/field approval | BLOCKED | Qualified geologist review, supervised field pilot, owner approvals, production infrastructure, legal clearance and real-device acceptance are required. |

## GitHub Actions evidence

| Workflow | Run | Result |
|---|---|---|
| Backend CI | [Run 45557088943](https://github.com/Amos463/Chimba-smart-/actions/runs/45557088943) | Failed: Redis test used hardcoded port 56379. The endpoint was corrected in `b834071`. The subsequent [run 45558488839](https://github.com/Amos463/Chimba-smart-/actions/runs/45558488839) passed integration tests (34 passed, 3 skipped), migrations and JS syntax, but failed `pip-audit` with 127 advisories across 5 packages. Patched dependency set is locally audited; hosted rerun pending. |
| Engine CI | [Run 45557089004](https://github.com/Amos463/Chimba-smart-/actions/runs/45557089004) | PASS. Synthetic engine tests, registry checks and isolated image build completed successfully. |
| Android testing builds | [Run 45557089303](https://github.com/Amos463/Chimba-smart-/actions/runs/45557089303) | Failed because deprecated SDK `tools` was requested. Fixed by pinning the setup action and requesting platform-tools, Android 36 and build-tools 36.0.0. [Rerun 45558488726](https://github.com/Amos463/Chimba-smart-/actions/runs/45558488726) succeeded and uploaded [artifact 14997580735](https://github.com/Amos463/Chimba-smart-/actions/runs/45558488726/artifacts/14997580735). Checksums are in `ANDROID_RELEASE_REPORT.md`. |
| Web/PWA checks | [Run 45557089165](https://github.com/Amos463/Chimba-smart-/actions/runs/45557089165) | PASS: JavaScript syntax, Flutter analyze/tests, web build and artifact upload. This is not browser E2E evidence. [Web artifact](https://github.com/Amos463/Chimba-smart-/actions/runs/45557089165/artifacts/14996162524). |
| Release validation | [Run 45558488738](https://github.com/Amos463/Chimba-smart-/actions/runs/45558488738) | PASS: backend and Flutter release gates passed on `main`; owner gate and publish job were skipped as intended. No release was published. |

The GitHub API integration returned HTTP 403 for repository Actions settings and manual dispatch. This does not prevent push-triggered runs. No tag was created and no release was published.

## Tests and operational checks

- Local backend API tests: **26 passed, 1 skipped, 1 warning**. The Redis availability test was skipped because local Redis/Docker was unavailable.
- Python backend `compileall`: **PASS**.
- All five root workflow YAML files parsed locally: **PASS**.
- Updated backend dependency pins were audited locally with `pip-audit -r backend/requirements.txt`: **No known vulnerabilities found**. A hosted rerun is still needed.
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
