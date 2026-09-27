---
title: L2-A3 addendum (card 108-6) - row 2 routed through the SelectorTunnel outer-face verb
date: 2026-09-27
card: task_108-6.json
source: tools/bench/cards/split_plan_108_l2a3.md (the page; rows, gates and saved-file list unchanged); docs/d1-loop12-17-split-plan.md PD222(g)
status: plan
---
# L2-A3 addendum — card 108-6

The one-page plan is `tools/bench/cards/split_plan_108_l2a3.md` (rows 1-6, §5 criteria). Only §2's coverage note changes:

- Row 2 (`a3_ind_count`, indicator born on `#11336` SelectorTunnel outer face `t11346`, frame `#23166`) was UNROUTABLE in the
  top-level dry (`tools/bench/diag_c108b_dry.log:39`). Card 108-4 built and scratch-verified the verb:
  `gscript.create_indicator_nested(W, face, None)` accepts a SelectorTunnel outer face and goes through the owner
  CaseStructure's Terms[] entry on the face's wire → `OpCreateIndicatorNested_v0` (`tools/gscript.py:3867-3953`; record
  `tools/bench/scratch_verify/gscript.create_indicator_nested_20260927_141618.json`, 24/0).
- Card 108-6 routes stagexec to it: `stagexec.tunnel_outer_face` now accepts owner class `LoopTunnel` or `SelectorTunnel`
  (`FACE_ROUTES`, `tools/stagexec.py:307-325`), used by the real route (`:1803`) and the dry route (`:2097`). Self-test
  106/0 incl. T38f (SelectorTunnel face routes) and T38g (inner face / other diagram / case selector / sink face refused)
  (`tools/bench/selftest_stagexec_c108f.log`).
- Re-simulated: `tools/bench/plan_l2a3_sim_c108f.log` — FINAL, 6 steps, cdiff 8→8→7→6, end == the 6 open rows; plan md5
  `f2341cab…` (was `7cab639c…`; the rows are unchanged). Top-level dry PASS, 0 UNROUTABLE, STEPX diff 0 on all six ops
  (`tools/bench/stage_d1_l2a3_dry_c108f.log:24-38`); pre-run PASS 10/0 (`tools/bench/stage_d1_l2a3_prerun_c108f.log`).
- Recipe `tools/recipes/stage_d1_l2a3.py` unchanged (md5 `3fcefd3b…`, 107 lines, rows only from the plan).
- Next: ONE launch under bgrun → `claudeDev\D1_l2_a3_<ts>.vi` (rule-6 GUI save, ExecState 0 by design, never run).
