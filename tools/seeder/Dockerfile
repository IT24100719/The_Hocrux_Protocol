# One-shot provisioner for a fully-automated `docker compose up`.
# Generates the static artefacts, publishes the HX-02 ciphertext/flag to the
# shared volume, waits for CTFd, then seeds challenges/flags/attachments/prereqs/
# hints/theme/pages. The repo is mounted at /repo at runtime (not copied), so it
# always provisions from the current source + integration.yml.
FROM python:3.12-slim
RUN pip install --no-cache-dir pyyaml pillow piexif scapy reportlab
WORKDIR /repo
COPY entrypoint.sh /usr/local/bin/seeder-entrypoint.sh
RUN chmod +x /usr/local/bin/seeder-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/seeder-entrypoint.sh"]
