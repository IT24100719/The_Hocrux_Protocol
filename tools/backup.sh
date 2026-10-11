#!/usr/bin/env bash
# Snapshot FULL CTFd state — everything the seeder does NOT reproduce:
# player accounts, solves, scores, awards, hint unlocks, submissions (the
# database) plus uploaded challenge files. Run this before any reset, and
# periodically during a graded event.
#
#   tools/backup.sh                 -> backups/horcrux-<timestamp>.tgz
#
# Restore with tools/restore.sh <that file>.
set -euo pipefail
cd "$(dirname "$0")/.."

TS=$(date +%Y%m%d-%H%M%S)
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

echo "[backup] dumping database ..."
docker compose exec -T db pg_dump -U ctfd --clean --if-exists --no-owner ctfd \
  | gzip > "$STAGE/ctfd-db.sql.gz"

echo "[backup] archiving uploads ..."
# NB: path kept inside the sh -c string so Git Bash (MSYS) doesn't rewrite
# /var/uploads into a Windows path before docker sees it.
docker compose exec -T ctfd sh -c 'cd /var/uploads && tar czf - .' > "$STAGE/uploads.tar.gz"

mkdir -p backups
OUT="backups/horcrux-$TS.tgz"
tar -C "$STAGE" -czf "$OUT" ctfd-db.sql.gz uploads.tar.gz
echo "[backup] wrote $OUT"
ls -lh "$OUT"
