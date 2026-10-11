# Soundtrack

Drop three looping tracks in **this folder** and the live CTF will play them:

    audio/ambient.mp3      # default — while exploring the board
    audio/tension.mp3      # the Fred temptation (after HX-03)
    audio/finale.mp3       # the endgame / capstone

Then turn it on in `ctfd-theme/horcrux-preview/scenes.json`:

    "audio": {
      "enabled": true,        <-- flip this
      "volume": 0.45,          (0.0–1.0)
      "tracks": {
        "ambient": "/audio/ambient.mp3",
        "tension": "/audio/tension.mp3",
        "finale":  "/audio/finale.mp3"
      }
    }

Apply it:

    docker compose up -d                      # picks up the new /audio mount
    docker compose run --rm seeder            # re-injects the theme with audio enabled

## How it behaves
- A `♪ on / ♪ off` toggle appears bottom-right; the choice is remembered per browser.
- Browsers block autoplay, so music starts on the player's **first click**, not on load.
- Phases cross-fade automatically on the real story events (solve → temptation → finale);
  back on the board it returns to `ambient`.
- Same three files also drive the preview mockup (`horcrux-preview/`), served from
  `horcrux-preview/audio/` — copy them there too if you want sound in the demo.

## Notes
- **.mp3** is safest (universal). `.ogg` / `.m4a` also work if you change the filenames
  in the config. You can point a phase at the same file as another to reuse a track.
- Keep files reasonably small (a 1–3 min loop, ~2–5 MB each) so the page stays light.
- Use music you have the right to use — see the recommendations the build notes list
  (freely-licensed / CC0 ambient sources). Do not ship copyrighted film scores.
- `.mp3`/`.ogg`/`.m4a` here are gitignored (see `.gitignore`); this README is tracked.
