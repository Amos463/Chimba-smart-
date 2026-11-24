# Open-source engine integration report

## Implemented adapters

### PyKrige

- Ordinary Kriging through `pykrige.ok.OrdinaryKriging`.
- Validates unique coordinates, QA/QC, sample type, and minimum sample count.
- Persists input hash and grid/variance output.
- Synthetic test passed.

### GemPy

- GemPy 2026.0.3 implicit 3D surface adapter.
- Accepts explicit contacts, an exact 6-value extent, resolution, orientation constraints, surface name and structural group.
- Creates a GemPy structural frame and executes `compute_model`.
- Synthetic real-model computation passed.
- No fallback or fabricated scalar field is produced.

### LoopStructural

- LoopStructural 1.12.0 implicit foliation adapter.
- Accepts XYZ constraints and origin/maximum bounds.
- Builds `GeologicalModel`, creates a foliation feature, evaluates a regular grid and rejects no-finite-value outputs.
- The packaged Claudius synthetic dataset returned finite values.

### pyGIMLi

- pyGIMLi 1.6.1 ERT forward-modelling adapter.
- Accepts electrode coordinates and A/B/M/N four-point measurements.
- Creates a pyGIMLi mesh and executes `pygimli.physics.ert.simulate`.
- Three synthetic measurements were reproduced positively.
- Inversion is not yet claimed: only real forward modelling is implemented.

### PyGSLIB

- Not implemented. No `pygslib` distribution is available on PyPI.
- The registry truthfully reports the dependency as unavailable.
- A source-distributed package, license review and isolated container are owner dependencies before implementation.

## Data conversion

Engine parameters are carried into the durable job input and added to the job dataset before validation/execution. The adapter output retains the CRS, input hash, engine version, warnings and method.

## Failure behavior

- Invalid inputs produce rejected jobs.
- Missing libraries produce unavailable/rejected status.
- Exceptions are converted to failed/rejected job results rather than fabricated success.
- Heavy engines are isolated in `requirements-open-source-engines.txt`; core requirements remain free of these optional packages.

## Runtime isolation

- Core API and core worker use `backend/Dockerfile`.
- Heavy engine jobs are routed to RQ queue `chimbasmart-engines`.
- `backend/Dockerfile.engines` installs the optional scientific dependencies in a separate container.
- Docker Compose includes an `engine-worker` service with Redis/PostgreSQL dependencies.
- If the engine worker is unavailable, queue submission remains a durable infrastructure failure rather than a fake successful result.

## Remaining scientific work

- GemPy: validate stratigraphic ordering and multiple surfaces/fault relationships.
- LoopStructural: support folds, faults and unconformities beyond foliation.
- pyGIMLi: implement and test measured-data inversion with explicit error models.
- PyGSLIB: obtain a legal source/distribution package and isolate native dependencies.
- GDAL/QGIS: provide native/container processing only after license and deployment design review.
