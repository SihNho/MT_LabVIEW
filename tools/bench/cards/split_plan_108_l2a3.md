---
title: L2-A3 split page - the two 1.2->1.1 crossings of group A, by local variable (PD221(d))
date: 2026-09-27
card: task_108-2.json
source: docs/d1-loop12-17-split-plan.md PD221(d) (:1885), 181(c) (:708-711), 182(c) (:729-732); CLAUDE.md 1c''
status: plan
---
# L2-A3 — cycle 108 (one page)

**Input (anchor):** `claudeDev\D1_l2_a2_20260927_132125.vi`, md5 `807c803e…` (card 108-1 PASS 20/0), never modified. Its graph
was read READ-ONLY from a byte copy by `tools/bench/diag_c108b_graph.py` → `tools/bench/graph_l2a2_20260927.json` md5 `e34e97c7…`
(`tools/bench/diag_c108b_graph.log:259`, 7/0). `cdiff_frame(S1, L2-A2)` = the 8 rows of 108-1 (`:260-268`); `#23541`'s partner
is `#10757 t10874` (`:269`).

## 1. What #10886 does with the two rows (F1, rule-1a note) — `tools/bench/facts_c108b_bed.log`

- `#10886` is a **CompoundArithmetic** on the 1.1 body `#639` (`:4-7`). Its 3 inputs: `t10895` ← `#10382 Not '.not. x?'` (w10447),
  `t10898` ← ControlTerminal `'Auto-Focus'` (w7527), `t10942` ← `#11529 Less? 'x < y?'` (w10543). Same in S1 (`:29-32`).
- Downstream, to the first sink (`:27-28`): `#10886 'result'` → `#10285 Not` (w6525) → `#1469` **Property `'Fix to a Certain
  Pattern'`.Value** (w3461, an implicit write of a front-panel control). Nothing on this path reaches saved data or a display;
  per `docs/camera-acquisition-facts.md:266-272` that control gates the `#10407` autofocus case (the ASI focus MOTOR).
  So the two rows feed the autofocus ENABLE (`enable = NOT(reseed-And) AND Auto-Focus AND (count < Limit)`).
- The S1 edges to re-make (rule 1a: same source uid + terminal): `10382.x` ← `#9647 And 'x .and. y?'` t9668 (S1 w9921, `:52`);
  `11529.x` ← `#11336` SelectorTunnel outer `'Value'` t11346 (S1 w11389, `:54`), i.e. `#10150 'x+1'` f1 / `#9907 'Value'` f0
  through the selector (`diag_c108b_graph.log:267`).
- On the L2-A2 file both sources are in the 1.2 body `#23166` (`diag_c108b_graph.log:257`): `#9647 t9668` on w25415 (→ `#10465`
  selector tunnel), `#11336 t11346` on w25386 (→ `#25371` RSR). Both sinks are on 1.1 `#639`: `10382.x` sits on a SOURCELESS stub
  w9921 (no other terminal), `11529.x` on a SOURCELESS w11389 shared with `#7311` RightShiftRegister `t11005` (facts `:9,12`).

## 2. How 181(c)'s carrier was made, and the verbs this stage uses

- `#23541` was made in S3a: `build_index_array` on the top diagram → `create_indicator(Nodes[0].Terminals[2])` → delete the Index
  Array → `move_in` to `#639` (`docs/cycle27-plan.md:1630-1636,1730-1737`); wired later by `wire_indicators` (`:2640-2655`); its
  reader Local `#23523` sits in loop 1.5 (`ct23541_facts_80.log:7`). 181(c) only MOVED it with `#10757` (L2-A1); L2-A2 re-wired
  it by `OpCtlSinkWire_v1`.
- This stage uses today's `stagexec` CREATE_ROUTES (`tools/stagexec.py:198-208`), the ones `plan_disp.json` r5/r6 used for the
  delivered display artefact (217(e)): **`indicator`** = `gscript.create_indicator_nested` born on the source terminal +
  `set_control_label` + `set_visible(False)`; **`local_read`** = `stagekit.create_local_read` + `move_in`; the Local → sink wire =
  `connect` (`nested` route, bare Local source).
