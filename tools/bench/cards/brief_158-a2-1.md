# Brief 158-a2-1 (assignment 158-2): PD385(a)(b)(c) tool fix, offline - wire-0 loop inner face act = `connect_term_uid`

Read first: `CLAUDE.md`, `docs/script-writing.md`, `docs/d1/ring-p5.md` item 385 (all of it) and item 384 (a)(b), then
`tools/bench/diag_c158_a1_1_facts.md` (card 158-a1-1: why `connect_nested_v1` could not be used; probe log
`tools/bench/prep_c158_a1_1_probe.log:3-8`), `tools/bench/diag_c158_a1_2_facts.md` (checkpoints, already built: stagexec df82d75e),
`tools/bench/diag_c157_a1_1_facts.md` (`loop_inner_face_route`, the wire-0 `cfw` route and the three OPEN lines).
Base pins: stagexec df82d75e, stagekit 0d8f6d25, stagesim eb99c6ba, addrcheck 207beb0d, stage_prerun 9decb20f, gscript 1a80236e.
No LabVIEW, no hook edit, no recipe / plan / pred / licence / P5 file edit, no edit to `stage_prerun.py` or `gscript.py`.
Rule 1a: only how a stage tool ADDRESSES a wire and what it PRINTS changes; no VI content or computation.

## What to build (the tools are the deliverable; call existing functions, do not copy them)
**(a) The live act for an UNWIRED While/For LoopTunnel inner face.** Today `loop_inner_face_route` (`stagexec.py:1626`) returns
route 'cfw' with `src_wire0=True` for such a face, and the live `cfw` act calls `_cfw(int(rs["wire_uid"]), ...)` = `_cfw(0, ...)`
(`stagexec.py:3134-3136`) - there is no wire to branch. Change the ACT, not the route finder:
- face WIRED -> `cfw` exactly as now (same call, same arguments);
- face UNWIRED (`src_wire0`) -> ONE call of the existing terminal-uid op `gscript.connect_term_uid(target, sink_uid, src_uid)`
  (`tools/gscript.py:5141-5163`, OpConnectTermUid_v0), the way the existing `connect_term_uid` route does it
  (`stagexec.py:3500-3520`, `CONNECT_TERM_UID_HOW`): `src_uid` = the inner face's TERMINAL uid (`rs["term_uid"]`), `sink_uid` = the
  SAME `#376` input terminal uid the wired case uses (op 15's checkpoint read for ops 16/17), both read from the op's checkpoint
  read, not from the plan. Reuse the existing result checks (a wire came back; Is Broken? True; junk Invoke(s) left). One function
  for the wire-0 act, called from the act; its docstring names its self-test (script-writing.md rules 1 and 9).
- Case / Flat Sequence inner faces with wire 0 still stop with their existing text (157-a1-1 C1-C3 stay green).
- If a graph row the act needs (term uid of the face, dst term uid) is missing from the read, RETURN with the row you could not find.

**(b) Named census variant.** `ROUTE_CENSUS["connect_term_uid"]` (`stagexec.py:309`) gets ONE new named variant for a LoopTunnel
inner-face source (name it e.g. `loop_inner_face_wire0`). Its delta is NOT typed: it is computed from where the dst sits on the sim
graph - dst inside a Case frame -> the delta of `register_end_case_border` (SelectorTunnel 1, OuterTerminal 1, InnerTerminal 2,
Wire 2 - measured R1, `stagexec.py:310-311`); dst on the same diagram as the face -> `{"Wire": 1}`. Mark the variant UNMEASURED
in a comment AND in the value the op carries (so the scratch card can quote "predicted vs measured"). The recorded-variant
cross-check `selftest_case_frame_c124` U01 compares ROUTE_CENSUS with `census_samples.json`; do not break it - follow how the FS
variants are kept out of it (`stagexec.py:319-329`) and state what you did. `stagesim.py` and `addrcheck.py` are NOT in this card's
write globs; if the variant needs a simulator or address-check change, RETURN with the file:line and the exact change.

## Measure, in this order (report all as FACTS)
1. BEFORE any edit: store the op lists of every stored plan the way `tools/bench/prep_c158_a1_1_regress.py` does (reuse by CALL),
   and the suite counts it prints (stagexec 141/0, stagesim 106/0, selftest_c158_runcheck 10/0, etc.; the two known failing
   suites are case_frame_c124 28/1 and t6_regress 9/2 - record them as found). Compare against `tools/bench/sim/ring_p5s02a_c158/before.json`.
2. After the edit: the same. Every stored plan compiles to the SAME ops; suite counts unchanged except pin strings you re-pin.
3. New `tools/bench/selftest_c158_wire0face.py` on recorded data (the sim steps under `tools/bench/sim/ring_p5s02a/`, the graph
   owners `selftest_c157_innerface.py` used; reuse its fixtures by call): (i) ops 16 and 17 of `plan_ring_p5s02a.json` through the ACT
   path on a recording backend: face wired -> `cfw`, dst (1,1,6) / (1,1,9); face wire 0 -> `connect_term_uid` with src = the face
   term uid (#24360 / #24367) and sink = the SAME dst term uid as the wired case; (ii) Case and Flat Sequence inner face with
   wire 0 -> the existing stop text; (iii) the census variant for ops 16/17 is the register_end_case_border delta (dst in a Case
   frame) and is marked unmeasured; (iv) `checkpoint_ops(p5s02a)` still (0,1,3,6,8,9,12,15,16,17).
4. Re-pin ONLY md5 strings in pinned self-tests that fail on the stagexec/stagekit pin (`selftest_c155_basecase_frame.py:206`,
   `selftest_c156_passwire.py:161`, `selftest_c157_innerface.py`, `selftest_c158_runcheck.py` if any) and nothing else. Counts after:
   c155 21/0, c156 20/0, c157 13/0 (or the stated total), c158_runcheck 10/0.
5. Report the new md5 of stagexec (stagekit only if touched); stagesim, addrcheck, stage_prerun, gscript, hooks must be unchanged.

Facts file `tools/bench/diag_c158_a2_1_facts.md` (<= 45 lines, facts only, an `OPEN:` line per unresolved thing, before/after
op-list and suite lines as file:line). Return the standard <= 30-line summary. Failure budget 2.
