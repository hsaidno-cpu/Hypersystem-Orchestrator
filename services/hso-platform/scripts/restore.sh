#!/usr/bin/env sh
set -eu

: "$HSO_DATABASE_URL"
: "$BACKUP_FILE"
test -n "$HSO_DATABASE_URL"
test -n "$BACKUP_FILE"
test -f "$BACKUP_FILE"
sha256sum --check "$BACKUP_FILE.sha256"
echo "WARNING: this operation replaces objects in the target database."
echo "Run only against an explicitly approved recovery target."
pg_restore "$HSO_DATABASE_URL" --clean --if-exists --no-owner --no-acl "$BACKUP_FILE"
