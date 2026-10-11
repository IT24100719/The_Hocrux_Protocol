#!/usr/bin/env python3
"""HX-01 - The Marauder's Map.

Produces dist/marauders_map.png: the challenge image with the flag + web clue
LSB-embedded into the BLUE channel (terminated by the sentinel ::END::), so
`solve.py` and `zsteg -a` recover it. Reads values from integration.yml.

SOURCE IMAGE: if `Marauders_Map.png` sits next to this script, it is used as the
base artwork (the operator's own/licensed map) — this is the permanent HX-01
image and build-all.sh / generate.py will NOT overwrite it with a drawn map.
If that file is absent, an ORIGINAL aged "castle map" is drawn from scratch
instead (not based on any existing/copyrighted image) as a fallback.
"""
import yaml, random, math, hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[2]
CFG = yaml.safe_load((ROOT / "integration.yml").read_text())
FLAG = CFG["flags"]["hx01"]
PORTAL = CFG["handover"]["web_portal_path"]
USER = CFG["handover"]["web_target_user"]
SENTINEL = "::END::"

HERE = Path(__file__).parent
OUT = HERE / "dist"; OUT.mkdir(exist_ok=True)
SOURCE = HERE / "Marauders_Map.png"   # operator-supplied artwork (preferred)

payload = (f"{FLAG}\nWEB CLUE: The Chamber portal lives at {PORTAL} on the CTFd "
           f"host. The diary remembers a researcher named '{USER}'. Log in as "
           f"that account to reach what it hides.{SENTINEL}")

PARCH = (226, 208, 167); INK = (74, 55, 33); INK2 = (112, 88, 54); FADE = (171, 149, 108)


def font(size, bold=False):
    cands = (["C:/Windows/Fonts/georgiab.ttf", "C:/Windows/Fonts/timesbd.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"] if bold else
             ["C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/times.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"])
    for c in cands:
        try: return ImageFont.truetype(c, size)
        except Exception: pass
    return ImageFont.load_default()


