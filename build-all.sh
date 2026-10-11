#!/usr/bin/env bash
# Regenerate every static artefact from integration.yml, then inject the
# HX-03 ciphertext into .env for the HX-02 container.
set -euo pipefail
cd "$(dirname "$0")"
# Pick the first interpreter that actually runs. On Windows/Git Bash a broken
# "python3" Store stub may shadow the real one, so we validate each candidate.
PY=""
for cand in python3 python py; do
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "import sys" >/dev/null 2>&1; then
    PY="$cand"; break
  fi
done
[ -n "$PY" ] || { echo "[!] no working python interpreter found on PATH"; exit 1; }
echo "[*] using interpreter: $PY"
echo "[*] HX-01 stego";     "$PY" challenges/hx01-stego/generate.py
echo "[*] HX-03 crypto";    "$PY" challenges/hx03-crypto/generate.py
echo "[*] HX-04 forensics"; "$PY" challenges/hx04-forensics/generate.py
echo "[*] HX-05 network";   "$PY" challenges/hx05-network/generate.py
CT=$(cat challenges/hx03-crypto/dist/ciphertext.txt)
FLAG2=$(grep -E '^[[:space:]]*hx02:' integration.yml | grep -oE 'HORCRUX\{[^}]*\}' | head -1)
if [ -f .env ]; then
  for kv in "HX02_CIPHERTEXT=$CT" "HX02_FLAG=$FLAG2"; do
    key="${kv%%=*}"
    grep -q "^$key=" .env && sed -i "s|^$key=.*|$kv|" .env || echo "$kv" >> .env
  done
  echo "[+] injected HX02_FLAG + HX02_CIPHERTEXT into .env from integration.yml"
else
  echo "[!] no .env yet - copy .env.example to .env, then re-run to inject"
fi
echo "[+] artefacts in challenges/*/dist/. HX-06 VM: vagrant up in challenges/hx06-vault/"
