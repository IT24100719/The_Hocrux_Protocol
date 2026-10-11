#!/usr/bin/env bash
# Provision the whole CTF, then exit (one-shot). Idempotent and safe to re-run.
set -euo pipefail
cd /repo

# Clear the readiness marker up front so the proxy serves the loading screen for
# the whole provisioning window. Without this, the marker from a previous run
# persists in the provision_state volume, so on a rebuild/restart the gate is
# already open and the loading screen never shows.
mkdir -p /run/horcrux && rm -f /run/horcrux/ready

echo "[seeder] generating static artefacts (if missing)..."
if [ ! -f challenges/hx01-stego/dist/marauders_map.png ]; then
  python challenges/hx01-stego/generate.py
  python challenges/hx03-crypto/generate.py
  python challenges/hx04-forensics/generate.py
  python challenges/hx05-network/generate.py
else
  echo "[seeder] artefacts already present — skipping generation"
fi

echo "[seeder] publishing HX-02 ciphertext + flag to the shared volume..."
mkdir -p /shared
cp challenges/hx03-crypto/dist/ciphertext.txt /shared/ciphertext.txt
python -c "import yaml; print(yaml.safe_load(open('integration.yml'))['flags']['hx02'])" > /shared/hx02_flag

echo "[seeder] seeding CTFd at ${CTFD_URL:-http://ctfd:8000} ..."
python tools/seed_ctfd.py --test-user

# Signal readiness: the proxy now stops serving the loading screen and proxies CTFd.
mkdir -p /run/horcrux && touch /run/horcrux/ready
echo "[seeder] done — the CTF is provisioned (readiness marker set)."
