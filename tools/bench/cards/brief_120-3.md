# brief 120-3 — Dequeue and Case-in-loop-body plan routes (OFFLINE prep, PD237(k))

`labview: none`. Code + offline self-tests only; the scratch verification in LabVIEW is a later card.

Facts (120-1): Dequeue and a Case structure inside a loop body exist in gscript only — `gscript.queue_node('dequeue')`
(`tools/gscript.py:1339-1359`) and `gscript.case_in` (`tools/gscript.py:3508`), with `case_frames` (`:3479`). stagexec's
create route for queues accepts only `obtain|enqueue` (`tools/stagexec.py:306-307`, `CREATE_ROUTES` `:198`).

- **R1 Dequeue:** extend the stagexec queue create route to `queue_kind: dequeue`, following the Enqueue route built
  in cycle 118 (PD234(i): the creator's automatic tunnel when the queue refnum comes from outside the loop), and the
  matching stagesim model (the node, its terminals `queue`, `timeout in ms`, `element`, `timed out?`, `error in/out`
  with the names gscript's op actually yields — cite where the names come from; if no measured sample exists, mark the
  terminal names UNMEASURED so the scratch card measures them).
- **R2 Case in a loop body:** a create route `case_in` (a Case structure placed in a given loop body with a boolean
  selector source, frames False/True), plus routes to (i) wire from outside into a frame (input tunnel), (ii) wire from a
  frame to outside (output tunnel; both frames must be wired or the tunnel is "use default if unwired" — record which the
  model assumes, and mark it UNMEASURED if no sample exists), (iii) place a node INSIDE a given frame. stagesim models
  for each.
- **R3** Self-tests: extend `selftest_stagexec*` / `selftest_stagesim*` style tests (fake COM, no LabVIEW) for R1 and R2,
  plus the full existing stagexec/stagesim self-test suites re-run: 0 new failures against the counts on record
  (`tools/bench/selftest_stagesim_c118d.log`, `tools/bench/selftest_stagexec_c118d.log`); name any pre-existing failure.
- **R4** Additive only: every existing route and its behaviour unchanged (a LabVIEW card may be importing stagexec at
  the same time; do not rename or move anything).
- **R5** Write `tools/bench/scratch_plan_c120_routes.md`: the ≤ 120-line scratch-VI check a later LabVIEW card runs to
  verify R1/R2 (what it builds, what it reads back, pass criteria) — the plan only, not run.