def draw_original():
    """Fallback: draw an ORIGINAL aged castle map (no copyrighted source)."""
    W, H = 1024, 720
    random.seed(1991)
    img = Image.new("RGB", (W, H), PARCH)
    d = ImageDraw.Draw(img)

    # --- parchment texture: speckle + faint stain rings + edge darkening ---
    px = img.load()
    for _ in range(14000):
        x, y = random.randint(0, W - 1), random.randint(0, H - 1)
        v = random.randint(-16, 10)
        r, g, b = px[x, y]; px[x, y] = (max(0, min(255, r + v)), max(0, min(255, g + v)), max(0, min(255, b + v)))
    for _ in range(26):
        cx, cy, rr = random.randint(0, W), random.randint(0, H), random.randint(26, 120)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(198, 178, 136))
    for i in range(60):   # vignette
        a = int(60 * (1 - i / 60))
        d.rectangle([i, i, W - 1 - i, H - 1 - i], outline=(120 - a // 2, 96, 60))

    # --- border frame + corner flourishes ---
    d.rectangle([26, 26, W - 27, H - 27], outline=INK, width=3)
    d.rectangle([34, 34, W - 35, H - 35], outline=INK2, width=1)
    for (cx, cy) in [(26, 26), (W - 27, 26), (26, H - 27), (W - 27, H - 27)]:
        d.arc([cx - 16, cy - 16, cx + 16, cy + 16], 0, 360, fill=INK2, width=2)

    # --- faint survey grid ---
    for gx in range(60, W - 40, 56):
        d.line([(gx, 44), (gx, H - 44)], fill=(205, 185, 142))
    for gy in range(60, H - 40, 56):
        d.line([(44, gy), (W - 44, gy)], fill=(205, 185, 142))

    # --- rooms (original floorplan) + labels ---
    rooms = [
        (90, 110, 320, 300, "THE ARCHIVE WING"),
        (360, 90, 560, 230, "OWLERY"),
        (610, 120, 900, 300, "GREAT HALL"),
        (120, 360, 360, 560, "THE VAULTS"),
        (430, 330, 640, 500, "GALLERY OF RUNES"),
        (700, 360, 920, 600, "TOWER STAIR"),
    ]
    lab = font(16, bold=True)
    for (x0, y0, x1, y1, name) in rooms:
        d.rectangle([x0, y0, x1, y1], outline=INK, width=3)
        d.rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], outline=INK2, width=1)
        for hatch in range(x0 + 10, x1 - 8, 16):   # faint hatching
            d.line([(hatch, y0 + 6), (min(hatch + 10, x1 - 6), y0 + 16)], fill=(206, 186, 143))
        tw = d.textlength(name, font=lab)
        d.text(((x0 + x1) / 2 - tw / 2, (y0 + y1) / 2 - 8), name, fill=INK, font=lab)

    # --- corridors connecting rooms ---
    corr = [((320, 205), (360, 160)), ((560, 160), (610, 205)), ((235, 300), (240, 360)),
            ((540, 230), (535, 330)), ((640, 410), (700, 430)), ((360, 450), (430, 420)),
            ((760, 300), (800, 360))]
    for (a, b) in corr:
        d.line([a, b], fill=INK2, width=6)
        d.line([a, b], fill=PARCH, width=2)

    # --- compass rose (top-right) ---
    ccx, ccy, cr = 930, 110, 46
    d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], outline=INK, width=2)
    d.ellipse([ccx - cr + 8, ccy - cr + 8, ccx + cr - 8, ccy + cr - 8], outline=INK2, width=1)
    for ang, nm in [(-90, "N"), (0, "E"), (90, "S"), (180, "W")]:
        rad = math.radians(ang)
        ex, ey = ccx + math.cos(rad) * cr, ccy + math.sin(rad) * cr
        d.line([(ccx, ccy), (ex, ey)], fill=INK, width=2)
        d.polygon([(ccx + math.cos(rad) * cr * .5 - math.sin(rad) * 7, ccy + math.sin(rad) * cr * .5 + math.cos(rad) * 7),
                   (ex, ey),
                   (ccx + math.cos(rad) * cr * .5 + math.sin(rad) * 7, ccy + math.sin(rad) * cr * .5 - math.cos(rad) * 7)],
                  fill=INK)
    cf = font(14, bold=True)
    d.text((ccx - 5, ccy - cr - 18), "N", fill=INK, font=cf)

    # --- wandering footprint trail (generic ink footprints) ---
    def footprints(path):
        for i in range(len(path) - 1):
            (x0, y0), (x1, y1) = path[i], path[i + 1]
            seg = math.hypot(x1 - x0, y1 - y0); steps = max(1, int(seg / 26))
            ang = math.atan2(y1 - y0, x1 - x0)
            for s in range(steps):
                t = s / steps; cx = x0 + (x1 - x0) * t; cy = y0 + (y1 - y0) * t
                side = 7 if s % 2 == 0 else -7
                ox = cx - math.sin(ang) * side; oy = cy + math.cos(ang) * side
                sole = [(ox - 4, oy - 7), (ox + 4, oy - 7), (ox + 3, oy + 7), (ox - 3, oy + 7)]
                d.polygon(sole, fill=(90, 68, 40))
                d.ellipse([ox - 4, oy - 10, ox + 4, oy - 4], fill=(90, 68, 40))
    footprints([(150, 660), (240, 560), (240, 300), (420, 210), (540, 230), (540, 420),
                (660, 470), (760, 470), (800, 360)])

    # --- title banner ---
    tf = font(30, bold=True); sub = font(15)
    title = "~  Map of the Archive Wing  ~"
    d.text((W / 2 - d.textlength(title, font=tf) / 2, 54), title, fill=INK, font=tf)
    note = "Surveyed from memory by the Archive Night Watch"
    d.text((W / 2 - d.textlength(note, font=sub) / 2, 92), note, fill=INK2, font=sub)
    return img


def embed(image, text):
    """LSB-embed text into the BLUE channel (done last, on the final pixels)."""
    bits = "".join(f"{b:08b}" for b in text.encode())
    p = image.load(); w, h = image.size; i = 0
    if len(bits) > w * h:
        raise SystemExit(f"image too small: holds {w*h} bits, need {len(bits)}")
    for y in range(h):
        for x in range(w):
            if i >= len(bits): return image
            r, g, b = p[x, y][:3]
            p[x, y] = (r, g, (b & ~1) | int(bits[i])); i += 1
    return image


# --- pick the base image: operator artwork if present, else draw the fallback ---
if SOURCE.exists():
    img = Image.open(SOURCE).convert("RGB")
    print(f"[+] using supplied artwork {SOURCE.name} ({img.size[0]}x{img.size[1]})")
else:
    img = draw_original()
    print(f"[+] {SOURCE.name} not found — drew the original fallback map ({img.size[0]}x{img.size[1]})")

img = embed(img, payload)

# Metadata red-herring (the "doormat" the hints warn about): nothing useful here.
meta = PngImagePlugin.PngInfo()
meta.add_text("Comment", "Cartographer's note: the map hides more than it shows. "
              "Metadata is only the doormat; the secret is woven into the picture.")
meta.add_text("Author", "The Archive Night Watch, cartographers")
img.save(OUT / "marauders_map.png", pnginfo=meta)
print(f"[+] wrote {OUT/'marauders_map.png'}  ({img.size[0]}x{img.size[1]}, flag {FLAG})")

# --- integrity hash for the distributed master (design 9.2) ---
_d = hashlib.sha256((OUT / "marauders_map.png").read_bytes()).hexdigest()
(OUT / "SHA256SUMS").write_text(f"{_d}  marauders_map.png\n", newline="\n")
print(f"[+] wrote {OUT/'SHA256SUMS'}")
