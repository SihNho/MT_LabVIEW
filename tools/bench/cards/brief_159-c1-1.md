---
card: 159-c1-1
status: current
date: 2026-10-10
---
# Brief 159-c1-1 (assignment 159-3) - OFFLINE: split check on the real 94ffff94 graph + plan_ring_p5s02b.json (PD388(a)(c)(e)(h), PD389)

Offline, no LabVIEW, no stage-tool or hook edit, step 2 is NOT launched. Read `docs/d1/ring-p5b.md` PD388 + PD389 and `docs/d1/ring-p5.md`
PD379(c), PD387(f) (lines ~376-381) first; `docs/script-writing.md` binds you (call shared functions, no pasted blocks).

Base = the REAL graph of the adopted in-between file `D1_ring_p5s02a_20261010_023239.vi` (94ffff94): `tools/bench/graph_ring_p5s02a_20261010_032547.json`.
Action source = `tools/bench/plan_ring_p5s02r_in.json` (d84634bd, A24..A80, all groups) and how `plan_ring_p5s02a.json` (4284c22a) was cut from it
(`tools/bench/prep_c156_a1_1_mk.py`, `prep_c156_a1_1_session.json`). `tools/stage_prerun.py` has a `--rebase` / `rebind` route to move a plan onto a
real graph (PD366, PD277-280). Use the EXISTING routes; a route that cannot express something is an OPEN line with the refusing file:line, never a new tool.

## 1. Split check (facts first)
Measure on the real 94ffff94 graph, per PD388(h) / PD387(f): (a) does any group cross the A60/A61 boundary (list every group of A24..A80 with its
first/last action and quote the ones touching A60/A61); (b) step 2 = A24..A60 planned MAIN from the memory model (`tools/bench/memory_model.json`
START_ASSUMED 603.4, measured start 593.8) with the per-action table the planner prints; (c) the verdict by the PD388(h) rule as written: keep A24..A60
iff no group is cut and planned MAIN <= 675, otherwise the last whole-group boundary that fits (name it and its MAIN). Record the numbers in
`tools/bench/diag_c159_c1_1_facts.md`. Do not change `START_ASSUMED`.

## 2. `tools/bench/plan_ring_p5s02b.json`
On the real 94ffff94 graph (rebased, rows only from the graph and the PDs; no uid retyped). FIRST action = `delete_wire 10394` (existing verb in
stagekit / stagesim / stagexec - quote where it is accepted), then A24..A60 or the cut from section 1. The plan carries, for each of A28, A35, A32, A39
(a connect onto a terminal that already carries a source-only stub, `tools/bench/attrib_c159_p5s02a.md:54-55`): the MERGE assumption written as an
ASSUMPTION (not a measured fact), the uid the merged wire is expected to have (read it off the sim end of the plan, quote), and the sentence that
CEN2 judges it by wire ends (PD389(b)). Use whatever notes field the plan schema already allows; if none, put the same four lines in the facts file and
list the schema gap as OPEN. The plan must compile (`stage_prerun.py` plan compile / simulate route: quote the command and its result: actions
accepted, REALSIM, planned MAIN per checkpoint) with `unverified`-style gates reported as they are, not suppressed.

## Report `tools/bench/diag_c159_c1_1_facts.md` (<= 40 lines, facts only)
Split table + verdict; the plan md5; action count; command + result of the compile; the four MERGE rows (action, stub terminal, expected uid, assumption
text location); `OPEN:` lines. Also quote md5 before == after for 94ffff94 (023239.vi), s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, and that
`tools/stage_prerun.py`, `tools/stagekit.py`, `tools/stagexec.py`, `tools/stagesim.py` md5 are unchanged (pins in the card).
