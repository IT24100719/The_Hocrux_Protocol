# Spirit-sigils — editable icons

Each fragment's Patronus / spirit-sigil is just one SVG file here. **To change an
icon, replace its file and reload the page. No code, no rebuild.**

| File | Stage | Who | Current art |
|------|-------|-----|-------------|
| `hx01.svg` | HX-01 Steganography | Remus Lupin (Moony) | wolf, howling |
| `hx02.svg` | HX-02 Web | Peter Pettigrew (Wormtail) | rat |
| `hx03.svg` | HX-03 Cryptography | Severus Snape | stag (antlered) |
| `hx04.svg` | HX-04 Forensics | Albus Dumbledore | phoenix |
| `hx05.svg` | HX-05 Networking | Sirius Black (Padfoot) | sitting dog |
| `hx06.svg` | HX-06 Linux / Vault | Bellatrix Lestrange | formless wisp (she never cast a Patronus) |

## How to swap an icon
1. Get any **silhouette SVG** (single colour works best). Good free sources:
   - **game-icons.net** (CC BY 3.0) — huge, built to read small. Download or grab the
     raw file from `github.com/game-icons/icons`.
   - **SVG Repo** (filter **CC0**) or **freesvg.org** (Public Domain) — no attribution.
2. Save it over the matching file, keeping the name (e.g. `hx03.svg`).
3. Reload. That's it.

## What the page does for you (so almost any SVG "just works")
On load the page fetches each file and **sanitizes** it:
- drops a full-size background rectangle if the icon has one (game-icons ship a black
  bg rect — it's removed automatically);
- forces every fill/stroke to `currentColor`, so the icon takes the silver-blue
  Patronus colour and glow in both light and dark mode (anything explicitly
  `fill="none"` is left alone, so line/outline icons keep working);
- strips `width`/`height` so it scales to the node.

So you can drop in a raw game-icons SVG (black square and all) and it still renders
correctly. You do **not** need to pre-process anything.

## Tips
- Prefer **bold, simple silhouettes** — they read at ~44 px on the progress strip.
- `hx03.svg` is a **stag (antlered)** by author's choice. (Note: canonically Snape's
  Patronus is a *doe*; a stag reads as Prongs/James. The hornless doe is kept in
  `_sources/doe.svg` if you ever want to switch back.)
- `hx06.svg` is intentionally **formless** (Bellatrix had no Patronus). If you ever
  give her an animal, a raven/bat suits a dark witch.

## Licensing / credits (keep this accurate if you swap art)
- `hx01`, `hx02`, `hx03`, `hx05` — from **game-icons.net** by **Lorc** and
  **Delapouite**, **CC BY 3.0** (hx03 = "stag-head" by Lorc). Attribution belongs
  in the theme footer/credits.
- `hx04`, `hx06` — **original** silhouettes, no attribution required.
- `_sources/` holds the untouched downloads kept for provenance.
