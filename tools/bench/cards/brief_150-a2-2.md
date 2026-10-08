---
card: 150-a2-2
status: current
date: 2026-10-08
---
# Brief 150-a2-2 - retry of 150-a2-1: the direction part of rebind's old-terminal key; offline, ALONE

Read first: `tools/bench/cards/brief_150-a2-1.md` (the whole change, unchanged unless stated here) and `tools/bench/diag_c150_a2_1_facts.md`.
`tools/stage_prerun.py` is already edited by 150-a2-1 (md5 3e5fdd53, key at :3832-3846, `renamed_old` :3805, RENAMED-OLD log :4294-4295). KEEP that edit and
amend it; do NOT revert to dcd45aba. Pre-edit records `selftest_rebind_c150_pre.{log,json}` stay the reference for R1-old and R4.

## Measured (150-a2-1): what failed
Post-edit R1: `BINDING: the created objects differ (name-free shape): ['LoopTunnel x0 simulated vs x3 real']` (BuildArray fixed). R2: 4 of 5 renames listed;
t9505 on #9503 is not matched as old. Context: `prep_c147_a1_3_rebase.log:12` `BASE-FLIPS seeded 6 terminal(s) on 3 undirected tunnel(s): [9503, 10177, 29777]`
- an undirected tunnel's terminals have no stable `is_source` before they are wired, so `is_source` is not an identity.

## Decision for this retry (judgement-assumption, written down per CLAUDE.md 2c; the judgement session may overturn it)
Old-terminal identity = (term_uid, owner_uid, term_class). `is_source` is COMPARED for an old terminal and a difference is an INFO line, never a refusal and never a
reason to file the terminal as created: `FLIPPED-OLD <uid> #<owner> src <a>-><b>` in `info['flipped_old']` (add to the info.update default), logged by the CLI beside
RENAMED-OLD. NEW is still decided by (uid, owner) not being in `before`; a CLASS change at the same (uid, owner) still refuses (R3a). Everything else as 150-a2-1.
FIRST MEASURE (one line each, from the actual rows, before editing): for the 3 real LoopTunnels in `real_new` after the 150-a2-1 edit, which uids/owners are they,
and is `is_source` the only attribute that differs from the `before` row? If something other than is_source differs, STOP and RETURN with the diff - do not edit.

## Self-test changes (`tools/bench/selftest_rebind_c150.py`, <= 120 lines)
R1 new code binds s07 onto the real s06 (and the old code refuses, from the pre record). R2 `renamed_old` = exactly the 5 measured renames. R3a class change at
the same (uid, owner) refuses. R3b a synthetic direction flip of an OLD NON-tunnel terminal is an INFO line (`flipped_old`), not a refusal. R4 s05->s06 same node map
as the pre record (30 uid pairs). Add a count of `flipped_old` for the s06->s07 inputs to the facts file.

## Regression, invariants, return conditions: as 150-a2-1 (BEFORE counts are the 150-a2-1 AFTER logs `prep_c150_a2_1_<t>_after.log`; selftest_rebase_uidreuse_c143_4
is already 2/2 + KeyError rc 1 before and after, pre-existing, same counts = pass). stage_prerun old md5 for this card = 3e5fdd53; quote new. No hook edit.
After the self-test passes ALSO run, offline, `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s07v18.json --graph tools/bench/graph_ring_p4s06_20261008_192149.json`
ONLY IF it writes nothing outside `tools/bench/sim/ring_p4_s07v18*` and the plan's base (that is the next card's job: DO NOT run it here; R1 covers the binding).

## Report: append to `tools/bench/diag_c150_a2_1_facts.md`? NO - write `tools/bench/diag_c150_a2_2_facts.md` (<= 30 lines): the measurement, diff line ranges, R1-R4 (+R3a/R3b), regressions, md5 table, `OPEN:` line.
