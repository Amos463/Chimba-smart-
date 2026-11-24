# ChimbaSmart v0.5.0-rc1 — matokeo ya marekebisho

## Yaliyorekebishwa kwenye code

1. **Alembic:** `0001_initial` sasa ni DDL iliyo wazi, si `Base.metadata.create_all`; migrations 0002–0006 zinafuata. `alembic.ini` ina logging sections. Fresh SQLite migration imepita na `alembic check` imerudisha `No new upgrade operations detected`.
2. **Trend:** inatumia log1p + RANSAC/Huber, inakataa coordinate duplicate/collinear, na hutumia aina moja ya sampuli kwa run. Ikiwa aina mbili zina idadi sawa, mtumiaji lazima achague.
3. **Assay:** hakuna kuchagua assay ya mwisho kimyakimya. Primary assays zinazopingana hazitumiki kwenye grade analysis; blank, standard, duplicate, batch, tolerance na below-detection metadata zimeongezwa.
4. **QA/QC:** blank/standard/duplicate iliyofail au ambayo haijatatuliwa huzuia Trend, IDW na Kriging. Bila QA/QC controls, mfumo unaonyesha onyo badala ya kudai matokeo yamehakikiwa.
5. **Ramani:** projected coordinates hutumia uwiano sawa wa mita kwa X/Y; kuna north arrow na scale bar. Hii bado ni coordinate plot, si GIS kamili.
6. **Login:** throttle inafungamanishwa na username+IP; IP ina kikomo tofauti cha juu zaidi ili jaribio la mtu mmoja lisifungie akaunti nyingine kwa urahisi. Counters ni process-local; production yenye workers nyingi inahitaji Redis.
7. **Token/offline:** 401 haiifuti token wala queue ya kifaa; token default ni siku 30. Refresh/revocation bado haipo, hivyo mtumiaji atahitaji kuingia tena mtandao ukipatikana baada ya token ku-expire.
8. **Strike/dip:** UI inasema wazi strike ni Right-Hand Rule na dip ni angle ya 0–90°, si dip direction.
9. **Watumiaji wengi/kifaa kimoja:** queue na picha zimefungamanishwa na username+project. Rekodi za legacy zisizo na owner hupelekwa manual review, si kutumwa kwa akaunti nyingine.
10. **Picha:** browser na server hure-encode picha ili kuondoa EXIF/GPS; server huthibitisha image format na pixel bounds; hash + unique constraint huzuia duplicate upload. Picha yenye kosa la kudumu huwekwa rejected bila kuzuia sync ya rekodi nyingine.
11. **PDF:** renderer ikishindwa, API hurudisha 503; HTML haitolewi chini ya jina la `.pdf`.
12. **Tests:** kuna tests za API, QA/QC, multiple assays, sample-type filtering, image upload idempotency, optional PyKrige na PostgreSQL/PostGIS. Kuna manual browser IndexedDB smoke page.

## Uthibitisho uliofanyika kwenye workspace hii

- Python compileall: PASS.
- JavaScript syntax (`node --check` kwa app.js na sw.js): PASS.
- NumPy smoke tests: Trend, IDW grid, QA/QC gate, sample type separation na downhole composite: PASS.
- Pydantic below-detection validation: PASS.
- Alembic fresh SQLite upgrade hadi `0006_attachment_dedupe`: PASS.
- Alembic metadata parity (`alembic check`): PASS.

## Bado lazima kuthibitishwa ndani ya Codespaces kabla ya pilot

- Full pytest suite: haikuendeshwa hapa kwa sababu mazingira ya sasa hayana `bcrypt` na mtandao wa kusakinisha dependencies haukupatikana. Codespaces script itasakinisha requirements na kuendesha tests.
- PostgreSQL/PostGIS: migration test ipo, lakini inahitaji disposable PostGIS database na `TEST_POSTGRES_URL`; haikuendeshwa hapa.
- PyKrige: adapter ipo; test inahitaji `requirements-geostatistics.txt` na data sahihi ya majaribio.
- Browser IndexedDB/photo sync: smoke test ipo, lakini lazima ifunguliwe kwenye browser halisi ya Android/origin ya PWA.
- Flutter: skeleton tu, si client ya matumizi.
- Hakuna Leaflet basemap, offline map tiles, leseni polygons, 3D modelling au desurveying kamili.
- QA/QC hii ni msingi wa validation, si LIMS, laboratory accreditation au sign-off ya geologist.
- Rate limiting bado ni process-local; production yenye workers nyingi inahitaji Redis. Token refresh/revocation, audit trail kamili, backups/restore drills na object storage production bado ni kazi.

**Uamuzi:** RC1 ya engineering kwa verification na controlled pilot preparation. Si production certification, si resource estimation software iliyothibitishwa, na si JORC/NI 43-101 reporting system.
