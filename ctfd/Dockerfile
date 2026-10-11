# CTFd 3.7.7 + Postgres driver.
# The upstream ctfd/ctfd:3.7.7 image ships only PyMySQL, so a
# DATABASE_URL of postgresql+psycopg2://... crashes with
# "ModuleNotFoundError: No module named 'psycopg2'". The BUILD_SPEC pins
# Postgres 16, so we add the (pure-wheel, no build-tools) psycopg2 driver
# on top of the pinned image rather than changing the database.
FROM ctfd/ctfd:3.7.7
USER root
RUN pip install --no-cache-dir "psycopg2-binary==2.9.9"
# Horcrux starting-points plugin: grants new players a welcome balance so early
# hints are reachable (and HX-01 hints can be costed like the rest). Configured
# via HORCRUX_START_POINTS (see docker-compose.yml / .env).
COPY plugins/ /opt/CTFd/CTFd/plugins/
USER 1001
