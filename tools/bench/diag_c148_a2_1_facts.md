---
card: 148-a2-1
date: 2026-10-08
status: current
---
# 148-a2-1 facts - fp-60 (assignment env leaks into self-tests), T0b re-pin

## Measurement (before any edit) - `tools/bench/diag_c148_a2_1_measure.log`
- This material session's own env: CYCLE_SESSION=1, CYCLE_ROLE=assign, ASSIGN_STATE=tools/bench/assign/state_148_2.json (log:3). The leak path is inherited env.
- Copy of state_148_1.json (c3edbffd) at tools/bench/diag_c148_a2_1_tmp/state_copy.json, its sticky handback cleared (else check_dispatch returns before writing). selftest_chat_p1.py under the leaked env: rc 1, 37/46 (log:7).
- The copy GAINED `handback c-outside-purpose: card p1s-A: flags.write ['tools/**','docs/**','.claude/agents/**'] reaches the PLAN file docs/d1/ring-p4c.md` (log:8). This is the same text as state_148_1.json:47. Leak confirmed (M1 ok, log:9). Live state_*.json md5 unchanged (log:10).

## Edits
| edit | path:line |
|---|---|
| card outside tools/bench/cards (env ASSIGN_CARDS_DIR overrides) is logged to guard_assign_ignored.log beside the state and refused with no state write | tools/hooks/guard_assign.py:387 (helpers :360-376, docstring :32-35) |
| module-level drop of ASSIGN_STATE/CYCLE_ROLE/CYCLE_SESSION | selftest_assign_flow.py:53, selftest_chat_p1.py:48, selftest_chat_p2.py:42, selftest_guard_session.py:43, selftest_guard_session_pairing.py:42 |
| assign_flow throwaway states name their cards dir on purpose (ASSIGN_CARDS_DIR) | selftest_assign_flow.py:119, :337 |
| T0b re-pinned to licence 7f70bbf9 (the 5 rename keys == L5) | selftest_c147_b1_2.py:123 |
| new self-test L1-L5 | tools/bench/selftest_c148_assign_leak.py |
Census by grep: selftest_c148_guard_fp.py imports guard_assign in-process only and spawns no hook, so it was not edited.

## New self-test selftest_c148_assign_leak.py
- pre-edit (HEAD hooks + self-tests): rc 1, 2/5; L1, L4, L5 fail (diag_c148_a2_1_leak_pre.log)
- post-edit: rc 0, 5/5 (diag_c148_a2_1_leak_post.log)
- post-edit self-tests + the PRE-EDIT guard_assign copy (diag_c148_a2_1_tmp/guard_assign_pre.py, eb8ba4d6): rc 1, 3/5; L1, L4 fail (diag_c148_a2_1_leak_precand.log)

## Existing self-tests, assignment env stripped (pre: diag_c148_a2_1_pre.log, post: diag_c148_a2_1_post.log)
| self-test | pre rc / count | post rc / count |
|---|---|---|
| selftest_assign_flow | 0 / 16/16 | 0 / 16/16 |
| selftest_c148_guard_fp | 0 / 6/6 | 0 / 6/6 |
| selftest_guard_session | 0 / 27/27 | 0 / 27/27 |
| selftest_guard_session_pairing | 0 / 10/10 | 0 / 10/10 |
| selftest_chat_p1 | 1 / 44/46 (t_binds FileNotFoundError, O1) | 1 / 44/46 same two |
| selftest_chat_p2 | 1 / 23/24 (t_soft_alert FileNotFoundError) | 1 / 23/24 same |
selftest_c147_b1_2: rc 0, 17 pass / 0 fail (diag_c148_a2_1_c147.log).

## fp-60
`py tools/gate_fp.py drain --id fp-60 --fixed tools/hooks/guard_assign.py:387 --selftest selftest_c148_assign_leak` -> DRAINED.

## md5
guard_assign bbaa2325 (was eb8ba4d6); assign_flow 47906beb; chat_p1 8753ee8a; chat_p2 69460108; guard_session_pairing 45592a58; guard_session selftest d4f63b2f; c147_b1_2 1dd09f3d; leak test 76c84f49; driver diag_c148_a2_1_run.py 5074981e. Invariants unchanged: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, licence 7f70bbf9, recipe d947df5d, guard_session.py e1b661b5. All 12 live state_*.json md5 identical at start and end (state_148_2 d6cc8779). LabVIEW processes: 0 before and after every run.

OPEN: a card outside tools/bench/cards is REFUSED, not allowed. The brief's "ignored" was read as "no state write". chat_p1 (t_binds, O1) and chat_p2 (t_soft_alert) fail the same way before and after this card, and that is not diagnosed here.
