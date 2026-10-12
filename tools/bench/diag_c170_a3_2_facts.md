---
type: facts
status: current
date: 2026-10-13
card: 170-a3-2
---
# Card 170-a3-2 - P6 replay copy: FAIL at the --dry (A2), nothing built

## What ran
| step | log | result |
|---|---|---|
| plan literal `tools/bench/plans/plan_replay_swap_170.json` (md5 9ec7a13e367c76ad01e7261e8b1ec715) | - | written; structure of plan 110 |
| `PLANS["170"]` added (the only recipe edit), recipe md5 2bb111e2 -> fa94e80c9bdb6d1b7f2b5a9186165ddb | `tools/recipes/stage_replay_swap.py:23-24` | edited |
| `stage_prerun.py --dry ... --plan 170` | `tools/bench/stage_replay_swap_170_dry.log:4-12` | DRY FAIL 0/1, rc 1, 3 s |
| --prerun, prior-art review, build launch | - | NOT RUN (card returns at the first unexpected result) |

## Facts
- Dry gates: K1 input md5 c2d9c13c PASS, graph JSON found PASS, A1 PASS (`stage_replay_swap_170_dry.log:4-6`).
- First fail, verbatim: "FAIL  A2 p6 BEFORE: #6810 calls get buff image-lost frames.vi, #22692 calls IMAQdx Get Image.vi
  {6810: None, 22692: None}" (`stage_replay_swap_170_dry.log:9`); fatal, so A3-A6/C1-C3 not reached (coverage 40/69, :11).
- The dry census comes from the graph JSON; `graph_ring_p6_20261012_212645.json` contains neither callee name
  (grep "get buff image|IMAQdx Get Image": 0 matches) nor the strings "6810"/"22692" as keys (0 matches).
- This is the gap already recorded: "callee_name_in_P6: NOT-DETERMINED (the P6 graph has no graph_summary.subvi_calls ...)"
  (`tools/bench/p6_replay_facts.md:43`). Plan 110's graph did carry both callees (plan_replay_swap_110.json "note", R0).
- The dry printed FAIL, not PASS-UNVERIFIED, so the brief's DRY-UNVERIFIED-OK route does not apply as written.
- Plans unchanged: 78 cdc14e32..., 95 ea7cf810..., 110 6b5ef7e5bba88eb79445132e06c91188 (md5sum after the edits).
- Hygiene: no LabVIEW launched (dry is files-only); no `*p6*` file in claudeDev\replay; tasklist shows no LabVIEW.exe;
  no original opened; bed c2d9c13c read only (K1 PASS).
- extra_pins add P5 75773b0d, P5-1 7f2582ae, unpaced get-buff 842ecad9 and paced buf e40ec867 (card hygiene list); the bed
  is pinned by input_pin "P6", not duplicated.

## Card 170-a3-4 (retry): callees read 12/0; dry A2 FAILs again, by the dry's construction (gate-fp fp-103)
- Byte-copy census (diag_replay_lib.census): 101 calls; #6810 -> background VIs\get buff image-lost frames.vi, #22692 -> IMAQdx.llb\IMAQdx Get Image.vi; scratch deleted, pins/bed unchanged, refs live 0, LabVIEW gone (`diag_c170_a3_4_callees.log:24-26,32-48`). Graph `graph_ring_p6_callees_20261013_011441.json` md5 31641b28ac4439df80f0ed6212e28427 (no terminals/objs, so find_graph keeps fbc7b7ee).
- plan 170 input.graph repointed (md5 9ec7a13e -> 01c21526); plans 78/95/110 cdc14e32/ea7cf810/6b5ef7e5 unchanged; fbc7b7ee unedited.
- Dry again: FAIL A2 {6810: None, 22692: None}, graph still graph_ring_p6_20261012_212645.json (`stage_replay_swap_170_dry2.log:6,10`).
- Why (code): the dry never reads input.graph (plan_base_graphs reads base.path, stage_prerun.py:211-230); g.subvis is a stub (fake_gscript graph-backs 5 readers, :656-666) whose Fake iterates empty (:440-452); taint scored per gate statement (:816-820) and the census is the statement before the gate (stage_replay_swap.py:41-42) -> FAIL, not UNVERIFIED. Plan 110's dry predates that rule: "UNVERIFIED A2 disp ... (dry: read stub data)" (stage_replay_swap_110_dry.log:10).
- Not run: prerun X10, prior-art review, launch. No replay copy exists.
