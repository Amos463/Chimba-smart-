# ChimbaSmart v0.5.0-rc1 — Offline-first geological field capture

**Hii ni handoff ya engineering kwa Codespaces, si release iliyothibitishwa sokoni.** Soma `docs/STATUS.md`, `docs/DATA_CONTRACT.md` na `docs/ENGINE_CONTRACT.md`.

## Hali ya clients
- `frontend/`: PWA ya browser; inaweza kuongezwa kwenye home screen ya Android/iOS na kutumika desktop browser. Inakusanya sampuli/GPS, assay, orientation, picha na queue ya offline kupitia IndexedDB. iOS/Android native Flutter bado si clients zilizokamilika.
- `mobile/`: Flutter skeleton tu.
- `backend/`: FastAPI + SQLAlchemy; SQLite kwa dev, PostgreSQL/PostGIS kwa server.

## Codespaces verification
```bash
chmod +x scripts/codespaces_verify.sh
./scripts/codespaces_verify.sh
```
Kisha anzisha API: `cd backend && python -m app.cli create-user juma 'Nenosiri-Lako-LenyeNguvu' && uvicorn app.main:app --host 0.0.0.0 --port 8000` (weka JWT_SECRET imara kabla ya mazingira ya pamoja).

## Docker/PostGIS
```bash
cp .env.example .env
# Weka POSTGRES_PASSWORD na JWT_SECRET salama ndani ya .env
docker compose config
docker compose up --build
```
Picha zinahifadhiwa kwenye Docker volume `attachments_data`; DB kwenye `pgdata`. Panga backup ya volumes kabla ya data halisi.

## Engines
- Tayari kwenye code: trend2d, orientation mean, IDW na downhole length-weighted compositing.
- PyKrige: adapter ipo; dependency ni hiari kupitia `backend/requirements-geostatistics.txt`; test itajiruka kama haijasakinishwa.
- GemPy, LoopStructural, PyGSLIB, pyGIMLi: hazijakamilika; hazipaswi kutumika kwa kazi ya kitaalamu hadi adapters, tests na data contracts zikamilike.

- Trend huchagua aina moja ya sampuli kwa kila run (idadi zikiwa sawa lazima uchague), hutumia log1p + RANSAC/Huber, hukataa pointi zinazojirudia na huonyesha outlier count.
- Assay nyingi zinazotofautiana hazichaguliwi kimyakimya; assay below-detection haichukuliwi kama grade ya sifuri.
- QA/QC ya msingi: blank, certified standard na duplicate; control iliyofail au isiyokamilika huzuia trend/IDW/Kriging. Bila controls, mfumo huonyesha wazi kuwa matokeo hayajathibitishwa. Hii bado si LIMS wala uthibitisho wa maabara.
- Upload ya picha huthibitisha format kwa Pillow, hure-encode picha upande wa seva ili kuondoa EXIF/GPS, huweka ukubwa wa pixel salama, na hash huzuia upload ya picha ileile kujirudia kwa sampuli.
- Ramani hutumia projected coordinates kwa uwiano sawa, north arrow na scale bar; bado si GIS basemap/offline tiles wala leseni polygon viewer.

Matokeo ni uchambuzi wa awali tu, si JORC/NI 43-101 au resource estimate. Access token default ni siku 30; refresh/revocation na Redis-backed throttling bado vinahitajika kwa production kubwa. `mobile/` ni skeleton; PWA ndiyo client iliyopo kwa field capture.
