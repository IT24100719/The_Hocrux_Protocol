# HX-03 — The Runes of Hogwarts (Cryptography)

Stage 3 of The Horcrux Protocol. A message recovered from the diary is
scrambled with a classical cipher and a themed key.

**Category:** Cryptography · **Points:** 200 · **Flag:** `HORCRUX{...}` (set from `integration.yml`)

## What the player receives
- `dist/ciphertext.txt` — the scrambled message.
- `dist/case_note.txt` — supporting context.

## Skill practiced
Identifying a classical cipher and recovering the plaintext using a key carried
over from the previous stage.

## Files in this stage
- `generate.py` — builds the `dist/` artifacts.

## Rebuild the artifact
```bash
python generate.py   # regenerates dist/ (the seeder also does this on first run)
```
