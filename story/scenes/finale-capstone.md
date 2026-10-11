# Finale — The Capstone · Dumbledore, and the Office Again

> **The 7th challenge**, unlocked after HX-06. To *save* Dumbledore, George must
> pass a **reckoning that recombines all six handovers** — which doubles as
> anti-cheat (unanswerable without having walked every stage). This is separate
> from the midpoint Temptation: the Temptation risks the *world*; the Capstone
> decides only **Dumbledore's fate and George's homecoming** (the world is
> already saved by reaching this point).
>
> **Branches:**
> - **PASS (solve the capstone)** → Dumbledore pulled out whole → the Fred reveal
>   (the hooded Unspeakable was Fred; `GRED & FORGE` finally read) → the circular
>   "Office, Again" ending (reveal + C + A + B from bible §8) closing on the
>   opening scene.
> - **FAIL / don't solve** → Dumbledore spends the last of himself to end it —
>   sacrifices this version again; the loop goes **dark**, no office to return to.
>   (The world still saved; George's peace is not.)
>
> **Implementation:** CTFd capstone challenge. Either a multi-input quiz or a
> single composite flag built from the recombined handovers (answers listed
> below). Solving = PASS cinematic. The FAIL cinematic is the finale's state for
> anyone who reaches it but hasn't solved the capstone (the "if you stop here"
> ending) — not a punishment lockout.

---

## The reckoning — capstone answers (for the builder)

Each is a handover the player already recovered; together they gate the good end.

| # | In-story prompt | Answer |
|---|-----------------|--------|
| 1 | The name the diary remembered — the face you wore past the Chamber lock | `triddle` |
| 2 | The key that broke the runes — the name it was all keyed to | `RIDDLE` |
| 3 | The compromised account the archive flagged | `USER-472` |
| 4 | The outbound indicator rebuilt from the logs (host : port @ time) | `10.10.20.45:4444 @ 23:47:16` |
| 5 | The vault the fire named, and the code to open it | `10.10.20.60` / `GRINGOTTS-472` |
| 6 | The six, in the order you met them | Moony · Wormtail · Snape · the Headmaster · Padfoot · Bellatrix |

---

## Cinematic cut (second person — in-theme interstitials)

**[ON ENTER — shown when the capstone unlocks]**

Five carried home. The archive is quiet now; the fire is out; the vault stands
open and empty. Only one shape still fights in the rifts — Dumbledore, and the
last of him: his own wraith, the directive he cut from himself and would hand to
no one else.

You come back for him, the way he asked. He is nearly spent. To pull a soul this
deep against a current this strong, the tool is not enough — you need the whole
road, everything the six of them taught you, braided into one thread strong enough
to hold him. *Prove you walked it. Name what you carried.*

**[THE RECKONING — the capstone]**

Lay the whole investigation down at once: the name the diary remembered
(**triddle**); the key that broke the runes (**RIDDLE**); the account the archive
flagged (**USER-472**); the indicator you rebuilt (**10.10.20.45:4444, 23:47:16**);
the vault the fire named and its code (**10.10.20.60 / GRINGOTTS-472**); and the
six, in the order you met them. Braid them into one, and the thread will reach him.

**[PASS — "The Office, Again"]**

The thread holds. You throw it the length of the war and it *catches*, and you
pull — and Albus Dumbledore comes up out of his own wraith **whole**, the
directive guttering out in your grip like a candle pinched between two fingers. It
is over. The rifts fall quiet. Somewhere a worn place in time begins, at last, to
heal.

A figure has been standing at your shoulder the whole way, you realize — the
hooded Unspeakable who armed you on your first night, who never left. He reaches
up and lowers the hood.

Fred.

The one who lived. The brother from the branch where *you* fell, who built the
mercy you have carried in your pocket through every door. You turn the tool over
with hands that have stopped working properly and finally read what was always on
the back of it — **GRED & FORGE** — and understand you have been holding his hand
since the very first fragment.

