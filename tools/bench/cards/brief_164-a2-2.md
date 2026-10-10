---
card: 164-a2-2
status: current
date: 2026-10-10
---
# Brief 164-a2-2 (assignment 164-2, retry of 164-a2-1) - OFFLINE: plan `plan_ring_p5s02d.json` for the groups J + K3 only (K3f onward is a later step)

`labview: none`, no `--launch`, no `tools/hooks` edit, no edit of `tools/stagekit.py`, `stagexec.py`, `stagesim.py`, `stage_prerun.py`, `stage_shared.py`, `prep_plan_flow_lib.py`.
Card 164-a2-1 did Parts 1, 2 and 4 and is FINAL for them (facts `tools/bench/diag_c164_a2_1_facts.md`, read it): r_in is now `4d93c82d` (dst-only frame on A69/A79; compares 8/0), the compile
ACCEPTS the dst-only K3/K4 shape, `#31517` is quoted, card 158-a3-3 is retired. Do NOT redo them. What failed: its maker passed all five groups, the prefix rule (MAIN + rows only) chose all 28 rows
(A53..A80), and the route check then raised 2 UNROUTABLE: K3f A70 (k14, w_k3f -> #8776) and K4f A80 (k20, w_k4f -> #24342), both the INNER face of a LoopTunnel (`stagexec.py:1930`). That is a
measured fact about K3f/K4f, not something to fix here. Decision (assignment session, written assumption, PD397(c) "groups left over become the next step"): this step takes the longest whole-group
prefix that is ROUTABLE, which is **J + K3 (A53..A69, 17 rows, MAIN 642.5)**; K3f, K4, K4f are left for the next step.

## Do
1. Current `tools/bench/plan_ring_p5s02d.json` e3054ab6 is a Final-False file: copy it aside as `plan_ring_p5s02d_all28_false.json` (md5 quoted). `plan_ring_p5s02d_jonly.json` 1152ce60 stays.
2. `tools/bench/prep_c164_a2_2_mk.py` (<= 60 lines): copy of `prep_c164_a2_1_mk.py` with the group list `["J","K3"]` (CALL `prep_plan_flow_lib.make_step_plan`; no other change; the old maker is not edited). The prefix rule then
   tries J, then J+K3. Run it. The plan is written ONLY by `stagesim.simulate`.
3. Gates quoted with PASS/FAIL: ROWS, SB (REALSIM final True on 3d5196ab, failed None, all actions replayed, 0 PROVISIONAL, route check PASS, 0 UNROUTABLE), C compile (op list + checkpoints; the pass-wire
   op for K3 = `connect_term_uid` `register_end_case_border`), X10 MAIN, X8 control_path_lint, X17, no-group-split, action id range. The STUB gate: state whether it still fails for this prefix (it must not, K3f is not in it).
4. If J+K3 fails any gate other than STUB: FAIL, return the first failing line, write nothing else. Do NOT try a different prefix or shape and edit no tool.
5. On success also write `prep_c164_a2_2_session.json` (the maker does it) and compute the K3-group Error-List-relevant fact the later pred needs: the list of plan action ids A53..A69 with their op kinds (from the compile).

## Report `tools/bench/diag_c164_a2_2_facts.md` (<= 30 lines, facts only)
md5 of every output; MAIN and rows for J and J+K3; plan md5 + final + REALSIM line; route rows (k, op, route) and the UNROUTABLE count; compile ops + checkpoints; STUB line; the
UNCHANGED md5 list (tools, memory_model, graph 3d5196ab, EL 26d45c71, r_in 4d93c82d, VIs); `OPEN:` lines with file:line (include: K3f/K4f inner-face route needs a decision before the next step).
