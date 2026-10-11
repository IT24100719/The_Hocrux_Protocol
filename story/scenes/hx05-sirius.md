# HX-05 — Sirius Black · the Floo Network

> Wraps the networking stage. Filter `floo_network.pcap` with
> `ip.addr == 10.10.20.45 && tcp.port == 4444` (the indicator from HX-04) to
> isolate the one intended TCP stream, then Follow TCP Stream to read the
> payload: vault host **10.10.20.60**, user **vault**, code **GRINGOTTS-472**,
> and the flag (`HORCRUX{fl00_p0wd3r_tr4c3d}` — "floo powder traced"). Handover
> out: the full vault contract → HX-06.
>
> Canon ties: Sirius only ever reached the people he loved through **fire**
> (hunted; caged at Grimmauld Place, where the Weasleys/George stayed in OotP);
> he died through the **Veil in the Department of Mysteries** — George's own
> workplace; and the vault ahead is kept by **Bellatrix**, his cousin and his
> killer (→ sets up "you'll be wrong about her"). Release beat: the man who was
> never free in life goes out at last — as Padfoot, running. Mirrors George's
> arc: *don't spend what you're given waiting to join the dead.*

---

## Cinematic cut (second person — in-theme interstitials)

**[ON UNLOCK — shown when HX-05 opens]**

*A friend waits in the fire,* Dumbledore said. The Floo is a roar of it — a
thousand calls flickering through the flames, chatter and green light and
nonsense — but one call was placed for *you*, and you carry the trace to find it:
the host, the port, the minute it was lit — **10.10.20.45:4444, 23:47:16.** Filter
the fire down to the one conversation that doesn't belong. **Follow it. Read what
comes through the flames.**

**[ON SOLVE — shown when the flag is accepted]**

The noise falls away and a single conversation stands alone, burning steady — a
message pushed through the fire the way the hunted always sent them. A vault at
**10.10.20.60**; a name to wear at the door, **vault**; a code to speak,
**GRINGOTTS-472**; and the fragment, riding the flames — **floo powder traced.**

And a face in the hearth, grinning as though it's been waiting years for the
company: Sirius Black, who never once in his life could reach the people he loved
any way but this.

*"There he is,"* Sirius says. *"Took you long enough. I always did have to shout
through a fireplace to get anyone's attention."*

*"I knew you,"* you say. *"Grimmauld Place. The summer before —"*

*"Before. Everyone's got a* before." *The grin tightens. "I went out through a
curtain in a room just down the hall from where you work now. Never did get a
goodbye out of it. Bit of a theme, me."*

He gives you the road the way he gave everything — fast, reckless, whole. *"The
vault's kept by my cousin. She killed me, since you're asking — family runs warm
like that. But the old man's right, and it galls me to say it: she isn't what she
was."* Then, quieter, the only wholly serious thing he ever says: *"You've gone
grey in a room full of the dead, George. I did that — spent the little I got after
the war waiting to join them. Don't. Whatever's left for you out there — go and
live in it."*

You raise the tool and let him *out* — out, at last, for the first time in a life
that was one cage after another — and he goes not as a man but as a great black
dog, running, the way he never once got to.

---

## Prose cut (third-limited past — companion writeup)

*A friend waits in the fire,* Dumbledore had said, and the Floo, when George
reached it, was nothing but fire — a roar of green light, a thousand calls
flickering through a thousand grates, chatter and gossip and nonsense stacked a
castle deep. But one of them had been placed for him. He carried the trace to find
it the way you carry a name through a crowd: the host, the port, the exact minute
the thing had been lit. He filtered the roar down to the single conversation that
had no business in it, and he followed it into the flames.

The noise fell away, and one call stood alone, burning steady — a message shoved
through the fire the way the hunted had always had to send them, fast and low and
trusting the flames to carry it to someone who loved you enough to be watching.
There was a vault at 10.10.20.60; a name to wear at its door; a code to speak,
*GRINGOTTS-472*; and, riding on top of it all, the fragment: *floo powder traced.*

And a face in the hearth, grinning as if it had been waiting years for someone to
answer — Sirius Black, who had never, in his whole cornered life, been able to
reach the people he loved any way but this.

"There he is." The old recklessness, intact. "Took you long enough. I always did
have to shout through a fireplace to get anybody's attention."

"I knew you," George said, and found it was true and ached. "Grimmauld Place. The
summer before —"

"*Before.*" Sirius's grin thinned. "Everyone's got a before. I went out through a
curtain, you know — a room just down the corridor from the one you haunt now.
Didn't get a goodbye out of it. That's rather been the theme with me." He said it
lightly, the way he said everything that cost him, and George — who passed that
archway most days without letting himself look at it — had nothing to say back.

Then Sirius gave him the road the way he had given everything in his life: all at
once, reckless, holding nothing back. "The vault's kept by my cousin. She killed
me, since you're too polite to ask — the family runs warm like that." The old
bitterness, and under it something stranger. "But Albus is right, and it costs me
to say it. She isn't what she was. None of us are, out here."

And then, because even Sirius Black ran out of jokes eventually, he said the one
serious thing. "You've gone grey in a room full of the dead, George. I know the
look because I wore it. I spent the little time I got after the war waiting for a
chance to go and join the ones I'd lost — and then I got my wish, through a
curtain, and I have regretted it every moment since." He leaned close enough that
the fire warmed George's face. "Whatever's left out there for you — and there is
something; I can see it on you better than you can — go and *live* in it. Don't do
what I did. Promise a dead man that much."

George raised the tool. And he let Sirius out — *out*, for the first time in a
life that had been one cage after another, Azkaban and Grimmauld and the long
hunt and the Veil — and Sirius Black did not leave as a man at all. He left as a
great black dog, already running, ears back and legs stretched and the whole open
dark in front of him, the way he had never once in his life been let to run.
