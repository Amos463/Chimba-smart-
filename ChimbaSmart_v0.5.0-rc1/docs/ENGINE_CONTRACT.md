# Mkataba wa processing engines v1.1

Kila engine inapokea `dataset.build()` yenye CRS iliyotajwa, raw collar/survey/interval, sampuli huru (`samples`), assay (`assays`), orientation na `input_hash`. Engine inarudisha JSON-safe output yenye `input_hash`, CRS, parameters/method na warnings.

| Engine | Hali kwenye ZIP hii | Maelezo |
|---|---|---|
| `trend2d` | Imeandikwa | Regression ya mwelekeo kwa sampuli huru zenye assay g/t pekee. Haichanganyi downhole assay na collar. |
| `orientation` | Imeandikwa | Mean orientation ya strike/dip; phone compass inaonya kuwa ni low-confidence. |
| `idw` | Imeandikwa + tests zinahitajika | IDW grid ya uchunguzi kwa NumPy; si kriging. |
| `downhole_composite` | Imeandikwa | Length-weighted compositing ya downhole assay intervals; haifanyi desurveying wala domain estimation. |
| `pykrige` | Adapter imeandikwa; dependency ya hiari | Ordinary Kriging kupitia PyKrige; inahitaji Codespaces runtime validation na variogram review. |
| `gempy` | READY on isolated engine dependency | GemPy 2026.0.3 runs a real implicit 3D surface model with contacts, orientations and explicit extent. |
| `loopstructural` | READY on isolated engine dependency | LoopStructural 1.12.0 evaluates real implicit foliation constraints over a regular grid. |
| `pygslib` | BLOCKED | No PyPI package/source distribution has been established; no fabricated adapter. |
| `pygimli` | READY for ERT forward modelling | pyGIMLi 1.6.1 runs real synthetic ERT forward responses; inversion is still not verified. |

## Availability verification 2026-11-24

- PyKrige is importable and `test_optional_engines.py` ran as part of the backend suite.
- GemPy, LoopStructural, PyGSLIB and pyGIMLi are not installed in the current environment.
- Their registry entries remain `adapter_ready=false` and `NotImplementedError`/validation unavailable behavior is retained.
- No synthetic or fabricated results are reported for these engines.

`adapter_ready` ni false kwa engines zisizotekelezwa. Mfumo hautazipokea kama kazi zilizokamilika. Vizingiti vya sampuli ni vya awali; mtaalamu lazima achague variogram, QA/QC na model assumptions.
