---
type: fact
status: current
date: 2026-10-02
source: tools/bench/fs_tunnel_naming_table.json (card 131-1, PD270(b))
---

# Crossing tunnel names — every recorded crossing (render of the JSON; the JSON carries every citation)

Faces per created tunnel, chain order from the source: in / out (/ other case frame). `?` = not on disk (the binder never
compares Selector names, `tools/stagexec.py:1000-1030`). FSIT rows (frame-to-frame) are outside the rule.

| run / op | source (owner class, uid) | name | wired | net tunnels | borders | faces measured |
|---|---|---|---|---|---|---|
| 126-6 B1 | SubVI #6897 | current image number | yes | CIN | case, FS | Sel CIN/CIN/CIN · FSOT CIN/CIN |
| 126-6 B2 | Diagram #644 | '' | yes | '' | case, FS | all '' |
| 126-6 B3 | SubVI #23289 | New Image | no | – | For-out, FS-out ×2, While-in, case, FS | For in 'New Image', every other face '' |
| 127-1 A_i | Diagram #644 | '' | yes | '' | case, FS | all '' |
| 127-1 A_bn | SubVI #6897 | CIN | yes | CIN | case, FS | all CIN |
| 126-4 Q1 | Function #27401 | x-y*floor(x/y) | no | – | FS | FSOT '' |
| 126-4 Q3 | Function #27401 | x-y*floor(x/y) | yes | '' | FS | FSOT '' |
| 129-4 pin2 op 27/29/31 | Function #27401 | x-y*floor(x/y) | no/yes/yes | –/''/'' | FS | FSOT '' |
| 129-4 pin2 op 33 | SubVI #6897 | CIN | yes | CIN | case, FS | Sel ? · FSOT CIN |
| 130-6 pin3 op 20/22 | Function #27401 | x-y*floor(x/y) | no/yes | –/'' | FS | FSOT '' |
| 130-6 pin3 op 24 | SubVI #6897 | CIN | yes | CIN | case, FS | Sel ? · FSOT CIN |
| 130-6 pin3 op 26 | SubVI #6865 | Image Out | yes (w3040, no other terminal) | none | case, FS | Sel ? · FSOT Image Out |
| 126-4 W1, pin2 op 23, pin3 op 16 | (FSIT, frame to frame) | | | | | outside the rule |

Rule fitted (stagesim `_cross_tunnel_name`, self-test G78/G79 and `selftest_stagesim_tunnel_naming.py`): the name is the
SOURCE terminal's name when its owner is a SubVI ('' for a primitive Function); a wired source names every face, an unwired
source only the face it feeds. The 129-7 rule (copy the net's existing tunnel names) failed pin3 op 26 because w3040 had no
tunnel. Equally consistent with the rows: "an indexing For exit drops the name" instead of "unwired names only the first
face" — no recorded row separates the two.
