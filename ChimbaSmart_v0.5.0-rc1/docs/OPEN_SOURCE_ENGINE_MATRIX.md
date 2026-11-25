# Open-source engine matrix

Audit date: 2026-11-24

| Engine / integration | Maintainer ecosystem | Selected version | License | Python 3.12 | Adapter status | Runtime evidence |
|---|---|---|---|---|---|---|
| PyKrige | PyKrige project | 1.7.3 | BSD-3-Clause | Compatible | PASS | Ordinary kriging synthetic test passed |
| GemPy | GemPy project | 2026.0.3 / gempy-engine 2026.0.3.post1 | EUPL-1.2 | Compatible | PASS | Real implicit model compute test passed |
| LoopStructural | Loop3d project | 1.12.0 | MIT | Compatible | PASS | Claudius synthetic dataset executed and returned finite values |
| pyGIMLi | pyGIMLi project | 1.6.1 / pgcore 1.6.0 | Apache-2.0 | Compatible | PARTIAL | Three-measurement synthetic ERT forward model passed; inversion not verified |
| PyGSLIB | OpenGeoStat | Source `0.0.0.7.1.1` at `c26c3bff20c7cc16583c94fb850e17600b9a610d`; Linux Conda `0.0.0.6.0.0` CPython 3.8 | Mixed MIT/GPL source; component notices need review | Python 3.12 source build unsupported (`numpy.distutils` missing); binary targets 3.8 | BLOCKED | Source build and official Conda package import both failed in isolated tests; details in server deployment report |
| PyProj / PROJ | PyProj maintainers | 3.8.0 | MIT | Compatible | PARTIAL | CRS conversion dependency installed and existing geo tests use it |
| GDAL | GDAL/OSGeo | Not installed | LGPL-style OSGeo licensing | External-system dependency | PARTIAL | Native package and container workflow not yet provisioned |
| QGIS | QGIS Desktop / server ecosystem | Not integrated | GPL-2.0-or-later | External desktop/service dependency | PARTIAL | PostgreSQL/PostGIS remains available; no QGIS processing service |
| PostgreSQL/PostGIS | PostgreSQL/PostGIS community | Docker image 16-3.4 where tested | PostgreSQL License / GPL | Operational | PARTIAL | Disposable migration test passed; service deployment verification remains environment-specific |
| Isolated RQ engine worker | Redis/RQ | RQ 2.4.0 / Redis 7 | BSD family / Redis licensing | Configured | PARTIAL | Queue routing is implemented; worker crash/recovery test remains external |

## PyGSLIB official source evidence

- Repository: <https://github.com/opengeostat/pygslib> (not archived; last push 2024-10-03).
- Official Anaconda channel: <https://anaconda.org/opengeostat/pygslib>.
- Latest Linux package found: `pygslib-0.0.0.6.0.0-py38hd844fa7_0.tar.bz2`, SHA-256 `950cae27c49c22619f7da6ba43d9cc58a2009804055ffdadb91d90833a258b99`.
- The package expects old `libgfortran.so.4` and transitively imports VTK/netCDF.
- No matching maintained Python 3.12 Linux binary was found.
- Direct source installation on Python 3.12 fails while loading metadata because the setup script imports `numpy.distutils`.
- Isolated Conda installation initially failed on missing `libgfortran.so.4`; with an ABI-matched `libgfortran4=7.5.0`, import failed with `undefined symbol: H5Pset_fapl_ros3` from the VTK/netCDF stack.

## Classification rules

- **PASS**: adapter performs a real library call and a synthetic execution test passes for its documented scope.
- **PARTIAL**: dependency or infrastructure exists but full commercial workflow verification is incomplete.
- **BLOCKED**: no compatible, reproducible or license-clear implementation is available.

No engine is presented as a certified mineral resource or geotechnical result. Results remain exploratory until competent-person review.
