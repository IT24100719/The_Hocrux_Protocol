# The Horcrux Protocol: Shadows Over Hogwarts

A six-stage, story-driven Capture-the-Flag (CTF) that runs entirely in Docker.
Clone it, run one command, and play through a narrated hacking investigation in
your browser. All data is synthetic — run it on a local/isolated machine, not the
public internet.

PS: The Contributions are not displayed correctly,to view live click contributors.
---

## The story

Years after the war, you are **George Weasley** : now an Unspeakable in the
Department of Mysteries. Something the dark lord left behind never trusted death
to keep him, and it is beginning to wake. Armed with a device that can pull a
soul back out of time, you must recover **six lost fragments** before the threat
breaks loose.

Each fragment is guarded by the memory of someone who fell. To reach each one you have to **break a
real security challenge**. Solve it, lay the past to rest, and the next door
opens. Along the way the ghosts tempt you with a bargain of your own... and the
finale asks whether you can bring the whole case home.

The narrative plays out as cinematic interludes inside the CTF platform: a
prologue, an "arrival" and a "sealing" scene for every stage, a midpoint
temptation, and a capstone finale quiz — so it reads like a story, not just a
scoreboard.

## What the CTF covers

Six stages, each a different discipline. They **unlock in order** (you must solve
one to reveal the next), ramping from beginner to intermediate:

| # | Stage | Category | Skill you practice |
|---|-------|----------|--------------------|
| HX-01 | The Marauder's Map | **Steganography** | Finding data hidden inside an image |
| HX-02 | The Chamber of Secrets | **Web exploitation** | Bypassing a weak authentication flow |
| HX-03 | The Runes of Hogwarts | **Cryptography** | Breaking a classical cipher with a recovered key |
| HX-04 | The Restricted Section | **Forensics** | Correlating logs and reading leftover metadata |
| HX-05 | The Floo Network | **Network analysis** | Isolating a suspicious stream in a packet capture |
| HX-06 | The Gringotts Vault | **Linux privilege escalation** | SSH enumeration and a bounded misconfiguration |

All flags follow the format `HORCRUX{...}`. Hints are available on each stage for
a small point penalty.

---

## Prerequisites

Before you start, make sure you have:

1. **Docker** — installed **and running**. This is the only hard requirement; the
   whole CTF runs in containers.
   - **Windows / macOS:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
     (on Windows, keep the WSL 2 backend). **Launch Docker Desktop and wait until
     it says "Engine running" before continuing.**
   - **Linux:** `curl -fsSL https://get.docker.com | sh`, then
     `sudo usermod -aG docker "$USER"` and log out/in so you can run Docker
     without `sudo`.
2. **Git** — to clone the repo.
   - **Windows:** [Git for Windows](https://git-scm.com/download/win) (also gives
     you **Git Bash**, handy for running `start.sh`).
3. **Resources & ports:** ~4 GB free disk and ~2 GB RAM for the containers, and
   the host ports **8000** (web) and **2222** (SSH) free.

**Confirm Docker is actually running** before going further:

```bash
docker run --rm hello-world
```

If that prints a "Hello from Docker!" message, you're ready. If it errors with
something like *"cannot connect to the Docker daemon"*, Docker isn't running —
start Docker Desktop (or the Docker service) and try again.

---

## Step-by-step: clone and run

### 1. Clone the repository

```bash
git clone https://github.com/IT24100719/The_Hocrux_Protocol.git
```
```bash
cd The_Hocrux_Protocol
```

### 2. (Optional) configure — the launcher does this for you

On first run, `start.sh` / `start.ps1` automatically create a `.env` file from
`.env.example` with freshly generated secrets, and print the admin password.
**You don't need to edit anything to play on a single machine.**

Edit `.env` only if you want to customize:
- `LAB_IP` — `127.0.0.1` for a single machine (default), or the host's LAN IP to
  let other machines on your lab network reach it.
- `CTFD_ADMIN_NAME` / `CTFD_ADMIN_EMAIL` / `CTFD_ADMIN_PASSWORD` — the admin
  account (the password is auto-generated; set your own here if you prefer).

To regenerate everything, delete `.env` and launch again.

### 3. Launch

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

**Linux / macOS / Git Bash:**
```bash
./start.sh
```

**Headless / no auto-open browser (any OS):**
```bash
docker compose up -d --build
```

The first run **builds the images and provisions the CTF (~1–2 minutes)**. Your
browser opens on a loading screen and **auto-advances to the CTF** once
provisioning finishes. Watch progress any time with:

```bash
docker compose logs -f seeder
```

### 4. Open and play

Replace `LAB_IP` with your value (default `127.0.0.1`):

| What | Where |
|------|-------|
| CTFd (main site) | `http://LAB_IP:8000/` |
| HX-02 web stage | `http://LAB_IP:8000/chamber` |
| HX-06 vault (SSH) | `ssh vault@LAB_IP -p 2222` |

- **Players:** click **Register** on the site and create your own account, then
  start at HX-01. Each solve unlocks the next stage.
- **Admin:** log in with the `CTFD_ADMIN_*` values from your `.env` (the launcher
  printed the generated admin password on first run).

---

## Stop / reset

```bash
docker compose down        # stop everything, keep all data (accounts, progress)
```
```bash
docker compose down -v     # stop and wipe the database for a totally fresh start
```

To start again later, just run the launcher (or `docker compose up -d`) again.

---

> **Windows line-endings note:** the repo ships a `.gitattributes` that keeps the
> `.sh` scripts as **LF**, so they work inside the Linux containers. If you ever
> hit a `bad interpreter` error after editing a script, normalize it with:
> ```bash
> sed -i 's/\r$//' start.sh build-all.sh tools/*.sh challenges/hx06-vault/*.sh tools/seeder/entrypoint.sh
> ```
