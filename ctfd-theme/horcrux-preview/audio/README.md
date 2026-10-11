# Audio / soundtracks — where to add it

The player is already wired. **To add music: put track files in this `audio/`
folder and (optionally) edit the `"audio"` block in `scenes.json`. No code.**
Nothing is bundled — it's silent until you add files.

## 1. Where the files go
Drop your tracks in this folder. By default the theme looks for:

| File | Plays during |
|------|--------------|
| `audio/ambient.mp3` | the intro, the board, and the rift interludes (the main theme) |
| `audio/tension.mp3` | the Temptation (the rift / "A voice in the fire") |
| `audio/finale.mp3`  | the Finale (reckoning + endings) |

`tension` and `finale` are optional — if a file is missing, that phase just keeps
playing `ambient`. So the minimum is a single `ambient.mp3`.

## 2. Configuration (`scenes.json` → `"audio"`)
```json
"audio": {
  "enabled": true,
  "volume": 0.45,
  "tracks": {
    "ambient": "audio/ambient.mp3",
    "tension": "audio/tension.mp3",
    "finale":  "audio/finale.mp3"
  }
}
```
- `enabled`: `false` hides the ♪ button and plays nothing.
- `volume`: `0`–`1`.
- `tracks`: phase → file path. You can rename files or point anywhere under the
  theme; just keep the paths matching. Add more phases later by adding a key here
  and calling `audioPhase("yourkey")` in the engine.

## 3. How playback behaves
- **Autoplay:** browsers block audio until the user interacts, so the theme starts
  music on the **first click/tap**. The **♪ on / ♪ off** button (top-right, next to
  the light/dark toggle) toggles mute, and the choice is remembered.
- **Looping:** every track loops automatically — use seamless loops for `ambient`.
- Phase switches are automatic: board → `ambient`, Temptation → `tension`,
  Finale → `finale`, then back to `ambient`.

## 4. Formats & size
- Use **`.mp3`** (widest browser support) or `.ogg`. Keep them modest (a few MB);
  a short, well-looped ambient bed beats a huge file.

## 5. Where to get music (legal)
Use **royalty-free / CC0** music, or tracks you've licensed:
- **Pixabay Music** (royalty-free, no attribution)
- **Free Music Archive** (filter to CC)
- **Incompetech / Kevin MacLeod** (CC-BY — credit required)
- **OpenGameArt** (filter CC0)

**Do not use the Harry Potter film score** (Hedwig's Theme, etc.) — it's
copyrighted. Pick royalty-free/CC0 atmospheric tracks, or music you own the rights
to. For CC-BY tracks, keep the attribution in the theme credits.
