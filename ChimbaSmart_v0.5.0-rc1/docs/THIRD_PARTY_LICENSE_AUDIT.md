# Third-party license audit

Audit date: 2026-11-25

This is an engineering dependency inventory, not legal advice. Commercial distribution must be reviewed by the project owner or legal counsel.

## Direct scientific dependencies

| Dependency | Version | License metadata | Commercial action |
|---|---|---|---|
| GemPy | 2026.0.3 | EUPL-1.2 | Review copyleft/network and distribution obligations; preserve attribution and EUPL notice |
| gempy-engine | 2026.0.3.post1 | EUPL-1.2 | Review with GemPy; include upstream notice text |
| LoopStructural | 1.12.0 | MIT | Preserve MIT notice and attribution |
| loop-common | 0.2.0 | MIT | Preserve MIT notice |
| loop-interpolation | 0.3.0 | MIT | Preserve MIT notice |
| PyKrige | 1.7.3 | BSD-3-Clause metadata in upstream package | Preserve BSD notice |
| pyGIMLi | 1.6.1 | Apache-2.0 metadata; pgcore Apache-2.0 | Preserve Apache notices and source attribution |
| pyproj | 3.8.0 | MIT metadata | Preserve MIT notice; PROJ native component may have separate notices |
| NumPy | 2.5.5 | BSD family upstream metadata | Preserve BSD notices |
| SciPy | 1.18.1 | BSD-3-Clause with SciPy copyright text | Preserve upstream license and notices |
| PyGSLIB source | upstream source `0.0.0.7.1.1` / official Linux Conda `0.0.0.6.0.0` | Mixed: root MIT license, `setup.py` declares `GPL and MIT`; GPL-3 Cython and GPL-2 KT3D/KPROP source plus Stanford/GSLIB notices | Do not commercially integrate or redistribute until per-file provenance, applicable license texts and counsel clearance are completed |

## Core direct dependencies

| Dependency | Version | License metadata |
|---|---|---|
| FastAPI | 0.165.0 | MIT (declared in generated Python SBOM) |
| SQLAlchemy | 2.0.40 | MIT upstream |
| Alembic | 1.15.2 | MIT upstream |
| Pydantic | 2.11.4 | MIT upstream |
| PyJWT | 2.15.1 | MIT |
| Starlette | 1.10.0 | BSD-3-Clause (FastAPI transitive dependency) |
| pytest | 9.0.3 | MIT (test dependency) |
| python-multipart | 0.0.34 | Apache-2.0 |
| Pillow | 13.0.0 | MIT-CMU |
| bcrypt | 4.3.0 | Apache-2.0 |
| psycopg | 3.2.13 | LGPL-3.0-only |
| Redis | 6.4.0 | upstream license metadata unavailable in this environment |
| RQ | 2.4.0 | upstream license metadata unavailable in this environment |
| WeasyPrint | 70.0 | BSD upstream; transitive native/system libraries require separate notice review |

## External or system components

- PostgreSQL: PostgreSQL License.
- PostGIS: GPL-2.0-or-later components require source-distribution/legal review.
- GDAL/PROJ: not deployed as a pinned application dependency; native licenses must be checked if packaged.
- QGIS: GPL-2.0-or-later; do not bundle/redistribute without GPL-compliant attribution and source obligations review.

## Source-disclosure flags

1. GemPy and gempy-engine use EUPL-1.2. Legal review is required for commercial SaaS, binary and redistribution models.
2. PostGIS/QGIS GPL components may impose source obligations when distributed or combined as a non-GPL product distribution.
3. WeasyPrint and native PDF dependencies require transitive OS/package notice review.
4. PyGSLIB has an official source and Conda distribution, but file-level license scope is mixed and the Linux binary is not currently importable with a reproducible supported native stack. It remains blocked.

## Required next actions

- Review the Python CycloneDX snapshot at `DEPENDENCY_SBOM_PYTHON.cdx.json`; generate the corresponding Dart/native SBOM and lock unpinned Python dependencies.
- Retain upstream `LICENSE`/`NOTICE` files in release source and binary distributions where required.
- Have counsel review the EUPL and GPL implications of the chosen SaaS and app-distribution model.
- Do not claim commercial license clearance until counsel sign-off is recorded.
