# Processing engine contract v1.2

Kila engine inapokea `dataset.build()` yenye CRS iliyotajwa, raw collar/survey/interval, sampuli huru (`samples`), assay (`assays`), orientation na `input_hash`. Engine inarudisha JSON-safe output yenye `input_hash`, CRS, parameters/method na warnings.

| Engine | Runtime status | Maelezo |
|---|---|---|
| `trend2d` | PASS | Regression ya mwelekeo kwa sampuli huru zenye assay g/t pekee. Haichanganyi downhole assay na collar. |
| `orientation` | PASS | Mean orientation ya strike/dip; phone compass inaonya kuwa ni low-confidence. |
| `idw` | PASS | IDW grid ya uchunguzi; si kriging. |
| `downhole_composite` | PASS | Length-weighted compositing ya assay intervals; haifanyi desurveying wala domain estimation. |
| `pykrige` | PASS | Ordinary Kriging kupitia PyKrige 1.7.3; synthetic test passed, variogram review remains mandatory. |
| `gempy` | PASS | GemPy 2026.0.3 computes implicit surface from explicitly supplied contacts and extent. |
| `loopstructural` | PASS | LoopStructural 1.12.0 computes foliation values on a grid from constraints. |
| `pygslib` | BLOCKED | Official OpenGeoStat Conda/source located; source build and Linux binary runtime are blocked as documented. |
| `pygimli` | PARTIAL | pyGIMLi 1.6.1 synthetic ERT forward modeling passed; measured-data inversion is not implemented. |

## Runtime verification 2026-11-25

- Latest suite: backend 35 passed, 1 skipped with disposable Redis; optional-engine suite 4 passed.
- GemPy, LoopStructural and pyGIMLi were installed only in the isolated local validation environment and runtime-tested.
- PyGSLIB is unavailable to the production API registry until an importable supported worker environment exists.
- No synthetic or fabricated results are reported for unavailable functionality.

The adapter readiness flag only means a library call exists; it does not indicate geological or commercial certification. Domain experts must select variograms, QA/QC and model assumptions.
