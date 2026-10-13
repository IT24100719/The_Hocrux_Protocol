#!/usr/bin/env bash
# One-command launcher: bring the stack up AND open the CTF in a browser.
# The browser lands on the provisioning loading screen and auto-advances to
# CTFd the moment the seeder finishes. (A container can't open the host browser,
# so this little host-side wrapper does it.)  Linux / macOS / Git-Bash.
set -euo pipefail
cd "$(dirname "$0")"

# First run on a fresh clone has no .env (it's gitignored). Create one from the
# template with freshly generated secrets so the stack is self-contained — no
# manual editing required. Delete .env to regenerate.
if [ ! -f .env ]; then
  echo "[start] no .env found — generating one from .env.example with fresh secrets"
  cp .env.example .env
  # `tr | head -c` makes head close the pipe early, so tr dies with SIGPIPE
  # (141); the trailing `|| true` keeps that from aborting under pipefail. The
  # hex chars are already captured before tr is signalled.
  gen(){ LC_ALL=C tr -dc 'a-f0-9' </dev/urandom 2>/dev/null | head -c "$1" || true; }
  DBP="$(gen 32)"; SK="$(gen 48)"; ADMINPW="$(gen 18)"
  sed -i.bak \
    -e "s/^DB_PASSWORD=.*/DB_PASSWORD=${DBP}/" \
    -e "s/^CTFD_SECRET_KEY=.*/CTFD_SECRET_KEY=${SK}/" \
    -e "s/^CTFD_ADMIN_PASSWORD=.*/CTFD_ADMIN_PASSWORD=${ADMINPW}/" .env
  rm -f .env.bak
  echo "[start] admin account -> user: admin  password: ${ADMINPW}"
  echo "[start] (saved in .env — keep it; it is gitignored and not shared)"
fi

LAB_IP="$(sed -n 's/^LAB_IP=//p' .env 2>/dev/null | tr -d '\r' | head -1)"
[ -n "${LAB_IP:-}" ] || LAB_IP=127.0.0.1
URL="http://${LAB_IP}:8000/"

echo "[start] bringing the stack up (first run builds + provisions — ~1-2 min)..."
# Prefer the project's subnet (172.20.0.0/24) when it is free; if another Docker
# network already uses it, fall back to Docker's auto-assignment so the stack
# still comes up instead of failing with "pool overlaps".
PIN_ARGS="-f docker-compose.yml -f docker-compose.pin.yml"
NETS="$(docker network ls -q 2>/dev/null)"
if [ -n "$NETS" ] && docker network inspect $NETS 2>/dev/null | grep -q "172.20.0.0/24"; then
  echo "[start] 172.20.0.0/24 is already in use — letting Docker auto-assign a subnet"
  PIN_ARGS=""
fi
docker compose $PIN_ARGS up -d --build

echo "[start] opening ${URL}"
if command -v xdg-open >/dev/null 2>&1;   then xdg-open "$URL" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1;      then open "$URL"
elif command -v powershell.exe >/dev/null 2>&1; then powershell.exe -NoProfile -Command "Start-Process '$URL'" >/dev/null 2>&1
elif command -v cmd.exe >/dev/null 2>&1;   then cmd.exe /c start "" "$URL" >/dev/null 2>&1
else echo "[start] open this in your browser: $URL"; fi

echo "[start] done. The loading screen will switch to the CTF automatically when ready."
echo "[start] follow provisioning with:  docker compose logs -f seeder"
