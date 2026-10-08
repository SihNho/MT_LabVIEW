---
type: brief
status: current
date: 2026-10-08
---
# Brief 147-a1-3 — s06 re-made on the REAL adopted s05 graph: rebase, X10 start, cut, #2626 licence, pred, recipes, dry + prerun — OFFLINE, ALONE (PD353(f), PD354(a))

Cards 147-a1-1 and 147-a1-2 passed (facts `tools/bench/diag_c147_a1_1_facts.md`, `diag_c147_a1_2_facts.md`). Now known:
- s05 is adopted: `claudeDev\D1_ring_p4s05_20261008_002621.vi`, md5 3f9ac26b; real graph `tools/bench/graph_ring_p4s05_20261008_013759.json` (cbeeadf5);
  measured fresh load **606.7 MB**, written to `memory_model.json` `load_by_vi/3f9ac26b…` (now 88eeb037).
- The s06 maker `tools/bench/prep_c147_a1_2_mk.py` (d57fdd4f) allows branch -> connect for a source made in an earlier session (op 116), and compares the s06 sim end
  with v18's. It was run on the PROVISIONAL base (start 623.5, cut ops 115..129). That start is void; this card re-runs on the real graph.
- #2626 on the adopted s05 (`diag_c147_a1_1_t2626.log:8-12`): out 2813 unwired; in 2832 / 4160 / 4165 unwired; in 4168 wired (wire 25283); data type UNREAD.
  Same picture as s04.

## Do
1. Copy the maker to a card-local `tools/bench/prep_c147_a1_3_mk.py` (change only what the real-graph base needs: the base graph path, the start rule, log/session names).
   Rebase s06 on the REAL s05 graph with `stage_prerun.py --rebase` (FALLBACK 0, no hand patch). X10 start = `x10_start(3f9ac26b)` = measured load 606.7 (`load_by_vi`)
   + op-0 read (the one start rule used by pred, maker and prerun; quote the three numbers). Cut = longest group-respecting prefix of v18 ops 115.. whose MAIN-recipe
   prerun X10 <= 680.0 (the prerun's own line decides; do not hand-pick). Report cut, MAIN and scratch X10, margins to 680 and MEMSTOP 695, first op over 680,
   +-5 MB sensitivity. Rerun the end comparison: s06 sim end == v18 sim over the same ops (cdiff 0, else RETURN).
2. #2626 licence per PD352(d): if the cut contains v18 ops 118 / 119 (t4160 / t4165), write the `pb-licence/1` uid-keyed licence file in the form stage_prerun / X11
   expect (read how the 145 / 146 licence files and `stage_prerun.py` X11 are built, do not invent a format), keyed to the adopted-s05 uids from the t2626 log. If 118 / 119
   are not in the cut, X11 must PASS unlicensed; say which session carries them. Do not extend the licence to anything else.
3. Pred EL by `tools/elrule.py` (a5ee7d5c, UNCHANGED) from the adopted s05 EL expected file `tools/bench/errorlist_expected_D1_ring_p4s05_20261008_002621.json`
   (55 items) as the start read. Write `plan_ring_p4_s06v18_pred.json` (follow `prep_c146_a1_2_pred.py`). Report total and per-class.
4. New recipes `tools/recipes/stage_d1_ring_p4_s06v18.py` and `stage_d1_ring_p4_s06v18_scratch.py`, copies of the s05 pair with ONLY the plan / pred / base / licence
   names changed. In the NEW scratch recipe only, make the Error List step ADVISORY (PD354(a)): print `EL-ADVISORY` with total and per-class diff against the pred,
   and return non-zero ONLY when a class appears that is in neither the start read nor the pred, or |total diff| > 3. Every structural gate (E1 real == sim, D new/lost,
   PB, prim, term identity, peak <= limit) stays exactly as in the s05 scratch recipe. Show the diff of the scratch recipe against the s05 scratch recipe by file:line.
5. Dry (sandbox) and prerun of BOTH recipes: 0 FAIL on each. `--scratch-required` on the plain recipe: expected exit 3 (the scratch has not run). Quote each result line.
6. Also exercise the advisory EL step offline (a synthetic read: one case with an unseen class -> non-zero, one with a total diff of 4 -> non-zero, one with diff 2 and
   known classes -> zero). Offline, no LabVIEW.
7. md5 before/after: protected files unchanged — `stagexec.py`, `stagekit.py`, `stagesim.py`, `stage_prerun.py`, `tools/elrule.py`, v18 plan, the whole s05 tree, the adopted
   s05 `.vi`, s04 95e408ff, s03 282301ca, bed 39511877, and `memory_model.json` stays 88eeb037 (this card does NOT write it). No LabVIEW process.

## Never
LabVIEW, camera, motor; a scratch or real launch; editing a stage tool, elrule, v18 or any s05 file; changing a memory_model.json parameter; clearing a refusal by editing
the plan. If a stage tool must change, RETURN with the file:line and the exact refusal.

## Return
`result/1` and the facts file `tools/bench/diag_c147_a1_3_facts.md`: start rule numbers, cut, X10s, margins, licence (or the sessions carrying 118 / 119), pred
total/per-class, scratch-recipe diff, dry / prerun / `--scratch-required` lines, advisory-step test, protected md5 before/after, new file md5s.
