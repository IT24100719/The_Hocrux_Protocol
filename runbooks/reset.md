# Reset / recovery runbook

Three levels, smallest blast radius first.

> **Back up player progress FIRST.** The seeder reproduces the CTF *definition*
> (challenges, hints, theme) but NOT player data — accounts, solves, scores,
> awards, hint unlocks all live only in the database + uploads volume. A
> `down -v` wipes them. Before any destructive step, and periodically during a
> graded event:
>
>     tools/backup.sh                          # -> backups/horcrux-<timestamp>.tgz
>     tools/restore.sh backups/horcrux-<ts>.tgz  # roll back to a snapshot (overwrites current)
>
> Backups are gitignored (they contain student data). Keep them off-box too.

---

## A. Service restart (keeps ALL data)
Containers only; the Postgres volume persists, so challenges, hints, theme,
users and solves all survive untouched.

    docker compose down          # keep volumes
    docker compose up -d

---

## B. Full rebuild / fresh DB (recreates the whole CTF from source)
Use after `docker compose down -v`, a wiped volume, or a setup-wizard re-run.
Everything we configure by hand is reproduced from version-controlled sources by
`tools/seed_ctfd.py` — challenges, flags, attachments, the prerequisite chain,
the 18 chained hints, the parchment theme + story layer + hint-dialog fix, and
(optionally) the test account.

    # 0. one-time: make sure .env has CTFD_ADMIN_* + CTF_NAME (see .env.example)
    #    and Python deps are present:  pip install pyyaml

    # 1. (re)generate the challenge attachments into challenges/*/dist/
    ./build-all.sh

    # 2. bring the platform up on a fresh DB
    docker compose down -v        # WIPES the database (and all volumes)
    docker compose up -d --build

    # 3. seed everything (runs the setup wizard from .env, then loads it all)
    pip install pyyaml            # once, if not already installed
    python tools/seed_ctfd.py --test-user

    # 4. rebuild the HX-02 web app (its own container, not in the DB)
    docker compose up -d --build hx02-web

Admin after a full reset = `CTFD_ADMIN_NAME` / `CTFD_ADMIN_PASSWORD` from `.env`.
The seeder is **idempotent** — safe to re-run; it updates in place and never
duplicates. It auto-runs the setup wizard only when the instance is fresh.

### Seeder auth
- Fresh instance → reads `CTFD_ADMIN_*` from `.env`, runs setup, logs in, mints
  its own API token.
- Already set up → either let it log in with `.env` creds, or export an admin
  token to skip login:  `CTFD_TOKEN=ctfd_... python tools/seed_ctfd.py`

### Seeder flags
    --test-user     also (re)create the hidden auror_tester player account
    --no-theme      skip the theme/story injection (challenges + hints only)
    --no-files      skip attachment uploads (e.g. dist/ not built yet)
    --base-url URL  target a non-default CTFd (default http://127.0.0.1:8000)

### Sources the seeder reads
    ctfd-config/challenges.yml   names, categories, values, descriptions, state, attachments
    ctfd-config/hints.yml        18 hints (content + cost), 3 tiers per stage (5/20/50 % of value)
    integration.yml              the flags (gitignored, private)
    challenges/*/dist/*          attachments (produced by build-all.sh)
    ctfd-theme/horcrux-inject/   theme + story + hint-dialog fix (via build_inject.py)

### Starting points (so hints are reachable + HX-01 hint use counts)
The `horcrux_starting_points` plugin (baked into the ctfd image, see `ctfd/`)
grants every NEW player `HORCRUX_START_POINTS` (default 100, in `.env`) on
creation, so the costed HX-01 hints are affordable from the start. It fires on a
full rebuild automatically — no extra step. Only if you add the plugin to an
*already-running* instance do pre-existing players need a one-time backfill award.

### Grading reports
Every hint unlock (all stages now, since HX-01 is costed too) is logged, and the
capstone quiz is scored server-side (never shown to the player — only the
pass/fail ending is). Both are reproduced on a rebuild (plugins baked into the
ctfd image; the finale table is auto-created):

    python tools/hint_report.py            # per player: hints used, points spent, stages
    python tools/hint_report.py --detail   # one row per hint unlocked
    python tools/finale_report.py          # per player: capstone first-try/best score, attempts, pass/fail

---

## C. Targeted fixes

### Static artefacts only (HX-01, 03, 04, 05)
    ./build-all.sh                 # regenerates all from integration.yml
    # verify every distributed master against its recorded hash:
    for s in challenges/*/dist/SHA256SUMS challenges/*/dist/*.sha256; do
      (cd "$(dirname "$s")" && sha256sum -c "$(basename "$s")"); done
    # re-attach without a full seed:
    python tools/seed_ctfd.py --no-theme

### HX-02 web container
    docker compose rm -sf hx02-web
    docker compose up -d --build hx02-web
    # smoke test — needs a cookie jar (-c/-b): the SQLi login sets the Flask
    # session on the 302, which must be carried to /chamber/diary.
    curl -s -c /tmp/cj -b /tmp/cj \
         --data-urlencode "username=triddle'--" --data-urlencode "password=x" \
         -L http://$LAB_IP:8000/chamber/login | grep -o "Diary of T. Riddle"

### Theme / story / hint-dialog only (no challenge changes)
    CTFD_TOKEN=ctfd_... python ctfd-theme/horcrux-inject/build_inject.py
    # or, via the seeder (challenges are idempotent):
    CTFD_TOKEN=ctfd_... python tools/seed_ctfd.py

### HX-06 vault
Container (default) — rebuilt from challenges/hx06-vault/ (shared `provision.sh`):

    docker compose up -d --build hx06-vault     # fresh vault, SSH on $LAB_IP:2222
    # smoke test (from a box with sshpass):
    sshpass -p GRINGOTTS-472 ssh vault@$LAB_IP -p 2222 \
      'sudo find /etc/hostname -exec cat /root/final_fragment.txt \; -quit'

Real lab VM (alternative, target 10.10.20.60):

    VBoxManage snapshot gringotts-vault restore clean
    VBoxManage startvm gringotts-vault --type headless
