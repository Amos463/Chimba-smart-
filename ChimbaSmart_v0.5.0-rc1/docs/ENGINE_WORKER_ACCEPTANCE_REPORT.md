# Engine worker acceptance report

Status date: 2026-11-25
Overall status: **PARTIAL**

## Evidence matrix

| Requirement | Status | Evidence / gap |
|---|---|---|
| API-to-Redis enqueue | PASS | Disposable live stack accepted authenticated project/job work and routed it to Redis/RQ. |
| Worker-to-database persistence | PARTIAL | A queued job was consumed and persisted with engine version, input hash and a genuine scientific-input rejection reason. This verifies durable job/error recording, not a successful field-grade result. |
| Worker restart | PARTIAL | A job queued while the standard worker was stopped ran after worker restart. |
| Crash recovery | NOT RUN | No forced worker crash test with an active job was completed. |
| Retry policy | NOT RUN | Retry/backoff and exhausted-retry behavior have not been verified. |
| Isolated engine-worker image | PASS | [Engine CI run 45560541814](https://github.com/Amos463/Chimba-smart-/actions/runs/45560541814) built the engine-worker image successfully. Container execution against live Redis and PostgreSQL remains unverified. |
| Scientific result through isolated worker | NOT RUN | No successful scientific job was observed end-to-end through the isolated image and persisted database output. |

## Engine runtime status

| Engine | Status | Verified scope |
|---|---|---|
| Trend2D, Orientation, IDW, DownholeComposite | PASS | Synthetic/core tests; outputs remain exploratory. |
| PyKrige 1.7.3 | PASS | Synthetic ordinary-kriging adapter test. |
| GemPy 2026.0.3 | PASS | Synthetic implicit-model execution. |
| LoopStructural 1.12.0 | PASS | Claudius foliation evaluation returned finite values. |
| pyGIMLi 1.6.1 | PARTIAL | Synthetic ERT forward modeling works; inversion/reference recovery is not implemented. |
| PyGSLIB | BLOCKED | Python 3.12 source build fails on removed `numpy.distutils`; official CPython 3.8 Linux package fails import with `undefined symbol: H5Pset_fapl_ros3`. Mixed MIT/GPL source needs legal review. |

## Acceptance gate

Exercise the isolated worker with a scientifically valid reference dataset, then terminate it during a job, restart it, and verify idempotent retry, database results, provenance and audit history. Do not claim pyGIMLi inversion or PyGSLIB support before reproducible reference tests pass.
