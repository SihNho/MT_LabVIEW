---
type: facts
status: current
date: 2026-10-08
card: 146-a3-1
---
# Card 146-a3-1 facts: s05 57 reproduced; no `carry` from the plan and states can reach 55 class-exact -> RETURN, elrule.py NOT edited

## Reproduction (`tools/bench/diag_c146_a2_1_repro.log`, 2/0)
- `predict(st0, last, 58, made, extra_owner_states=(base,), subvis)` as `prep_c146_a1_3_pred.py:105-111` -> **57**: new [input -32, local -30],
  closed [local 30001, sr 29403, sr 29648].
- READ per class (`diag_c146_a2_1_variants.log`, items classed by text): s04 5e53096a {local 2, BuildArray 3, IndexArray 3, SubVI 1, sr 2} ->
  s05 06a59001 {local 2, BuildArray 3, IndexArray 3}; **change {IndexArray 0, BuildArray 0, SubVI -1, local 0, cond 0, sr -2} = -3**.
  The SubVI item is s04 read #14 "SubVI 'TrackNbeads four-fold over-kernel-v3.vi': required input 'Image In' is not wired" (`diag_c146_a2_1_probe2.log`).
- PRED V0 per class: IndexArray **+1** (new -32), SubVI **0**, local 0, sr -2.

## Cause (code)
- `tools/elrule.py:153-158`: the A rule counts only nodes in `created`; `session_prediction` (`:223-225`) passes this session's `made` and no `carry`,
  so a base node closed by this session is in neither `items(st0)` nor `items(last)`.
- Only 3 non-created nodes have a sink wired during s05 (`diag_c146_a2_1_probe.log`; s01..s04: none): #29843 IndexArray (array, index -> all
  wired), #5058 SubVI ('Image In' wired, three '' rows stay unwired), #29724 SubVI SQ1 ('discards', 'Latest' wired; table rule 2 = no item).
- #29843 is a node s04 MADE (uids in s05 start minus s04 start = 13 nodes, `diag_c146_a2_1_probe4.log`); after the rebase the s05 plan keeps no
  link to s04 (`base` = real fsmap, no `sim_of`; sym of st0 empty).
- #5058 is a base SubVI whose 'Image In' requiredness is measured only in the base EL text; `subvi_requiredness.json` (13b0d75f) has only
  RingPickSlot_v0 / RingSeqCheck_v0, and no state or graph carries a base SubVI's VI name. A carried SubVI with unknown identity is
  `uncertain`, never counted (`elrule.py:136-149`).

## Candidates measured with the EXISTING `predict(carry=...)` (`diag_c146_a2_1_variants.log`, no edit)
| variant | carry | s05 total | IndexArray | SubVI | local | sr | class-exact | s01..s04 new/closed |
|---|---|---|---|---|---|---|---|---|
| READ | - | 55 | 0 | -1 | 0 | -2 | - | - |
| V0 (now) | none | 57 | +1 | 0 | 0 | -2 | no | 51/53/55/58 |
| V1 | nodes the previous session made (start-state diff) | 56 | 0 | 0 | 0 | -2 | no (SubVI) | identical |
| V2 | owners of plan `open_rows` | 57 | +1 | 0 | 0 | -2 | no | - |
| V3 | every non-created start owner | 56 | 0 | 0 | 0 | -2 | no (SubVI) | identical (69 SubVIs uncertain) |
| VX | V1+V2 + a NOT-measured table row 'Image In' rule 1 for #5058 | 55 | 0 | -1 | 0 | -2 | yes | - |
- VX shows the missing data: the SubVI class needs #5058's VI identity + its 'Image In' rule 1 from a measured source. V1 also needs the previous
  session's start state, which `session_prediction(plan, base_total)` does not receive.

## Self-tests (no edit, so before == after): selftest_elpred 21/0, selftest_s5 22/0, selftest_c_e3 64/0
(`selftest_c146_before_elpred.log`, `_s5.log`, `_c_e3.log`).

## md5 (all unchanged): elrule.py a5ee7d5c, selftest_elpred.py e0baa236, memory_model.json 559be4cf, read file 06a59001, plan s05 1fc9b486,
plan s06 8f33ad75, subvi_requiredness.json 13b0d75f. No LabVIEW launched (card labview none).
