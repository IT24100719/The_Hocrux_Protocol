#!/usr/bin/env python3
"""Reference solver / validation for HX-01."""
import sys
from PIL import Image
SENTINEL = "::END::"
img = Image.open(sys.argv[1] if len(sys.argv) > 1 else "dist/marauders_map.png")
px = img.load(); w, h = img.size; bits = ""
for y in range(h):
    for x in range(w):
        bits += str(px[x, y][2] & 1)
chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits) - 7, 8)]
text = "".join(chars)
print(text.split(SENTINEL)[0])
