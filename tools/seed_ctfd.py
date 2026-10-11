#!/usr/bin/env python3
"""Seed / re-seed a CTFd instance for The Horcrux Protocol.

Makes the whole CTF reproducible after a FULL DB reset (`docker compose down -v`),
a setup-wizard re-run, or any fresh bring-up. Idempotent: safe to run repeatedly.

It recreates, from version-controlled sources, everything we configure by hand:
  * the 6 challenges  (name / category / value / description / state)  <- ctfd-config/challenges.yml
  * their static flags                                                  <- integration.yml
  * their attachments (marauders_map.png, ciphertext.txt, ...)          <- challenges/*/dist/  (build-all.sh)
  * the linear prerequisite chain (HX-02 needs HX-01, ... anonymized)
  * the 18 hints (content + cost), CHAINED tier1->tier2->tier3          <- ctfd-config/hints.yml
  * the parchment theme + story layer + hint-dialog fix                 <- ctfd-theme/horcrux-inject/build_inject.py
  * (optional) a disposable test player account                        <- --test-user

AUTH, two ways:
  * export CTFD_TOKEN=<admin API token>   -> used directly (an already-set-up CTFd)
  * else   -> reads admin creds from .env (CTFD_ADMIN_NAME/EMAIL/PASSWORD, CTF_NAME),
              runs the setup wizard if the instance is fresh, logs in, mints a token.

Usage:
    ./build-all.sh                         # make sure dist/ attachments exist first
    python tools/seed_ctfd.py              # seed using .env creds (or $CTFD_TOKEN)
    python tools/seed_ctfd.py --test-user  # also (re)create the auror_tester account
Intended for the isolated lab only.
"""
import argparse, json, mimetypes, os, re, sys, time, uuid
import http.cookiejar, urllib.request, urllib.parse
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path):
    env = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


ENV = load_env(os.path.join(ROOT, ".env"))


def cfg(key, default=None):
    return os.environ.get(key) or ENV.get(key) or default


class CTFd:
    """Thin CTFd client: cookie session + CSRF nonce, or Token auth."""

    def __init__(self, base):
        self.base = base.rstrip("/")
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar),
            urllib.request.HTTPRedirectHandler())
        self.nonce = None
        self.token = None

    # ---- low level ----
    def _open(self, req):
        last = None
        for _ in range(4):
            try:
                return self.opener.open(req, timeout=20)
            except urllib.error.HTTPError as e:
                return e               # let callers inspect status/body
            except Exception as e:
                last = e; time.sleep(0.5)
        raise last

    def get_html(self, path):
        req = urllib.request.Request(self.base + path, headers={"Accept": "text/html"})
        return self._open(req).read().decode("utf-8", "replace")

    def grab_nonce(self, path="/login"):
        html = self.get_html(path)
        m = re.search(r"'csrfNonce'\s*:\s*\"([0-9a-f]+)\"", html) \
            or re.search(r'name="nonce"[^>]*value="([0-9a-f]+)"', html) \
            or re.search(r'csrfNonce["\']?\s*[:=]\s*["\']([0-9a-f]+)', html)
        self.nonce = m.group(1) if m else None
        return self.nonce

    def post_form(self, path, fields, files=None):
        body, ctype = encode_multipart(fields, files or {})
        req = urllib.request.Request(self.base + path, data=body, method="POST",
                                     headers={"Content-Type": ctype})
        return self._open(req)

    def api(self, method, path, data=None, files=None):
        # NOTE: CTFd only treats a request as an API call (and honours the
        # Authorization: Token header) when Content-Type is application/json.
        # Without it, even GETs get redirected to /login. So we always set it
        # except for multipart file uploads.
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = "Token " + self.token
        elif self.nonce:
            headers["CSRF-Token"] = self.nonce
        if files is not None:
            body, ctype = encode_multipart(data or {}, files)
            headers["Content-Type"] = ctype
        elif data is not None:
            body = json.dumps(data).encode()
        else:
            body = None
        req = urllib.request.Request(self.base + "/api/v1" + path, data=body,
                                     method=method, headers=headers)
        r = self._open(req)
        raw = r.read().decode("utf-8", "replace")
        try:
            return getattr(r, "status", 200), json.loads(raw)
        except Exception:
            return getattr(r, "status", 0), {"_raw": raw[:200]}


