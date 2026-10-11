# HX-06 Gringotts vault — Docker target (same provisioning as the Vagrant VM).
# A locked-down SSH box with exactly ONE bounded flaw: the `vault` user may run
# /usr/bin/find as root with no password. Solve path:
#   ssh vault@<host> -p 2222            # password recovered in HX-05
#   sudo -l                              # (root) NOPASSWD: /usr/bin/find
#   sudo find . -exec /bin/sh \; -quit   # -> root shell  (GTFOBins)
#   cat /root/final_fragment.txt
FROM ubuntu:22.04

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      openssh-server sudo iptables \
 && rm -rf /var/lib/apt/lists/*

# Shared provisioning: vault account, protected flag, the sudo-find misconfig.
# Override the defaults at build time to match integration.yml if you change it.
ARG VAULT_USER=vault
ARG VAULT_PASS=GRINGOTTS-472
ARG FINAL_FLAG=HORCRUX{g0bl1n_m4d3_v4ult_0wn3d}
COPY provision.sh /tmp/provision.sh
RUN VAULT_USER="$VAULT_USER" VAULT_PASS="$VAULT_PASS" FINAL_FLAG="$FINAL_FLAG" \
      bash /tmp/provision.sh \
 && rm -f /tmp/provision.sh \
 && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
 && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
 && mkdir -p /run/sshd

# Egress lockdown + sshd launcher (see entrypoint.sh). Needs cap_add NET_ADMIN.
COPY entrypoint.sh /usr/local/bin/vault-entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/vault-entrypoint.sh \
 && chmod +x /usr/local/bin/vault-entrypoint.sh

EXPOSE 22
CMD ["/usr/local/bin/vault-entrypoint.sh"]
