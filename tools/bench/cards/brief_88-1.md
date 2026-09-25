# Brief 88-1 (cycle 88 judgement) — measurements only

Why: the cycle-start ERRORLIST verdict is MISMATCH (`tools/bench/errorlist_D1_l2_a1_20260925_235224_20260926_002916_reuse.json`).
Cycle 87 (a firefighter) added `isnotconnectedtoanything` and `zerosources` to `tools/errorlist_check.py` WIRE_CLASSES
(:324-330) WITHOUT an answered review; its peer run `tools/bench/peer_c87-errorlist-extras.log` has no BGRUN END. One
item, "Polymorphic terminal cannot accept this data type.", stays unexplained. PD194(a) makes the file the bed only
after the P2 check passes.

## (C) FIRST — the owed review, in the FOREGROUND
`powershell -Command "& 'tools/peer.ps1' -Agent claude -Role hypothesis -TimeoutSec 780 -Slug c87-errorlist-extras -TaskFile tools/bench/peer_task_c87_errorlist_extras.txt"`
(with a review/1 card via -ReviewCard if peer.ps1 requires one). Report the verdict on claims (1), (2) and (3) and its
cheapest discriminating test, citing path:line. Do NOT edit errorlist_check.py on its answer.

## (A) PD194(a) P2 check, read-only, on the bed
- Desk-check first. For each of sr1_L0, sr2_L0, sr3_L0, tun1 and tun2, take the predicted source uid and sink
  (term/owner) from `tools/bench/sim/l2a1/step_*.json`, citing file:line.
- Then read the bed in LabVIEW. Address each sink as a SelectorTunnel OUTER face (owner_class/term_class/objs, as
  `OpTunOuterWire_v1` does).
- Return a 5-row table: sole-source uid · sole sink · source==planned · sink==planned · ordered-pass `Is Broken?`.

## (B) Error List after Remove Bad Wires, on a SCRATCH copy only
1. Make a byte copy `claudeDev\D1_l2a1_scratch_88_<ts>.vi`, run RBW on it, then read its Error List (the
   `lv_errorlist.py` / `errorlist_check.py` route). Never save it.
2. Report the item count by class.
3. For each of these items, say whether it is PRESENT or ABSENT after RBW: the "Polymorphic terminal" item, the 9
   "not connected to anything" items, and the "Less? … right shift register" item.
4. If the existing RBW path reports which wires it deleted, list them with their end terminals (owner uid/class,
   term name).

## Close
The bed md5 is still `51d9b8a3af5b4240cdc2ad193d9b4f41`, the scratch is deleted, and LabVIEW is gone (tasklist).
