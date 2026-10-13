# HX-06 — The Gringotts Vault (Linux privilege escalation)

Stage 6 of The Horcrux Protocol, the capstone. The player SSHes into the vault
host, enumerates, finds a single bounded misconfiguration, and reads the final
fragment.

**Category:** Linux / privilege escalation · **Points:** 400 · **Flag:** `HORCRUX{...}` (set from `integration.yml`)

## Access
```
ssh vault@LAB_IP -p 2222
```
The password is the investigation code recovered in HX-05.

## Skill practiced
Enumeration and exploiting one intentional, bounded misconfiguration to escalate
privileges and read a root-only file.

## Files in this stage
- `Dockerfile` — builds the vault container.
- `provision.sh` / `setup.sh` — plant the user, the flag, and the misconfiguration.
- `entrypoint.sh` — runtime startup (SSH, egress rules).
- `verify.sh` — self-check that the intended path still works.
- `Vagrantfile` — alternative VM build (host-only, no internet).

## Run
Built and served automatically by `docker compose up` (the `hx06-vault` service).
