---
type: facts
status: current
date: 2026-10-08
---
# Card 150-a2-2 facts: rebind old-terminal key (uid, owner, term class); is_source change = FLIPPED-OLD info (PASS)
Offline, no LabVIEW process (tasklist 21:09). Retry of 150-a2-1; its 3e5fdd53 edit kept and amended.
## Measured first (prep_c150_a2_2_measure.py -> prep_c150_a2_2_measure.log:3-6, rc 0)
- Real rows whose 150-a2-1 key missed but (uid, owner) is in N's base: 3, all InnerTerminal on LoopTunnels:
  t29779 #29777, t9505 #9503, t10179 #10177; each before is_source False -> real True; ONLY is_source differs (term_name/wire ignored).
- = the 3 BASE-FLIPS tunnels of prep_c147_a1_3_rebase.log:12; t9505 is also the 5th rename (missing from 150-a2-1's R2).
## Edit (stage_prerun.py 3e5fdd53 -> 6208b7b7; py_compile rc 0, prep_c150_a2_2_compile.log)
- :3788-3790 docstring; :3806 `flipped_old: []` in info.update default; :3836 comment; :3837-3856 key = (uid, owner, term_class),
  `old_src` + `flipped_old` append; :4305-4306 CLI `FLIPPED-OLD <uid> #<owner> src a->b` after RENAMED-OLD. Nothing else.
## Self-test selftest_rebind_c150.py --phase post (selftest_rebind_c150_post2.log, 7/0, rc 0)
- R0 HEAD blob dcd45aba. R1 old code refuses `BuildArray x0/x1, LoopTunnel x2/x3` (exec of HEAD, same as pre record); new binds,
  map_nodes {-19:30300, -17:30294, -10:30290, -5:30287}.
- R2 renamed_old == the 5 renames exactly (t2832/t4160/t4165 #2626 array->element; t9505/t9508 #9503 Value->'').
- FLIPPED-OLD s06->s07 count 3: (29779,29777), (9505,9503), (10179,10177), all False->True.
- R3a class change of old t2813 #2626 refuses (BINDING BuildArray x0 vs x1). R3b direction flip of t2813 (BuildArray, non-tunnel) binds,
  (2813,2626) in flipped_old. R4 s05->s06 map_nodes and all 30 M pairs == selftest_rebind_c150_pre.json.
## Regression (150-a2-1 AFTER -> now; logs prep_c150_a2_2_<t>_after.log)
- selftest_rebind_c142_5 4/0 -> 4/0 rc 0; selftest_rebind_c132_5 7/0 -> 7/0; selftest_rebase_c132_6 8/0 -> 8/0.
- selftest_rebase_uidreuse_c143_4 2 pass/2 fail + KeyError 'sim_of' rc 1 NO RESULT LINE -> identical (pre-existing).
## Invariants (md5 now = brief): stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, graph a3ecb92b, plan s07 10a4f59a,
prov148 aeae610e, memory_model 8eec443c, adopted_scratch 658fe5b9. s05/s06/bed VIs: hashing outside the project dir is refused by the
sandbox; no LabVIEW process, claudeDev not written. No hooks edit; --rebase not run.
Hook: guard_write flagged card 149-a3-4's stale pin dcd45aba on each edit - logged fp-65 (dup of fp-64), edit not blocked.
OPEN: a CLASS change is the only old-terminal refusal left inside rebind's key; is a direction flip on a non-tunnel old terminal (R3b) acceptable as info?
