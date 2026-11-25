# Full backup and restore report

Status date: 2026-11-25
Overall status: **PARTIAL** — complete production-equivalent restore has not passed.

## Evidence

| Component / check | Status | Result |
|---|---|---|
| PostgreSQL/PostGIS logical dump and restore | PARTIAL | Disposable logical dump restored into a fresh database. |
| Project and records | PASS (limited sample) | Restored database contained 1 project and 1 record. |
| Jobs | PASS (limited sample) | Restored database contained 3 jobs. |
| Audit history | PASS (limited sample) | Restored database contained 12 audit events. |
| Attachment files | PARTIAL | A separate attachment-volume marker file was restored and SHA-256 checked. No real attachment object/metadata relationship was included in this full path. |
| Migrations on restored system | NOT RUN | No complete restored application upgrade/readiness sequence was performed. |
| API checks against restored environment | NOT RUN | API health, project access and record/attachment retrieval were not tested against the restored database and files. |
| Recovery-point/recovery-time objective | NOT RUN | No timed disaster-recovery exercise. |

This evidence is stronger than a marker-only database test, but it does not qualify as a complete application restore: the project/record/job/audit database and attachment marker were separate checks.

## Required completion

Restore a consistent database dump and all attachment objects into isolated PostgreSQL/PostGIS and storage, apply migrations, verify project-scoped API access and attachment checksums/relationships, exercise readiness and representative APIs, then record restore duration and row/object reconciliation. Do not restore into production without owner approval.
