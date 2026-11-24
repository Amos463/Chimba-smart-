#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo '[1/7] Python syntax'
python -m compileall -q backend/app backend/migrations backend/tests
echo '[2/7] Install backend dependencies'
python -m pip install -r backend/requirements.txt
echo '[3/7] Backend tests'
(cd backend && python -m pytest -q)
echo '[4/7] Alembic migration chain on fresh SQLite'
(cd backend && rm -f chimbasmart_migration_check.db && DATABASE_URL=sqlite:///./chimbasmart_migration_check.db AUTO_CREATE_TABLES=0 alembic upgrade head && rm -f chimbasmart_migration_check.db)
echo '[5/7] Frontend JavaScript syntax'
node --check frontend/app.js
node --check frontend/sw.js
echo '[6/7] Docker Compose config (no containers started)'
if command -v docker >/dev/null 2>&1; then POSTGRES_PASSWORD='temporary-check-password' JWT_SECRET='temporary-check-secret-at-least-32-characters' docker compose config --quiet; else echo 'Docker haipo; compose config imeachwa.'; fi
echo '[7/7] Engine availability'
(cd backend && python - <<'PY'
from app.engines import ENGINES
for k,e in ENGINES.items(): print(f'{k}: adapter_ready={e.adapter_ready}, library_installed={e.library_installed}, version={e.version}')
PY
)
echo 'VERIFY COMPLETE — soma matokeo yote; si production certification.'
