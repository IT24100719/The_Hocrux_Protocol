#!/usr/bin/env python3
"""HX-04 - The Restricted Section. Builds restricted_section.zip of synthetic
artefacts. The identifier correlates across access.log and system.log to a
suspicious outbound beacon; the flag sits in the EXIF of evidence.jpg, which
notes.txt points to. All data is synthetic."""
import yaml, zipfile, hashlib, random, io
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
import piexif, piexif.helper
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parents[2]
CFG = yaml.safe_load((ROOT / "integration.yml").read_text())
H = CFG["handover"]
FLAG = CFG["flags"]["hx04"]
IDENT = H["identifier"]; SIP = H["source_ip"]; SPORT = H["source_port"]
TS = H["timestamp"]; DATE = H["capture_date"]

OUT = Path(__file__).parent / "dist"; OUT.mkdir(exist_ok=True)
STAGE = OUT / "restricted_section"; STAGE.mkdir(exist_ok=True)
random.seed(472)

users = ["USER-103", "USER-220", "USER-305", IDENT, "USER-511", "USER-640"]
paths = ["/library", "/common-room", "/greathall", "/floo-console", "/potions"]

# ---- access.log : bury the identifier among normal sessions ----
base = datetime.strptime(f"{DATE} 23:40:00", "%Y-%m-%d %H:%M:%S")
lines = []
t = base
for _ in range(60):
    t += timedelta(seconds=random.randint(1, 12))
    u = random.choice(users); pth = random.choice(paths)
    # the lead: the identifier hits the floo console just before the beacon
    if t.strftime("%H:%M:%S") >= "23:47:00" and u == IDENT:
        pth = "/floo-console"
    lines.append(f"{t.strftime('%H:%M:%S')} {u} {random.choice(['GET','POST'])} {pth} 200")
# guarantee the key line exists at a deterministic time
lines.append(f"23:47:09 {IDENT} POST /floo-console 200")
lines.sort()
(STAGE / "access.log").write_text("\n".join(lines) + "\n")

# ---- system.log : the matching outbound beacon ----
sys_lines = [
    f"Sep 18 23:46:40 hogwarts-archive sshd[1821]: Accepted session for svc-archive",
    f"Sep 18 23:47:02 hogwarts-archive floo[2213]: console session opened by {IDENT}",
    f"Sep 18 {TS} hogwarts-archive floo[2213]: outbound connection ESTABLISHED "
    f"-> {SIP}:{SPORT} (unexpected egress)",
    f"Sep 18 23:47:51 hogwarts-archive floo[2213]: transfer complete, 4213 bytes",
    f"Sep 18 23:48:10 hogwarts-archive systemd[1]: floo.service: consumed 00:01:12 CPU",
]
(STAGE / "system.log").write_text("\n".join(sys_lines) + "\n")

# ---- notes.txt : points the investigator at the image ----
(STAGE / "notes.txt").write_text(
    "Investigator handover notes\n"
    "---------------------------\n"
    f"- Account of interest flagged by the archive team: {IDENT}\n"
    "- The account accessed the Floo console right before an unexpected egress.\n"
    "- A screenshot was captured from the console and saved as evidence.jpg.\n"
    "- Metadata on that capture was NOT scrubbed. Check it.\n"
    "- Reconstruct the outbound indicator (host, port, time) for the packet team.\n")

# ---- evidence.jpg : flag hidden in EXIF UserComment ----
im = Image.new("RGB", (480, 300), (24, 28, 38))
dd = ImageDraw.Draw(im)
dd.text((20, 20), "FLOO CONSOLE - SESSION CAPTURE", fill=(180, 200, 255))
dd.text((20, 60), f"operator: {IDENT}", fill=(200, 200, 200))
dd.text((20, 90), "status: EGRESS DETECTED", fill=(255, 120, 120))
dd.rectangle([20, 140, 460, 280], outline=(90, 100, 120))
dd.text((30, 150), "nothing to see in the pixels -", fill=(120, 130, 150))
dd.text((30, 175), "the note said check the metadata.", fill=(120, 130, 150))
exif = {"Exif": {piexif.ExifIFD.UserComment:
        piexif.helper.UserComment.dump(f"Recovered fragment: {FLAG}")}}
im.save(STAGE / "evidence.jpg", exif=piexif.dump(exif))

# ---- report.pdf : synthetic incident note (background noise) ----
c = canvas.Canvas(str(STAGE / "report.pdf"), pagesize=A4)
c.setFont("Helvetica-Bold", 14); c.drawString(70, 780, "Hogwarts Archive - Preliminary Incident Note")
c.setFont("Helvetica", 10)
for i, ln in enumerate([
    "Classification: Internal - Synthetic exercise data only.",
    "Summary: Anomalous egress observed from the archive host during the night window.",
    "The Floo console service initiated an outbound connection not seen in baseline traffic.",
    "Correlate the operator account against the access log and the system log.",
    "Pass the reconstructed network indicator to the packet-analysis team (HX-05).",
    "No real systems, accounts, or personal data are involved in this exercise."]):
    c.drawString(70, 750 - i * 18, ln)
c.save()

# ---- case_note.txt : lore intake memo (framing; no EXIF spoiler) ----
(STAGE / "case_note.txt").write_text(f"""\
================================================================
  DEPARTMENT OF MYSTERIES - UNSPEAKABLE DIVISION
  CASE FILE: THE HORCRUX PROTOCOL        CLASSIFICATION: UMBRAL
================================================================
 Ref       : DM-HX04-ARCHIVE
 Logged by : G. Weasley, Unspeakable - Time Room
 Re        : Restricted-section evidence intake

 Bundle recovered from the restricted archive after the account named in the
 Chamber cipher - {IDENT} - was flagged. Every file here is a copy; the
 originals are sealed.

 Correlate that account across the logs and hold to the window around 23:47.
 The outbound indicator can be rebuilt from what is here. Treat nothing as
 background.

 What the logs will not tell you is why the archive went so quiet that night,
 or why - since before any of us noticed - one man has been holding a line
 between this thing and the rest of us. We are only now beginning to see him.
                                                              - G.W.
 MANIFEST
   access.log  system.log  notes.txt  report.pdf  evidence.jpg
================================================================
""")

# ---- zip + checksum ----
zip_path = OUT / "restricted_section.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(STAGE.iterdir()):
        z.write(f, f"restricted_section/{f.name}")
digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
(OUT / "restricted_section.sha256").write_text(f"{digest}  restricted_section.zip\n", newline="\n")
print(f"[+] wrote {zip_path}")
print(f"[+] flag in EXIF: {FLAG}")
print(f"[+] indicator: {SIP}:{SPORT} @ {TS}")
print(f"[+] sha256: {digest}")
