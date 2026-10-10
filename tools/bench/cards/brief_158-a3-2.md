---
card: 158-a3-2
status: current
date: 2026-10-10
---
# Brief 158-a3-2 (assignment 158-3) - P5-2 STEP-1 SCRATCH, RETRY of 158-a2-2 under the PD386 gates; adopt as `D1_ring_p5s02a_<ts>.vi`; the ONE LabVIEW card

This is `tools/bench/cards/brief_158-a2-2.md` again (read it, and through it brief_156-a2-1 / 155-a3-1 / 155-a3-2 / 154-a3-3 / 3b: launch, adopt,
final Error List, graph read, `load_by_vi`, invariants, LabVIEW-gone) with ONLY the deltas below. Scratch 158-a2-2 built the planned graph (E1 real == sim
at every checkpoint) and stopped on four gates that judged convention (`tools/bench/diag_c158_a2_3_facts.md`). Card 158-a3-1 (PASS) changed how those
gates JUDGE (PD386, `docs/d1/ring-p5.md` ~313-350) and nothing else: read `tools/bench/diag_c158_a3_1_facts.md` first. This card is a `retry_of` card
(`"retry_of": "stage_d1_ring_p5s02a_scratch.py"`): ONE run. Helper scripts: copy `diag_c158_a2_2_{adopt,inv,checklaunch}.py` and the
`diag_c155_a3_2_*` family to `diag_c158_a3_2_*` (names, ids, pins, paths ONLY; say which lines changed). Call shared functions, do not paste a block you can
import (`docs/script-writing.md`).

## Pins (md5 in the task; a mismatch is a RETURN)
stagekit **07f9e35f**, pred **ed84b5fd**, scratch recipe **64b4f18b** (all changed by 158-a3-1); stagexec 7a712ccb, stagesim eb99c6ba, vigraph a7eb58c7,
stage_prerun 9decb20f, addrcheck 207beb0d, gscript 1a80236e; plan `plan_ring_p5s02a.json` 4284c22a, licence e8fd6a98, MAIN recipe b52b9ff5,
graph 6716c499, memory_model c87d170a, `docs/d1/ring-p5.md` 0f9ac5b0. Adopted P5-1 `claudeDev\D1_ring_p5s01_20261009_124542.vi` 7f2582ae is never edited;
the scratch runs on a NEW byte copy.

## Deltas against brief_158-a2-2
1. **Pre-checks on the NEW bytes, FIRST.** Re-run dry (expect PASS, unverified 0) and prerun (expect 16/0, X10 planned MAIN 674.7 <= 675) for the MAIN and the
   scratch recipe, `--scratch-required` and `--check-launch`; quote the lines (`diag_c158_a3_1_*.log` hold the same runs - a re-run on unchanged bytes is not an
   edit). **Planned MAIN above 675: RETURN with the number, no re-cut, no launch.**
2. **Launch command** exactly as in `tools/bench/prep_c158_a3_1_checklaunch.log` (ALLOW lines): `py tools/bgrun.py --material --max-min 50 --log
   tools/bench/diag_c158_p5s02a_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py`, plus `--retry-card tools/bench/cards/task_158-a3-2.json`
   when the gate asks for it. NO `--unverified-card` and no `DRY-UNVERIFIED-OK` (the dry PB is a real PASS now). The scratch's own log is
   `diag_c158_p5s02a_scratch.log` (NEW name; the old `diag_c156_...` log is not appended to). A gate refusing your own command text is a false positive:
   `py tools/gate_fp.py log`, no env bypass; RETURN with the refusal text.
3. **ONE scratch** under `bgrun --material` on a NEW byte copy of 7f2582ae, ops 1..17. Quote E1 real == sim at every checkpoint (0,1,3,6,8,9,12,15,16,17;
   diff must be 0), the FATE lines of ops 10-12 (mv_376 / mv_3052 / mv_3453), the act of ops 16/17 and the per-op CLASS census line the recipe prints for
   ops 16/17 (OPCENSUS), and the final census against `census_overall` = MEASURED-SCRATCH (CEN2 must PASS, all 13 classes equal).
4. **Gates.** Quote the outcome of PB, D, TD, CEN2, CD, INV, E1, X10 (metered start / peak vs 597.5 / planned). RECORD rows are expected and are quoted
   with their ids (the two #376 tag rows, wire 24091 stub). **Any BLOCK gate FAIL = RETURN with the facts; NO second run in this card and none by anyone
   (the assignment session hands it back).** A FAIL on a RECORD row is a gate bug: RETURN with the row.
5. **Adopt** (structural PASS only), final Error List with total + per class, fresh-instance load + graph json + md5, `load_by_vi` entry (only that entry of
   `memory_model.json`; key-by-key diff quoted), invariants md5 before = after, handles, LabVIEW closed AND verified gone: exactly as brief_158-a2-2
   item 5. The graph is the base of the step-2 plan: quote the rows brief_156-a2-1 item 5 lists. Write the adopted file path + md5 on one line in the facts.
6. **After adoption only: delete the failed copy** `claudeDev\D1_ring_p5s02a_20261009_152721.vi` (md5 cac5236b - verify the md5 first) and its resume record
   (grep `152721` under `tools/bench/`; quote the path). Do not delete before the adopted file is accepted. Do not delete anything else.
7. **Step-2 plan (offline, NOT launched), only after adoption:** read `docs/d1/ring-p5.md` PD379(c) and the P5-2 step list; write the step-2 plan on the
   ADOPTED real graph (new `plan_ring_p5s02b*.json` or the name PD379 gives; do not touch the step-1 plan files), run its dry + prerun, and dispatch
   `prior_art_review.py` once (a PROVEN pattern is exempt - quote `PROVEN-PATTERN` if the log says so). Quote verdicts and md5. If the step-2 plan needs
   a stage-tool change or a judgement, write an `OPEN:` line and stop: the plan is the deliverable of this item, not a launch.
8. **Quote md5 of s09 eb1d0f31, P5-1a 2482fe7b and P5-1 7f2582ae before and after.** No `tools/hooks` edit, no recipe / pred / licence / stage-tool edit
   of the step-1 files, no original opened, no motor or camera. Concurrent cards: none.

## Report `tools/bench/diag_c158_a3_2_facts.md` (<= 45 lines)
Pre-check numbers; gate outcomes per op class; E1 per checkpoint and for ops 10-12; act + OPCENSUS of ops 16/17; CEN2 equality; metered start/peak vs
597.5 / planned; adopted file + md5 + load MB; EL total + per-class; graph json + md5 + the quoted rows; `load_by_vi` diff; invariants; handles; failed copy
+ resume record deleted; LabVIEW gone; step-2 plan path + md5 + dry / prerun / prior-art verdicts. `OPEN:` line. Facts only. Dispatch a hypothesis peer only
if a gate FAILS.
