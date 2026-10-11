# The Horcrux Protocol — Launch Guide (Windows & Linux)

A six-stage Harry-Potter-themed CTF that runs entirely in Docker. This guide takes
a **fresh Windows or Linux machine** from zip to a playable CTF in ~10 minutes.

> **Isolated lab only.** All data is synthetic. Never expose this to the public
> internet — keep it on localhost or a private lab LAN.

---

## 0. What you need (one-time install)

**Windows 10/11**
- **Docker Desktop** → https://www.docker.com/products/docker-desktop/
  During install, keep the **WSL 2** backend (the default). Reboot if asked.
- **Git for Windows** (gives you *Git Bash*) → https://git-scm.com/download/win
  (Optional — only needed if you want to run the `.sh` scripts. You can use the
  PowerShell path instead and skip this.)

**Linux**
- **Docker Engine + Compose v2** →
  ```bash
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER"   # then log out/in so docker runs without sudo
  ```
- Verify: `docker compose version` should print v2.x.

Confirm Docker is running (both OSes): `docker run --rm hello-world` prints a success message.

---

## 1. Unzip

Extract the zip anywhere, e.g. `C:\horcrux-ctf\` (Windows) or `~/horcrux-ctf/` (Linux).
Open a terminal **inside that folder** (the one containing `docker-compose.yml`).

> **Windows + Git Bash:** the shell scripts must keep **LF** line endings. This zip
> ships them as LF; don't let an editor convert them to CRLF. If a script fails with
> `bad interpreter` or similar, run:
> ```bash
> sed -i 's/\r$//' start.sh build-all.sh tools/*.sh challenges/hx06-vault/*.sh tools/seeder/entrypoint.sh
> ```

---

## 2. Configure (secrets)

This package already includes a working **`.env`** and **`integration.yml`**, so it
runs as-is. These two files contain secrets (admin password, DB password, the CTF
flags) — fine for a private lab, but:

- **Change the secrets** before any shared/graded deployment: edit `.env` and set new
  `DB_PASSWORD`, `CTFD_SECRET_KEY`, and `CTFD_ADMIN_PASSWORD`.
- **Set `LAB_IP`** for how players reach it:
  - `LAB_IP=127.0.0.1` → single machine, only this box can reach it (default).
  - `LAB_IP=<this host's LAN IP>` (e.g. `192.168.56.10`) → other machines on the lab
    LAN can reach it. Published ports bind to that interface only.
- `HORCRUX_START_POINTS=100` → welcome points each new player gets.

(You do **not** need to touch `HX02_FLAG` / `HX02_CIPHERTEXT` — the build injects them
from `integration.yml`.)

---

## 3. Launch

**Windows (PowerShell — easiest):**
```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

**Windows (Git Bash) or Linux/macOS:**
```bash
./start.sh
```

**Any OS, no auto-open browser (headless servers):**
```bash
docker compose up -d --build
```

`start.sh` / `start.ps1` bring the whole stack up **and open your browser** on a dark
**provisioning loading screen**, which auto-advances to the CTF the moment it's ready.
First run builds images + provisions everything — **~1–2 minutes** (watch it with
`docker compose logs -f seeder`, wait for *"the CTF is provisioned"*).

The one-shot `seeder` container does everything: generates the challenge artefacts,
seeds CTFd (6 challenges, flags, attachments, unlock-in-order prerequisites, 18 hints,
the parchment theme + story layer, the briefing page) and creates a test user. No
host-side Python or API token needed.

---

## 4. Play

Replace `LAB_IP` below with whatever you set (default `127.0.0.1`):

| What | Where |
|---|---|
| **CTFd (main site)** | `http://LAB_IP:8000/` |
| HX-02 web challenge | `http://LAB_IP:8000/chamber` |
| HX-06 vault (SSH) | `ssh vault@LAB_IP -p 2222` |

**Logins (from `.env` / the seeder):**

| Role | User | Password |
|---|---|---|
| CTFd **admin** | `admin` | `Horcrux-admin-2026` |
| Test participant | `auror_tester` | `HxLab-test-2026` |
| HX-06 vault SSH | `vault` | `GRINGOTTS-472` |

Real players **self-register** their own CTFd account (and get the welcome points
automatically). Challenges unlock in order (HX-01 → HX-06).

---

## 5. Audio (optional, already set up)

If `audio/ambient.mp3`, `audio/tension.mp3`, `audio/finale.mp3` are present and
`scenes.json` has `audio.enabled: true`, the CTF plays a soundtrack (ambient → tension
→ finale) with a ♪ toggle + volume slider, bottom-right. Browsers start it on the
player's first click. To change tracks, replace the files in `audio/` and re-run
`docker compose run --rm seeder`. See `audio/README.md`.

---

## 6. Stop / reset / move

```bash
docker compose down            # stop, keep all data
docker compose down -v         # stop AND wipe the database + volumes (fresh start)
```

- **Re-provision without wiping** (e.g. after editing story/theme): `docker compose run --rm seeder`
- **Carry player progress to another host:** on the old host `tools/backup.sh`, copy the
  `.tgz`, deploy clean on the new host, then `tools/restore.sh backups/horcrux-<ts>.tgz`.
- More detail in `runbooks/deploy.md` and `runbooks/reset.md`.

---

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `Cannot connect to the Docker daemon` / `dockerDesktopLinuxEngine` | Docker Desktop isn't running — start it and wait for the whale icon to go steady, then retry. |
| Browser shows the loading screen and never advances | Provisioning still running or failed — `docker compose logs -f seeder`. It advances when the readiness marker is set. |
| `port is already allocated` (8000 or 2222) | Another process uses the port. Stop it, or change the published port in `docker-compose.yml`. |
| Shell script fails on Windows (`\r`/`bad interpreter`) | Line endings got converted to CRLF — run the `sed` command in step 1. |
| SSH to HX-06 warns about a changed host key | A rebuild regenerated it — `ssh-keygen -R "[LAB_IP]:2222"` then retry. |
| Admin page shows the setup wizard | DB was wiped and the seeder hasn't finished — wait for it, or re-run `docker compose run --rm seeder`. |

---

## 8. HX-06 as a real VM (optional)

HX-06 ships as a container (SSH on `:2222`) and needs nothing extra. For a real lab VM
at `10.10.20.60` instead, install VirtualBox + Vagrant and run
`(cd challenges/hx06-vault && vagrant up)`. Same provisioning, identical solve path.
