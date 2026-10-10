# card 160-f2-1 facts (offline re-pin of three suites, labview none)

## selftest_c156_passwire.py  md5 2b628fab -> 6ad1e1bd
- pins :162-163 stagekit 07f9e35f -> 1441bb4c, stage_prerun 9decb20f -> 7605116f, stagesim eb99c6ba -> a3261b56; docstring :32-33 (old docstring said stagekit aec03c6c).
- RESULT PASS 20/0 (selftest_c156_passwire_c160.log:34), BGRUN END rc=0 after 590s (:35) = last pass 20/0 (selftest_c156_passwire.log:66).
- run used --max-min 14, not the brief's 6: last pass took 538s (selftest_c156_passwire.log:67).

## selftest_c155_basecase_frame.py  md5 fd4fe9c7 -> 7286edd8
- pins :207-208 stagekit 07f9e35f -> 1441bb4c, stage_prerun 9decb20f -> 7605116f; docstring :28-29.
- RESULT PASS 21/0 (selftest_c155_basecase_frame_c160.log:25), rc=0 after 40s = last pass 21/0 (selftest_c155_basecase_frame.log:75).

## selftest_c156_b2_2_invcheck.py  md5 fa02918e -> c6460301
- pin loop :99-102 stagexec 25a1494c -> c4a6e0b6, stagesim eb99c6ba -> a3261b56, stagekit aec03c6c -> 1441bb4c, stage_prerun 9decb20f -> 7605116f.
- FAIL-case expected line :91: stagekit's FULL md5 aec03c6c4b31... -> 1441bb4ca75e... (the inner gate echoes the stagekit md5 on disk).
- RESULT FAIL 19/1 (selftest_c156_b2_2_invcheck_c160.log:183, rc=1); last pass 20/0 (selftest_c156_b2_2_invcheck.log:163).
- OPEN: gate "ring-p5.md drift listed (742e54c4 -> aa238a09)" (suite :83) expects new md5 aa238a09; found 99c812e6 (log DRIFT lines, before
  and after). Doc md5, not a tool pin, so not re-pinned.
- before/after replay: MISMATCH 0, reproduced 46 PASS each, DRIFT 14 / 13 (log :83 :165).
- DRIFT after: snapshot gate "P4 recipes / plans / preds + tools/hooks/** unchanged (153 files)" now lists tools/hooks/guard_cycle.py and its .pyc
  as changed since the 156 snapshot. This card did not edit them.

## md5 unchanged (before == after this card)
stagekit 1441bb4c, stagesim a3261b56, stagexec c4a6e0b6, stage_prerun 7605116f, addrcheck 207beb0d, vigraph a7eb58c7, gscript 1a80236e.
VIs 94ffff94 / eb1d0f31 / 2482fe7b / 7f2582ae: NOT hashed. The permission layer refused md5sum on the claudeDev paths. This card did not open or write any .vi.
tools/hooks: no edits by this card.
