#!/usr/bin/env sh
set -eu

: "$HSO_DATABASE_URL"
: "$BACKUP_DIR"
test -n "$HSO_DATABASE_URL"
test -n "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
target="$BACKUP_DIR/hso-$timestamp.dump"

pg_dump "$HSO_DATABASE_URL" --format=custom --no-owner --no-acl --file="$target"
sha256sum "$target" > "$target.sha256"
chmod 0600 "$target" "$target.sha256"
echo "Backup created: $target"
echo "Store the backup and digest in a separate encrypted, access-controlled location."
