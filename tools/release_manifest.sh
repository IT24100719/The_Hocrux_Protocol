#!/usr/bin/env bash
# Release manifest — records pinned versions, built image digests, and static
# artefact hashes (design §9 deployment step 10 / BUILD_SPEC §6 hardening).
# Run at release time and save the output alongside the git tag:
#     tools/release_manifest.sh > RELEASE_MANIFEST.txt
set -euo pipefail
cd "$(dirname "$0")/.."

echo "# The Horcrux Protocol — release manifest"
echo "# generated (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

echo "## Pinned versions (VERSIONS.md)"
sed 's/^/  /' VERSIONS.md 2>/dev/null || echo "  (VERSIONS.md missing)"
echo

echo "## Built image IDs (sha256)"
for img in horcrux-ctfd:3.7.7-pg horcrux-hx06-vault horcrux-ctf-hx02-web \
           postgres:16-alpine redis:7-alpine nginx:1.27-alpine ubuntu:22.04; do
  id=$(docker image inspect "$img" --format '{{.Id}}' 2>/dev/null || true)
  printf "  %-28s %s\n" "$img" "${id:-<not present>}"
done
echo

echo "## Static artefact hashes"
found=0
while IFS= read -r f; do
  found=1; echo "  [$f]"; sed 's/^/    /' "$f"
done < <(find challenges -name 'SHA256SUMS' -o -name '*.sha256' | sort)
[ "$found" = 1 ] || echo "  (none — run ./build-all.sh first)"
echo

echo "## Notes"
echo "  - Record the HX-06 VM snapshot ID here if the Vagrant VM is used."
echo "  - Confirm published ports bind LAB_IP only (proxy :8000, vault :2222)."
