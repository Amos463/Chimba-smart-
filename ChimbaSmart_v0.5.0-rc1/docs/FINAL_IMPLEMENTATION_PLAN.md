# Final implementation plan

This plan tracks remaining work by evidence and dependency. It is not a completion claim.

## Immediate code/CI work

1. **PASS** — Reconcile overview, commercial audit, data contract and engine documentation with implementation and PyGSLIB source findings.
2. **PARTIAL** — Add GitHub-hosted CI for core backend, optional engine smoke tests, Flutter Android and Flutter web builds. YAML parses locally; GitHub execution still requires a push/Actions runner.
3. **PARTIAL** — Add stronger Flutter offline repositories, versioned schema and API lifecycle; keep PWA as existing primary field client until equivalent tests pass.
4. **PARTIAL** — Expand pyGIMLi from forward modelling to validated inversion using synthetic reference cases.
5. **BLOCKED** — PyGSLIB isolated runtime: needs an official compatible Linux build or maintainers' supported Python/NumPy recipe, plus a resolved VTK/HDF5/GFortran stack.

## Runtime and release gates

6. **NOT RUN** — Actual API → Redis → isolated worker → persisted job acceptance; worker restart/crash/retry and Redis/database recovery.
7. **NOT RUN** — Browser PWA offline capture, forced termination/restart, interrupted attachments, conflict recovery, multi-device pull/push.
8. **NOT RUN** — Full project/database/PostGIS/attachments backup and clean restore with API checks.
9. **BLOCKED** — Android real-device field acceptance and production signature; owner signing material is required.
10. **BLOCKED** — iOS release build/signing requires macOS/Xcode and owner Apple credentials.
11. **BLOCKED** — Tanzania authorized field pilot, qualified geological review, and customer acceptance.
12. **BLOCKED** — Commercial legal clearance for EUPL/GPL components, PyGSLIB mixed license, dependency transitive notices and privacy terms.

## Release decision

Do not label the product commercially ready until steps 6-12 have signed evidence and the remaining PARTIAL requirements have acceptance criteria.