def encode_multipart(fields, files):
    boundary = "----hx" + uuid.uuid4().hex
    out = []
    for k, v in fields.items():
        out.append(("--" + boundary).encode())
        out.append(('Content-Disposition: form-data; name="%s"' % k).encode())
        out.append(b"")
        out.append(str(v).encode("utf-8"))
    for k, (fname, content) in files.items():
        ct = mimetypes.guess_type(fname)[0] or "application/octet-stream"
        out.append(("--" + boundary).encode())
        out.append(('Content-Disposition: form-data; name="%s"; filename="%s"'
                    % (k, fname)).encode())
        out.append(("Content-Type: %s" % ct).encode())
        out.append(b"")
        out.append(content)
    out.append(("--" + boundary + "--").encode())
    out.append(b"")
    return b"\r\n".join(out), "multipart/form-data; boundary=" + boundary


def log(msg): print(msg, flush=True)


# ------------------------------------------------------------------ setup/login
def needs_setup(c):
    html = c.get_html("/setup")
    return 'name="password"' in html and ('setup' in html.lower())


def run_setup(c):
    name = cfg("CTFD_ADMIN_NAME", "admin")
    email = cfg("CTFD_ADMIN_EMAIL", "admin@lab.test")
    pw = cfg("CTFD_ADMIN_PASSWORD")
    ctf_name = cfg("CTF_NAME", "The Horcrux Protocol")
    if not pw:
        sys.exit("Fresh CTFd needs CTFD_ADMIN_PASSWORD in .env (and name/email).")
    c.grab_nonce("/setup")
    log(f"[setup] creating admin '{name}' and CTF '{ctf_name}'")
    fields = {
        "ctf_name": ctf_name, "ctf_description": "An isolated pen-testing lab.",
        "user_mode": "users", "name": name, "email": email, "password": pw,
        "ctf_theme": "core-beta", "challenge_visibility": "private",
        "account_visibility": "private", "score_visibility": "private",
        # public so players can self-register (Register button + /register).
        # Challenges/accounts/scores stay private: login still required to see them.
        "registration_visibility": "public", "verify_emails": "false",
        "nonce": c.nonce,
    }
    r = c.post_form("/setup", fields)
    st = getattr(r, "status", 0)
    if st not in (200, 302):
        sys.exit(f"[setup] failed (HTTP {st}). Body: {r.read()[:200]!r}")
    log("[setup] done")


def ensure_registration_open(c):
    """Make sure players can self-register, on every run (not just fresh setup),
    so an already-provisioned instance picks it up too. Idempotent."""
    try:
        st, r = c.api("PATCH", "/configs", {"registration_visibility": "public"})
        ok = isinstance(r, dict) and r.get("success")
        log(f"[config] registration_visibility=public ({'ok' if ok else 'HTTP '+str(st)})")
    except Exception as e:
        log(f"[config] could not set registration_visibility: {e}")


def login(c):
    name = cfg("CTFD_ADMIN_NAME", "admin")
    pw = cfg("CTFD_ADMIN_PASSWORD")
    if not pw:
        sys.exit("Need CTFD_ADMIN_PASSWORD in .env to log in (or set CTFD_TOKEN).")
    c.grab_nonce("/login")
    r = c.post_form("/login", {"name": name, "password": pw, "nonce": c.nonce})
    # after login, grab a fresh nonce from an authenticated page for API CSRF
    c.grab_nonce("/challenges")
    log(f"[auth] logged in as '{name}'")


def ensure_token(c):
    """Mint an admin API token so the rest (incl. build_inject) can use it."""
    st, r = c.api("POST", "/tokens", {})
    if st == 200 and r.get("success"):
        c.token = r["data"]["value"]
        log("[auth] minted API token")
        return c.token
    log(f"[auth] could not mint token (HTTP {st}: {str(r)[:120]}); using session CSRF")
    return None


def wait_up(c, tries=60):
    """Block until CTFd answers (fresh `docker compose up` needs a few seconds)."""
    for i in range(tries):
        try:
            c.opener.open(urllib.request.Request(c.base + "/", headers={"Accept": "text/html"}), timeout=5)
            return True
        except Exception:
            if i == 0:
                log("[*] waiting for CTFd to come up ...")
            time.sleep(2)
    sys.exit(f"[!] CTFd never responded at {c.base}")


