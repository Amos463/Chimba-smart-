# Open-source engine matrix

Audit date: 2026-11-24

| Engine / integration | Maintainer ecosystem | Selected version | License | Python 3.12 | Adapter status | Runtime evidence |
|---|---|---|---|---|---|---|
| PyKrige | PyKrige project | 1.7.3 | BSD-3-Clause | Compatible | READY | Ordinary kriging synthetic test passed |
| GemPy | GemPy project | 2026.0.3 / gempy-engine 2026.0.3.post1 | EUPL-1.2 | Compatible | READY | Real implicit model compute test passed |
| LoopStructural | Loop3d project | 1.12.0 | MIT | Compatible | READY | Claudius synthetic dataset executed and returned finite values |
| pyGIMLi | pyGIMLi project | 1.6.1 / pgcore 1.6.0 | Apache-2.0 | Compatible | READY for ERT forward modelling | Three-measurement synthetic ERT forward model passed |
| PyGSLIB | GSLIB ecosystem | No released PyPI distribution found | Source/distribution license not established | Unavailable | BLOCKED | No package or source distribution is configured |
| PyProj / PROJ | PyProj maintainers | 3.8.0 | MIT | Compatible | READY | CRS conversion dependency installed and existing geo tests use it |
| GDAL | GDAL/OSGeo | Not installed | LGPL-style OSGeo licensing | External-system dependency | PARTIAL | Native package and container workflow not yet provisioned |
| QGIS | QGIS Desktop / server ecosystem | Not integrated | GPL-2.0-or-later | External desktop/service dependency | PARTIAL | PostgreSQL/PostGIS remains available; no QGIS processing service |
| PostgreSQL/PostGIS | PostgreSQL/PostGIS community | Docker image 16-3.4 where tested | PostgreSQL License / GPL | Operational | PARTIAL | Disposable migration test passed; service deployment verification remains environment-specific |
| Isolated RQ engine worker | Redis/RQ | RQ 2.4.0 / Redis 7 | BSD family / Redis licensing | Configured | PARTIAL | Queue routing is implemented; worker crash/recovery test remains external |

## Classification rules

- **READY**: adapter performs a real library call and a synthetic execution test passes.
- **PARTIAL**: dependency or infrastructure exists but full commercial workflow verification is incomplete.
- **BLOCKED**: no compatible, installable or license-clear implementation is available.

No engine is presented as a certified mineral resource or geotechnical result. Results remain exploratory until competent-person review.
