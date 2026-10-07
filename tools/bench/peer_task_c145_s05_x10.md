ATTACK this claim about tools/bench/prep_c145_a2_6_pred.log (script tools/bench/prep_c145_a2_6_pred.py; recipes tools/recipes/stage_d1_ring_p4_s05v18.py and stage_d1_ring_p4_s05v18_scratch.py, not launched).

Observed: "X10 peak 685.4 at start 605.4 <= fail threshold 680.0" fails (rc=1). The provisional s05 plan (card 145-a1-P1,
prep_c145_p1_mk.log) predicted 678.5 at a provisional start of 598.5 MB.

Claim under attack: this is NOT a defect of the memory model or of the plan. The start load rose because the real
session-4 file (D1_ring_p4s04_20261007_215031.vi 95e408ff, adopted cycle 145) measured 605.4 MB on fresh load
(diag_c145_2_graph.log), 6.9 MB above the provisional 598.5; the per-op increments are unchanged, so the peak moves by the
same +6.9. The X10 check worked as designed (it refuses a launch that would exceed the 680 MB cap). The fix is a re-cut of
s05 at op 120 (679.8 MB, per tools/bench/cards/result_145-a2-6.json OPEN), not a change of the model or the limit.

Already ruled out: none measured. Files: tools/bench/memory_model.json, tools/bench/cards/result_145-a2-6.json,
tools/bench/cards/result_145-a1-P1.json, tools/bench/cards/result_145-a2-1.json, docs/d1/ring-p4b.md.
