# The Horcrux Protocol: Shadows Over Hogwarts

Six-stage CTF Play Box for an isolated lab. All data synthetic; never expose to the internet.

## Build
    cp .env.example .env            # set LAB_IP, DB_PASSWORD, CTFD_SECRET_KEY, CTFD_ADMIN_*
    # ensure integration.yml is present (gitignored — copy it if you cloned)
    ./start.sh                      # bring up + auto-provision + open the CTF in a browser
    # Windows (no Git Bash):  powershell -ExecutionPolicy Bypass -File start.ps1
    # or plain, no browser:   docker compose up -d --build   (then docker compose logs -f seeder)

The browser opens on a dark **provisioning loading screen** and auto-advances to
the CTF the moment the seeder finishes (first run ~1-2 min).

The one-shot `seeder` container generates the artefacts and seeds CTFd
(challenges, flags, attachments, prereqs, 18 hints, theme, pages, test user) — no
host-side Python needed. HX-06 runs as a container (SSH on :2222); for a real lab
network at 10.10.20.60 use the VM instead: `(cd challenges/hx06-vault && vagrant up)`.
Host-driven alternative: `./build-all.sh && docker compose up -d --build && python tools/seed_ctfd.py --test-user`.

Participants reach CTFd at http://$LAB_IP:8000/ ; HX-02 at /chamber ;
HX-06 via `ssh vault@$LAB_IP -p 2222` (password recovered in HX-05).
Admin after seeding = `CTFD_ADMIN_NAME` / `CTFD_ADMIN_PASSWORD` from `.env`.

`tools/seed_ctfd.py` makes the whole CTF reproducible: it runs the setup wizard
on a fresh DB, then (re)creates the 6 challenges, their flags/attachments, the
unlock-in-order prerequisite chain, the 18 chained hints, and the parchment theme
+ story layer. It is idempotent — re-run it any time. See `runbooks/reset.md` for
the full reset/rebuild procedure (incl. `docker compose down -v`).

## Secrets & release boundary
Infrastructure secrets (DB password, CTFd `SECRET_KEY`, admin password, API
tokens) live only in `.env` / `integration.yml` / `answer-key/`, all gitignored.
The six CTF **flags** are content and appear in design files (story, HX-06
provisioning, the stego clue), so **this repo is PRIVATE** — do not publish it
without scrubbing. Before a release:

    gitleaks detect --config .gitleaks.toml --redact -v   # once git-initialised
    ./build-all.sh && (for s in challenges/*/dist/SHA256SUMS challenges/*/dist/*.sha256; \
        do (cd "$(dirname "$s")" && sha256sum -c "$(basename "$s")"); done)
    tools/release_manifest.sh > RELEASE_MANIFEST.txt       # versions, image IDs, hashes

Only the proxy (`:8000`) and the HX-06 vault (`:2222`) publish ports, both bound
to `$LAB_IP` — never `0.0.0.0`.

## Layout
    start.sh / start.ps1   one-command launch: up + provision + open browser
    integration.yml        single source of truth (private)
    docker-compose.yml      platform stack
    proxy/                  nginx routing (/chamber -> HX-02, / -> CTFd)
    challenges/hx0*/        per-stage generators + dist/ artefacts
    answer-key/             solutions (private)
    runbooks/reset.md       recovery / full rebuild
    runbooks/deploy.md      deploy on another computer (incl. migrating player data)
    ctfd-config/            challenges.yml + hints.yml (declarative CTF definition)
    tools/seed_ctfd.py      idempotent seeder (challenges, hints, prereqs, theme)
    tools/backup.sh         snapshot player progress (db + uploads); restore.sh to roll back
    tools/release_manifest.sh  versions + image IDs + artefact hashes (run at release)
    .gitleaks.toml          secret-scan config (flags allowlisted; infra secrets caught)
    tools/hint_report.py    grading report: hints used per player
    tools/finale_report.py  grading report: capstone-quiz score per player (hidden from players)
    ctfd/plugins/           horcrux_starting_points (welcome points) + horcrux_finale (quiz scoring)
    ctfd-theme/horcrux-inject/  parchment theme + story layer + hint-dialog fix
