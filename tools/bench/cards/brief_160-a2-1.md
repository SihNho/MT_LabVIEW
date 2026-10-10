---
card: 160-a2-1
status: current
date: 2026-10-10
---
# Brief 160-a2-1 (assignment 160-2) - OFFLINE: widen the delete branch to "Wire with no source row"; route a BASE register inner face like a plan-made one (PD391(b)(c))

`labview: none`: no LabVIEW process, no stage launched, no `tools/hooks` edit. Read `docs/d1/ring-p5b.md` PD391(a)(b)(c) and `docs/script-writing.md` first
(shared functions are CALLED; a NEW function carries a docstring naming its self-test). You edit `tools/stagesim.py` and `tools/stagexec.py` ONLY among the tools;
`tools/stagekit.py` (1441bb4c), `tools/stage_prerun.py` (7605116f), `tools/addrcheck.py`, `tools/vigraph.py` stay byte-unchanged.
Facts you need are already measured: `tools/bench/diag_c160_b2_1_facts.md` (why routes 4/7 fail, `stagexec.py:866-877`, `:1918-1920`, precedent `diag_c154_p5s01a_scratch.log:229`).

## Step 0 - baseline BEFORE any edit (a file, not a memory)
Write `tools/bench/diag_c160_a2_1_baseline.py` + `.json`: compile `plan_ring_p5s01a.json` and `plan_ring_p5s01b.json` with the CURRENT `stagexec.compile_plan` the way
`tools/bench/selftest_c158_runcheck.py` / `diag_c160_b1_1` do (real owners from the saved graph the plan was made on, not a stub), and store the full op lists
(kind + all args) plus, for each, the list of dict ends that are NOT a register face. This is the "before" side of pass items 4-5. Do it before touching stagexec.

## Part 1 - delete branch: from "0 terminal rows" to "a Wire with NO SOURCE terminal row" (PD391(b))
`stagesim.op_delete_wire` and `stagexec`'s `delete_wire` compile (the branch card 160-a1-1 added; find it, do not re-derive): the condition becomes "uid is a Wire object
in the CURRENT state and has no terminal row with `is_source` true" (0 rows, or sink rows only). Simulator effect for a sink-only wire: the Wire object is removed, its
sink rows STAY with `wire_uid` 0 (unwired), no pair changes (a sourceless wire has none), nothing else moves. A Wire WITH a source row keeps today's path (terminal-resolved
delete) or is refused exactly as before; absent uid and non-Wire uid unchanged. The live act is still `stagekit.delete_wire` uid path - call it, no `remove_bad_wires`.
"Already gone" is never a successful delete.

Self-test: extend `tools/bench/selftest_c160_delwire.py` (12/0 today) on the saved 94ffff94 graph `graph_ring_p5s02a_20261010_032547.json`. New cases, each quoted:
(T-a) delete w10394, w24264, w24300 (one plan, in that order): all three gone, t24139 and t24235 are unwired (wire_uid 0, rows kept), every other terminal row and every
(source, sink, frame) pair equal before/after (use the shared pair/row functions the existing cases use); (T-b) w24285 (a source-only stub: LSR #24133 source t24190)
and one wire with both a source and a sink row are refused or take the old path - show which, by comparing with the pre-edit result recorded in Step 0 style (the temp
copy of the unedited files, deleted at the end, as 160-a1-1 did); (T-c) T1..T5 of the old suite unchanged. Print `RESULT <pass>/<fail>`; the old 12 stay green.

## Part 2 - compile: a BASE register inner face as the dict end of a tunnel group (PD391(c))
In `stagexec`'s compile (`:865-877` region), a dict end that is the `InnerTerminal` of a base-graph `RightShiftRegister` / `LeftShiftRegister` must compile exactly like a
plan-made `srR` / `srL` symbol: to a `connect_term_uid` op taking the `register_end_case_border` branch (`:868-874`). The register's identity (node uid, side) is read from the
graph rows by a shared lookup (`base_registers` / `loop_of` already exist in the route state, see `diag_c160_b2_1_read.log:22-23`) - do not retype uids. Correct the stale
docstring at `stagexec.py:32` in the same edit. If `stagesim` shares the compile or has its own copy of that decision, change it identically; if it has none, say so.
No edit to `Addr._triple` (option b2 is not used).
Self-tests (new file `tools/bench/selftest_c160_regface.py` + `.log`, `RESULT n/0`):
(R1) build a temporary plan = `plan_ring_p5s02b_in.json` plus `delete_wire` rows for w24264 before A32 and w24300 before A39 (uids read from the t24139 / t24235 sink rows of
the graph, not typed; name it `diag_c160_a2_1_plan_tmp.json`, NOT `plan_ring_p5s02b*`); run `stagesim.simulate` + the route check on the 94ffff94 graph: routes 4 and 7 must be
ROUTABLE, 0 UNROUTABLE, and say the compiled op kind for each; (R2) `plan_ring_p5s01a.json` and `plan_ring_p5s01b.json` compile to op lists IDENTICAL to Step 0's json
(compare programmatically; print the two md5s); (R3) a plan row whose dict end is NOT a register face compiles as in Step 0; (R4) the same dict end on an LSR face
(A28/A35 shape) still compiles as before the edit (MERGE rows stay `cfw`, PD391(d)).
If R1 cannot pass without a change outside `compile`/`stagesim` shared with it, STOP and return FAIL with the line (no `Addr._triple` edit, no design fallback: PD391).

## Then, on the NEW bytes
Re-run `selftest_c159_cen2_ends.py` (8/0), `selftest_c158_runcheck.py` (10/0), `selftest_c158_wire0face.py` (24/0), `selftest_c160_delwire.py` (12 + new), `selftest_c160_stagemap.py` (5/0).
They pin `stagesim`/`stagexec` md5 prefixes: re-pin ONLY the prefixes this edit moved (edit the PINS dict and its docstring line naming old -> new). A count that differs
from its last pass is a FAIL of this card, not a re-pin. Every other file pinning a moved md5 (`selftest_c156_passwire`, `selftest_c155_basecase_frame`,
`selftest_c156_b2_2_invcheck`, ...) is listed as `OPEN:` with file:line - a later card re-pins them.

## Report `tools/bench/diag_c160_a2_1_facts.md` (<= 40 lines, facts only)
file:line of each change in stagesim and stagexec; the self-test result lines (delwire, regface, the four re-run suites) with old -> new pins; md5 before/after of stagesim and
stagexec; md5 UNCHANGED: stagekit 1441bb4c, stage_prerun 7605116f, addrcheck 207beb0d, vigraph a7eb58c7, `plan_ring_p5s01a.json`, `plan_ring_p5s01b.json`; VIs 94ffff94 / s09 eb1d0f31 / P5-1a 2482fe7b /
P5-1 7f2582ae unchanged (md5 of the claudeDev paths may be refused by the permission layer: then say "not hashed", do not work around); `tools/hooks` untouched. `OPEN:` lines.
