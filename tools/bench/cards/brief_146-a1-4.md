---
type: brief
status: current
date: 2026-10-08
---
# Brief 146-a1-4 — P4 session 5: ONE s05 scratch on a byte copy of 95e408ff -> adopt on full PASS (docs/d1/ring-p4b.md PD329(a), PD352)

Same shape as brief 145-a1-1 (`tools/bench/cards/brief_145-a1-1.md`, read it for the exact route; the s04 scratch it describes reached full PASS 24/0 and
was adopted). s05 = v18 ops 98..114 (21 actions, cut by card 146-a1-3, facts `tools/bench/diag_c146_a1_3_facts.md`, 70640876). Prerun on the new bytes:
MAIN X10 680.0 (margin 0.0), SCRATCH X10 674.9 (margin 5.1), both 16/0; X11 PASS unlicensed (ops 118/119 are in s06). Pred EL = 57 by `tools/elrule.py`, base 58.

## Steps
1. **Inputs unchanged before launch (md5; any difference = RETURN):** plan `tools/bench/plan_ring_p4_s05v18.json` 1fc9b486, pred `_pred.json` 961f30c4,
   `_in.json` 8fe54f01, recipes `tools/recipes/stage_d1_ring_p4_s05v18.py` 23c08932 / `_scratch.py` cd14eb47, `memory_model.json` 559be4cf;
   the s04 adopted file `claudeDev\D1_ring_p4s04_20261007_215031.vi` **95e408ff** (318509 B), s03 `D1_ring_p4s03_20261007_202957.vi` 282301ca,
   bed `D1_ring_p3b2b_20261002_130007.vi` 395118775a52bc90073f4449b99f899d. Re-run `--dry` + `--prerun ... --scratch-required` on the current bytes first
   (expected exit 3, census unpredicted). A gate that demands prior-art or a review: the pattern is PROVEN (s04 passed the same shape) -> `PROVEN-PATTERN`; a false
   refusal goes to `tools/gate_fp.py`, never an env bypass.
2. **ONE scratch run** of `plan_ring_p4_s05v18.json` with `stage_d1_ring_p4_s05v18_scratch.py` on a BYTE COPY of 95e408ff (the original is never opened for
   editing). Record the METERED start (fresh load + op-0 read) and the PEAK in MB.
3. **Predictions (a miss = RETURN with facts, LabVIEW closed, files saved; no diagnose-and-retry):** every op real == simulated; prim gate PASS on every created
   node; D / TD identity gates PASS (keyed by uid, owner, name); peak <= 680 MB (`MEM_STOP_MB` 680; a stop there = RETURN, not a re-cut, the judgement session
   decides); MEMSTOP 695 not hit; Error List **57** by `errorlist_check` against the pred's EL block (a third value = RETURN); census is unpredicted by design ->
   write the MEASURED census into `plan_ring_p4_s05v18_pred.json` by a script citing the log line.
4. **All PASS => ADOPT** by `stagexec.adopt_scratch` called BY IMPORT from a script (the CLI form is refused, fp-39; `adopted_scratch.jsonl` entry) as
   `claudeDev\D1_ring_p4s05_<stamp>.vi`; md5 recorded; full Error List read (`--role final`) + `tools/bench/errorlist_expected_D1_ring_p4s05_<stamp>.json`;
   then in a FRESH LabVIEW instance: load (MB measured) + whole-graph read -> `tools/bench/graph_ring_p4s05_<stamp>.json` with md5. Handle count before/after flat (+-100).
5. **#2626 facts (pass item 5):** from that graph read, the terminal NAMES and TYPES of Build Array #2626 at the end of s05 (all inputs, wired or not, by uid).
   This is the evidence the s06 licence (ops 118/119) will be keyed on.
6. 95e408ff, s03 282301ca, bed 39511877 md5 unchanged before and after. LabVIEW closed and verified gone (`tasklist`).

## Never
Open the bed, s03 or 95e408ff for editing; launch any other plan; run a second scratch inside this card; edit stage tools (stagexec / stagekit / stagesim /
stage_prerun / gscript / elrule) — a tool fault is a RETURN plus a gate-fp entry; save a broken intermediate other than through the adopt path; touch the camera
or any motor; touch s06 files (`plan_ring_p4_s06v18*`, `prep_c146_a1_5*`).

## Return
`result/1` with: gate table, metered start and peak MB, EL count (+ any extra/missing item), census written, adopted file + md5, final EL, load MB, graph file + md5,
the #2626 table, protected md5 before/after, handles before/after, `tasklist` after. Facts file `tools/bench/diag_c146_a1_4_facts.md`.
