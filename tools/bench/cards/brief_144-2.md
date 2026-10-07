---
type: brief
status: current
date: 2026-10-07
---
# Brief 144-2 — P4 session 3: ONE scratch → adopt on full PASS (PD336(a), docs/d1/ring-p4b.md:215-229; EL rule PD349)

## Steps
1. **Gates before launch.** Pred `tools/bench/plan_ring_p4_s03v18_pred.json` (e1ff772c, EL **55** by the PD349 rule, X10 676.4 at 596.0) and both
   recipes at their current bytes (main 61b0faf5, scratch fa6423ab) were dry-run and prerun 16/0 by card 144-1
   (`tools/bench/prep_c144_1_facts.md`). If `guard_cycle` / `guard_peer` demands a prior-art review because the recipe bytes changed since the
   cycle-143 NOVEL review (`archive/peer/2026-10-03-priorart-c143-p2-p4s03v18.md`), run `tools/prior_art_review.py` on the s03 recipe
   (only the changed lines + new op kinds are owed); verdict `novel` -> go on; any other verdict is released only by a cited `REFUTED:` / `FIXED:`
   line (CLAUDE.md §5). Cannot release -> RETURN. A false gate refusal goes to `tools/gate_fp.py`, not to an env bypass.
2. **ONE scratch run** of `tools/bench/plan_ring_p4_s03v18.json` (da66a030, 20 actions = v18 ops 59..78) with
   `tools/recipes/stage_d1_ring_p4_s03v18_scratch.py` on a BYTE COPY of `claudeDev\D1_ring_p4s02_20261003_110001.vi`
   (md5 `84cac48781c7c915c8f0d7e8fb079341`, the adopted session-2 file). `--scratch-required` runs in the accepted `--prerun ... --scratch-required`
   form (exit 3 expected: census unpredicted).
3. **Predictions (a miss is a RETURN with the facts, LabVIEW closed, files saved — no diagnose-and-retry):**
   - every op real == simulated; prim gate PASS on every created node; D / TD identity gates PASS (key (uid, owner, name));
   - `new:LRB1.value` / `new:LWB1.value` resolve on the CREATED Locals (card 144-1: both resolve to terminal `BufDiff` in the sim); a refusal
     there is a RETURN (fix = the measured-name rule, PD335(b));
   - peak <= 680 MB (X10 676.4 at 596.0); MEMSTOP 695 not hit;
   - Error List **55** (`errorlist_check` against the pred's EL block); a third value is a RETURN;
   - census: unpredicted by design — write the MEASURED census into `plan_ring_p4_s03v18_pred.json` by a script that cites the log line (PD264(c)).
4. **All PASS => ADOPT** the scratch file as `claudeDev\D1_ring_p4s03_<stamp>.vi` by `stagexec.adopt_scratch` **called by import** from a script
   (the CLI form is refused under `labview: none`, fp-39; `adopted_scratch.jsonl` entry, PD329(a) — no second run on the s02 file); md5
   recorded; full Error List read (`--role final`) + `errorlist_expected_D1_ring_p4s03_<stamp>.json`; then in a FRESH LabVIEW instance: load
   (MB measured) + whole-graph read -> `tools/bench/graph_ring_p4s03_<stamp>.json` with md5.
5. s02 file md5 `84cac487...` and the bed `D1_ring_p3b2b_20261002_130007.vi` (395118775a52bc90073f4449b99f899d) checked unchanged before and
   after. Handle count flat (+-100). LabVIEW closed and verified gone (`tasklist`).

## Never
- open the bed or the s02 file for editing; launch `plan_ring_p4_s02v18.json`, `plan_ring_p4_s02.json`, `plan_ring_p4_rasrest.json` (all done or
  SUPERSEDED); run a second scratch inside this card; edit stage tools (stagexec / stagekit / stagesim / stage_prerun / gscript) — a bench-tool fault
  is a RETURN, gate-fp entry, not a patch;
- save a broken intermediate other than through the adopt path.

## Return
`result/1` with: gate table, peak, EL count (+ any extra/missing item), census written, adopted file + md5, final EL, load MB, graph file + md5,
s02 md5 before/after, handles before/after, `tasklist` after, and a JEV-LADDER row for any failing log. Facts file: `tools/bench/diag_c144_2_facts.md`.
