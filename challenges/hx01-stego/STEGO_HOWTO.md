# Swap the HX-01 image yourself (hide a flag in any picture)

Do this whenever you want a different-looking map (or to build a new stego
challenge). Three steps: pick an image, embed the secret, attach it in CTFd.

## 0. Rules that aren't optional
- **Use an image you made or are licensed to use.** Not official/film/web art.
- **Output must be PNG.** LSB stego is destroyed by JPEG and lossy WebP, so the
  deliverable is always a lossless `.png` (the tool enforces this). Your *source*
  image can be any format; the *output* players download must be PNG.

## 1. Embed the secret
From `challenges/hx01-stego/`:

```bash
python embed.py <your_image.(png|jpg|webp|...)> dist/marauders_map.png \
  "HORCRUX{m1sch13f_m4n4g3d}
WEB CLUE: The Chamber portal lives at /chamber on the CTFd host. The diary remembers a researcher named 'triddle'. Log in as that account to reach what it hides."
```

- The message is whatever you want recovered. For HX-01 it's the flag + the web
  clue (above). The tool appends the `::END::` sentinel automatically.
- The image must be big enough: it needs `len(message_bytes) x 8` pixels
  (the HX-01 message ≈ 1600 pixels — any ≥ ~50x50 image is plenty).

## 2. Verify it recovers
```bash
python solve.py dist/marauders_map.png      # prints your message back
# optional, if installed:  zsteg -a dist/marauders_map.png
```
If `solve.py` prints your flag + clue, it's good.

> Prefer to regenerate the built-in original map instead of supplying your own?
> Just run `python generate.py` — it draws an original map and embeds the
> payload from `integration.yml`.

## 3. Attach it in CTFd
**Easiest — admin UI (no token):**
1. Log in as admin → **Admin Panel → Challenges → HX-01 — The Marauder's Map**.
2. Open the **Files** tab.
3. **Delete** the existing `marauders_map.png`, then **Upload** your new PNG.
4. Save. (Download it once as a player to confirm it's the new one.)

**Scripted — API (needs an admin token):** see
`ctfd-theme/horcrux-inject/build_inject.py` for the pattern, or:
```bash
# delete old file, then:
curl -s -H "Authorization: Token <TOKEN>" \
     -F "challenge_id=1" -F "type=challenge" \
     -F "file=@dist/marauders_map.png" \
     http://127.0.0.1:8000/api/v1/files
```

## Same trick for a brand-new stego challenge
`embed.py` works on any image + any message, so you can hide a different flag in
a different picture, then create a new CTFd challenge and attach the PNG the same
way (step 3).
