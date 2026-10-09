---
card: 156-a2-1
status: current
date: 2026-10-09
---
# Brief 156-a2-1 - P5-2 STEP-1 SCRATCH + adopt as `D1_ring_p5s02a_<ts>.vi` (docs/d1/ring-p5.md PD379); the ONE LabVIEW card; in-between file (NOT counted toward the cap of 6)

This is `tools/bench/cards/brief_155-a3-1.md` + `brief_155-a3-2.md` again (read both, and through them brief_154-a3-3 / 3b: launch, adopt,
final Error List, graph read, `load_by_vi`, invariants, LabVIEW-gone) with ONLY the changes below. The plan this card launches is the
offline output of card 156-a1-1: read `tools/bench/diag_c156_a1_1_facts.md` first (step 1 = actions 1..23 / 17 ops = groups A B C D E F1 F2,
MAIN 672.1, Executor 667.0, EL 45 -> 47 on both elrule totals). The helper scripts to copy are the 155 pair
`tools/bench/diag_c155_a3_1_{inv,peek}.py` and `diag_c155_a3_2_{adopt,elexp,mkgraph,graph,memload,nodes,inv}.py` (-> `diag_c156_a2_1_*`;
names, ids, pins, paths ONLY; say which lines changed). Call shared functions instead of pasting a block you can import
(`docs/script-writing.md`); a block you must copy is an `OPEN:` line with file:line.

## Inputs (md5 pinned in the task; a mismatch is a RETURN)
Plan `plan_ring_p5s02a.json` 4284c22a (60-action all-plan cut at action 23), pred 31d8e9be, licence e8fd6a98, MAIN recipe
`stage_d1_ring_p5s02a.py` b52b9ff5, scratch recipe `_scratch.py` 71c3aed4, adopted P5-1 `claudeDev\D1_ring_p5s01_20261009_124542.vi`
7f2582ae (never edited; the scratch runs on a NEW byte copy), graph 6716c499, memory_model c87d170a, stagexec **25a1494c** (changed by card
156-a1-2: the t3/t4 pass-wire route; the op list of this plan was shown EQUAL before/after, `diag_c156_a1_2_facts.md`), stagesim eb99c6ba,
stagekit aec03c6c, stage_prerun 9decb20f, vigraph a7eb58c7, addrcheck 207beb0d, gscript 1a80236e.

## Deltas against brief_155-a3-1 / 3-2
1. **Pre-checks on the final bytes, FIRST, then launch.** Verify the md5s; re-run dry (expect PASS 1/0, PASS-UNVERIFIED PB), prerun
   (expect PASS 16/0, X10 MAIN 672.1 against the 675 limit, Executor 667.0, X17 PASS, X14 WARN rows 23), `--scratch-required` rc 3 and
   `--check-launch` ALLOW, and quote them. stagexec changed after the cycle-156 prerun records were written: if the launch gate reports a
   stale prerun record for that reason, re-run dry + prerun on the unchanged recipes (running them is not editing them) and quote the new
   lines. A different count / X10 / rc is a RETURN with the facts. The prior-art review is ANSWERED `novel`
   (`archive/peer/2026-10-09-priorart-priorart-c156-a1-1-p5s02a.md:319`); if a gate still refuses, `py tools/gate_fp.py log`, no env bypass,
   RETURN with the refusal text. No recipe, plan, pred, licence, stage-tool or hook edit in this card.
2. **Launch:** ONE scratch under `bgrun --material` on a NEW byte copy of 7f2582ae (file `D1_ring_p5s02a_<stamp>.vi` as the scratch
   recipe names it), ops 1..17 (actions 1..23). E1 real == sim at every checkpoint, and **quote E1 for EACH of the three `move_in` ops**:
   mv_376 op 10 (step_10 9b820f15), mv_3052 op 11 (step_11 b290d35f), mv_3453 op 12 (step_12 24d481f4) from `plan_ring_p5s02a_pred.json`.
   D / TD / PB by position key under vigraph a7eb58c7; licence; X11; peak <= 675 planned / 680 fail / MEMSTOP 695. Record the METERED
   start MB against 597.5 (x10_start of 7f2582ae) and the peak against X10 MAIN 672.1 / Executor 667.0; no recalibration. First LabVIEW
   use of the P5-2 route set (refnum SR on 1.7 plus Dequeue/Release by the `primitive` route, a new Case receiving moved nodes, the 1.7
   counter SR). RETURN at the first result differing from the prediction; no second launch (a retry is a new card). LabVIEW 2026 only, the
   instance the recipes start; no original opened; no motor or camera. The bed stays s09.
3. **Adopt** (structural PASS only): `stagexec.adopt_scratch` by import (PD354(a)). The scratch recipe saves `D1_ring_p5s02a_<stamp>.vi`
   and that IS the adopted name - no rename. Quote path + md5 and the adopt/1 record. A refusal => RETURN with it (file:line).
4. **Final Error List** of the adopted bytes (elrun wrapper; 0 items read = environment fault, not an answer): expected file
   `tools/bench/errorlist_expected_D1_ring_p5s02a_<stamp>.json`. Quote the TOTAL and PER-CLASS counts vs the P5-1 base 45 and vs the pred
   (47 on both elrule totals; per class input 3, not-connected 22, loose-ends 21, two-types 1; `diag_c156_a1_1_facts.md:27`). Non-gating
   (PD354, PD370(a)): another count is REPORTED and the file written from what was read.
5. **Fresh-instance load + graph read:** `tools/bench/graph_ring_p5s02a_<stamp>.json` + md5 + load MB. Quote the rows the NEXT step is built
   on: the new refnum SR on 1.7 (L/R inner/outer terminals, which are wired), the Dequeue and Release nodes and their terminals, the new
   Case (frames, selector, tunnels, which nodes are inside), the 1.7 counter SR, `#376` / `#3052` / `#3453` owners, loop 1.7's condition
   terminal source, and the open terminals. The graph is the base of the step-2 plan.
6. **`memory_model.json`:** ONLY one `load_by_vi` entry for the adopted file's md5 (form of the 155 memload helper). Key-by-key diff quoted
   (before c87d170a); no limit, coefficient, MEMSTOP or X10 value changes.
7. **Invariants** md5 before = after: stagekit aec03c6c, addrcheck 207beb0d, stagexec 25a1494c, stagesim eb99c6ba, gscript 1a80236e,
   vigraph a7eb58c7, stage_prerun 9decb20f, the P5-1 adopted VI 7f2582ae, graph 6716c499, the P5-1a / P5-1b files, the plan / pred / licence /
   recipes above, `docs/d1/ring-p5.md` 742e54c4, every stored P4 recipe/plan/pred, `tools/hooks/**`. Handle counts before/after recorded; no
   byte copy / `_elc_*` left except the adopted file; `tasklist` LabVIEW count 0 at the end (closed AND verified gone).
8. **Concurrent cards:** none. A gate refusing your OWN command text is a false positive: `py tools/gate_fp.py log`.

## Report `tools/bench/diag_c156_a2_1_facts.md` (<= 45 lines)
Pre-check numbers; gate outcomes per op class; E1 for the three move_in ops; metered start/peak vs 597.5 / 672.1 / 667.0; adopted file +
md5 + load MB; EL total + per-class vs 45 / 47; graph json + md5 + the quoted rows; `load_by_vi` diff; invariants; handles; LabVIEW gone.
`OPEN:` line. Facts only. Dispatch a hypothesis peer only if a gate FAILS.
