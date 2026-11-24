# ChimbaSmart — data contract v1 (design baseline)

This is a proposed shared data contract for field capture and server processing. It is **not implemented or validated against the engines yet**. Each record must carry `project_id`, globally unique `record_uuid`, `created_at_utc`, `updated_at_utc`, `created_by`, `device_id`, `source_method`, `crs`, coordinate units, and a quality/status record.

## Core spatial reference
- Store source coordinates and CRS identifier (prefer EPSG code or explicit WKT); never assume every project uses the same datum/UTM zone.
- Store horizontal and vertical units, vertical datum, elevation source, GPS horizontal accuracy, timestamp, and location method.
- Keep original raw values and normalized values separately. Do not silently transform or overwrite source data.

## Geological observations
- `observation_uuid`, XYZ, observation type, lithology, weathering, alteration, mineralization, texture, grain size, contact/fault/fracture attributes, notes, confidence, observer, photos and attachments.
- Planar structures: strike, dip, dip direction, measurement convention (e.g. right-hand rule), instrument/method, and quality.
- Linear structures: trend/azimuth, plunge, lineation type and convention.
- GemPy/LoopStructural need correctly classified surface/contact points and orientation constraints; a GPS point alone is not enough.

## Samples and laboratory results
- `sample_uuid`, human-readable sample code, sample type, XYZ/location, collection time, collector, material, mass, interval `from_depth`/`to_depth` where relevant, preparation, dispatch/batch, laboratory, method, analyte, result, unit, detection limit, QA/QC role (blank/standard/duplicate), certificate/file reference and chain-of-custody events.
- Keep sample identity separate from assay results: one sample may have many analytes/results and repeat assays.

## Drillhole dataset
- Collar table: `hole_id`, X, Y, Z, maximum depth, hole type, coordinate reference.
- Survey table: `hole_id`, measured depth, azimuth, dip, survey method and instrument; include enough stations to represent deviation.
- Interval tables: `hole_id`, `from_depth`, `to_depth`, lithology/alteration/assay/RQD or other values. Validate intervals against collar depth and survey.
- Store downhole point observations and structural measurements as linked child records.
- This collar/survey/interval pattern is required by Leapfrog Geo and is also the basic pattern used by PyGSLIB drillhole workflows.

## Geophysics
- Store method-specific survey lines/stations, sensor/electrode geometry, measured values, units, timestamps, instrument make/model/serial, calibration, acquisition settings, topography, operator, raw source file and processing history.
- For ERT/IP, preserve electrode positions and current/potential measurement geometry. A phone magnetometer reading is a separate low-confidence observation type and must not be substituted for professional magnetic survey data.

## Engine adapters
- GemPy: map contacts/surface points and orientations into structural elements/groups; require a declared model extent and stratigraphic/structural relationships.
- LoopStructural: map XYZ, feature names, interface/contact identifiers, orientation/gradient constraints and stratigraphic order.
- PyGSLIB: build collar, survey and interval tables; validate, composite, desurvey, domain-code, block-model, estimate and validate.
- PyKrige: provide coordinates, variable values, variogram choices and explicit grid/search parameters; record uncertainty and validation.
- pyGIMLi: use method-specific data containers with sensor geometry, measurements and topography.
- QGIS/PostGIS: preserve CRS and support spatial layers/raster/vector formats; QGIS is GIS infrastructure, not a single geology engine.

## Processing provenance
Every job/result must record input dataset version/hash, engine name/version, adapter version, parameters, start/end times, logs, warnings, output files, validation metrics, uncertainty, and reviewer/approval state. Results are estimates, not certified mineral resources unless a qualified competent person completes the applicable reporting process.
