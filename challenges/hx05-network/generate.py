#!/usr/bin/env python3
"""HX-05 - The Floo Network. Builds floo_network.pcap: realistic background
traffic plus ONE intended TCP conversation to the suspicious host:port that
carries flag5 and the HX-06 contract. Filter in Wireshark with
  ip.addr == <source_ip> && tcp.port == <source_port>  then Follow TCP Stream.
All addresses and payloads are synthetic."""
import yaml, random
from pathlib import Path
from datetime import datetime
from scapy.all import Ether, IP, TCP, UDP, DNS, DNSQR, DNSRR, Raw, wrpcap

ROOT = Path(__file__).resolve().parents[2]
CFG = yaml.safe_load((ROOT / "integration.yml").read_text())
H = CFG["handover"]
FLAG = CFG["flags"]["hx05"]
ATT_IP = H["source_ip"]; ATT_PORT = H["source_port"]
TGT = H["target_host"]; VUSER = H["vault_user"]; CODE = H["investigation_code"]
DATE = H["capture_date"]
OUT = Path(__file__).parent / "dist"; OUT.mkdir(exist_ok=True)
random.seed(4444)

ARCHIVE = "10.10.20.30"          # the beaconing archive host
MAC_A = "02:00:00:00:00:30"; MAC_B = "02:00:00:00:00:45"; MAC_GW = "02:00:00:00:00:01"
t0 = datetime.strptime(f"2026-{DATE[5:]} 23:45:00", "%Y-%m-%d %H:%M:%S").timestamp()
pkts = []

def at(ts, pkt):
    pkt.time = ts
    pkts.append(pkt)

# ---- background noise: DNS lookups + short HTTP sessions to unrelated hosts ----
sites = [("10.10.20.30", "10.10.20.9", "library.hogwarts.lab"),
         ("10.10.20.31", "10.10.20.9", "owlpost.hogwarts.lab"),
         ("10.10.20.32", "10.10.20.9", "greathall.hogwarts.lab")]
ts = t0
for src, dns, host in sites:
    ts += random.uniform(2, 9)
    at(ts, Ether(src=MAC_A, dst=MAC_GW)/IP(src=src, dst=dns)/UDP(sport=random.randint(40000,60000), dport=53)/DNS(rd=1, qd=DNSQR(qname=host)))
    ts += 0.03
    at(ts, Ether(src=MAC_GW, dst=MAC_A)/IP(src=dns, dst=src)/UDP(sport=53, dport=40000)/DNS(qr=1, qd=DNSQR(qname=host), an=DNSRR(rrname=host, rdata="10.10.20.80")))
    # tiny HTTP exchange on port 80
    sp = random.randint(40000, 60000)
    ts += 0.2
    at(ts, Ether(src=MAC_A, dst=MAC_GW)/IP(src=src, dst="10.10.20.80")/TCP(sport=sp, dport=80, flags="S", seq=1000))
    at(ts+0.01, Ether(src=MAC_GW, dst=MAC_A)/IP(src="10.10.20.80", dst=src)/TCP(sport=80, dport=sp, flags="SA", seq=5000, ack=1001))
    at(ts+0.02, Ether(src=MAC_A, dst=MAC_GW)/IP(src=src, dst="10.10.20.80")/TCP(sport=sp, dport=80, flags="A", seq=1001, ack=5001))
    at(ts+0.03, Ether(src=MAC_A, dst=MAC_GW)/IP(src=src, dst="10.10.20.80")/TCP(sport=sp, dport=80, flags="PA", seq=1001, ack=5001)/Raw(load=f"GET /{host.split('.')[0]} HTTP/1.1\r\nHost: {host}\r\n\r\n"))
    at(ts+0.05, Ether(src=MAC_GW, dst=MAC_A)/IP(src="10.10.20.80", dst=src)/TCP(sport=80, dport=sp, flags="PA", seq=5001, ack=1080)/Raw(load="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok"))

# ---- THE intended stream: archive -> attacker:4444 at 23:47:16 ----
msg = (f"FLOO TRANSFER :: next vault host {TGT} :: user {VUSER} :: "
       f"investigation code {CODE} :: fragment {FLAG}\n")
