# Ukaguzi wa v0.4-pre1 (static; hakuna pytest/Postgres/browser iliyoendeshwa)

## Zilizothibitishwa na kurekebishwa kwenye patch hii
1. `alembic.ini` haikuwa na sehemu za logging; `env.py` inaita `fileConfig` -> `KeyError: 'formatters'` (imethibitishwa). Ingeshindwa hatua [4/7] ya verify na Docker CMD. **Imerekebishwa.**
2. PWA: picha yenye kosa la kudumu (415/413) ilitupa exception na kuzuia push/pull/analysis zote milele. Sasa inahamishiwa `rejected`. **Imerekebishwa.**
3. `backend/.env.example` ilikuwa na `\n` kama maandishi. **Imerekebishwa.**

## Bado kabla ya data halisi (haijarekebishwa)
- Migration `0001` inatumia `create_all` ya models za sasa; si historia halisi, mabadiliko ya baadaye hayatahamishwa. Tengeneza initial migration wazi kwa `alembic revision --autogenerate` kwenye Postgres.
- Trend inachanganya `sample_type` zote (soil, stream_sediment, rock_chip) na ni regression ya mstari kwenye g/t zilizoinama; nugget moja inaweza kuamua mwelekeo. Ongeza kichujio cha aina + log/robust.
- Assay nyingi kwa sampuli: inachukuliwa ya mwisho kimyakimya; hakuna QA/QC (blank/standard/duplicate) wala detection limit.
- Plot ya offline inapima x na y kwa kujitegemea (umbo linapotoshwa), haina scale/north; Leaflet na mipaka ya leseni zimeondolewa.
- Throttle ya login ni kwa username pekee (mtu anaweza kumfungia mwingine); 401 inafuta token na kuhitaji login mtandaoni.
- UI haisemi convention ya strike (right-hand rule): hatari ya data potofu.
- Mtumiaji mwingine kwenye kifaa kimoja: queue ya zamani inakataliwa 403 kwa batch nzima. Picha hazizuiwi marudio; EXIF GPS haiondolewi.
- Hakuna test ya IndexedDB queue, upload ya picha iliyofanikiwa, PyKrige, wala Postgres/PostGIS.
