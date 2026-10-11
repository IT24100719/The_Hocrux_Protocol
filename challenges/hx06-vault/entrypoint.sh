#!/bin/sh
# Egress lockdown for the vault container.
#
# The report specifies HX-06 on a "host-only / internal network, no public
# route". A Docker `internal: true` network gives that no-internet property but
# ALSO blocks the published SSH port (verified) — and players must SSH in. So we
# keep the box on a normal bridge (SSH publishes) and instead drop all
# container-INITIATED egress here, which reproduces the host-only property:
#   - loopback allowed
#   - replies to the inbound SSH connection allowed (ESTABLISHED/RELATED)
#   - every new outbound connection (i.e. the internet) dropped
# Needs cap_add: [NET_ADMIN] (set in docker-compose.yml). Degrades gracefully if
# the capability or iptables is missing — the box still runs, just without the
# egress block.
if command -v iptables >/dev/null 2>&1; then
  if iptables -F OUTPUT 2>/dev/null; then
    iptables -A OUTPUT -o lo -j ACCEPT
    iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    iptables -P OUTPUT DROP
    echo "[vault] egress locked down (outbound internet blocked; SSH replies allowed)"
  else
    echo "[vault] WARNING: could not set iptables (missing NET_ADMIN?) — egress NOT blocked" >&2
  fi
fi

exec /usr/sbin/sshd -D -e
