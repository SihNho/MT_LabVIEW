---
type: facts
status: current
date: 2026-10-09
card: 154-a3-3
---
# Card 154-a3-3 facts: BLOCKED before the launch. guard_cycle refused the P5-1a scratch (fp-75); string fix + prior-art + dry/prerun all PASS; LabVIEW never opened
## Step 1, string fix (Edit tool, MAIN recipe only; the scratch recipe does not carry the strings)
- `tools/recipes/stage_d1_ring_p5s01a.py:173` "session 8's in-between file" -> "P5-1a's in-between file"; `:191` "P4 (v18 session 8)" -> "P5 (P5-1a)".
- MAIN md5 f3cbe6a0 -> aee20128 (`diag_c154_a3_3_inv_before.log`); scratch unchanged 3b02d9a7.
- Re-run: dry MAIN 1/0 (`diag_c154_a3_3_dry.log`), scratch 1/0 (`_scr_dry.log`); prerun MAIN 16/0, X10 677.3, Executor 672.2, X17 PASS, X14 WARN rows 20 / 15
  (`_prerun.log`); prerun scratch 16/0, X10 672.2 (`_scr_prerun.log`); `--scratch-required` rc 3, CENSUS-UNPREDICTED rows 1..20 (`_scrreq.log:3`);
  `--check-launch` scratch ALLOW rc 0 (`_checklaunch.log`). All == diag_c154_a3_2b_facts.md.
## Step 2, prior art
- After the edit the stop-record gate (tools/stop_record.py:765-771) refused even an md5sum of the recipe: novel record released for sha d4c0528daf2e, disk e95b32c0e743.
- `tools/priorart_diff.py` finds no approved sibling for this file name -> `--diff-from` unavailable; ran a full `prior_art_review.py` with a plan naming only the two lines
  (`diag_c154_a3_3_priorart_plan.md`). ANSWERED `PRIOR-ART: novel` in 24 s, novel record written for e95b32c0e743
  (`archive/peer/2026-10-09-priorart-priorart-c154-a3-3-p5s01a-strings.md:293`; disposition written under "What was done with it").
## Step 3, launch: REFUSED, not run
- `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c154_p5s01a_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s01a_scratch.py`
  -> guard_cycle: "DUE inference-over-measurement: 33 occurrences (threshold 3) ... newest 2026-10-09-retrospective-cycle152.md".
- The decision exists: `docs/violation-decisions.md:1992` "## inference-over-measurement — 2026-10-09 07:0x" with `DECISION: device` (:1998).
  `tools/violations.py:94` DEC_RE needs HH:MM digits; "07:0x" gives stamp "2026-10-09 00:00" (:100), equal to the retro's filename stamp (:119), and the
  discharge needs it strictly greater (:206). So the slug stays DUE. Logged `fp-75` (gate guard_cycle) in tools/bench/gate_fp_queue.jsonl.
- guard_cycle has no gate-fp release (no gate_fp reference in tools/hooks/guard_cycle.py); `docs/violation-decisions.md` is outside this card's write globs.
  No other command form starts a recipe build. Steps 4-7 (adopt, EL, graph, load_by_vi) not reached; memory_model.json unchanged 6f2b5687.
## Invariants / LabVIEW
- `diag_c154_a3_3_inv_after.log` 39/0: every step-8 pin + card input unchanged (MAIN recipe == its 'before' record aee20128); 153 P4 recipe/plan + tools/hooks
  files unchanged vs snapshot (material_marker.log excluded, hook-written); no _elc_/scratch_c154_ left; claudeDev holds only D1_ring_p4s09_20261009_060515.vi
  of p4s09/p5s01a. LabVIEW never started: tasklist count 0 before and after. Handles: not read (no LabVIEW instance).
OPEN: fixing the decision heading "07:0x" -> a real HH:MM (docs/violation-decisions.md:1992) is a judgement/doc edit; after it the launch is re-issued unchanged.
