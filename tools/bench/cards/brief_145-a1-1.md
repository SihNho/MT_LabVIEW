---
type: brief
status: current
date: 2026-10-07
---
# Brief 145-a1-1 — P4 session 4: ONE scratch → adopt on full PASS (docs/d1/ring-p4b.md PD350; EL rule PD349)

## Steps
1. **Inputs unchanged before launch.** Verify md5: plan `tools/bench/plan_ring_p4_s04v18.json` 9ff46b0e, pred `plan_ring_p4_s04v18_pred.json` 90eff870,
   recipes `tools/recipes/stage_d1_ring_p4_s04v18.py` fe3f630c / `_scratch.py` f5e4bdf8, s03 file `claudeDev\D1_ring_p4s03_20261007_202957.vi`
   282301ca, bed `D1_ring_p3b2b_20261002_130007.vi` 395118775a52bc90073f4449b99f899d. Any byte changed => `--dry` + `--prerun` PASS on the
   CURRENT bytes first (accepted form `--prerun ... --scratch-required`, exit 3 expected: census unpredicted).
   If `guard_cycle` / `guard_peer` demands a prior-art review (recipe bytes new since the s03 NOVEL review), run `tools/prior_art_review.py` on the
   s04 recipe (only changed lines + new op kinds owed; s04 adds the first subVI drop `RingPickSlot_v0.vi` / `RingSeqCheck_v0.vi`); `novel` -> go on; any
   other verdict is released only by a cited `REFUTED:` / `FIXED:` line (CLAUDE.md §5). Cannot release -> RETURN. A false gate refusal goes to
   `tools/gate_fp.py`, never an env bypass.
2. **ONE scratch run** of `plan_ring_p4_s04v18.json` (v18 ops 79..97, 23 actions, 19 ops) with `stage_d1_ring_p4_s04v18_scratch.py` on a BYTE COPY of
   the s03 file (282301ca).
3. **Predictions (a miss = RETURN with facts, LabVIEW closed, files saved — no diagnose-and-retry):**
   - every op real == simulated; prim gate PASS on every created node; D / TD identity gates PASS, keyed by (uid, owner, name); W1 While `#16483`
     keyed by (uid, class) (PD350(d));
   - both subVI drops (PS1 op 79 `RingPickSlot_v0.vi`, SQ1 op 88 `RingSeqCheck_v0.vi`) resolve;
   - peak <= 680 MB: X10 says 680.1 at 598.5, the recipe's runtime stop `MEM_STOP_MB` 680 is the guard; **a stop there = RETURN** (pre-decided fix:
     re-cut to ops 79..96, PD350(b)); MEMSTOP 695 not hit;
   - Error List **60** (`errorlist_check` against the pred's EL block); a third value is a RETURN;
   - census: unpredicted by design — write the MEASURED census into `plan_ring_p4_s04v18_pred.json` by a script citing the log line (PD264(c)).
4. **All PASS => ADOPT** by `stagexec.adopt_scratch` **called by import** from a script (the CLI form is refused under `labview: none`, fp-39;
   `adopted_scratch.jsonl` entry, PD329(a) — no second run on the s03 file) as `claudeDev\D1_ring_p4s04_<stamp>.vi`; md5 recorded; full Error List
   read (`--role final`) + `errorlist_expected_D1_ring_p4s04_<stamp>.json`; then in a FRESH LabVIEW instance: load (MB measured) + whole-graph read
   -> `tools/bench/graph_ring_p4s04_<stamp>.json` with md5.
5. **Gate on `diag_c144_2_el.log` rc=1** (a comparison against the superseded s02 expected file; PD350(c)): if a gate holds the launch on it, follow that
   gate's own route (Jev ladder NEXT-ACTION, else ONE hypothesis review citing `tools/bench/diag_c144_2_elexp.log`: extra 0 / missing 0 vs the s03
   expected file). Never a bypass. If no gate holds it, note "n/a".
6. s03 file md5 282301ca and bed 39511877 checked unchanged before and after. Handle count flat (+-100). LabVIEW closed and verified gone (`tasklist`).

## Never
- open the bed or the s03 file for editing; launch any earlier plan (s02v18, s02, rasrest, s03v18 — done/SUPERSEDED); run a second scratch inside
  this card; edit stage tools (stagexec / stagekit / stagesim / stage_prerun / gscript) — a bench-tool fault is a RETURN plus a gate-fp entry;
- save a broken intermediate other than through the adopt path; touch the camera or any motor.

## Return
`result/1` with: gate table, peak, EL count (+ any extra/missing item), census written, adopted file + md5, final EL, load MB, graph file + md5,
s03 md5 before/after, handles before/after, `tasklist` after, JEV-LADDER row for any failing log. Facts file: `tools/bench/diag_c145_1_facts.md`.
