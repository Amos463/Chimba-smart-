# Hali halisi — ChimbaSmart v0.4-pre1 (handoff ya Codespaces)

**Toleo hili ni patch ya kabla ya runtime verification, si commercial release.** ZIP imefanyiwa ukaguzi wa syntax tu katika mazingira haya. Backend tests, migration ya PostGIS, upload ya picha, PWA runtime na engine outputs lazima vithibitishwe Codespaces.

## Mabadiliko yaliyoandaliwa
1. **Data model:** sampuli huru (`sample`) zimetenganishwa na drillhole collar; assay (`assay`) ni rekodi tofauti na inaweza kuongezwa baadaye kwa sample iliyopo. Assay za downhole zinabaki interval; hazichukuliwi kuwa eneo la collar.
2. **Trend 2D:** inatumia surface samples zenye assay g/t pekee. Dataset ina collars, surveys, intervals, orientations, samples na assays kando, pamoja na `input_hash`.
3. **Offline queue:** IndexedDB queue ya simu, pending photos, sync push + pull cursor, na rejected/conflict archive yenye maelezo. Rekodi zenye dependency inayosubiri hubaki retryable; permanent invalid/conflict haziangamizwe kimyakimya. Pull inaendelea kutoka cursor iliyohifadhiwa.
4. **Offline map:** PWA inahifadhi analysis ya mwisho na ina coordinate plot ya sampuli inayofanya kazi bila tile server; sampuli mpya za ndani zinaongezwa kwenye plot. Hii si downloadable offline basemap/tile package.
5. **Picha:** picha JPEG/PNG/WEBP hadi MB 10 huhifadhiwa IndexedDB ikiwa offline, kisha hutumwa `/attachments`; API ina project authorization, MIME allowlist, SHA-256, na metadata. Docker Compose ina persistent volume. Picha zinahusishwa na sample_id.
6. **Engine registry:** `trend2d`, `orientation`, `idw`, `downhole_composite` zina adapters; `pykrige` adapter imeandikwa na dependency imeongezwa. `gempy`, `loopstructural`, `pygslib`, `pygimli` zimetajwa wazi kuwa hazijakamilika na haziwezi kuendeshwa.
7. **Provenance:** IDW/PyKrige results zinajumuisha input hash, CRS, method na parameters. Job model bado ni `BackgroundTasks`; si durable queue ya production.

## Bado lazima kuthibitishwa/kujengwa
- Tests hazijaendeshwa hapa kwa sababu mazingira hayana `bcrypt` (na huenda dependencies nyingine); `pip install -r backend/requirements.txt` kisha `pytest` Codespaces.
- Alembic migration `0003_samples_assays` na PostGIS generated geometry/GIST index haijaendeshwa.
- PyKrige inahitaji install + runtime tests, variogram diagnostics na geologist review.
- GemPy, LoopStructural, PyGSLIB na pyGIMLi bado hazina working adapters.
- PWA offline coordinate plot si offline topo/geology basemap. Map tile packages, Bluetooth instrument import, richer sample photo gallery/download, and sync conflict resolution workflow bado vinahitaji kazi.
- `sync/pull` inahifadhi server records kwenye IndexedDB lakini hakuna merge UI ya ku-edit incoming conflicts.
- Token revocation/refresh, distributed rate limiting, durable job queue (RQ/Celery), malware scan, formal audit log, backups/restore, storage retention policy na security review bado vinahitajika.
- Flutter client bado ni skeleton; PWA ndiyo client inayoweza kutumika sasa kupitia browser/installable PWA. iOS native/App Store build inahitaji macOS/Xcode.
- CRS/vertical datum, survey methodology, sampling protocols, QA/QC (blanks, standards, duplicates, custody), uncertainty and geological interpretation lazima zikaguliwe na wataalamu. Hakuna output inayothibitisha mineral resource.

## Amri ya kwanza Codespaces
Tumia `scripts/codespaces_verify.sh` iliyo ndani ya ZIP. Itasakinisha requirements, kuendesha compile/test, kujaribu Docker Compose config, Alembic upgrade kwenye SQLite ya majaribio, na kuonyesha engine registry. Isipofaulu, rekebisha kabla ya kuendelea.


## v0.5 engineering hardening
- Initial schema is explicit Alembic DDL; `0003` only adds sample PostGIS geometry; `0004` adds assay QA/QC metadata.
- Assay roles: primary, blank, standard, duplicate. Blank/standard/duplicate checks are advisory QA flags; they do not certify a laboratory batch.
- Trend: one sample type per run, log1p grade transform, deterministic RANSAC + Huber refinement; reports outlier count and selected sample type.
- Multiple differing primary assays are not silently resolved; the sample is excluded from grade trend until reviewed.
- Plot uses projected coordinates with equal aspect, north arrow and approximate scale; it is not a basemap/GIS license-boundary viewer.
- Offline JWT is retained after 401 so local data is not discarded; access token default is 30 days. Production should add refresh/revocation and Redis-backed rate limiting.


## v0.5.0-rc1 engineering changes
- Explicit immutable Alembic baseline plus migrations through 0006; fresh SQLite migration and `alembic check` verified in this workspace.
- Trend/IDW/Kriging use a single sample type per run; ambiguous equal-count types require explicit selection. QA/QC fail or unresolved controls block grade-dependent engines.
- Assay roles, below-detection qualifier, multiple-assay conflict handling, robust trend, RHR labels, projected map scale discipline, IP+username throttling, offline queue ownership, and server image sanitization are included.
- Remaining external verification: full pytest suite in Codespaces (bcrypt unavailable in this build workspace), live PostgreSQL/PostGIS migration test, real browser IndexedDB/photo upload test, PyKrige runtime test if optional dependency installed, and Flutter remains a skeleton.

## Commercial hardening baseline (2026-11-24)

- Verified 29 backend tests pass and 1 PostgreSQL/PostGIS test is skipped in the local environment.
- Verified migration chain 0001-0007 upgrades on SQLite and `alembic check` reports no model drift.
- Resolved the PyKrige requirement conflict using `PyKrige==1.7.3`.
- Added refresh-session hashes, rotation/reuse revocation, password-reset tokens, audit events and UTC-normalization fixes.
- Added request size, CORS, security-header and readiness middleware.
- Remaining critical production work: Redis-backed throttling, durable RQ/Celery jobs, complete role matrix, live PostgreSQL/PostGIS testing, backup/restore proof, conflict resolution UI and production cross-platform builds.
