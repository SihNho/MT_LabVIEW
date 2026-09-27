---
title: L2-A3 relaunch addendum (card 109-2) - the recipe's own gates fixed, rows and routes unchanged
date: 2026-09-27
card: task_109-2.json
source: tools/bench/cards/split_plan_108_l2a3.md (the page; rows 1-6 unchanged); tools/bench/cards/split_plan_108_l2a3_c108f.md; docs/d1-loop12-17-split-plan.md PD222(g)
status: plan
---
# L2-A3 relaunch addendum — card 109-2

Plan `tools/bench/plan_l2a3.json` md5 `f2341cab…` unchanged (rows, routes, open rows). Only the recipe's gates change
(`tools/recipes/stage_d1_l2a3.py`, 120 lines):

- **Why:** card 108-6's run (`tools/bench/stage_d1_l2a3.log`) did all 6 ops at STEPX diff 0, E1 + both CT PASS, then died at
  the recipe's own LB gate, `KeyError 'term_class'` (`:171-181`): `allterms.read_terms` rows carry no `term_class`
  (`tools/allterms.py:45-46,85`). Same class as 108-4 (`tools/bench/diag_c108d_selind.log:41`). Review:
  `archive/peer/2026-09-27-c108f-l2a3-termclass.md` (disposed).
- **F1 LB:** a ControlTerminal row = `term_uid` in `report_all('ControlTerminal')` (live) / the simulated ControlTerminal
  objects + simulated ControlTerminal rows (dry; `tools/stagesim.py:976-983` models a created indicator as a row only).
  Local = `owner_class 'Local'` on the same rows. Never `owner_class == 'ControlTerminal'` (panel terminals are 'Diagram').
- **F2 dry:** CT and LB now run in dry on the simulated end rows (the old `[] if DRY` skip is gone); IB and RBW print
  `GATE <id> NOT RUNNABLE IN DRY: <why>`. Dry PASS unverified 0 (`tools/bench/stage_d1_l2a3_dry_c109b.log`); pre-run PASS
  10/0 (`tools/bench/stage_d1_l2a3_prerun_c109b.log`).
- **F3 IB:** AFTER the save, per re-wired sink (`#10382` t10393, `#11529` t13163 from the plan's wire rows), the ordered
  idempotent second pass `stagekit.cfw_second_pass` + `expect_is_broken_false(wire_uid=<the sink's wire>)` — prior art
  `tools/recipes/stage_d1_l2a1.py:82-91`, order per `docs/NAMES.md:1098-1104` (never above a save point). The in-memory VI
  is not saved again. Then RBW on a scratch of the saved file, as before.
- **F4 class grep:** `term_class` reads in `tools/recipes/stage_*.py` + `tools/stagekit.py`: the only read on
  `read_terms` rows was `stage_d1_l2a3.py:66`; every other hit reads a plan/graph/`read_live` row (which carries it) or
  writes a literal.
- **Next:** ONE launch under bgrun → `claudeDev\D1_l2_a3_<ts>.vi` (rule-6 GUI save, ExecState 0 by design, never run).
