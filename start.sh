#!/usr/bin/env bash
# One-command launcher: bring the stack up AND open the CTF in a browser.
# The browser lands on the provisioning loading screen and auto-advances to
# CTFd the moment the seeder finishes. (A container can't open the host browser,
# so this little host-side wrapper does it.)  Linux / macOS / Git-Bash.
set -euo pipefail
cd "$(dirname "$0")"

LAB_IP="$(sed -n 's/^LAB_IP=//p' .env 2>/dev/null | tr -d '\r' | head -1)"
[ -n "${LAB_IP:-}" ] || LAB_IP=127.0.0.1
URL="http://${LAB_IP}:8000/"

echo "[start] bringing the stack up (first run builds + provisions — ~1-2 min)..."
docker compose up -d --build

echo "[start] opening ${URL}"
if command -v xdg-open >/dev/null 2>&1;   then xdg-open "$URL" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1;      then open "$URL"
elif command -v powershell.exe >/dev/null 2>&1; then powershell.exe -NoProfile -Command "Start-Process '$URL'" >/dev/null 2>&1
elif command -v cmd.exe >/dev/null 2>&1;   then cmd.exe /c start "" "$URL" >/dev/null 2>&1
else echo "[start] open this in your browser: $URL"; fi

echo "[start] done. The loading screen will switch to the CTF automatically when ready."
echo "[start] follow provisioning with:  docker compose logs -f seeder"
