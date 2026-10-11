#!/usr/bin/env python3
"""HX-03 - Runes of Hogwarts. Vigenere-encrypts a plaintext containing
flag3 + the forensic identifier, key themed on the Chamber clue."""
import yaml
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
CFG = yaml.safe_load((ROOT / "integration.yml").read_text())
FLAG = CFG["flags"]["hx03"]; KEY = CFG["handover"]["cipher_key"]
IDENT = CFG["handover"]["identifier"]
OUT = Path(__file__).parent / "dist"; OUT.mkdir(exist_ok=True)

def vigenere(text, key, dec=False):
    res = []; ki = 0; key = key.upper()
    for ch in text:
        if ch.isalpha():
            base = 65 if ch.isupper() else 97
            k = ord(key[ki % len(key)]) - 65
            if dec: k = -k
            res.append(chr((ord(ch) - base + k) % 26 + base)); ki += 1
        else:
            res.append(ch)
    return "".join(res)

plaintext = (f"The compromised researcher account is {IDENT}. Pull its activity "
             f"from the restricted archive and follow the outbound trail. "
             f"The fragment is {FLAG}")
ct = vigenere(plaintext, KEY)
(OUT / "ciphertext.txt").write_text(ct + "\n")
print(f"[+] wrote {OUT/'ciphertext.txt'}")
print(f"[+] key={KEY}  decrypt check -> {vigenere(ct, KEY, dec=True)[:55]}...")

# --- lore case note (framing only; no key, no plaintext) ---
NOTE = """\
================================================================
  DEPARTMENT OF MYSTERIES - UNSPEAKABLE DIVISION
  CASE FILE: THE HORCRUX PROTOCOL        CLASSIFICATION: UMBRAL
================================================================
 Ref       : DM-HX03-RUNES
 Logged by : G. Weasley, Unspeakable - Time Room
 Re        : Recovered cipher - Chamber research account

 The attached text was pulled from the research account the Chamber keeps
 as its own. It will not read plainly, and it was never meant to.

 We have seen this hand before. The contingency does not invent; it borrows.
 It keeps the victim's own habits, so the message hides inside a pattern the
 victim themselves would have used - not a single shift, then, but a
 repeating key. And the key is a name. This place says it over and over, if
 you are listening.

 Break it and it names the account the directive first wore, and points the
 way on: into the restricted archive, and the trail that leads out of it.
                                                              - G.W.
 ENCLOSED
   ciphertext.txt - recovered from the account, encrypted.
================================================================
"""
(OUT / "case_note.txt").write_text(NOTE)
print(f"[+] wrote {OUT/'case_note.txt'}")

# --- integrity hashes for the distributed masters (design 9.2) ---
import hashlib
sums = "".join(f"{hashlib.sha256((OUT/n).read_bytes()).hexdigest()}  {n}\n"
               for n in ("ciphertext.txt", "case_note.txt"))
(OUT / "SHA256SUMS").write_text(sums, newline="\n")
print(f"[+] wrote {OUT/'SHA256SUMS'}")
