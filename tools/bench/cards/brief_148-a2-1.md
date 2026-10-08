---
card: 148-a2-1
status: current
date: 2026-10-08
---
# Brief 148-a2-1 - fix fp-60 (self-tests leak the assignment session's env into guard_session/guard_assign), then re-pin T0b (offline tooling card, ALONE)

No LabVIEW process. Plan of record: `docs/d1/ring-p4c.md` PD359(b)(c). Run ALONE: no other card is live. `tools/stagekit.py` (06b8d844), `stagexec.py` (1bab9cf9), `gscript.py` (1a80236e), `elrule.py` (a5ee7d5c), `memory_model.json`, the s06 plan/pred/in/licence/recipes and the plan file `docs/d1/ring-p4c.md` are NOT edited. The live `tools/bench/assign/state_*.json` files are NOT edited and NOT used as a test target.

## Authorised edits (PD359(b), fp-60 only)
`tools/hooks/guard_assign.py`; the self-tests that spawn `guard_session.py`/`guard_assign.py` (census by grep: `selftest_assign_flow.py`, `selftest_chat_p1.py`, `selftest_chat_p2.py`, `selftest_guard_session_pairing.py`, `selftest_guard_session.py` - confirm the list); one NEW self-test file `tools/bench/selftest_c148_assign_leak.py`. PD359(c): `tools/bench/selftest_c147_b1_2.py`, T0b ONLY (P0 is already re-pinned).

## Measurement FIRST (before any edit)
Copy a live state file (`tools/bench/assign/state_148_1.json`) to a throwaway path under `tools/bench/diag_c148_a2_1_tmp/`, record its md5, run `tools/bench/selftest_chat_p1.py` once with `ASSIGN_STATE` (and `CYCLE_ROLE`, `CYCLE_SESSION` as the assignment session has them) pointing at the COPY. Quote: did the copy gain a hand-back / refusal naming `p1s-A`? (the leak confirmed) or not (return with the facts and stop). md5 of every live `state_*.json` identical before and after.

## To produce
1. The measurement above (result quoted).
2. Fix, part 1: in every self-test of the census that spawns `guard_session.py`/`guard_assign.py`, the child's environment drops `ASSIGN_STATE`, `CYCLE_ROLE`, `CYCLE_SESSION` unless that test sets its own throwaway `ASSIGN_STATE` on purpose.
3. Fix, part 2: `tools/hooks/guard_assign.py` writes a hand-back only for a card file under `tools/bench/cards/` (any other path is logged and ignored, no state write).
4. New self-test `tools/bench/selftest_c148_assign_leak.py`: reproduces the leak with a throwaway state copy (a fixture card outside `tools/bench/cards/` + a polluted env), FAILS on the HEAD hooks/self-tests (show it by `git stash`-free means: run it against the pre-edit copy of `guard_assign.py` taken before step 3), passes after.
5. Existing guard_assign / guard_session / chat_p1 / chat_p2 / assign_flow self-tests: rc + counts before and after (rc 0 or the same as pre-fix).
6. fp-60 drained via `tools/gate_fp.py` (never hand-edit the queue).
7. `selftest_c147_b1_2.py` T0b (line ~123): edit to the current licence 7f70bbf9 (it carries the renames; expects the 5 rename keys). ONLY T0b. Run: 17 pass / 0 fail, rc quoted.
8. After: md5 list of every edited file and the invariant files; live `state_*.json` md5 unchanged; LabVIEW process count 0 before/after.

## Report (`tools/bench/diag_c148_a2_1_facts.md`, <= 40 lines)
Measurement result; table edit -> `path:line`; self-test rc/counts before/after; fp-60 status; md5 list; `OPEN:` line. Facts only.
