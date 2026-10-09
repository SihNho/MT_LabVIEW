---
card: 154-a3-2b
status: current
date: 2026-10-09
---
# Brief 154-a3-2b - RETRY of 154-a3-2: P5-1 is CUT at the longest prefix that fits X10 <= 680 (docs/d1/ring-p5.md PD374(e)); the plan maker's cut; OFFLINE, LabVIEW 0

Why: card 154-a3-2 replayed the whole form-S fragment clean (32 actions = 22 ops, pass A and REALSIM, 0 PROVISIONAL) but X10 MAIN = 701.0 > 680 (`diag_c154_a3_2_facts.md`, `prep_c154_a3_2_mk.log:164-165`; prefixes: ops 1..14 = 677.3, 1..15 = 681.2). PD374(e) says: "If the plan maker cuts a step above 40 actions or above X10 680, the cut point is the plan maker's, inside the same order, and each extra cut is one more in-between file." This card makes that cut. The first brief said "do not cut"; that sentence is withdrawn for this card ONLY.

This is `tools/bench/cards/brief_154-a3-2.md` again (read it first, then `diag_c154_a3_2_facts.md` and `prep_c154_a3_2_mk.py`, the maker that already works: copy it) with ONLY the changes below.

## Changes against brief_154-a3-2.md
1. **The piece is called P5-1a.** Plan `tools/bench/plan_ring_p5s01a.json`, pred `_pred.json`, licence `_licence.json`, recipes `tools/recipes/stage_d1_ring_p5s01a.py` + `_scratch.py`, sim dir `tools/bench/sim/ring_p5s01a/**`, maker `prep_c154_a3_2b_mk.py` (copy of `prep_c154_a3_2_mk.py`; list the changed lines), saved-file name `D1_ring_p5s01a_<ts>.vi`. The files of card 154-a3-2 (`plan_ring_p5s01*.json`, `prep_c154_a3_2_*`) are NOT overwritten and stay the record of the whole fragment.
2. **The cut (the only decision here, by a rule, not a feeling):** P5-1a = the LONGEST prefix of the 22 compiled ops, taken in the same order, whose X10 MAIN is <= 680.0 by `stage_prerun.x10_start` + the same formula (expected: ops 1..14, 677.3, ending with the count-SR R2 group). Map ops back to ACTIONS: the prefix must end on an action boundary, and the action list for the prefix is the first k actions of the whole fragment (quote k and the op count). A prefix that cannot be formed that way: RETURN with the numbers. P5-1a must also keep <= 40 actions.
3. **The remainder is written down, not planned:** in the facts file list the actions NOT in P5-1a (their ids, the census rows they carry, their op numbers), and the open rows P5-1a leaves at its END (the TIE list of the prefix replay: every end row that P5-1a makes, with owner and terminal), so the next plan (P5-1b, on the real P5-1a graph) can start from them. No plan for the remainder is written now - it needs the real graph.
4. **Everything else unchanged:** pass A AND REALSIM on the s09 graph 22f967b5 over the PREFIX, 0 PROVISIONAL, step files quoted; pred under vigraph a7eb58c7 (E1; D/TD/PB by position key; EL per class, both elrule totals, non-gating; base EL = s09's expected file, quote its total); licence by script; sink gate; X11 if there is a Build Array; recipes (copies of the s09 pair, names, pins, plan path, base VI path/md5, output name ONLY); dry + prerun PASS on final bytes, X10 / X17 / X14 / `--scratch-required` rc / `--check-launch` quoted; prior-art review of the plan answered, release lines as the gate requires. NOT launched.
5. **Invariants md5 before = after** (as brief_154-a3-2.md step 8; `prep_c154_a3_2_inv.py` is the copy source). No LabVIEW process before or after. No stage-tool or hook edit.

## Return conditions
The longest fitting prefix cannot end on an action boundary; the prefix replay shows a PROVISIONAL step or a refusal; a dry / prerun refusal; a prior-art verdict not releasable; a protected md5 moved; a second failure at the same place.

## Report `tools/bench/diag_c154_a3_2b_facts.md` (<= 45 lines)
The cut (k actions, n ops, X10 MAIN vs 680); remainder action list + the end-row (TIE) list of the prefix; replay result (pass A + REALSIM, PROVISIONAL count); pred checks and EL totals (both); licence; sink gate / X11; dry / prerun numbers, X10, X17, X14, `--scratch-required` rc, `--check-launch`; prior-art verdict + release lines; file names + md5; invariants; `OPEN:` line. Facts only.
