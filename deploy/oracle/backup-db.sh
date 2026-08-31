#!/usr/bin/env bash
# Nightly DB backup, shipped off-VM to Oracle Object Storage — this is what
# replaces Neon's invisible backups now that Postgres is self-hosted on
# this VM (see CLAUDE.md's Oracle migration section for why). Runs via
# /etc/cron.d/its-db-backup (see this directory's README.md); the bucket's
# own lifecycle rule prunes old backups, not this script.
set -euo pipefail

BUCKET="its-db-backups"
DB_NAME="fireservice"
TIMESTAMP="$(date +%F)"
DUMP_FILE="/tmp/fireservice-${TIMESTAMP}.sql.gz"

sudo -u postgres pg_dump "$DB_NAME" | gzip > "$DUMP_FILE"

oci os object put \
    --bucket-name "$BUCKET" \
    --file "$DUMP_FILE" \
    --name "db-backups/fireservice-${TIMESTAMP}.sql.gz" \
    --force

rm -f "$DUMP_FILE"
echo "$(date -Iseconds) backup uploaded: db-backups/fireservice-${TIMESTAMP}.sql.gz"
