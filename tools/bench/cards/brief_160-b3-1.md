---
card: 160-b3-1
status: current
date: 2026-10-10
---
# Brief 160-b3-1 (assignment 160-2) - OFFLINE: plan_ring_p5s02b.json FINAL on the real 94ffff94 with the two stub deletes (PD391(a)(d)(f))

`labview: none`: json only, no LabVIEW process, nothing launched, no `tools/hooks` edit, no tool edit. Read `docs/d1/ring-p5b.md` PD391 first. Card 160-a2-1 PASSED:
`tools/stagesim.py` is now 95a162ba (delete branch = a Wire with no source row), `tools/stagexec.py` ddf23a31 (a base register inner face compiles to `connect_term_uid`
`register_end_case_border`); facts `tools/bench/diag_c160_a2_1_facts.md`. `stagekit` 1441bb4c, `stage_prerun` 7605116f, `vigraph`, `addrcheck` are unchanged.

## What to build
`tools/bench/prep_c160_b3_1_mk.py` (+ `.log`, `prep_c160_b3_1_session.json`) = the flow of `tools/bench/prep_c160_b1_1_mk.py` (4fe22a40; read it - it maps with the shared `stagekit`
functions and gates every step) with these changes only. Copy the file and edit it; do not import it (it runs at top level) and do not retype uids:
1. Re-pin to the new bytes: stagesim 95a162ba, stagexec ddf23a31; brief pin = this file; `plan_ring_p5s02b_c159.json` (caef7e1c) and the b1 plan below as inputs.
2. First keep the b1 output: copy the current `plan_ring_p5s02b.json` (09ebc7a6, final False) to `plan_ring_p5s02b_b1.json` before the rebuild, as b1 did with c159.
3. Input plan for `stagesim.simulate` = `tools/bench/plan_ring_p5s02b_in2.json`, written by the script from `plan_ring_p5s02b_in.json` (56bfddd3, stays unchanged) by inserting two `delete_wire`
   rows exactly as `selftest_c160_regface.py:70-79` does for its temp plan: `dw_go` before the group of A32 (`t_go`, routes 4) and `dw_ho` before A39 (`t_ho`, route 7); the wire uids
   (w24264, w24300) are READ from the graph rows of the sink terminals (t24139, t24235), never typed. Row 1 stays the `delete_wire` of w10394 (the A13 remnant). Total 20 actions.
   Give the two new rows a `why` that says: PD391(a) sink-only stub on the base register inner face, deleted before the group's connect.
4. The `why` of A32 and A39 (the two former MERGE rows on stubs w24264 / w24300) becomes "stub deleted first (PD391); fresh connect to the register inner face; uid NOT predicted; CEN2 judges by ends".
   A28 and A35 (LSR faces, stubs w24285 / w24312) keep MERGE with the expected uid; keep their `why` as in the input.
5. Gates (each prints a FACT line and a gate line): the ROWS gate compares delete(10394) + stagekit-mapped A24..A40 against the input except the `why` of MERGE rows, then the 20-action
   plan against input + the two inserted rows only; SB (REALSIM final True on 94ffff94, failed None, 20/20 replayed, 0 PROVISIONAL, route check PASS and **0 UNROUTABLE**, quote every route
   row's k / op / route); MERGE-END for A28/A35 only (A32/A39 stubs no longer exist: assert t24139/t24235 are NOT on the stub wires w24264/w24300 at the sim end and carry a wire with
   a source); C compile (quote the op list and checkpoints; the old expectation "8 ops" is stale - state the new count and why); X10 planned MAIN <= 675 at START_ASSUMED 603.4 (quote the
   number); X8 control_path_lint; X17; U pins. Where a b1 expectation is stale because of the deletes, change the expectation and say so in the report - never loosen a gate silently.
6. Output `tools/bench/plan_ring_p5s02b.json` is written ONLY by `stagesim.simulate` (final True). `plan_ring_p5s02b_in.json` and `plan_ring_p5s02b_c159.json` stay byte-unchanged.

## FAIL conditions (return FAIL with the line, do not work around)
Route check shows any UNROUTABLE; final False; MAIN > 675; any mapped row differs from the input. A tool edit looks needed -> FAIL (hand back); no tool edit is allowed in this card.

## Report `tools/bench/diag_c160_b3_1_facts.md` (<= 35 lines, facts only)
md5 of every input and output (in, in2, plan final, b1 plan, c159 plan, graph, 94ffff94 VI); the gate lines quoted with PASS/FAIL; the 20 action ids in order; route rows; compile op list;
MAIN number; md5 UNCHANGED list (s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, 94ffff94, stagekit, stage_prerun, stagesim 95a162ba, stagexec ddf23a31); `OPEN:` lines.
Claude dev dir md5s may be refused by the permission layer: then say "not hashed", do not work around.
