#!/usr/bin/env python3
"""Generate the original 'sealed fragment' emblem used on locked challenge cards.

An original Department-of-Mysteries / Time-Room hourglass seal — no copyrighted
artwork. Edit the COLORS below (or the geometry) and re-run to restyle it:

    python tools/gen_seal.py        # writes ctfd-theme/horcrux-inject/seal.svg

Then redeploy the theme (build_inject.py, or tools/seed_ctfd.py).
To use your OWN image instead, see ctfd-theme/horcrux-inject/SEAL.md.
"""
import math
import os

# ---- colours (darker antique gold on near-black bronze) ----
DARK = "#140d06"    # ring + hourglass + frame
GOLD = "#8a6a26"    # inner field + outer ring stroke
TICK = "#c3ad7f"    # clock ticks / rim marks

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "ctfd-theme", "horcrux-inject", "seal.svg")


def build():
    ticks = []
    for k in range(12):
        a = math.radians(k * 30)
        x1, y1 = 50 + 40 * math.sin(a), 50 - 40 * math.cos(a)
        x2, y2 = 50 + 45 * math.sin(a), 50 - 45 * math.cos(a)
        ticks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
    sparks = []
    for cx, cy, r in [(34, 48, 2.1), (66, 48, 2.1), (50, 72, 1.8)]:
        sparks.append(
            f'<path d="M{cx} {cy-r}L{cx+r*0.3:.1f} {cy-r*0.3:.1f}L{cx+r} {cy}'
            f'L{cx+r*0.3:.1f} {cy+r*0.3:.1f}L{cx} {cy+r}L{cx-r*0.3:.1f} {cy+r*0.3:.1f}'
            f'L{cx-r} {cy}L{cx-r*0.3:.1f} {cy-r*0.3:.1f}Z"/>')
    return (
        '<svg viewBox="0 0 100 100" class="hxc-seal-svg" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="50" cy="50" r="48" fill="{DARK}"/>'
        f'<circle cx="50" cy="50" r="48" fill="none" stroke="{GOLD}" stroke-width="1.6"/>'
        f'<g stroke="{TICK}" stroke-width="1.3" stroke-linecap="round">{"".join(ticks)}</g>'
        f'<circle cx="50" cy="50" r="38" fill="{GOLD}"/>'
        f'<circle cx="50" cy="50" r="38" fill="none" stroke="{DARK}" stroke-width="1.4"/>'
        f'<g fill="{DARK}">'
        '<rect x="35" y="31" width="30" height="3.4" rx="1"/>'
        '<rect x="35" y="65.6" width="30" height="3.4" rx="1"/>'
        '<path d="M38 35 L62 35 L50 50 L62 65 L38 65 L50 50 Z"/>'
        f'{"".join(sparks)}'
        '</g></svg>'
    )


if __name__ == "__main__":
    svg = build()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg + "\n")
    print(f"[+] wrote {OUT} ({len(svg)} bytes) — redeploy with build_inject.py / seed_ctfd.py")
