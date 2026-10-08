---
card: 150-a2-3
status: current
date: 2026-10-08
---
# Brief 150-a2-3 - s07 prepared on the REAL s06 graph: rebase, X10, pred, recipes, licence, dry + prerun; offline, NOT launched (PD365(d))

Plan of record `docs/d1/ring-p4c.md` PD365(d) (lines 284-290) and PD364(c). Read first: `tools/bench/diag_c150_a1_1_facts.md` (the 30-action cut, start 599.7,
MAIN 678.8), `tools/bench/diag_c150_a2_2_facts.md` (the fixed `rebind`; stage_prerun is now 6208b7b7 - do NOT edit it), `tools/bench/cards/brief_149-a3-4.md`
(the rebase/dry/prerun form) and `brief_148-a3-3.md` / `brief_150-a1-1.md` (how the pred and recipes are regenerated). Offline: no LabVIEW, camera or motor.

## Steps
1. **Rebase** `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s07v18.json --graph tools/bench/graph_ring_p4s06_20261008_192149.json`
   (under bgrun if the hook asks). Quote rc, the REBIND / RENAMED-OLD / FLIPPED-OLD lines, plan md5 before (10a4f59a) / after. Expected: PASS now.
   If it is refused again, quote the refusal verbatim with file:line and RETURN (no stage-tool edit).
2. **X10 after the rebase** (the rebased plan, start from the measured load). Need MAIN <= 680. If it is over, cut to the longest prefix <= 680 (no re-plan, no
   split of an action group); quote range, count, X10, margins, first op over 680.
3. **Regenerate** `plan_ring_p4_s07v18_pred.json` (EL base = s06's measured 51 items) and the MAIN + scratch recipes `tools/recipes/stage_d1_ring_p4_s07v18.py` /
   `_scratch.py` for the (rebased, possibly cut) action list: base/start/cut/pred only - copy the working pattern of the s06 pair and the 148/150 makers; no new op kind.
   Run X11 (the `p4_rbB_sel_t4168` row on #2626, op 150, if it is in the cut) and quote the result.
4. **Licence by script**: write `tools/bench/plan_ring_p4_s07v18_licence.json` (pb-licence/1, same form as `plan_ring_p4_s06v18_licence.json` 7f70bbf9) FROM the rebased
   plan, never typed: `rename_by_uid` for #2626 only if X11 flags op 150; `renames` = every BASE sink terminal (uid, owner) that an s07 connect row wires, `from`/`to`
   unset (= any name; `tools/stagekit.py:1412-1421` reads it). State how many entries and which owners.
5. **Dry + prerun** on the FINAL bytes of both recipes and the plan; `--scratch-required` quoted (expected exit 3 per the s06 pattern). Quote X10 lines for MAIN and
   scratch and the margins to 680 / 695. A false-positive gate goes to `py tools/gate_fp.py log` (never an env bypass); a hook edit is never made.
6. **Prior art:** this is a proven pattern (s03-s06 passed the same route). Run the DIFF-ONLY prior-art review of the scratch recipe only if the launch gate asks for
   one (non-parameter changed lines vs the s06 scratch recipe); otherwise quote `PROVEN-PATTERN`. Say which.
7. **Invariants** (md5 before = after): stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun 6208b7b7, s06 VI 569ffbf5, s05 3f9ac26b,
   bed 39511877, memory_model 8eec443c, adopted_scratch 658fe5b9, graph a3ecb92b, `sim/ring_p4_s06v18/**`, the s06 plan/pred/licence/recipes, no `tools/hooks/**`. Every file this
   card changes is listed by md5 before/after. No LabVIEW process; no `--launch`.

## Return conditions
A rebase or prerun refusal (verbatim + file:line); a prerun gate failing twice at the same place; a protected md5 moved; MAIN > 680 even for the shortest meaningful
prefix; a hook false positive that blocks the deliverable (log it with gate_fp.py first).

## Report `tools/bench/diag_c150_a2_3_facts.md` (<= 35 lines)
Rebase output, plan md5 before/after, cut and X10 numbers, X11, licence summary, dry/prerun/scratch-required results with exit codes, files changed, invariants. `OPEN:` line. Facts only.
