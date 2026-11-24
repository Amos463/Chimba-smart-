# ChimbaSmart v0.5.0-rc1

## Engineering hardening
- Replaced `0001_initial` model `create_all()` with explicit Alembic DDL generated from the current baseline metadata.
- Kept PostGIS generated geometry columns in dedicated migrations and configured Alembic autogenerate to ignore migration-managed `geom` columns/indexes.
- Added assay QA/QC roles: primary, blank, standard and duplicate, including certified value, RPD tolerance, batch ID and below-detection qualifier.
- Conflicting multiple primary assays are excluded from grade trends instead of silently selecting the latest record.
- Trend analysis separates sample types, applies log1p grade transform and deterministic RANSAC + Huber refinement, and reports excluded outliers.
- QA/QC failure blocks trend, IDW and Kriging jobs.
- IDW and PyKrige no longer mix sample types and require unique spatial coordinates.
- Map plot uses projected coordinates with equal aspect, north arrow and scale bar; report plot follows the same scale discipline.
- Strike input is labelled as Right-Hand Rule; dip angle is distinct from dip direction.
- Login throttling key combines username and client IP; successful login clears that pair's counters.
- Expired-token 401 no longer deletes the local token/queue; token default lifetime is 30 days pending refresh-token implementation.
- PWA queue and image uploads are scoped to logged-in username and project; legacy unowned queue entries are moved to manual review rather than pushed under another user.
- Browser-side and server-side image re-encoding removes EXIF metadata; attachment upload is hash-idempotent.
- Invalid permanent image upload responses are moved to rejected records and no longer stop unrelated sync.
- PDF generation fails explicitly if PDF renderer is unavailable; HTML is never returned under a `.pdf` filename.
- Added regression tests for trend outliers, multiple assays, QA/QC roles, successful/idempotent image upload, optional PyKrige and PostGIS migration.

- Grade analysis selects one sample type per run; ties require explicit selection. QA/QC controls that fail or remain unresolved block trend, IDW and Kriging.
- Added duplicate-coordinate and non-projected CRS guards; Arc 1960 UTM limited to southern zones 35S–37S.
- Added migration 0006 for attachment content deduplication; verified fresh SQLite migration chain and Alembic metadata parity.
