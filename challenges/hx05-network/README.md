# HX-05 — The Floo Network (Network analysis)

Stage 5 of The Horcrux Protocol. A capture full of ordinary traffic hides one
conversation that does not belong.

**Category:** Networking · **Points:** 300 · **Flag:** `HORCRUX{...}` (set from `integration.yml`)

## What the player receives
- `dist/floo_network.pcap` — the packet capture to analyze.
- `dist/case_note.txt` — supporting context.

## Skill practiced
Filtering a capture, isolating the suspicious stream, and reading what it
carries toward the vault.

## Files in this stage
- `generate.py` — builds the `dist/` artifacts.

## Rebuild the artifact
```bash
python generate.py   # regenerates dist/ (the seeder also does this on first run)
```
