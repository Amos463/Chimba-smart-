#!/usr/bin/env bash
set -euo pipefail
python -m compileall -q backend/app backend/migrations
(cd backend && python -m pytest -q)
echo "Flutter (si lazima): cd mobile && flutter pub get && flutter analyze && flutter test"
