---
card: 149-a2-1
status: current
date: 2026-10-08
---
# Brief 149-a2-1 - PD361(b) discriminator, then PD361(c) hand-back provenance + pre-fix wrapper env (tooling, ALONE, no LabVIEW)

Plan of record: `docs/d1/ring-p4c.md` PD361(b)(c), PD362(e). No LabVIEW process may exist before, during or after (`tasklist`).
Run ALONE: no other card live.

## Step 1 - PD361(b), a measurement, BEFORE any edit
The second "p1s-A" hand-back was written at 2026-10-08 16:47:46 KST (t 1791445665.97, `tools/bench/assign/state_148_3.json`).
Quote, from the wrapper's own run times in `tools/bench/diag_c148_a3_1_suites.log` / `.py`, which child (tree PRE or NOW, suite) was
running at that second. Facts only: tree, suite, start/end times, the line numbers. A NOW child is a RETURN (status FAIL, first_fail
"NOW child at 16:47:46"): then make NO edit of step 2 and stop.

## Step 2 - PD361(c), only if step 1 names a PRE child
1. `tools/hooks/guard_assign.py` (md5 bbaa2325): a state hand-back is honoured only when it carries provenance - the dispatched card's
   path under `tools/bench/cards/` and its id (the format the fixed code writes; read the writer first). An entry without it is LOGGED
   and IGNORED. Keep the existing trigger classes and messages otherwise.
2. `tools/bench/diag_c148_a3_1_suites.py` (the reference wrapper that runs a pre-fix tree): remove `ASSIGN_STATE`, `CYCLE_ROLE`,
   `CYCLE_SESSION` from every child's environment.
3. NEW `tools/bench/selftest_c149_handback_provenance.py`: feeds an old-format hand-back (no provenance) into a state COPY under %TEMP%;
   it must FAIL on the pre-edit guard_assign.py (bbaa2325, kept as a %TEMP% copy) and pass after. Quote rc and counts of both runs.
4. Existing self-tests `selftest_guard_assign*.py` (if present), `selftest_guard_session.py`, `selftest_guard_session_pairing.py`,
   `selftest_chat_p1.py`, `selftest_chat_p2.py`, `selftest_assign_flow.py`, `selftest_c148_assign_leak.py`: run BEFORE the edit and AFTER;
   rc 0 or the same counts. A new difference is a RETURN, not a fix in this card. Never point any test at a live `tools/bench/assign/state_*.json`.

## Close
Invariants as `tools/bench/diag_c149_a1_2_inv.log` (stagekit, stagexec, gscript, elrule, errorlist_check, s06 569ffbf5, s05 3f9ac26b,
s04 95e408ff, s03 282301ca, bed 39511877, memory_model 88eeb037) unchanged; `adopted_scratch.jsonl` unwritten; no `claudeDev` file touched.
Report `tools/bench/diag_c149_a2_1_facts.md` (<= 40 lines): step-1 quote, edits with path:line, before/after self-test table, invariants.
`OPEN:` line. Facts only.
