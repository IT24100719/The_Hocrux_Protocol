#!/usr/bin/env bash
# HX-06 shared provisioning — the vault account, the protected final fragment,
# and the ONE deliberate, bounded sudo misconfiguration. Used by BOTH the
# Vagrant VM (setup.sh) and the Docker target (Dockerfile). It installs no
# packages and starts no service — each environment does that itself.
# Values default to integration.yml and may be overridden via env/build-args.
set -euo pipefail

VAULT_USER="${VAULT_USER:-vault}"
VAULT_PASS="${VAULT_PASS:-GRINGOTTS-472}"
# NB: do NOT use ${FINAL_FLAG:-HORCRUX{...}} — a brace-containing default breaks
# that expansion (bash closes at the first } and appends the trailing } literally,
# yielding a doubled brace). Assign the literal explicitly instead.
FINAL_FLAG="${FINAL_FLAG:-}"
[ -n "$FINAL_FLAG" ] || FINAL_FLAG='HORCRUX{g0bl1n_m4d3_v4ult_0wn3d}'

# --- low-privilege account (credentials handed over from HX-05) ---
id "$VAULT_USER" &>/dev/null || useradd -m -s /bin/bash "$VAULT_USER"
echo "${VAULT_USER}:${VAULT_PASS}" | chpasswd

# --- protected final fragment, root-owned, not world-readable ---
echo "$FINAL_FLAG" > /root/final_fragment.txt
chmod 600 /root/final_fragment.txt
chown root:root /root/final_fragment.txt

# --- the single deliberate, bounded misconfiguration ---
# vault may run /usr/bin/find as root with no password. GTFOBins:
#   sudo find . -exec /bin/sh \; -quit    -> root shell.
echo "${VAULT_USER} ALL=(root) NOPASSWD: /usr/bin/find" > /etc/sudoers.d/vault
chmod 440 /etc/sudoers.d/vault
visudo -cf /etc/sudoers.d/vault

# --- a little decoy enumeration surface so `sudo -l` is a real discovery ---
cat > /home/${VAULT_USER}/README.txt <<'NOTE'
Gringotts maintenance account.
Only authorised goblins may access the high-security vault.
NOTE
chown "${VAULT_USER}:${VAULT_USER}" /home/${VAULT_USER}/README.txt

echo "[+] HX-06 provisioning done (user=${VAULT_USER})"
