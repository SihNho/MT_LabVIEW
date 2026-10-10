# Brief 158-a1-1 (assignment 158-1): PD384(a)(b) tool fix, offline - wire-0 live act and run-closing checkpoints

Read first: `CLAUDE.md`, `docs/script-writing.md`, `docs/d1/ring-p5.md` item 384 (a)(b) and item 381, and
`tools/bench/diag_c157_a1_1_facts.md` (what card 157-a1-1 built and its three OPEN lines, which this card closes).
Base pins: stagexec 69b1a301, stagekit 0d8f6d25, stagesim eb99c6ba, addrcheck 207beb0d, stage_prerun 9decb20f. No LabVIEW,
no hook edit, no recipe / plan / pred / licence / P5 file edit. Rule 1a: only how stage tools ADDRESS a wire and what they
PRINT changes; no VI content or computation.

## What to build (two parts; the tools are the deliverable; call the existing functions, do not copy them)
**(a) Live act for an UNWIRED loop inner face.** `loop_inner_face_route` (`stagexec.py:1626`) returns route kind `cfw` for a
wire-0 inner face of a While/For LoopTunnel. The live act for `cfw` (`stagexec.py:3134-3136`) calls `_cfw(int(rs["wire_uid"]),
...)` = `_cfw(0, ...)`; there is no wire to branch (157-a1-1 OPEN 1). Change it so that:
- face WIRED -> `cfw` exactly as now (same call, same arguments);
- face UNWIRED (the `src_wire0` info flag) -> the term-to-term act of the `else` branch (`stagexec.py:3137-3146`,
  `connect_nested_v1`), with the SOURCE triple = (body diagram index, node index, terminal index) of the inner face on the
  owner loop's body diagram, taken from the graph/owners the route already used (`src_diag`, `src_loop`), the same DST triple
  as the wired case. Read how `info["src"]` is built for the `nested` route and build the same triple; one function, called
  from the act, with a docstring naming its self-test (script-writing.md rule 1 and 9).
- Case / Flat Sequence inner faces still stop with the existing text (157-a1-1 C1-C3 stay green).
The route function may keep returning a route for a wire-0 face; the change is what the ACT does with it. If a recorded graph row
needed for the triple is missing, RETURN with the row you could not find (failure budget 2) instead of guessing a shape.

**(b) Checkpoint rule = run-closing ops (PD384(b)).** `stagexec.checkpoint_ops` (`stagexec.py:2028`) now puts every `move_in` op
in the set. Change it: the checkpoint is the LAST op of each maximal run of consecutive `move_in` ops (a `move_in` followed
by a non-`move_in` op, or the last op of the plan, closes its run). BIND_KINDS ops, op 0 and the last op stay as now.
FATE lines (`fate_lines`, `stagexec.py:2036`, called from `Executor.run`): for a run, the FATE lines of EVERY `move_in` in the run
come from the run-closing op's read, compared with the checkpoint read before the run (the `prev_terms` of the run's first op);
the line format is unchanged and `step=<n>` stays the plan step of that move_in. A `move_in` not closing its run no longer prints
`FATE-UNREAD`. The Executor REFUSES before op 1 (ExecStop CHECKPOINT, like the add_sr/tunnel rule at its docstring) a caller-supplied
checkpoint set that lacks the run-closing op of any `move_in` run (157-a1-1 OPEN 3).
`stagekit.RingSession` keeps calling `checkpoint_ops` (`stagekit.py:1929`); touch stagekit only if that call needs it.

## Measure, in this order (report all as FACTS)
1. BEFORE any edit: store the op lists of every stored plan the way `tools/bench/prep_c157_a1_1_regress.py` does (reuse it by
   CALL or extend it; its before/after logs `prep_c157_a1_1_*.log` show the form), and the suite counts it prints.
2. After the edit: the same. Every stored plan compiles to the SAME ops; suite counts unchanged except what is listed below.
3. New `tools/bench/selftest_c158_runcheck.py` on recorded data (the sim steps under `tools/bench/sim/ring_p5s02a/`, the graph
   owners the c157 self-test used): (i) ops 16 and 17 of `plan_ring_p5s02a.json` through the ACT path on the sim backend:
   wired -> `cfw` with the DST triple (1,1,6) / (1,1,9); wire 0 -> `connect_nested_v1` with a SOURCE triple on body #23405 of
   WhileLoop #23041 and the SAME dst; (ii) Case/FS inner face with wire 0 still stops (reuse C1-C3 by call); (iii) p5s02a
   `checkpoint_ops` = (0,1,3,6,8,9,12,15,16,17); (iv) a set missing 12 (or 17) is refused before op 1 by the Executor
   (dry/sim backend); (v) FATE lines of ops 10-12 come from the op-12 read and still give the six M3 wires.
4. Re-pin ONLY the md5 strings in the pinned self-tests that fail on the stagexec/stagekit pin and nothing else:
   `selftest_c155_basecase_frame.py:206`, `selftest_c156_passwire.py:161`, and the pins inside `selftest_c157_innerface.py` if any
   (this card's globs include them); `selftest_c157_innerface.py` case (iv) (the old "every move_in" list) is UPDATED to the new
   rule and its change is stated in the facts. Counts after: c155 21/0, c156 20/0, c157 13/0 (or the stated new total).
5. Report the new md5s of stagexec / stagekit (stagesim, addrcheck, stage_prerun must be unchanged).

Facts file `tools/bench/diag_c158_a1_1_facts.md` (<= 45 lines, facts only, an `OPEN:` line per unresolved thing, with the
before/after op-list and suite lines as file:line). Return the standard <= 30-line summary. Failure budget 2.
