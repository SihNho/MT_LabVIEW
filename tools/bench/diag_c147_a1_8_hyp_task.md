ATTACK this claim about a failed prediction (card 147-a1-8, the ONE RETRY scratch of RING P4 v18 session 6; retry of card 147-a1-4).

Run: tools/recipes/stage_d1_ring_p4_s06v18_scratch.py (imports tools/recipes/stage_d1_ring_p4_s06v18.py, plan tools/bench/plan_ring_p4_s06v18.json,
25 actions / 21 ops, prerun 16/0) on a NEW byte copy of claudeDev\D1_ring_p4s05_20261008_002621.vi (3f9ac26b). Log
tools/bench/diag_c147_p4s06v18_scratch.log, segment from line 341 (lines 1-340 are card 147-a1-4's stopped run). BGRUN END rc=1 (:690), RESULT 16/4 (:683).
Change since 147-a1-4: the build recipe declares ONE sink gate SG on [23166,'Pos within cal image'] for op 21 (card 147-a1-7).

Observation (whole-file line numbers):
  - Ops 1..21 all ran. :620 op 19 delete_wire w23807 err '', node census 688 -> 688.
  - :626 op 20 STALE-ADDRESS on #10975 'array' of #10969 -> retry; :629 readback {'UID': 10969, 'Name': 'array', 'UID 2': 0, 'Is Broken?': False}; :631 err ''.
  - :637-644 op 21: STALE-ADDRESS on t5171; wire_indicators N[26] 'pos in cal image out' -> 'Pos within cal image' raised "target BROKEN after
    wiring" (bed is ExecState 0 by design); DEFERRED to the declared sink gate.
  - :648 SG PASS: indicator t3173 on wire 23807; source t5171 #5058 rows [(5171, 5058, 'pos in cal image out', 23807)] (t5171 on wire 23807 ONLY);
    sources on 23807 == [5171].
  - :649 E1 PASS (every checkpoint graph == simulated step, incl. op 21); :651 FR PASS; PRIM PASS (:588).
  - :652 FAIL D: new wires 15 vs sim 16, lost 7 vs sim 8. Real lost [10166,10187,28684,29006,29766,29787,9000] - w23807 NOT lost. (Dry run of the same
    recipe, tools/bench/diag_c147_a1_8_scr_dry.log, lists the sim's lost set incl. 23807 and 16 new incl. 10000025.)
  - :657 FAIL TD: unwired [(9505, 9503, 'Value')]; identities lost [(2832,2626,'array'), (4160,2626,'array'), (4165,2626,'array'), (9505,9503,'Value'),
    (9508,9503,'Value')], plan_deletes [], recycled_uids [2832,4160,4165,9505,9508].
  - :659 FAIL PB (FATAL, before save): missing open pairs '2626|Terminal|array|0..3'. Work copy not saved, deleted (H4 :668). Input 3f9ac26b unchanged.
  - :655 CENSUS-ALL new by class {IndexArray 1, InnerTerminal 2, Local 1, LoopTunnel 2, OuterTerminal 2, Terminal 4, Wire 12}, lost uids 2.

CLAIM to attack: the three misses (D, TD, PB) are NOT plan-row errors; they are side effects of ops 19-21 on the #5058 'pos in cal image out' net that
the simulator does not model - op 19's delete_wire did not remove w23807 (it is still the net of t5171/t3173 after op 21 and is absent from the real
lost set), op 20's t5171 -> #10975 wire is not on t5171 after op 21, and the #2626 Build Array 'array' terminals (2832/4160/4165, licensed rows in
tools/bench/plan_ring_p4_s06v18_licence.json) and #9503 'Value' terminals were re-created (recycled uids) by an earlier op, which E1 does not see
because it compares graphs in a way that tolerates recycled uids.

Give: the strongest reason the claim is wrong; an alternative explanation (in particular: which op first changed #2626 / #9503, and whether E1 PASS
with D/TD FAIL is itself a gate inconsistency); what would falsify the claim; the cheapest discriminating test (offline from the log / step files
under tools/bench/sim/ring_p4_s06v18/ if possible; a LabVIEW run only if nothing offline separates them). Relevant code: tools/stagexec.py,
tools/stagekit.py (wire_keys, term_identity_gates), tools/gscript.py wire_indicators (:2152-2155), archive/peer/2026-10-08-c147-a1-4-re1.md (the
previous review of the same row).
