# Change the "sealed fragment" seal

The emblem on locked challenge cards. Swap it anytime — no code.

## Use your own image
1. Drop your image in this folder, named `seal.<ext>`:
   - `seal.svg` (preferred — stays crisp at any size), or
   - `seal.png` / `seal.jpg` / `seal.webp` / `seal.gif`
   - **Use art you made or are licensed to use** — not film/franchise/official
     artwork (e.g. the Ministry-of-Magic seal). Keep it **small and roughly
     square**; it renders at ~44 px and is embedded into the theme, so a big
     file bloats every page. ~128×128 or a compact SVG is plenty.
2. Redeploy the theme:

   ```bash
   CTFD_TOKEN=<admin token> python ctfd-theme/horcrux-inject/build_inject.py
   # or, no token needed:
   python tools/seed_ctfd.py
   ```
3. Hard-refresh the board (Ctrl+F5).

`build_inject` picks the first file it finds in the order above: SVG is inlined,
a raster is base64 data-URI'd into an `<img>`. Both are clipped to a circle and
sized to the card, so any square-ish image becomes a round seal.

## Or restyle the built-in seal
The default is an original Department-of-Mysteries / Time-Room hourglass seal.
To recolour or reshape it, edit the `COLORS` (or geometry) at the top of
`tools/gen_seal.py` and run it, then redeploy:

```bash
python tools/gen_seal.py
python tools/seed_ctfd.py
```

> Only `seal.svg` is version-controlled by default. If you drop a raster
> `seal.png`/`.jpg`, remove `seal.svg` (or it wins) and keep your file in the repo
> so a reset reproduces it.
