# Brief for card 140-2 (judgement cycle 140, PD320(c)(e), `docs/d1/ring-p4.md`) — P4 LabVIEW session 1

Base: plan `tools/bench/plan_ring_p4_v14.json` 22f58271 (+ meta 29f6535b); recipes `tools/recipes/stage_d1_ring_p4s1.py` and
`_scratch.py` as the pattern (step-1 maker `tools/bench/prep_c139_7_s1.py`). Bed `claudeDev\D1_ring_p3b2b_20261002_130007.vi`
395118775a52bc90073f4449b99f899d — byte-copied, never edited, never run.

1. PLAN — `tools/bench/plan_ring_p4_s01.json` = v14 ops 1..16 (`p4_dw_23310` .. `p4_w_b_out`), FINAL, made by the 139-7 maker method
   (step-0 base rows accepted only as declared open rows of `plan_ring_p3b2b.json`, PD318(b); every new end-cdiff row tied to an
   action of this session, PD317(c)). Check: no `of` reference crosses the cut (op 17 `p4_x_i_rab1` is NOT in it).
2. RECIPE `tools/recipes/stage_d1_ring_p4_s01.py` (+ `_scratch.py`), ≤ 120 lines on stagekit: dry PASS, prerun PASS, X10 PASS with
   predicted peak ≤ 675 (PD320 predicts 673.4: start 606.1, N 16, R 11), `--scratch-required` verdict recorded. Predicted Error List
   count at the session end written (139-7 method: base 51 ± named created-sink items).
3. ONE SCRATCH RUN on a bed byte copy (`claudeDev\scratch_c140_2_*`): every op real == simulated, census + Is Broken? per op,
   ExecState read, memory peak recorded; Error List `--count-only --role scratch` vs the prediction; LabVIEW closed and verified gone.
4. LAUNCH GATE (mechanical, no judgement): ONLY IF every scratch gate PASSed AND the Error List count == the prediction, run ONE launch
   in a FRESH LabVIEW instance from the bed, saving the in-between file `claudeDev\D1_ring_p4s01_<timestamp>.vi` (not counted toward the
   6-file cap, user D-2026-10-02-02/-04). Same gates as the scratch; full Error List read of the saved file (`--role final`).
   Any other scratch result ⇒ return BEFORE the launch with the facts.
5. AFTER THE LAUNCH, in a fresh instance: the saved file's load MB (PD301 method) and a whole graph read
   (`tools/bench/graph_ring_p4s01_<ts>.json`, FS-aware reader as in 136-1). LabVIEW closed, verified gone. Scratch file deleted.
6. Facts `tools/bench/diag_c140_2_facts.md` (≤ 40 lines): peaks scratch/launch vs 673.4, EL counts vs prediction, in-between file md5,
   its load MB, graph file md5, route classes now measured. Do not move the STATUS bed key (the bed moves at P4's end).
   If the card passes 60 min before the launch starts, return (the hook refuses a new recipe start) — the launch is then its own card.
