#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON="python"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON="$ROOT/.venv/bin/python"; fi
echo '[1/7] Python syntax'
"$PYTHON" -m compileall -q backend/app backend/migrations backend/tests
echo '[2/7] Install backend dependencies'
"$PYTHON" -m pip install -r backend/requirements.txt
echo '[3/7] Backend tests'
(cd backend && "$PYTHON" -m pytest -q)
echo '[4/7] Alembic migration chain and metadata check on fresh SQLite'
MIGRATION_DB="$(mktemp "${TMPDIR:-/tmp}/chimbasmart-migration-check.XXXXXX.db")"
trap 'rm -f "$MIGRATION_DB"' EXIT
(cd backend && DATABASE_URL="sqlite:///$MIGRATION_DB" AUTO_CREATE_TABLES=0 "$PYTHON" -m alembic upgrade head && DATABASE_URL="sqlite:///$MIGRATION_DB" AUTO_CREATE_TABLES=0 "$PYTHON" -m alembic check)
echo '[5/7] Frontend JavaScript syntax'
node --check frontend/app.js
node --check frontend/sw.js
echo '[6/7] Docker Compose config (no containers started)'
if command -v docker >/dev/null 2>&1; then POSTGRES_PASSWORD='temporary-check-password' JWT_SECRET='temporary-check-secret-at-least-32-characters' docker compose config --quiet; else echo 'Docker haipo; compose config imeachwa.'; fi
echo '[7/7] Engine availability'
(cd backend && "$PYTHON" - <<'PY'
from app.engines import ENGINES
for k,e in ENGINES.items(): print(f'{k}: adapter_ready={e.adapter_ready}, library_installed={e.library_installed}, version={e.version}')
PY
)
echo 'VERIFY COMPLETE — soma matokeo yote; si production certification.'
