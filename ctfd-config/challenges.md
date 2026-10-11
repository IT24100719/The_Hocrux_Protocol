# CTFd setup

Flag type: regex  ^HORCRUX\{[A-Za-z0-9_\-]{4,64}\}$  (or exact per stage)

| Order | Challenge | Category | Attach | Prerequisite |
|-------|-----------|----------|--------|--------------|
| 1 | HX-01 Marauder's Map    | Steganography | marauders_map.png        | - |
| 2 | HX-02 Chamber of Secrets| Web           | link to /chamber         | HX-01 |
| 3 | HX-03 Runes of Hogwarts | Crypto        | ciphertext.txt           | HX-02 |
| 4 | HX-04 Restricted Section| Forensics     | restricted_section.zip   | HX-03 |
| 5 | HX-05 Floo Network      | Networking    | floo_network.pcap        | HX-04 |
| 6 | HX-06 Gringotts Vault   | Linux         | target 10.10.20.60       | HX-05 |

Set each "Prerequisite" via challenge Requirements so stages unlock in order.
Add the 3 hints per stage from the report, each with a 5% penalty.
