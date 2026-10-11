#!/usr/bin/env bash
# HX-06 Gringotts vault — Vagrant VM provisioning (Ubuntu 22.04). Run once as
# root via `vagrant up`, then power off and take an immutable snapshot 'clean'.
# The account/flag/misconfig all come from provision.sh (shared with the Docker
# target). For a Docker-only deployment, use the Dockerfile instead.
set -euo pipefail
cd "$(dirname "$0")"

apt-get update -y && apt-get install -y openssh-server sudo
bash provision.sh
systemctl enable --now ssh

echo "[+] provisioning complete. Power off and snapshot as 'clean'."
