---
card: 168-a1-1
status: current
date: 2026-10-12
---
# Facts 168-a1-1 - BuildArray census before/after RBW, #11261 'appended array' path (OFFLINE, stored graphs only)

Scripts: hash = `tools/bench/prep_c168_hashlib.py` `check(card_path, mode)` (self-test 3/0, `prep_c168_hashlib_selftest.log`, last run;
the log also holds an earlier run of the same self-test whose planted drift cases printed as GATE FAIL lines 12,16 (RESULT 3/0 at :18, last run :37) - the self-test now prints
them as EXPECTED-DRIFT), thin caller `tools/bench/diag_c168_a1_1_hash.py`; census = `tools/bench/diag_c168_a1_1_ba.py` (vigraph.dedupe_rows /
build4 / reach4 / path on the stored json; no new parser). No LabVIEW, no VI opened.

1. Hash before 8/0 (`diag_c168_a1_1_hash_before.log:11`), after 8/0 (`diag_c168_a1_1_hash_after.log:11`): 13 card inputs + 7 VI pins equal.
2. Graph md5s 7815af09 / c55317089 (`diag_c168_a1_1_ba.log:3-4`). Census gates 8/0 (`diag_c168_a1_1_ba.log:19`).
3. BuildArray nodes: 19 in both graphs, same uids (`diag_c168_a1_1_ba.log:5-6`; `p6_buildarray.md:6-32`).
4. Which Build Array has an unwired input: ONLY #11261, before AND after RBW (`diag_c168_a1_1_ba.log:5-6`; json `census.after.with_unwired_input`).
   All inputs wired: the other 18, incl. #2626 (`p6_buildarray.md:10`).
5. #11261 t11270 'array' and t11273 'element': wire 0, source none, in both graphs
   (`graph_ring_p6rbw_20261012_191349.json:terminals[1446],[1447]`; same indices in 7815af09; `diag_c168_a1_1_ba.log:7-8`).
6. #2626 inputs in 7815af09 all sourced: t2832<-#30300 IndexArray, t4160<-#30119 IndexArray, t4165<-#30216 IndexArray, t4168<-#4594 Function
   (`diag_c168_a1_1_ba.log:9`).
7. Terminal types: the graph stores none -> `unread` for every row (`p6_buildarray.md:4`).
8. #11261 sits on Diagram #23166 < WhileLoop #10170 < Diagram #686 (`p6_buildarray.md:15`); the owners table stops at #686, which is a
   frame of FlatSequence #681 (`graph_ring_p6rbw_20261012_191349.json` fs_measured.fs_frames."681").
9. Path, 7815af09: t11267 'appended array' -w25618-> t8323 'Force (pN) vs Extension (nm) ' (#23166 Diagram, term_class ControlTerminal,
   is_source false) (`graph_ring_p5s02e_20261012_173009.json:terminals[1445],[1700]`). vigraph.reach4 from t11267 reaches 1 terminal; t8323 has
   no outgoing edge (wire/sr/fs/local/global) and is the only terminal row with that label (no Local/Global of it) (`p6_buildarray.md:108-110`).
   Class from the graph, per sink and overall: **display-only** (an indicator with no outflow). Limit of the graph: control references /
   Property Nodes bound to the indicator are not modelled by vigraph (vigraph.py:28-31), so outflow through them is not measured.
10. Path, c5531708: t11267 carries no wire (`terminals[1445]` wire_uid 0); reach 0; t8323 also wire 0 (`p6_buildarray.md:111`).
11. Plan citation check: `docs/d1/ring-p4.md:52` names #11608 and #1359 as Force-vs-Extension display feeders, not #11261.
12. Delete prediction (c5531708): wires attached to any #11261 terminal = 0; Wire objects 2066 (2091 in 7815af09, json `graphs.*.wire_objs`);
    expected after deleting #11261: **2066** (`p6_buildarray.md:116`; `diag_c168_a1_1_ba.log:18`).

md5 of outputs:
- tools/bench/prep_c168_hashlib.py e212fa39839fa8be69becd0d36aceb13
- tools/bench/diag_c168_a1_1_hash.py be462cfad108f6802027e719a3b3cdee
- tools/bench/diag_c168_a1_1_ba.py ab1821c68d561085309637891bc3f66f
- tools/bench/p6_buildarray.json 302026dd2e7dbab7324f9dda75d0beea
- tools/bench/p6_buildarray.md 7dba759cef3149475e8ad9bd1d80ffe1
