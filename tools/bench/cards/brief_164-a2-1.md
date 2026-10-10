---
card: 164-a2-1
status: current
date: 2026-10-10
---
# Brief 164-a2-1 (assignment 164-2) - OFFLINE: hash inputs, K3/K4 pass-wire frame on the DST end only (PD398), compile, `plan_ring_p5s02d.json`, retire card 158-a3-3

`labview: none` (no LabVIEW process before, during or after), no `--launch`, no `tools/hooks` edit, no edit of `tools/stagekit.py`, `stagexec.py`, `stagesim.py`, `stage_prerun.py`,
`stage_shared.py`. Read `docs/d1/ring-p5c.md` PD397 and PD398 and `docs/script-writing.md` first. Round 1 (card 164-a1-1, facts `tools/bench/diag_c164_a1_1_facts.md`, `diag_c164_a1_2_facts.md`)
already built `tools/bench/prep_plan_flow_lib.py` (replay self-test 28/0) and the maker `tools/bench/prep_c164_a1_1_mk.py`. Reuse both: CALL, do not copy (`docs/script-writing.md`).

## Part 1 - hash the inputs FIRST and quote them
`tools/bench/prep_c164_a2_1_hash.py` (+ `.log`), md5 of every input listed on the card, plus the five VIs in `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev` (bytes only; if the
permission layer refuses, say "not hashed"): 564d8cbe `D1_ring_p5s02c_20261010_125755.vi`, f9ae7751, 94ffff94, 7f2582ae, eb1d0f31. Judgement-time values: VI 564d8cbe, graph 3d5196ab,
EL 26d45c71, memory_model 8fb432e4, r_in 4c8d3645 (current, src+dst frames), r_in_pre164 d84634bd (original), p5s02d 1152ce60 (J alone, round 1), stagekit dd57c1ca, stage_shared b688edd4,
stagexec a4df7e15, stagesim 95a162ba, stage_prerun 7605116f. A mismatch is explained BEFORE you go on (a pin that only drifted is not a reason to stop; a changed graph or plan input is).

## Part 2 - the pass-wire shape (PD398(a))
In `tools/bench/plan_ring_p5s02r_in.json` the actions A69 (`w_k3pass`) and A79 (`w_k4pass`) DROP the `frame` key on the SOURCE end and KEEP `"frame": "True"` on the DESTINATION end. Edit with the
Edit tool (no heredoc patch). Prove it with a compare script (`prep_c164_a2_1_cmp.py`, output in the log), both directions:
(i) against `plan_ring_p5s02r_in_pre164.json` (d84634bd, do NOT modify it): exactly 2 ADDED keys (the two dst `frame`); (ii) against 4c8d3645 (copy it first to `plan_ring_p5s02r_in_both164.json`): exactly 2
REMOVED keys (the two src `frame`). Anything else different = FAIL (restore from the d84634bd copy and redo). Quote old -> new md5.

## Part 3 - compile on the real graph, then the plan
Compile K3 and K4 on graph 3d5196ab with `stagexec.compile_plan` (through the prep flow, read-only): quote, for each of K3 and K4, the op kind that takes the pass wire, and that `case_pass_wire`
is True (stagexec.py:6286-6288 region) and the in-tunnel has its out-wire (stagexec.py:896-901 region). Quote the dst frame binding `#31517` with `creation_map/plan_ring_p5s02a_4284c22a_20261010_023453.jsonl:35`
(the binding record; `new:CQ7 'True'` -> sim -30 -> real #31517). **If the compile refuses the dst-only shape: FAIL, return the refusal text and stop. Try no other shape. Edit no tool (PD398(b)).**

Then run the maker (a copy of `prep_c164_a1_1_mk.py` as `prep_c164_a2_1_mk.py`, <= 60 lines, calling `prep_plan_flow_lib.make_step_plan`; the old maker is NOT edited) for the prefixes of WHOLE groups
(J ; J+K3 ; J+K3+K3f ; J+K3+K3f+K4 ; J+K3+K3f+K4+K4f). For each prefix quote planned MAIN (X10 on `SX.checkpoint_ops`, START = `stage_prerun.x10_start(564d8cbe)` called, limit 675 UNCHANGED, read-only) and rows.
The plan = the LONGEST prefix with MAIN <= 675 and rows <= 40 (stop at the first failing prefix; longer ones are bigger). A group is never split. The plan `plan_ring_p5s02d.json` is written ONLY by
`stagesim.simulate` with final True; the J-alone file 1152ce60 is copied aside first as `plan_ring_p5s02d_jonly.json` (fallback; used only if J+K3 > 675 or refused). Gates, each with a FACT line and a gate
line: ROWS, SB (REALSIM final True on 3d5196ab, failed None, 0 PROVISIONAL, 0 UNROUTABLE), C compile (op list + checkpoints), X10 MAIN, X8 control_path_lint, X17, no-group-split, action id range.

Known open item from round 1: the K3f/K4f sink wires (t8776 w10362, t24342 w25232) are already wired in 3d5196ab and no plan `delete_wire` removes them; the maker's STUB gate is non-fatal. State plainly,
for the chosen prefix, whether the prefix contains K3f / K4f and whether the STUB line is a real obstacle for that prefix (cite the rows). Do not edit the plan rows to make STUB pass.

## Part 4 - retire card 158-a3-3 (PD398(d))
Write `tools/bench/cards/result_158-a3-3.json` (`py tools/protocol.py new result --id 158-a3-3`, timeout <= 30 s; status `FAIL`, note "RETIRED - never dispatched; guard_assign refused it in cycle 158; PD398(d); never
re-pinned or run"). Validate it. Prove guard_write no longer lists it: call `open_card_pins` (tools/hooks/guard_write.py:77-128) read-only, quote that `plan_ring_p5s02r_in.json` is no longer pinned by 158-a3-3.
Do not edit the hook.

## FAIL conditions (return FAIL with the line, no workaround)
Compare shows more than the 2+2 keys; compile refuses the dst-only shape; Final False; any UNROUTABLE; MAIN(J) > 675; a tool edit looks needed (outside `tools/bench/prep_*`).

## Report `tools/bench/diag_c164_a2_1_facts.md` (<= 45 lines, facts only)
Part 1 md5 table (equal/changed); both compares + old -> new md5; K3/K4 compile op kinds + `case_pass_wire`; the `#31517` quote; MAIN and rows per prefix, the chosen prefix and its action ids; plan md5 + final +
REALSIM line; route rows; compile ops + checkpoints; K3f/K4f STUB statement; 158-a3-3 retirement proof; md5 UNCHANGED list (stagekit, stagexec, stagesim, stage_prerun, stage_shared, memory_model, graph, EL, the VIs);
`OPEN:` lines with file:line.
