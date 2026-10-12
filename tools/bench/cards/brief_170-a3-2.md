---
card: 170-a3-2
status: current
date: 2026-10-13
---
# Brief 170-a3-2 (assignment 170-3) - PD409(e)/PD410(d): the P6 replay copy `claudeDev\replay\D1_ring_p6_replay_<ts>.vi`

Plan: `docs/d1/ring-p6.md` PD409(e) (lines ~255-258), PD410(d), PD411(e). LabVIEW build, no VI Run, no hardware. Card 170-a3-1 PASSED (`tools/bench/cards/result_170-a3-1.json`): the paced stand-ins exist,
`replay\replay_get_buff_image_paced60.vi` 59ec66b6 (inner swapped to the paced buf `replay\replay_imaqdx_get_image_buf_paced60.vi` e40ec867). Their md5 are the pins below.

## What to build
A dated byte copy of the P6 bed `claudeDev\D1_ring_p6_20261012_212645.vi` (md5 c2d9c13c, a bed - NEVER saved or edited in place) in `claudeDev\replay\`, with the same two swaps as plan 110, by the existing recipe:
- #6810 (callee 'get buff image-lost frames.vi', loop 1.1) -> `replay\replay_get_buff_image_paced60.vi` (59ec66b6...; full md5 from the stage-1 result / `diag_c170_a2_3_facts.md`);
- #22692 (callee 'IMAQdx Get Image.vi', calibration frames) -> `replay\replay_get_image_cal.vi` (afce0d04346fc58234d28bcc0fc42e55), unchanged from plan 110.
Route: `tools/recipes/stage_replay_swap.py` with a NEW named plan literal. Make `tools/bench/plans/plan_replay_swap_170.json` the way `plan_replay_swap_110.json` is made (copy of its structure; schema `stageplan-lite/1`):
`input` = the bed (md5 c2d9c13c in full, graph `tools/bench/graph_ring_p6_20261012_212645.json` fbc7b7ee), `input_tag` "p6", `input_pin` "P6", `stage_name` "stage_replay_swap_170", `task` "170-a3-2",
`out_json` "stage_replay_swap_170.json", `copies` {"p6": "replay\\D1_ring_p6_replay_{ts}.vi"}, `extra_pins` = the buf stand-in a89dafc1 (full md5 from plan 110), the paced buf e40ec867 (full md5), the S1 replay copy 126f8497 (full md5 from plan 110),
S1 `D1_s1_copy.vi` 3e3d23ce, and the bed pin, and a `decisions` list R01-R07 as plan 110. Add `"170": "plans/plan_replay_swap_170.json"` to `PLANS` in the recipe (the ONLY recipe edit; PLANS keys the prerun records on every plan's md5).
Plans 78/95/110 stay byte-identical (quote their md5 before and after).

## Gates (stop at the first unexpected result; the recipe's A1-A6 and C1-C3, nothing new)
BEFORE: #6810 and #22692 each call the OLD callee by name on the bed (P6's graph stores no SubVI names, `p6_replay_facts.md:40` NOT-DETERMINED: this is the first time they are read - a different callee or a missing uid = RETURN, no swap);
ExecState 1 before the swap; replace_object x2 with no error; callee diff == exactly the two swaps; wire-edge diff 0 after the uid remap; ExecState 1 after; scripted save; COLD (fresh LabVIEW) ExecState 1, census == warm, md5 unchanged by the cold load.
Record md5 and size of the replay copy, and the callee census of both uids. Bed c2d9c13c, 75773b0d, 7f2582ae, 3e3d23ce, 126f8497, 842ecad9, a89dafc1 unchanged (stage pins).

## Launch sequence
`--dry` and `--prerun` on the edited recipe first (`py tools/stage_prerun.py --prerun tools/recipes/stage_replay_swap.py --plan 170` as the existing precedent in `diag_c110g_*`/`launch_c110*` shows); the prior-art review
is owed (the recipe changed; `flags.peers` has `priorart`): run it as guard_cycle names it and write its "What was done with it" under `archive/peer/` (that path is in this card's write globs).
Stub-only dry gates are named in the card `rules` ("DRY-UNVERIFIED-OK: ...") only if the dry prints PASS-UNVERIFIED - if it does and the card names none, RETURN BLOCKED with the dry's label list (do not relabel a gate as a row).
X10: the bed has `load_by_vi` c2d9c13c = 603.7 (PD408). If X10 refuses, RETURN BLOCKED with the text: no `memory_model.json` edit in this card, no stage_prerun/hook edit, no bypass.
Launch: `py tools/bgrun.py --material --max-min 45 --log tools/bench/launch_c170_p6swap.log -- py -u tools/recipes/stage_replay_swap.py --plan 170`.

## Hygiene and facts
No original opened; VI Server refs balanced (live 0); `tasklist` shows no LabVIEW at the end; only the replay copy and diag/recipe/plan files written. Facts `tools/bench/diag_c170_a3_2_facts.md` (<= 40 lines, file:line), including
the replay copy path, full md5, size, and the stage json path (`tools/bench/stage_replay_swap_170.json`).

## Not in this card
No leg, no compare, no hook/stage_prerun/plan-of-record/STATUS/INDEX edit. A new unexpected result = RETURN with the facts (a failed gate deletes nothing it did not create; report any partial file).
