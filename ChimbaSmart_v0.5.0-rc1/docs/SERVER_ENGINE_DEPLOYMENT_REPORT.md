# Server engine deployment report

Audit date: 2026-11-25

## Current layout

- Core API and standard RQ worker use Python 3.12 and `backend/Dockerfile`.
- Heavy optional engines are pinned in `backend/requirements-open-source-engines.txt` and use `backend/Dockerfile.engines`.
- Heavy jobs (GemPy, LoopStructural, PyGIMLi, PyKrige) route to Redis queue `chimbasmart-engines`.
- `docker-compose.yml` declares the `engine-worker` service.
- Core requirements do not install GemPy, LoopStructural or pyGIMLi.

## PyGSLIB investigation

Official repository: <https://github.com/opengeostat/pygslib>, default branch `master`, audited commit `c26c3bff20c7cc16583c94fb850e17600b9a610d`, last pushed 2024-10-03. The repository is not archived. The code reports version `0.0.0.7.1.1`; GitHub releases show only `v0.0.0.3`.

Official distribution evidence:

- The OpenGeoStat Anaconda channel lists Linux PyGSLIB `0.0.0.6.0.0`, CPython 3.8 build `py38hd844fa7_0`, SHA-256 `950cae27c49c22619f7da6ba43d9cc58a2009804055ffdadb91d90833a258b99`.
- The latest upstream source commit does not have a corresponding Linux Python 3.12 binary.
- Linux conda binary imports depend on old `libgfortran.so.4`; current conda-forge solving selected `libgfortran.so.5` unless pinned.
- After pinning `libgfortran4=7.5.0`, import failed in VTK/netCDF: `undefined symbol: H5Pset_fapl_ros3`.
- Upstream source build under Python 3.12 failed before compilation because `numpy.distutils` is unavailable. It also requires a Fortran compiler, Cython, NumPy build tooling and a large VTK/Pandas/SciPy stack.

## Decision

**PyGSLIB: BLOCKED for production integration; retained in the roadmap.** A Python 3.8 + legacy Fortran + VTK/HDF5 container is technically conceivable but no currently verified, reproducible official Linux runtime was established. We will not route production jobs to an adapter that cannot import or produce tested results.

PyGSLIB uses Fortran wrappers and documents drillhole compositing, variograms and block modelling. Its `setup.py` declares `license='GPL and MIT'`; root `LICENSE.txt` is MIT, but source includes GPL-3 Cython modules, GPL-2 KT3D/KPROP code and Stanford/GSLIB notices. This requires component-level provenance/legal review before commercial redistribution or service exposure.

## Recommended compatible alternatives

- Existing ChimbaSmart length-weighted downhole composite remains available; it does not claim PyGSLIB equivalence.
- PyKrige is the current BSD-licensed ordinary-kriging adapter and can cover a subset of variogram/kriging work.
- GSTools is a candidate for additional open-source variogram/kriging workflows after separate license/version/runtime review.
- None of these alternatives supplies a verified PyGSLIB-equivalent resource-estimation/block-model workflow. Keep those capabilities marked BLOCKED rather than substituting a made-up result.

## Deployment status

Docker Compose syntax is validated. The heavy engine container has not been built or run in a production-like deployment, and engine-worker job execution/recovery has not been verified. GitHub-hosted Actions are planned/added separately; no run exists until workflows execute on GitHub.