sp = 51472
tb = datetime.strptime(f"2026-{DATE[5:]} 23:47:16", "%Y-%m-%d %H:%M:%S").timestamp()
at(tb,        Ether(src=MAC_A, dst=MAC_B)/IP(src=ARCHIVE, dst=ATT_IP)/TCP(sport=sp, dport=ATT_PORT, flags="S", seq=7000))
at(tb+0.01,   Ether(src=MAC_B, dst=MAC_A)/IP(src=ATT_IP, dst=ARCHIVE)/TCP(sport=ATT_PORT, dport=sp, flags="SA", seq=9000, ack=7001))
at(tb+0.02,   Ether(src=MAC_A, dst=MAC_B)/IP(src=ARCHIVE, dst=ATT_IP)/TCP(sport=sp, dport=ATT_PORT, flags="A", seq=7001, ack=9001))
at(tb+0.05,   Ether(src=MAC_B, dst=MAC_A)/IP(src=ATT_IP, dst=ARCHIVE)/TCP(sport=ATT_PORT, dport=sp, flags="PA", seq=9001, ack=7001)/Raw(load=msg))
at(tb+0.06,   Ether(src=MAC_A, dst=MAC_B)/IP(src=ARCHIVE, dst=ATT_IP)/TCP(sport=sp, dport=ATT_PORT, flags="A", seq=7001, ack=9001+len(msg)))
at(tb+0.10,   Ether(src=MAC_A, dst=MAC_B)/IP(src=ARCHIVE, dst=ATT_IP)/TCP(sport=sp, dport=ATT_PORT, flags="FA", seq=7001, ack=9001+len(msg)))
at(tb+0.11,   Ether(src=MAC_B, dst=MAC_A)/IP(src=ATT_IP, dst=ARCHIVE)/TCP(sport=ATT_PORT, dport=sp, flags="FA", seq=9001+len(msg), ack=7002))

# ---- more trailing noise so the capture doesn't end on the payload ----
ts = tb + 5
for _ in range(6):
    ts += random.uniform(1, 4)
    src = random.choice(["10.10.20.31", "10.10.20.32"])
    at(ts, Ether(src=MAC_A, dst=MAC_GW)/IP(src=src, dst="10.10.20.9")/UDP(sport=random.randint(40000,60000), dport=53)/DNS(rd=1, qd=DNSQR(qname="owlpost.hogwarts.lab")))

pkts.sort(key=lambda p: p.time)
out = OUT / "floo_network.pcap"
wrpcap(str(out), pkts)
print(f"[+] wrote {out}  ({len(pkts)} packets)")
print(f"[+] intended stream: {ARCHIVE} -> {ATT_IP}:{ATT_PORT} @ 23:47:16")
print(f"[+] carries: host {TGT}, user {VUSER}, code {CODE}, flag {FLAG}")

# --- lore case note (framing; no filter, no creds) ---
(OUT / "case_note.txt").write_text(f"""\
================================================================
  DEPARTMENT OF MYSTERIES - UNSPEAKABLE DIVISION
  CASE FILE: THE HORCRUX PROTOCOL        CLASSIFICATION: UMBRAL
================================================================
 Ref       : DM-HX05-FLOO
 Logged by : G. Weasley, Unspeakable - Time Room
 Re        : Floo-network capture  ({DATE})

 Capture lifted from the floo relay the night the archive went still. Most of
 it is ordinary - libraries, owl-post, the great hall - and one conversation
 that belongs to none of them.

 Isolate that one and it carries the directive's next address in plain words:
 a vault, a keeper, and the word that opens it.

 We have followed this from a map, through a diary, out of a cipher and across
 the archive logs. It is gathering itself somewhere deep now - the way a thing
 does when it means to last. Follow it down, and finish this.
                                                              - G.W.
 ENCLOSED
   floo_network.pcap - relay capture, {DATE}.
================================================================
""")
print(f"[+] wrote {OUT/'case_note.txt'}")

# --- integrity hashes for the distributed masters (design 9.2) ---
import hashlib
sums = "".join(f"{hashlib.sha256((OUT/n).read_bytes()).hexdigest()}  {n}\n"
               for n in ("floo_network.pcap", "case_note.txt"))
(OUT / "SHA256SUMS").write_text(sums, newline="\n")
print(f"[+] wrote {OUT/'SHA256SUMS'}")
