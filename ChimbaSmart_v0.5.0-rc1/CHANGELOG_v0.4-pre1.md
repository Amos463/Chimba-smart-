# ChimbaSmart v0.4-pre1 — mabadiliko kutoka v0.3

- Added independent `Sample`, `Assay`, and `Attachment` entities plus Alembic migration 0003.
- Added typed sample and assay ingestion, including late-arriving lab assays.
- Reworked dataset construction so surface samples and downhole intervals remain separate.
- Restricted 2D grade trend to georeferenced surface samples with g/t assays.
- Added IndexedDB offline queue, rejected/conflict archive, push/pull cursor and offline coordinate plot.
- Added offline photo persistence and authenticated project-scoped attachment upload/download metadata endpoints.
- Added IDW, length-weighted downhole compositing and optional PyKrige Ordinary Kriging adapter.
- Explicitly disabled unimplemented GemPy, LoopStructural, PyGSLIB and pyGIMLi adapters.
- Added a single Codespaces verification script and refreshed data/engine/status documentation.

This is a pre-runtime handoff. See `docs/STATUS.md` for all limitations and required validation.
