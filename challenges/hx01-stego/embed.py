#!/usr/bin/env python3
"""Blue-channel LSB stego tool — hide a message in ANY image, output a PNG.

    python embed.py <input_image> <output.png> "<secret message>"

- Accepts any image Pillow can open (png/jpg/webp/bmp/...); the OUTPUT is always
  a lossless PNG (required — LSB stego does NOT survive JPEG/lossy WebP).
- Appends the sentinel ::END:: so the decoder knows where the message stops.
- Decode / verify with the bundled solve.py:   python solve.py <output.png>
  (and `zsteg -a <output.png>` also recovers it).

Use ONLY images you created or are licensed to use.
"""
import sys
from PIL import Image

SENTINEL = "::END::"


def embed(in_path, out_path, message):
    if not message.endswith(SENTINEL):
        message += SENTINEL
    img = Image.open(in_path).convert("RGB")
    bits = "".join(f"{b:08b}" for b in message.encode())
    w, h = img.size
    if len(bits) > w * h:
        sys.exit(f"image too small: holds {w*h} bits, need {len(bits)} "
                 f"(use a bigger image or a shorter message)")
    px = img.load(); i = 0
    for y in range(h):
        for x in range(w):
            if i >= len(bits):
                break
            r, g, b = px[x, y]
            px[x, y] = (r, g, (b & ~1) | int(bits[i])); i += 1
        if i >= len(bits):
            break
    img.save(out_path, "PNG")   # lossless
    print(f"[+] embedded {len(message)} chars into {out_path} ({w}x{h}, blue LSB)")


USAGE = ('usage:\n'
         '  python embed.py <input_image> <output.png> "<secret message>"\n'
         '  python embed.py <input_image> <output.png> --from-file <message.txt>\n'
         'Tip: --from-file avoids all shell-quoting headaches (great for\n'
         'multi-line messages, and on Windows PowerShell).')

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 4 and a[2] in ("--from-file", "-f"):
        embed(a[0], a[1], open(a[3], encoding="utf-8").read().rstrip("\n"))
    elif len(a) == 3:
        embed(a[0], a[1], a[2])
    else:
        sys.exit(USAGE)
