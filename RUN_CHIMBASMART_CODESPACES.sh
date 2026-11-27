#!/usr/bin/env bash
# One-command technical verification + Android Capacitor build.
# Optional push after a successful build: PUSH=1 ./RUN_CHIMBASMART_CODESPACES.sh
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$ROOT/ChimbaSmart_v0.5.0-rc1"
cd "$PROJECT"
fail(){ printf '\n[STOP] %s\n' "$*" >&2; exit 1; }
command -v python3 >/dev/null || fail "Python 3 haipo kwenye Codespace."
NODE_READY=0
if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
  NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
  if (( NODE_MAJOR >= 20 )); then NODE_READY=1; else echo "Node.js 20+ haipo; frontend/Android checks zitaachwa kwa GitHub Actions."; fi
else
  echo "Node.js/npm haipo; frontend/Android checks zitaachwa kwa GitHub Actions."
fi

# Use an isolated Python 3.12 environment. This avoids the Python 3.14 native-wheel
# failures previously encountered in Codespaces and does not alter system Python.
BASE_PY=''
if command -v python3.12 >/dev/null 2>&1; then
  BASE_PY="$(command -v python3.12)"
elif [[ "$(python3 -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || true)" == '12' ]]; then
  BASE_PY="$(command -v python3)"
elif command -v uv >/dev/null 2>&1; then
  if ! uv python find 3.12 >/dev/null 2>&1; then
    echo '[1/9] Installing isolated Python 3.12 via uv'
    uv python install 3.12 || fail 'Python 3.12 haikuweza kusakinishwa. Hakikisha Codespace ina internet.'
  fi
else
  fail 'Python 3.12 haipo na uv haipo. Fungua Codespace kwa .devcontainer image ya Python 3.12 au install uv.'
fi
if [[ ! -x "$PROJECT/.venv-release/bin/python" ]] || [[ "$("$PROJECT/.venv-release/bin/python" -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || true)" != '12' ]]; then
  rm -rf "$PROJECT/.venv-release"
  if [[ -n "$BASE_PY" ]]; then "$BASE_PY" -m venv "$PROJECT/.venv-release"; else uv venv --seed "$PROJECT/.venv-release" --python 3.12; fi
fi
PY="$PROJECT/.venv-release/bin/python"
export PYTHONUNBUFFERED=1 ENV=dev
export DATABASE_URL="sqlite:///$PROJECT/.release-check.sqlite"
export AUTO_CREATE_TABLES=0

printf '[2/9] Python version: '; "$PY" --version
"$PY" -m pip install --upgrade pip
"$PY" -m pip install -r backend/requirements.txt

echo '[3/9] Python compile check'
"$PY" -m compileall -q backend/app backend/migrations backend/tests

echo '[4/9] Backend automated tests'
 (cd backend && AUTO_CREATE_TABLES=1 "$PY" -m pytest -q)

echo '[5/9] Fresh SQLite migrations + Alembic metadata check'
MIGRATION_DB="$(mktemp "${TMPDIR:-/tmp}/chimbasmart-migration.XXXXXX.db")"
trap 'rm -f "$MIGRATION_DB" "$PROJECT/.release-check.sqlite"' EXIT
(cd backend && DATABASE_URL="sqlite:///$MIGRATION_DB" AUTO_CREATE_TABLES=0 "$PY" -m alembic upgrade head && DATABASE_URL="sqlite:///$MIGRATION_DB" AUTO_CREATE_TABLES=0 "$PY" -m alembic check)

echo '[6/9] JavaScript + shell syntax + backup bundle contract'
for script in scripts/*.sh; do bash -n "$script"; done
test -s docs/BACKUP_RESTORE.md
test -s docs/FULL_BACKUP_RESTORE_REPORT.md
echo 'Backup/restore scripts syntax na nyaraka: OK (functional restore test bado haijafanyika).'
if [[ "$NODE_READY" == '1' ]]; then
  for file in frontend/app.js frontend/sw.js frontend/field-workflows.js frontend/capacitor-bridge.js mobile/capacitor/scripts/stage-web-assets.mjs; do node --check "$file"; done
else
  echo 'JavaScript syntax check imeachwa kwa GitHub Actions kwa sababu Node.js 20+ haipo.'
fi

echo '[7/9] Docker Compose configuration check (no services started)'
if command -v docker >/dev/null 2>&1; then
  POSTGRES_PASSWORD='temporary-test-only-password' JWT_SECRET='temporary-test-only-secret-0123456789abcdef' docker compose config --quiet
else
  echo 'Docker haipo; Compose runtime check itafanyika GitHub Actions/server.'
fi

echo '[8/9] Capacitor sync + optional local Android build'
if [[ "$NODE_READY" == '1' ]]; then
  (cd mobile/capacitor && npm ci && npm run cap:sync)
else
  echo 'Capacitor sync imeachwa kwa GitHub Actions.'
fi
SDK_ROOT="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
JAVA_LINE="$(java -version 2>&1 | head -n 1 || true)"
if [[ "$NODE_READY" == '1' && -n "$SDK_ROOT" && ( "$JAVA_LINE" == *'21.'* || "$JAVA_LINE" == *'21"'* ) ]]; then
  (cd mobile/capacitor/android && ./gradlew --no-daemon clean assembleDebug assembleRelease bundleRelease)
  ART="$PROJECT/mobile/capacitor/testing-artifacts"
  mkdir -p "$ART"
  cp mobile/capacitor/android/app/build/outputs/apk/debug/app-debug.apk "$ART/chimbasmart-debug.apk"
  cp mobile/capacitor/android/app/build/outputs/apk/release/app-release.apk "$ART/chimbasmart-testing-signed.apk"
  cp mobile/capacitor/android/app/build/outputs/bundle/release/app-release.aab "$ART/chimbasmart-testing-signed.aab"
  (cd "$ART" && sha256sum chimbasmart-debug.apk chimbasmart-testing-signed.apk chimbasmart-testing-signed.aab > SHA256SUMS)
else
  echo 'Local Android SDK/Java 21 haijathibitishwa; GitHub Actions itajenga APK/AAB baada ya push.'
fi

echo '[9/9] Summary'
if [[ -d "$PROJECT/mobile/capacitor/testing-artifacts" ]]; then ls -lh "$PROJECT/mobile/capacitor/testing-artifacts"/*; fi
echo 'LOCAL TECHNICAL CHECKS PASSED. GitHub Actions is responsible for the hosted Android build when local SDK is unavailable.'

if [[ "${PUSH:-0}" == '1' ]]; then
  git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail 'Clone repository yako ya GitHub kwanza; usifanye push kutoka folder isiyo Git.'
  BRANCH="$(git -C "$ROOT" branch --show-current)"
  [[ -n "$BRANCH" ]] || fail 'Detached HEAD; chagua branch kwanza.'
  git -C "$ROOT" add ChimbaSmart_v0.5.0-rc1 RUN_CHIMBASMART_CODESPACES.sh .github/workflows
  if ! git -C "$ROOT" diff --cached --quiet; then
    git -C "$ROOT" commit -m 'Complete ChimbaSmart technical hardening and Android build'
  else
    echo 'Hakuna source changes mpya za ku-commit.'
  fi
  git -C "$ROOT" push origin "$BRANCH"
  echo "PUSH COMPLETE: origin/$BRANCH"
else
  echo 'Build imekamilika bila push. Baada ya kukagua, endesha: PUSH=1 ./RUN_CHIMBASMART_CODESPACES.sh'
fi
