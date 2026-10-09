---
card: 154-a3-2
status: current
date: 2026-10-09
---
# Brief 154-a3-2 - P5-1 PLAN MADE (not run) on the real s09 graph, form S; OFFLINE (docs/d1/ring-p5.md PD374(a)(c)(e)(f), PD375, PD376); LabVIEW 0

Why: card 154-a3-1 chose form S (`p5_route_census.md` `CHOSEN: S`, 10 S rows + the unchanged rows compile to 22 ops, no GAP) and registered the four DonorQueue_v0 uids for X17 (`stage_prerun.py` 9decb20f). This card writes the P5-1 plan, pred, licence and the two recipes, replays it in the simulator and runs dry + prerun. The next card (LabVIEW) launches it ONCE on a byte copy of s09. NOT launched here: no `--launch`.

## Read first (nothing else)
`docs/d1/ring-p5.md` PD374(a)(c)(e)(f), PD375, PD376; `tools/bench/diag_c154_a3_1_facts.md`; `tools/bench/p5_route_census.md` section "Card 154-a3-1"; the census script `tools/bench/diag_c154_a3_1_census.py` (its action lists A0 + S_REF ARE the P5-1 content: copy the actions out, do not retype uids or terminal names); `tools/bench/donor_queue_v0.json`; the s09 recipes (`tools/recipes/stage_d1_ring_p4_s09v18.py`, `_scratch.py`) and the s09 pred/licence (`plan_ring_p4_s09v18_pred.json`, `_licence.json`) as the copy sources for the shape of recipe, pred and licence; `tools/bench/plan_ring_p3a_make_v3b.py` for how a hand-built plan with `primitive` creates is written.

## Content of the plan (P5-1 = PD374(e) row 1 with PD376(a), base = REAL s09 graph `tools/bench/graph_ring_p4s09_20261009_062044.json` 22f967b5, VI `claudeDev\D1_ring_p4s09_20261009_060515.vi` eb1d0f31, never opened)
1. On 686 (frame 8): 1-D DBL constant (DonorQueue_v0 #52) + Obtain Queue (#108) by the `primitive` route; const -> 'element data type'.
2. NEW shift register on loop 1.2 `#10170` (body #23166): Obtain 'queue out' -> its LEFT outer terminal; L.inner -> case tunnel in -> Enqueue 'queue'; Enqueue 'queue out' -> case tunnel out -> R.inner; the False frame passes the refnum through; R.outer left unwired (P5-2).
3. NEW Case in body #23166 selected by RingSeqCheck #29724 'valid' t29900; True frame: Enqueue Element (#44) with `#2626` t2813 -> case tunnel -> 'element'; the enqueue-count shift register (I32, init 0, +1 in the True frame; False frame passes through).
4. `records final (1.2 to 1.7)` I32 indicator with -1 written on `#4866` (PD240(b) pattern); after loop 1.2 exits, a LOCAL write of the count SR's final value to it on 686 (ordered by the data dependency on 1.2's exit).
Error terminals of the queue nodes stay unwired. Rule 1a: nothing of the per-bead computation, `#2626`, `#376` or loop 1.1 / the ring is touched.

## Steps
1. **Plan maker:** a script `tools/bench/prep_c154_a3_2_mk.py` writes `tools/bench/plan_ring_p5s01.json` from the census action lists (A0 + S_REF; name every changed action versus the census and why). Count the actions: **<= 40** and the metered X10 **<= 680** (MEMSTOP 695 unchanged). Either bound exceeded: RETURN with the numbers (the cut is a judgement; do not cut).
2. **Replay** by stagesim, pass A AND REALSIM on the s09 graph 22f967b5: every op replays to its end, **0 PROVISIONAL steps**. Quote the step files and the per-op result. A refusal: RETURN with it verbatim (file:line), the op, the rows involved. No stagesim / stagexec / stagekit edit.
3. **Pred** `plan_ring_p5s01_pred.json` under `vigraph.py` a7eb58c7: E1 graph == sim for every op; D / TD / PB on POSITION keys (T6); Error List predicted per class with BOTH elrule totals (carry and no-carry), neither gating (PD370(a)); base EL = s09's expected file `tools/bench/errorlist_expected_D1_ring_p4s09_20261009_060515.json` (quote its total).
4. **Licence** `plan_ring_p5s01_licence.json` by script (PD365(d)); sink gate by census (zero allowed, as s09); X11 `--buildarray-check` if the plan has a Build Array (quote n/a otherwise).
5. **Recipes** `tools/recipes/stage_d1_ring_p5s01.py` + `_scratch.py` (copies of the s09 pair; names, pins, plan path, base VI path/md5, output name `D1_ring_p5s01_<ts>.vi` ONLY; list the changed lines). Row content comes only from the plan file.
6. **Dry + prerun** on the FINAL bytes of plan + both recipes: expected PASS for both; quote counts, X10 (Executor / MAIN), the START, X17 outcome (the four queue creates pass), X14 `proven:` line, `--scratch-required` rc and `--check-launch` (ALLOW or the refusal text). A refusal that is the gate's false positive on your OWN command text: `py tools/gate_fp.py log`, never an env bypass, RETURN with it.
7. **Prior-art review (new structure class: queue primitives, Case on 'valid', SR through case tunnels).** Run `py tools/prior_art_review.py` for this plan; quote the verdict. `novel` or an ANSWERED review whose findings you answer with `REFUTED:` / `FIXED:` lines in the review file as the gate requires. A verdict you cannot release by those rules: RETURN with the review path. Do not edit the plan to chase a finding without saying so in OPEN (a changed plan re-owes steps 2-6).
8. **Invariants md5 before = after:** stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, stagesim 78b8d5a1, gscript 1a80236e, vigraph a7eb58c7, stage_prerun 9decb20f, memory_model 6f2b5687, DonorQueue_v0.vi 81dba822, donor_queue_v0.json 15269b6c, s09 VI eb1d0f31 (never opened), graph 22f967b5, the s09 plan/pred/licence/recipes (9d622c95, 85dbb0ba, 6d003b8d, 4be3ff28, b1f6a87c), `docs/d1/ring-p5.md` 9c5ba571, every stored P4 recipe/plan/pred, `tools/hooks/**`. No LabVIEW process before or after (`tasklist`).

## Return conditions
Actions > 40 or X10 > 680; a PROVISIONAL step or a simulator refusal; a dry / prerun refusal; a prior-art verdict not releasable; a protected md5 moved; a second failure at the same place.

## Report `tools/bench/diag_c154_a3_2_facts.md` (<= 45 lines)
Action count and groups; replay result per op (pass A + REALSIM, step files, PROVISIONAL count); pred checks and EL totals (both); licence entries; sink-gate / X11; dry / prerun numbers, X10, X17, X14, `--scratch-required` rc, `--check-launch`; prior-art verdict and release lines; file names + md5 of plan, pred, licence, recipes; invariants; `OPEN:` line. Facts only; a result-dependent action is not yours.
