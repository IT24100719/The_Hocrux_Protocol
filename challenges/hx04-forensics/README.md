# HX-04 — The Restricted Section (Forensics)

Stage 4 of The Horcrux Protocol. The player correlates a suspect account across
the logs, reconstructs the outbound indicator, and finds what the metadata never
scrubbed.

**Category:** Forensics · **Points:** 200 · **Flag:** `HORCRUX{...}` (set from `integration.yml`)

## What the player receives
- `dist/restricted_section.zip` — the log bundle and evidence to analyze.

## Skill practiced
Correlating events across multiple logs, pivoting on an account identifier, and
reading leftover file metadata (e.g. EXIF) that a careless actor left behind.

## Files in this stage
- `generate.py` — builds `dist/restricted_section.zip` and its contents.

## Rebuild the artifact
```bash
python generate.py   # regenerates dist/ (the seeder also does this on first run)
```
