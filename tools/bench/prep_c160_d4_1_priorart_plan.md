---
card: 160-d4-1
status: current
date: 2026-10-10
---
# Plan under review: RING P5-2 step 2 (card 160-d4-1) - offline plan, not launched

Design: `docs/d1/ring-p5b.md` PD388 (:17-54), PD389 (:56-87), PD390 (:89-128), PD391 (:130-175). Base = the step-1 result 94ffff94
(graph `tools/bench/graph_ring_p5s02a_20261010_032547.json` 7ac24924, `ring-p5b.md:21-22`). Plan `tools/bench/plan_ring_p5s02b.json`
f4520b10 (FINAL, maker `tools/bench/prep_c160_b3_1_mk.py`, `diag_c160_b3_1_facts.md:8-13`), pred `plan_ring_p5s02b_pred.json` 48b50b29,
recipe `tools/recipes/stage_d1_ring_p5s02b.py` 083fda6d (+ `_scratch.py` 3f6fb898) (`diag_c160_c3_1_facts.md:8-10`).

## The 20 actions, by group (`diag_c160_b3_1_facts.md:15-16`; plan rows `plan_ring_p5s02b.json:136-342`)
- PD388(a) remnant: `dw_a13` = delete_wire w10394, the termless segment step-1 A13 left (`ring-p5b.md:26-31`; plan :136-139).
- F3: `t_in3` (in-tunnel #25223 keeps its source), `w_in3_t`, `w_in3_376` (plan :142-171).
- G: `t_gi` (LSR #24133 inner face), `w_gl` (MERGE onto t24190 / stub w24285), `w_g376`, `dw_go` = delete sink-only stub w24264,
  `t_go` (RSR #24083), `w_gout`, `w_gr` (fresh connect to t24139), `w_gpass` (pass through the timed-out frame) (plan :174-256).
- H: same shape on LSR #24187 / RSR #24150: `t_hi`, `w_hl` (MERGE onto t24288 / stub w24312), `w_h376`, `dw_ho` = delete w24300,
  `t_ho`, `w_hout`, `w_hr`, `w_hpass` (plan :259-342).
- Compiled: 10 ops - delete_wire 3, tunnel 3, connect_term_uid register_end_case_border 2, case_frame_wire 2; checkpoints
  [0,2,3,5,7,9,10] (`diag_c160_b3_1_facts.md:24-26`). MAIN 657.4 <= 675 at START_ASSUMED 603.4 (`:31`).
- Offline: REALSIM final True, 20/20, 0 PROVISIONAL, route check PASS, 0 UNROUTABLE (`diag_c160_b3_1_facts.md:19`). The recipe dry
  FAILS at gate L0 on the plan_in name `_in2` (fp-82, `diag_c160_c3_1_facts.md:24-27`); prerun / launch gates not yet run (`:28`).

## NEW vs earlier launches - what the reviewer must test
(i) Deleting a SINK-ONLY / termless stub wire by uid before its terminal is connected: w10394 (0 terminal rows), w24264 / w24300
    (sink row, no source row). New stagesim branch `sourceless_wire` (`diag_c160_a2_1_facts.md:13-14`); live delete = the existing
    `stagekit.delete_wire` uid path (`ring-p5b.md:97-101`); stagexec delete executor `:2896-2900` (`diag_c160_a2_1_facts.md:17`).
    Measured offline only: the old delete path left Wire 24264 in the object list (`diag_c160_a2_1_facts.md:11`). Never run in LabVIEW.
(ii) A BASE-graph RightShiftRegister inner face (t24139 / t24235) connected through `connect_term_uid` `register_end_case_border`
    (`stagexec.base_register_end`, `diag_c160_a2_1_facts.md:15-16`) instead of MERGE. Earlier launches used this route only for
    PLAN-MADE registers (`ring-p5b.md:142-143`: `diag_c154_p5s01a_scratch.log:229`, `diag_c155_p5s01b_scratch.log:137`).
(iii) MERGE kept for A28 `w_gl` / A35 `w_hl` (LSR source faces carrying stubs w24285 / w24312, route cfw; `ring-p5b.md:156-159`);
    pred expects the joined uid = the stub uid; CEN2 judges the Wire class by wire ENDS, not uid counts (`ring-p5b.md:69-76`;
    `diag_c160_c3_1_facts.md:13-15`). Not measured: "one ok wire per pair" is an ASSUMPTION (plan :192, :277).
(iv) Case tunnel groups G and H whose outside source is a BASE loop tunnel's / register's inner face (plan :174-181, :259-266).
(v) Predicted step-2-end Error List: CLEARED 5 (dw_a13, dw_go, dw_ho, w_gl MERGE, w_hl MERGE), RAISED 0, UNPREDICTED 2 (A32 w_gr,
    A39 w_hr), STANDING 51, TOTAL 51 (53 if each UNPREDICTED raises one) (`diag_c160_c3_1_facts.md:19-21`).

## Questions for prior art
(a) Has this project already deleted a sink-only or termless wire by uid in LabVIEW (any recipe / op), and did LabVIEW leave a
    loose end, auto-drop a tunnel, or renumber anything (`diag_c160_a2_1_facts.md:41` names a measured LoopTunnel auto-drop on the
    shared path)?
(b) Has `register_end_case_border` ever been run on a register the plan did NOT create, and what did it leave?
(c) Is there a recorded MERGE result (connect onto a terminal that already carries a stub) other than 24360/24367 (`ring-p5b.md:38-40`)?
(d) Does an existing shared function already insert stub deletes before a group connect (`diag_c160_b3_1_facts.md:34-35` asks)?