- ⚠️ Coverage: row A's source `#9647` is a Node (Function) → the measured Node route. Row B's source is a **SelectorTunnel** outer
  face; `create_indicator_nested`'s tunnel route takes LoopTunnels only (`tools/gscript.py:3872-3897`), so the row goes by the
  OWNER route (`stagexec.py:605`, `OWNER_ROUTED`) to `#10445`'s `Terminals[k]`. Create Indicator on a CaseStructure's Terminals[]
  entry has NO measurement on record (`gscript.py:3859-3861` records dangling indicators from a For loop's Terminals[] sweep).
- ❌ **MEASURED (top-level dry, `tools/bench/diag_c108b_dry.log:39`): row 2 is UNROUTABLE** — `create_indicator_nested addresses
  Traverse('Node') by uid; #11346 'Value' belongs to SelectorTunnel #11336, which is not a Node`. Rows 1, 3–6 route (STEPX diff 0,
  `:27-38`). **Missing verb: create an indicator on a SelectorTunnel (case-structure output tunnel) OUTER face.** Not built here
  (card 108-2 F5). ⚠️ The dry still ended `DRY PASS` and wrote a PASS record (`prerun_records.jsonl:213`): the recipe's E1 FAIL
  came after the first mutation and was downgraded to UNVERIFIED (`diag_c108b_dry.log:40-42`).

## 3. Rows (plan `tools/bench/plan_l2a3_in.json` → finalized `tools/bench/plan_l2a3.json`)

| # | action | where | S1 edge re-made |
|---|---|---|---|
| 1 | create hidden indicator `'autofocus reseed flag (1.2 to 1.1)'` born on `#9647 t9668` | 1.2 body `#23166` | w9921 source |
| 2 | create hidden indicator `'autofocus reset count (1.2 to 1.1)'` born on `#11336 t11346` | 1.2 body `#23166` | w11389 source |
| 3 | create Local READ of row 1's label | 1.1 body `#639` | — |
| 4 | create Local READ of row 2's label | 1.1 body `#639` | — |
| 5 | wire Local(3) → `#10382 'x'` t10393 | `#639` | w9921 sink |
| 6 | wire Local(4) → `#11529 'x'` t13163 | `#639` | w11389 sink |

Open rows after the stage (PB): the 6 non-group-A rows (376 ×2, 2626, 5058, 5696, 6085) — QRT / L2-B, unchanged.

**Simulated** (`tools/bench/plan_l2a3_sim.log:3-9`): FINAL, 6 steps ok; cdiff 8 → 8 through the four creates, 7 after row 5,
6 after row 6; end rows == the 6 open rows. `tools/bench/plan_l2a3.json` md5 `7cab639c…`. The 4 create steps ran on the
provisional rule (`opmodels/const.json` has no sim params), so E1 at run time is the backstop for them.

## 4. Sub-steps and saved files

| step | what | saved file | pass criterion |
|---|---|---|---|
| 0 (108-2, read only) | byte copy of L2-A2 → read_live + mloops + owner walk; cdiff(S1, L2-A2) | `tools/bench/graph_l2a2_20260927.json` | 8 rows; `#23541`↔`#10874`; input md5 unchanged; LabVIEW gone |
| 1 (108-2, offline) | stagesim finalize of `plan_l2a3_in.json` | `tools/bench/plan_l2a3.json` | FINAL; end cdiff == §3's 6 open rows; X9 pass; X10 printed |
| 2 (108-2, offline) | recipe `tools/recipes/stage_d1_l2a3.py` (≤120 lines, rows only from the plan); top-level `--dry`, `--prerun` | records in `prerun_records.jsonl` | dry PASS, pre-run PASS |
| 3 (judgement's next card — NOT launched here) | fresh LabVIEW, copy of L2-A2, 6 ops, gates below, gui_save (rule 6) | `claudeDev\D1_l2_a3_<ts>.vi` | §5 |

## 5. Criteria of the stage run (predicted)

| gate | predicted |
|---|---|
| input md5 | `807c803e…`, unchanged |
| L1 / E1 | 6 actions → 6 ops; every checkpoint read == its simulated step (diff 0) |
| CT (179(b) reader) on each new indicator | partners real == sim (`#9647 t9668` + `#10465`'s face; `#11336 t11346` + `#25371`'s face) |
| LB | each new label on exactly 1 ControlTerminal and 1 Local |
| D | new wires == the simulation's count; lost base wires == the simulation's (the two sourceless half-wires) |
| FU | frame-diagram set unchanged |
| PB frame-keyed cdiff(S1, end) (FATAL, before save) | == the 6 open rows (10382.x, 11529.x closed through the indicator → Local relay, `vigraph.py:606-615`) |
| ExecState | 0 by design (rows 376, 5058 open) — recorded, never run; gui_save (rule 6) |
| RBW on a scratch of the saved file | deletes no wire of a re-wired sink |
| LabVIEW gone at exit | true |
