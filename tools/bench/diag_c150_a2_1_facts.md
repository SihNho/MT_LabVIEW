---
type: facts
status: current
date: 2026-10-08
---
# Card 150-a2-1 facts: name-free rebind key fixes BuildArray #2626, but the DIRECTION part of the key now refuses LoopTunnels (FAIL)
Offline, no LabVIEW. Self-test `selftest_rebind_c150.py` (30a4dc5a). "Old code" = `git show HEAD:tools/stage_prerun.py` (md5 dcd45aba) exec'd in memory.
## Edit (stage_prerun.py dcd45aba -> 3e5fdd53; py_compile rc 0, prep_c150_a2_1_compile.log)
- :3786-3789 docstring; :3805 `renamed_old: []` in the info.update default; :3832-3846 key = (uid, owner, term_class, is_source) + renamed_old;
  :4294-4295 `RENAMED-OLD <uid> #<owner> 'a'->'b'` log after REUSE-NOTED. Nothing else.
## Pre-edit (selftest_rebind_c150_pre.log, 6/0, rc 0)
- R1 old and unedited code both refuse: `BINDING ... ['BuildArray x0 simulated vs x1 real', 'LoopTunnel x2 simulated vs x3 real']`.
- R4 s05->s06 binds, map_nodes == prep_c147_a1_3_rebase.log:4 (8 nodes), 30 uid pairs recorded in selftest_rebind_c150_pre.json (64e2e1fb).
## Post-edit (selftest_rebind_c150_post.log, 5/2, rc 1) - prediction FAILED
- R1 new code: `BINDING: the created objects differ (name-free shape): ['LoopTunnel x0 simulated vs x3 real']` (BuildArray mismatch gone).
- R2 renamed_old = 4 of 5: (2832,2626),(4160,2626),(4165,2626),(9508,9503); t9505 on #9503 NOT matched as old -> its class or direction differs.
- R3 class change and direction change of t2813 at (2813,#2626) each refuse (PASS). R4 map_nodes and all 30 M pairs == pre record (PASS).
- Known context, not re-diagnosed: prep_c147_a1_3_rebase.log:12 `BASE-FLIPS seeded 6 terminal(s) on 3 undirected tunnel(s): [9503, 10177, 29777]`
  - three undirected LoopTunnels whose terminal direction is seeded/flipped; 3 = the real count in the new refusal. Not measured here which 3 nodes.
## Regression (before -> after, logs prep_c150_a2_1_<t>_before/_after.log)
- selftest_rebind_c142_5 4/0 -> 4/0 rc 0; selftest_rebind_c132_5 7/0 -> 7/0; selftest_rebase_c132_6 8/0 -> 8/0.
- selftest_rebase_uidreuse_c143_4 2 pass/2 fail + KeyError 'sim_of', rc 1, NO RESULT LINE -> identical after (U1/U2 'base is not provisional'; pre-existing).
## Invariants (md5 after = brief values): stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, graph a3ecb92b, plan s07 10a4f59a,
prov148 aeae610e, memory_model 8eec443c, adopted_scratch 658fe5b9. s06/s05/bed VIs: no LabVIEW process, claudeDev not touched, not re-hashed.
Hook: guard_write flagged card 149-a3-4 pin of stage_prerun dcd45aba (no result, not bound) - logged fp-64, edit not blocked.
OPEN: the decided key's DIRECTION component misfiles undirected-tunnel terminals as created - key (uid, owner, term_class) without direction, or keep
direction and treat a flip on an old terminal as info like a rename? (R3's direction sub-case depends on the choice.)
