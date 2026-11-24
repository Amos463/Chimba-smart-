# ChimbaSmart geological data contract v1.2

## Shared envelope
Every sync record has UUIDv4, project UUID, record type, payload, UTC timestamps, device ID, source method, optional CRS and client hash. Server recomputes canonical SHA-256.

## Independent entities
- `sample`: sample_id, sample_type, lat/lon, elevation, GPS accuracy, lithology, description, location method. A surface sample is never encoded as a drillhole collar.
- `assay`: sample_id, numeric value, unit, lab, certificate reference, method and detection limit. Multiple assay records can be attached to one sample, including results received later.
- `collar`: drillhole/pit/trench origin and depth.
- `survey`: downhole station depth, azimuth and dip.
- `interval`: from/to depth and assay or lithology. Interval assays remain downhole data. They are not plotted at the collar as if they were surface coordinates.
- `orientation`: strike/dip, with source kind; phone compass readings are explicitly lower-confidence than surveyed measurements.

## Spatial discipline
Preserve raw coordinates and CRS. The current dataset builder projects coordinates into one project output CRS; mixed UTM zones and vertical datum transformations require explicit professional review. Phone GPS altitude is not a reliable structural elevation measurement.

## Engine mapping
GemPy needs contacts, orientations, structural groups, faults, extent and stratigraphic relationships. LoopStructural needs XYZ, feature IDs, contacts and orientations. PyGSLIB needs collar, survey, intervals, assays, domains and compositing. PyKrige needs XYZ/value, variogram and validation parameters. pyGIMLi needs method-specific measurements and electrode/sensor geometry.

## Quality and provenance
Preserve lab certificates, methods, units, detection limits, blanks, standards, duplicates and custody events as the laboratory workflow matures. Every result must retain input hash, engine/adapter version, parameters, warnings, logs, validation, uncertainty and reviewer state. Outputs are interpretations, not certified resources.


## Orientation convention (v0.5)
`strike_deg` MUST use the right-hand rule (RHR): looking along strike, the dip direction is 90 degrees clockwise from strike. `dip_deg` is the angle from horizontal (0–90), not dip direction. Store dip direction separately only if a future schema explicitly adds that field. Phone compass observations are provisional and must be checked for magnetic declination and instrument calibration before geological interpretation.
