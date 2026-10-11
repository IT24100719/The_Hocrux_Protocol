#!/usr/bin/env python3
"""HX-02 - The Chamber of Secrets.
A deliberately vulnerable research portal. ONE scoped flaw: the login query
is built by string formatting, so a SQL-injection payload bypasses auth.
After bypass (logging in as the researcher 'triddle'), the protected diary
page returns Flag 2 and the HX-03 ciphertext.

Intended for an isolated CTF lab only. Never deploy on a real network.
"""
import os, sqlite3
from flask import Flask, request, session, redirect, render_template_string

app = Flask(__name__)
app.secret_key = os.environ.get("HX02_SESSION_KEY", "chamber-dev-key")

TARGET_USER = os.environ.get("HX02_TARGET_USER", "triddle")
DB = "/tmp/chamber.db"   # /tmp is the only writable mount (read-only container)


def _read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return ""


# Flag + ciphertext resolve in this order so BOTH deploy styles work:
#   1. a shared volume written by the seeder container (fully-automated `up`),
#   2. the HX02_FLAG / HX02_CIPHERTEXT env vars (manual build-all.sh + .env),
#   3. a safe placeholder.
def hx02_flag():
    return _read("/shared/hx02_flag") or os.environ.get("HX02_FLAG", "") or "HORCRUX{replace_me}"


def hx02_ciphertext():
    return _read("/shared/ciphertext.txt") or os.environ.get("HX02_CIPHERTEXT", "") or "<ciphertext not injected>"


def init_db():
    con = sqlite3.connect(DB)
    con.execute("DROP TABLE IF EXISTS users")
    con.execute("CREATE TABLE users (username TEXT, password TEXT, role TEXT)")
    con.executemany("INSERT INTO users VALUES (?,?,?)", [
        ("admin", os.urandom(8).hex(), "admin"),
        (TARGET_USER, os.urandom(8).hex(), "researcher"),  # password unknown to player
        ("hagrid", "fang2001", "groundskeeper"),
    ])
    con.commit(); con.close()


