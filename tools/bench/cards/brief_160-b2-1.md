---
card: 160-b2-1
status: current
date: 2026-10-10
---
# Brief 160-b2-1 (assignment 160-1) - OFFLINE DIAGNOSIS: why does the route check refuse routes 4 and 7 of `plan_ring_p5s02b.json` ("node #24083 not in Diagram[124].Nodes[]")

`labview: none`: read files only, no LabVIEW process, no tool/recipe/plan edit, no `tools/hooks` edit. You write ONE file: `tools/bench/diag_c160_b2_1_facts.md`
(+ a throwaway `tools/bench/diag_c160_b2_1*.py` reader if you need one). `docs/script-writing.md` binds you (call shared functions: `tools/vigraph.py`, `tools/stagesim.py` readers).

## What is known (card 160-b1-1, `tools/bench/diag_c160_b1_1_facts.md`, `tools/bench/prep_c160_b1_1_mk.log:49-54`)
`plan_ring_p5s02b.json` (18 actions on the real graph `tools/bench/graph_ring_p5s02a_20261010_032547.json` = 94ffff94) replays 18/18 in REALSIM, but the route check
refuses 2 rows: route 4 (acts 8-10 `t_go`, `w_gout`, `w_gr`) and route 7 (acts 15-17 `t_ho`, `w_hout`, `w_hr`), message raised at `tools/stagexec.py:1920`
(`node not in uids` after `self.rd.node_uids(didx)`). #24083 and #24150 are the RIGHT shift-register nodes whose stub terminals (t24139, t24235) the MERGE rows A32 / A39
(`w_gr`, `w_hr`) connect to. The LEFT-register rows A28 / A35 (`w_gl`, `w_hl`, onto LSR #24133 / #24187) route fine as `cfw`. Routes 1,2,3,5,6,8 pass.

## Measure (facts, no decisions)
1. In the saved graph: for terminal rows t24139 and t24235 print `owner_class`, `owner_uid`, `term_class`, `term_name`, `is_source`, `wire_uid`; for #24083/#24150 their
   `owners` entry and parent loop; and the same for the LEFT pair (#24133 / #24187 and their terminals) for contrast.
2. Read `tools/stagexec.py` around :1860-1925 (the address resolution; `SR_CLS`, `FACE_ROUTED`, `loop_of`, `tunnel_owner`) and state, line by line, which `if` the RSR
   terminal t24139 fails to enter and why it falls through to the `Nodes[]` lookup (a `term_class` other than `OuterTerminal`? `loop_of` content? the route kind `tunnel`
   vs `cfw`?). Quote the lines. Also say which route kind (`tunnel` / `cfw` / `case_frame_wire`) the compiled op for act 10 takes and where that is decided
   (`stagexec.py` compile of a `wire` whose dst is on a register face).
3. Find EARLIER passing precedents in the repo of a wire onto a RIGHT-register face (inner or outer): `grep` the plan files `tools/bench/plan_ring_p*.json`, opmodels in
   `tools/bench/opmodels/*.json`, `docs/NAMES.md`, `docs/d1/ring-p5*.md` for `RightShiftRegister` / `RSR` / `add_shift_reg` sinks; quote file:line of the one that PASSED the route
   check (or LabVIEW) and the address form it used. If none exists say "no precedent found" and list the search commands.
4. List the options as facts (each with what file it would touch and whether it needs a NEW LabVIEW measurement): (a) a plan-only change (different source/sink direction,
   a different action kind or address form for the same wire), (b) a router extension in `stagexec.py` for this face, (c) anything else you find. State for each whether it
   changes any per-bead computation (it must not: rule 1a) and what the REALSIM / sim end result would be. Do NOT choose; end with `OPEN:` lines.

## Report `tools/bench/diag_c160_b2_1_facts.md` (<= 40 lines, facts only)
Rows of measure 1, the quoted lines of measure 2, the precedent (or none) of measure 3, the options table of measure 4. md5 UNCHANGED (before/after): `tools/stagekit.py` 1441bb4c,
`tools/stagesim.py` a3261b56, `tools/stagexec.py` c4a6e0b6, `tools/stage_prerun.py` 7605116f, `tools/bench/plan_ring_p5s02b_in.json` 56bfddd3; VIs 94ffff94 / s09 eb1d0f31 /
P5-1a 2482fe7b / P5-1 7f2582ae unchanged (md5 of the files, no LabVIEW); `tools/hooks` untouched.