# ------------------------------------------------------------------ challenges
def all_challenges(c):
    st, r = c.api("GET", "/challenges?view=admin")
    return {x["name"]: x for x in (r.get("data") or [])} if st == 200 else {}


def challenge_detail(c, cid):
    st, r = c.api("GET", f"/challenges/{cid}")
    return r.get("data", {}) if st == 200 else {}


def upsert_challenge(c, existing, spec):
    body = {k: spec[k] for k in ("name", "category", "value", "description", "state", "type")}
    if spec.get("connection_info"):
        body["connection_info"] = spec["connection_info"].replace("{LAB_IP}", cfg("LAB_IP", "127.0.0.1"))
    if spec["name"] in existing:
        cid = existing[spec["name"]]["id"]
        c.api("PATCH", f"/challenges/{cid}", body)
        log(f"[chal] updated #{cid} {spec['name']}")
    else:
        st, r = c.api("POST", "/challenges", body)
        if st != 200 or not r.get("success"):
            sys.exit(f"[chal] create failed for {spec['name']}: {r}")
        cid = r["data"]["id"]
        log(f"[chal] created #{cid} {spec['name']}")
    return cid


def ensure_flag(c, cid, content):
    st, r = c.api("GET", f"/flags?challenge_id={cid}")
    flags = r.get("data", []) if st == 200 else []
    for f in flags:
        if f.get("content") == content and f.get("type") == "static":
            return
    if flags:  # wrong/stale flag(s) present -> clear them
        for f in flags:
            c.api("DELETE", f"/flags/{f['id']}")
    c.api("POST", "/flags", {"challenge_id": cid, "content": content,
                             "type": "static", "data": ""})
    log(f"[flag] set for #{cid}")


def ensure_file(c, cid, path):
    det = challenge_detail(c, cid)
    want = os.path.basename(path)
    for f in det.get("files", []):
        if want in f:
            return
    if not os.path.exists(path):
        log(f"[file] MISSING {path} (run build-all.sh) — skipped for #{cid}")
        return
    with open(path, "rb") as fh:
        content = fh.read()
    st, r = c.api("POST", "/files",
                  data={"challenge_id": cid, "type": "challenge"},
                  files={"file": (want, content)})
    log(f"[file] uploaded {want} to #{cid}" if st == 200 else f"[file] FAILED {want}: {r}")


def set_requirement(c, cid, prereq_id):
    c.api("PATCH", f"/challenges/{cid}",
          {"requirements": {"prerequisites": [prereq_id], "anonymize": True}})
    log(f"[req]  #{cid} now requires #{prereq_id}")


# ------------------------------------------------------------------ hints
def reconcile_hints(c, cid, tiers):
    """Make the challenge's hints exactly `tiers` (list of {cost,content}),
    in ascending-id = tier order, chained tier2<-tier1, tier3<-tier2."""
    det = challenge_detail(c, cid)
    ids = sorted(h["id"] for h in det.get("hints", []))
    # match count
    while len(ids) < len(tiers):
        st, r = c.api("POST", "/hints", {"challenge_id": cid, "content": "…",
                                         "cost": tiers[len(ids)]["cost"], "type": "standard"})
        ids.append(r["data"]["id"])
    for extra in ids[len(tiers):]:
        c.api("DELETE", f"/hints/{extra}")
    ids = ids[:len(tiers)]
    # write content/cost + chain
    for i, hid in enumerate(ids):
        body = {"content": tiers[i]["content"], "cost": tiers[i]["cost"],
                "requirements": {"prerequisites": ([ids[i - 1]] if i else [])}}
        c.api("PATCH", f"/hints/{hid}", body)
    log(f"[hint] #{cid}: {len(ids)} hints set + chained")