# Themed templates (dark Chamber + parchment card). Form field names, the POST
# action, and the diary variables are unchanged -- the SQLi (triddle'--) is
# untouched. Google Fonts degrade to serif if the player has no internet.
_HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&amp;family=EB+Garamond:ital@0;1&amp;family=IM+Fell+English:ital@0;1&amp;display=swap" rel="stylesheet">
<style>
:root{--parch:linear-gradient(168deg,#e7d4ad,#dcc89d 55%,#cab689);--ink:#241a10;--ink2:#46351f;--wax:#7c2b22;--waxd:#5c1d17;--gold:#c79a3e;--edge:#9c8456}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:40px 22px;
 font-family:'EB Garamond',Georgia,serif;color:#d9c6a0;
 background:radial-gradient(90% 60% at 50% -10%,rgba(84,150,108,.13),rgba(10,16,12,0) 55%),radial-gradient(120% 90% at 50% 120%,rgba(10,20,14,.7),rgba(6,10,8,0) 60%),linear-gradient(180deg,#121a15,#0b0f0c 60%,#070a08)}
body::before{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;box-shadow:inset 0 0 220px rgba(0,0,0,.72);
 background-image:repeating-linear-gradient(0deg,transparent 0 40px,rgba(120,150,120,.03) 40px 41px),repeating-linear-gradient(90deg,transparent 0 40px,rgba(120,150,120,.03) 40px 41px)}
.card{position:relative;width:100%;background:var(--parch);border:1px solid var(--edge);border-radius:14px;color:var(--ink);
 box-shadow:0 30px 80px rgba(0,0,0,.7),inset 0 0 70px rgba(156,132,86,.3)}
.kicker{font-family:'Cinzel',serif;letter-spacing:.3em;font-size:10px;text-transform:uppercase;color:var(--ink2)}
h1{font-family:'Cinzel',serif;font-weight:700;margin:6px 0 2px;color:var(--ink)}
label{font-family:'Cinzel',serif;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink2);display:block;margin:14px 0 5px}
input{display:block;width:100%;padding:11px 12px;border:1px solid var(--edge);border-radius:8px;background:rgba(255,250,235,.55);color:var(--ink);font-family:inherit;font-size:16px}
input:focus{outline:none;border-color:var(--wax);box-shadow:0 0 0 3px rgba(124,43,34,.15)}
button{margin-top:22px;width:100%;padding:12px;border:1px solid var(--waxd);border-radius:9px;cursor:pointer;
 background:linear-gradient(var(--wax),var(--waxd));color:#f3e2d8;font-family:'Cinzel',serif;letter-spacing:.14em;text-transform:uppercase;font-size:13px}
button:hover{filter:brightness(1.08)}
.err{background:rgba(124,43,34,.12);border:1px solid rgba(124,43,34,.5);color:var(--wax);padding:9px 12px;border-radius:8px;text-align:center;margin:4px 0 2px;font-size:14px}
</style></head><body>"""

PAGE = _HEAD.replace("{title}", "The Chamber Portal") + """
<form class="card" method="post" action="/chamber/login" style="max-width:440px;padding:34px 34px 26px;text-align:center">
  <div class="kicker">Hogwarts Research Network</div>
  <h1 style="font-size:28px">The Chamber Portal</h1>
  <div style="font-style:italic;color:var(--ink2);margin-bottom:20px;font-size:15px">The diary remembers. Only the named may read it.</div>
  {% if msg %}<div class="err">{{ msg }}</div>{% endif %}
  <div style="text-align:left">
    <label for="u">Researcher name</label>
    <input id="u" name="username" autocomplete="off" placeholder="your name on the research team">
    <label for="p">Passphrase</label>
    <input id="p" name="password" type="password" autocomplete="off" placeholder="passphrase">
  </div>
  <button>Enter the Chamber</button>
  <div style="margin-top:18px;font-size:12px;color:var(--ink2)"><span style="color:var(--wax);font-size:16px">&#10070;</span><br>Restricted to authorised research staff.</div>
</form>
</body></html>"""

DIARY = _HEAD.replace("{title}", "Researcher Diary") + """
<div class="card" style="max-width:680px;padding:38px 40px 30px">
  <div class="kicker">Restricted &middot; Researcher Diary</div>
  <h1 style="font-size:30px">Diary of {{ user }}</h1>
  <div style="font-style:italic;color:var(--ink2);margin-bottom:22px">Private research notes. You are reading an account that was never meant to open to you.</div>
  <div style="font-family:'Cinzel',serif;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--wax);margin:26px 0 8px">Encrypted message recovered from this account</div>
  <pre style="font-family:'IM Fell English',Georgia,serif;font-size:16px;line-height:1.7;white-space:pre-wrap;word-break:break-word;background:rgba(60,44,24,.1);border-left:3px solid var(--gold);padding:16px 18px;border-radius:0 8px 8px 0;color:#3a2c18">{{ cipher }}</pre>
  <div style="font-family:'Cinzel',serif;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--wax);margin:26px 0 8px">Recovered fragment</div>
  <div style="font-family:'Cinzel',serif;letter-spacing:.08em;font-size:18px;text-align:center;color:#6a4e14;padding:14px;border-top:1px solid rgba(181,137,47,.5);border-bottom:1px solid rgba(181,137,47,.5)">{{ flag }}</div>
  <a href="/chamber/logout" style="display:inline-block;margin-top:24px;font-family:'Cinzel',serif;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink2);text-decoration:none;border:1px solid var(--edge);padding:8px 14px;border-radius:8px">&#8592; close the diary</a>
</div>
</body></html>"""


@app.route("/chamber")
def home():
    return render_template_string(PAGE, msg=None)


@app.route("/chamber/login", methods=["POST"])
def login():
    u = request.form.get("username", "")
    p = request.form.get("password", "")
    con = sqlite3.connect(DB); cur = con.cursor()
    # --- DELIBERATE VULNERABILITY: string-formatted query, no parameters ---
    query = "SELECT username, role FROM users WHERE username='%s' AND password='%s'" % (u, p)
    try:
        cur.execute(query)
        row = cur.fetchone()
    except sqlite3.Error:
        row = None
    finally:
        con.close()
    if row:
        session["user"] = row[0]
        return redirect("/chamber/diary")
    return render_template_string(PAGE, msg="Invalid credentials.")


@app.route("/chamber/diary")
def diary():
    if "user" not in session:
        return redirect("/chamber")
    # Pretty name for the heading (the account handle 'triddle' belongs to
    # T. Riddle). The stored session value / DB username are unchanged.
    name = "T. Riddle" if session["user"] == TARGET_USER else session["user"]
    return render_template_string(DIARY, user=name,
                                  cipher=hx02_ciphertext(), flag=hx02_flag())


@app.route("/chamber/logout")
def logout():
    session.clear(); return redirect("/chamber")


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
