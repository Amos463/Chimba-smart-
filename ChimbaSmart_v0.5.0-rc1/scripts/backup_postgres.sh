#!/usr/bin/env bash
set -euo pipefail
: "${DATABASE_URL:?Set DATABASE_URL}"
: "${BACKUP_DIR:?Set BACKUP_DIR}"
mkdir -p "$BACKUP_DIR"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
file="$BACKUP_DIR/chimbasmart-${stamp}.dump"
pg_dump --format=custom --no-owner --dbname="$DATABASE_URL" > "$file"
pg_restore --list "$file" >/dev/null
printf '%s\n' "$file"