# ------------------------------------------------------------------ pages
def seed_pages(c):
    """Upsert CTFd pages from ctfd-config/pages/*.md. The filename is the route
    (index.md -> the home page); the title is the first `# ` heading."""
    import glob
    pdir = os.path.join(ROOT, "ctfd-config", "pages")
    if not os.path.isdir(pdir):
        return
    st, r = c.api("GET", "/pages")
    existing = {p["route"]: p for p in (r.get("data") or [])}
    for path in sorted(glob.glob(os.path.join(pdir, "*.md"))):
        route = os.path.splitext(os.path.basename(path))[0]
        content = open(path, encoding="utf-8").read()
        m = re.search(r"^#\s+(.+)$", content, re.M)
        title = m.group(1).strip() if m else route
        body = {"route": route, "title": title, "content": content,
                "draft": False, "hidden": False, "auth_required": False, "format": "markdown"}
        if route in existing:
            c.api("PATCH", f"/pages/{existing[route]['id']}", body)
            log(f"[page] updated /{route}")
        else:
            c.api("POST", "/pages", body)
            log(f"[page] created /{route}")


# ------------------------------------------------------------------ test user
def ensure_test_user(c):
    name, email, pw = "auror_tester", "auror_tester@lab.test", "HxLab-test-2026"
    st, r = c.api("GET", f"/users?view=admin")
    for u in (r.get("data") or []):
        if u.get("name") == name:
            log("[user] auror_tester already exists"); return
    st, r = c.api("POST", "/users",
                  {"name": name, "email": email, "password": pw,
                   "type": "user", "verified": True, "hidden": True})
    log("[user] created auror_tester (hidden)" if st == 200 else f"[user] FAILED: {r}")


# ------------------------------------------------------------------ theme
def inject_theme(token, base):
    import subprocess
    script = os.path.join(ROOT, "ctfd-theme", "horcrux-inject", "build_inject.py")
    env = dict(os.environ, CTFD_TOKEN=token or "", CTFD_URL=base)
    log("[theme] injecting parchment theme + story layer + hint-dialog fix")
    p = subprocess.run([sys.executable, script], env=env)
    if p.returncode != 0:
        log("[theme] build_inject.py returned non-zero — check its output")


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description="Seed CTFd for The Horcrux Protocol.")
    ap.add_argument("--base-url", default=cfg("CTFD_URL", "http://127.0.0.1:8000"))
    ap.add_argument("--test-user", action="store_true", help="also create auror_tester")
    ap.add_argument("--no-theme", action="store_true", help="skip theme injection")
    ap.add_argument("--no-files", action="store_true", help="skip attachment uploads")
    args = ap.parse_args()

    chals = yaml.safe_load(open(os.path.join(ROOT, "ctfd-config", "challenges.yml"), encoding="utf-8"))["challenges"]
    hints = yaml.safe_load(open(os.path.join(ROOT, "ctfd-config", "hints.yml"), encoding="utf-8"))["hints"]
    integ = yaml.safe_load(open(os.path.join(ROOT, "integration.yml"), encoding="utf-8"))
    flags = integ["flags"]

    c = CTFd(args.base_url)
    log(f"[*] target {c.base}")
    wait_up(c)

    token = cfg("CTFD_TOKEN")
    if token:
        c.token = token
        log("[auth] using CTFD_TOKEN from environment")
    else:
        if needs_setup(c):
            run_setup(c)
        login(c)
        ensure_token(c)

    ensure_registration_open(c)

    existing = all_challenges(c)
    ids = {}
    for spec in chals:
        cid = upsert_challenge(c, existing, spec)
        ids[spec["key"]] = cid
        ensure_flag(c, cid, flags[spec["key"]])
        if not args.no_files:
            atts = spec.get("attachments") or ([spec["attachment"]] if spec.get("attachment") else [])
            for a in atts:
                ensure_file(c, cid, os.path.join(ROOT, a))
        reconcile_hints(c, cid, hints[spec["key"]])

    # linear prerequisite chain in declared order
    order = [s["key"] for s in chals]
    for i in range(1, len(order)):
        set_requirement(c, ids[order[i]], ids[order[i - 1]])

    seed_pages(c)

    if args.test_user:
        ensure_test_user(c)

    if not args.no_theme:
        inject_theme(c.token, c.base)

    log("\n[done] seed complete — %d challenges, %d hints."
        % (len(ids), sum(len(v) for v in hints.values())))


if __name__ == "__main__":
    main()
