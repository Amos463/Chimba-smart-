# Mkataba wa processing engines v1.1

Kila engine inapokea `dataset.build()` yenye CRS iliyotajwa, raw collar/survey/interval, sampuli huru (`samples`), assay (`assays`), orientation na `input_hash`. Engine inarudisha JSON-safe output yenye `input_hash`, CRS, parameters/method na warnings.

| Engine | Hali kwenye ZIP hii | Maelezo |
|---|---|---|
| `trend2d` | Imeandikwa | Regression ya mwelekeo kwa sampuli huru zenye assay g/t pekee. Haichanganyi downhole assay na collar. |
| `orientation` | Imeandikwa | Mean orientation ya strike/dip; phone compass inaonya kuwa ni low-confidence. |
| `idw` | Imeandikwa + tests zinahitajika | IDW grid ya uchunguzi kwa NumPy; si kriging. |
| `downhole_composite` | Imeandikwa | Length-weighted compositing ya downhole assay intervals; haifanyi desurveying wala domain estimation. |
| `pykrige` | Adapter imeandikwa; dependency ya hiari | Ordinary Kriging kupitia PyKrige; inahitaji Codespaces runtime validation na variogram review. |
| `gempy` | Haijakamilika | Inahitaji stratigraphic stack, structural groups, contacts na faults. |
| `loopstructural` | Haijakamilika | Inahitaji feature/contact/orientation constraints na model extent. |
| `pygslib` | Haijakamilika | Inahitaji compositing, domains, downhole survey/desurveying na assay QA/QC. |
| `pygimli` | Haijakamilika | Inahitaji method-specific measurements na electrode/sensor geometry. |

## Availability verification 2026-11-24

- PyKrige is importable and `test_optional_engines.py` ran as part of the backend suite.
- GemPy, LoopStructural, PyGSLIB and pyGIMLi are not installed in the current environment.
- Their registry entries remain `adapter_ready=false` and `NotImplementedError`/validation unavailable behavior is retained.
- No synthetic or fabricated results are reported for these engines.

`adapter_ready` ni false kwa engines zisizotekelezwa. Mfumo hautazipokea kama kazi zilizokamilika. Vizingiti vya sampuli ni vya awali; mtaalamu lazima achague variogram, QA/QC na model assumptions.