*"Look at the* state *of you,"* he says — and it is, simply and finally, *his*
voice, the worst and best sound in any world. *"Twenty-odd years, and you still
can't sleep a night through without me."* Then, because he is still Fred, the rest
is already tumbling out: *"Georgie — you have* got *to see what the Muggles have
been doing. No wands,
no blood, none of it, and they've split the atom, they've put a thinking-engine
the size of a Galleon in every pocket, they flung people at the* moon *and brought
them home again. I read ten years of their physics to build this."* He taps the
tool. *"Magic couldn't manage it alone. Took a dead Muggle's sums about time and a
bit of our sort of nonsense, stitched together with spit."*

*"You built it to reach me,"* you say. You know how his mind runs; you always did.

The grin goes quiet. *"I built it to bring you* back. *Spent years on it. And when
I finally understood it would only ever work the one way — that the dead stay dead,
that the most it could ever do was let the living set them down gently — I nearly
threw it in the Thames."* He shrugs, the old shrug. *"Then I thought: somewhere, in
some version of all this, someone is going to need to say goodbye properly. So I
signed the back of it and sent it where it was needed. Didn't know it would be you.
Glad it was."*

Then Dumbledore — whole, himself, unbearably gentle — steps *into* the old memory
and holds the door of it open for you, the way he once reached out of it to warn
you. Warm light. McGonagall's voice fading down a corridor. And your own Fred
beside you — the one you lost, the real and final one — while the living one
stands at your shoulder. You cannot have the brother back. You are no longer alone
in the losing.

You say the thing you never got to say. You trade the word one last time —
*"Gred." "Forge."* — and the prank McGonagall cut short all those years ago
finally lands, Peeves and all, the laugh the two of you never got to finish.

And then you close the loop yourself — gently, choosing it, the way it was once
forced shut to keep you safe. Fawkes lifts from the chair-back and wings home into
the memory, to his own time. The last thing you see is the office, warm and still:
the scene you began in — now a place you can finally leave.

**[FAIL — the dark loop]**

The thread frays. You reach the length of the war and come up short — a name
misremembered, a road half-walked — and there is not enough of it to hold him.

Dumbledore looks at you, and there is no blame in it, only the old tired kindness.
*"It is all right, George,"* he says. *"There is one thing left that a man who
cannot be saved can still do."* And he does it — turns on his own last wraith and
spends everything he is to snuff it, the warning-giver giving the final thing he
has. The directive dies with him. The world is saved.

He does not come home. The rifts close over nothing. And the loop you have lived
in for years goes **dark** — no office, no warm light, no Fred laughing in a
doorway. You saved everyone except the two you came here hoping to keep. It is a
good ending. It is not *yours.*

---

## Prose cut (third-limited past — companion writeup)

Five carried home, and the Network had gone quiet around him. The archive was
still; the fire was out; the vault stood open and emptied of everything but dust.
Only one shape still moved in the rifts — Dumbledore, and the last of him, his own
wraith, the one piece of the war he had cut from himself and refused to lay on
anyone else's shoulders. George came back for him, the way he had been asked, and
found him very nearly spent.

To pull a soul out of a current that deep the tool was not enough. He needed the
whole road — the name the diary had kept, the key the runes were cut to, the
account the archive had flagged, the indicator he had rebuilt from a dead man's
logs, the vault and its code that the fire had carried, and the six in the order he
had met them — all of it, braided into a single thread with enough of his
whole journey in it to reach the bottom of the war and hold.

He laid it all down at once. And the thread caught.

He threw it the length of everything and it held, and he pulled, and Albus
Dumbledore came up out of his own wraith *whole* — the directive guttering out in
George's grip like a candle pinched between finger and thumb. The rifts fell
silent. Somewhere a worn place in the world began, at long last, to knit.

There had been a figure at his shoulder the whole way, George realized now; there
had been, if he was honest, since the beginning — the hooded Unspeakable who had
pressed the tool into his hands on the first night and asked for nothing and never
gone away. The figure reached up and put back the hood.

It was Fred.

