#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 BACKUP.dump DESTINATION_DATABASE_URL" >&2
  exit 2
fi
backup="$1"
destination="$2"
if [[ "$destination" == *"$HOSTNAME"* ]] || [[ "$destination" == *"prod"* ]]; then
  echo "Refusing destination that appears to reference a live host" >&2
  exit 2
fi
createdb --dbname="$destination" >/dev/null 2>&1 || true
pg_restore --clean --if-exists --no-owner --dbname="$destination" "$backup"
psql --dbname="$destination" -v ON_ERROR_STOP=1 -c "SELECT 1"
