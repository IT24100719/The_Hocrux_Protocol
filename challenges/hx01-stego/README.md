# HX-01 — The Marauder's Map (Steganography)

Stage 1 of The Horcrux Protocol. The player recovers the first fragment, hidden
inside an image rather than in its labels.

**Category:** Steganography · **Points:** 100 · **Flag:** `HORCRUX{...}` (set from `integration.yml`)

## What the player receives
- `dist/marauders_map.png` — the attachment served in CTFd.

## Skill practiced
Looking past the image's metadata into the pixel data (least-significant-bit)
to recover a hidden message.

## Files in this stage
- `generate.py` — builds the distributable `dist/marauders_map.png`.
- `embed.py` — embeds the hidden payload into the base image.
- `solve.py` — reference solution that extracts the fragment.
- `STEGO_HOWTO.md` — author notes on the embedding technique.
- `clue.txt`, `Marauders_Map.png` — source material.

## Rebuild the artifact
```bash
python generate.py   # regenerates dist/ (the seeder also does this on first run)
```
