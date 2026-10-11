#!/usr/bin/env bash
# Restore a snapshot made by tools/backup.sh.
# WARNING: this OVERWRITES all current CTFd data (players, solves, scores, files)
# with the contents of the backup.
#
#   tools/restore.sh backups/horcrux-<timestamp>.tgz
#
set -euo pipefail
cd "$(dirname "$0")/.."

BK="${1:-}"
if [ ! -f "$BK" ]; then
  echo "usage: tools/restore.sh backups/horcrux-<timestamp>.tgz"
  echo "available:"; ls -1 backups/*.tgz 2>/dev/null || echo "  (none)"
  exit 1
fi

echo "[restore] !! OVERWRITING all current CTFd data from: $BK"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
tar -xzf "$BK" -C "$TMP"
[ -f "$TMP/ctfd-db.sql.gz" ] && [ -f "$TMP/uploads.tar.gz" ] || {
  echo "[restore] backup is missing ctfd-db.sql.gz or uploads.tar.gz"; exit 1; }

echo "[restore] stopping ctfd ..."
docker compose stop ctfd >/dev/null

echo "[restore] restoring database ..."
gunzip -c "$TMP/ctfd-db.sql.gz" | docker compose exec -T db psql -U ctfd -d ctfd -q >/dev/null

echo "[restore] restoring uploads ..."
docker compose run --rm --no-deps -T --entrypoint sh ctfd \
  -c 'rm -rf /var/uploads/* && tar xzf - -C /var/uploads' < "$TMP/uploads.tar.gz"

echo "[restore] starting ctfd ..."
docker compose start ctfd >/dev/null
echo "[restore] done — give CTFd a few seconds to come up."