Not the voice in the rift. Not the thing that had worn him at the midpoint. Fred —
the one who had lived, in the branch where it had been George who fell, who had
built the whole aching mercy George had carried in his pocket through six doors
and had never once understood. George turned the tool over with hands that had
stopped obeying him and read, finally, the two words that had been on the back of
it the entire time: *Gred & Forge.* He had been holding his brother's hand since
the Marauder's Map.

"Look at the state of you," Fred said — and it was, simply and finally, his voice,
the worst and best sound in any world. "Twenty-odd years, and you still can't sleep
a night through without me." And George laughed in the way that is indistinguishable
from the other thing.

And then, because he was still Fred, the rest of it came out in a flood. "Georgie,
you have no idea what the Muggles have been doing while we've all been waving
sticks about. No magic in them at all and they've split the atom — the *atom*,
George — they've got a thinking-engine the size of a Galleon in every pocket in
Britain, they flung a handful of people at the moon and had the nerve to bring
them *back.*" He rapped a knuckle against the tool. "I read ten years of their
physics to build this. Magic couldn't do it on its own — too proud, our sort, to
ask time nicely. Took a dead Muggle's arithmetic about clocks and a bit of proper
nonsense from our side, stitched together with spit and stubbornness."

"You built it to reach me," George said. He knew how his brother's mind ran; he
always had.

The grin went quiet, which on Fred was louder than shouting. "I built it to bring
you *back.* Spent years on it. Learned more dead men's equations than I'll ever
admit to. And when I finally understood the cursed thing would only ever work the
one way — that the dead stay dead, that the most it could manage was to let the
living set them down gently — I very nearly threw it in the Thames." He shrugged,
the old shrug, the one that had always meant *and here we are.* "Then I thought:
somewhere, in some version of all this, there's a poor sod who's going to need to
say a proper goodbye. So I signed the back of it, the way we signed everything,
and I sent it where it was needed. Didn't know it would end up in your hands. I'm
glad past saying that it did."

Then Dumbledore — whole, and himself, and unbearably gentle — stepped *into* the
old memory and held the door of it open, the way he had once reached out of it to
push George clear of what was coming. There was the warm light. There was
McGonagall's voice, trailing off down some corridor that had been dust for twenty
years. And there, beside him, was his own Fred — the one he had lost, the true and
final one — while the living one stood at his shoulder and let him have the moment
whole. He could not have the brother back. He understood that now in a way the
whole war had been teaching him. He was simply, for the first time, not alone in
the losing of him.

He said the thing he had never got to say. They traded the word one last time —
*Gred, Forge* — and the prank McGonagall had hauled them off before they could
enjoy finally, gloriously landed, Peeves cackling somewhere in the rafters, the
laugh the two of them had been owed and never paid.

And then George closed the loop himself. Gently. Choosing it, this time, the way
it had once been forced shut to keep him safe. Fawkes lifted from the back of the
chair and winged home into the memory, to his own time at last. And the final
thing George saw before he let it go was the office — warm, and still, and exactly
as it had been on the first page of all this — a place he could, at the very end,
walk out of on his own two feet.

---

### Alternate ending — if the reckoning fails

The thread frayed. He threw it the length of the war and came up short — a name
misremembered, a stretch of the road half-walked — and there was not enough of his
journey in it to hold the old man against the current.

Dumbledore looked at him, and there was no blame in it anywhere, only the tired
kindness George had known since he was eleven. "It is all right, George," he said.
"There is one thing left that even a man who cannot be saved may still do." And he
did it: he turned on the last of his own wraith and spent every remaining particle
of himself to put it out — the warning-giver giving the final thing he had to
give. The directive died with him. The world went on.

He did not come home. The rifts closed over nothing at all. And the loop George
had lived inside for years went dark — no office, no warm light, no brother
laughing in a doorway — because the one who had held it open had used the last of
himself to end a war instead.

George Weasley saved everyone except the two he had come to the end of the world
hoping to keep. It was a good ending, and a just one, and he would spend the rest
of his life knowing it was not the one he had been reaching for.
