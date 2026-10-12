# Card 169-a2-2 facts (gate-fp fp-98 / fp-99 / fp-100) - status FAIL (the fp-98 fix made a self-test worse and was reverted)

- Pins: all 8 card inputs matched their md5 at start; `protocol.py requires` PASS (tools/bench/cards/requires_169-a2-2.json).
- No LabVIEW, no hardware; every run was a stage_prerun dry/prerun with stubbed COM, or pure Python.

## fp-98 (X5 RBW class) - REVERTED, not drained
- Patch tried: `RBW_VERB_RE = ^remove_bad_wires(_scripted)?$` taken out of the x5_count wiring count (stage_prerun.py, beside RLE_VERB_RE).
  The self-test passed: selftest_c169_fp98_100.log:5 (A3: a copy of the 167 script with its label restored passes X5) and :6 (A4: one extra connect_wire op still FAILS).
- REGRESSION: selftest_stage_prerun_c115c went 9 pass/1 fail -> 8/2 (diag_c169_a2_2_before_c115c.log:13 -> diag_c169_a2_2_after_c115c.log:13).
  New failure: T8 "unplanned remove_bad_wires still a wiring op -> FAIL" (selftest_stage_prerun_c115c.py:14,52-53; card 115-3 pins that an
  UNPLANNED remove_bad_wires FAILs X5).
- Under the card rule, the edit was reverted (3 hunks). After the revert c115c is back to 9/1 (diag_c169_a2_2_reverted_c115c.log). fp-98 stays open.
- The 167 script passes X5 today without any fix, because its op label is `rbw_method410` (diag_c169_a2_2_prerun167_before.log:56, ops 0, PRERUN PASS 15/0 :67).
- selftest_c169_fp98_100.py A1-A4 test the reverted fix, so they will FAIL against the current stage_prerun.py.

## fp-100 (find_graph) - fixed, NOT drained (the card returned at the fp-98 regression)
- Patch: stage_prerun.py:202-208 (POST_EDIT_NOTE_RE plus its comment) and :278. In the glob search, a header-md5 match whose `note` contains "IN-MEMORY copy after"
  goes to FIND_SKIPPED. Plan base graphs are not affected.
- 4 files stamped 75773b0d carry that note: graph_ring_p6rbw_191349, p6rbwd_205248, p6rbwd_212149, p6_presave_212645 (diag_c169_a2_2_graphs.log;
  each has 2066 Wire objs, compared with 2091 in graph_ring_p5s02e_20261012_173009.json, file md5 7815af09). No other terminal-list graph with a note matches the phrase (diag_c169_a2_2_graphs_note.log).
- Self-test: B1 picks p5s02e/7815af09 (selftest_c169_fp98_100.log:8). B2 skips the 4 copies. B3: the older stage tools/recipes/stage_d1_ring_p5s02a.py still
  gets graph_ring_p5s01_20261009_125622.json, the graph named in diag_c157_a1_2_dry.log:19.
- 168 dry: it now picks p5s02e. R1 and D1 are UNVERIFIED (stub after mutation), not FAIL, and the result is DRY PASS-UNVERIFIED rc 0 (diag_c169_a2_2_dry168_after.log:7,19,27,56; selftest :11).
  The first fix alone makes the dry pass, so the D1 taint half (stage_prerun.py:622/:809) was NOT changed.

## fp-99 (run_vi on a grep) - fixed in tools/protocol.py only, NOT drained
- Patch: protocol.py:1199-1205. RUN_VI_CMD_RE is now matched against `_dispatch_text(cmd)` (fp-25: read-only segments dropped), except when a pipe feeds
  py/python/powershell/pwsh/iex, in which case the full command is judged.
- The fix needs no tools/hooks/** edit: guard_bash calls guard_card -> protocol.check_command (guard_bash.py:628-637), and MOTOR_BLOCKED_RE (guard_bash.py:124) needs py in command position.
- Self-test: C1 accepts `grep -n -i motor tools/bench/drive_original_copy_v5.py`. C2 still refuses `py -u <driver>`, the bgrun form and `cat <driver> | py -` (selftest_c169_fp98_100.log:12-15).

## Existing self-tests before -> after (logs tools/bench/diag_c169_a2_2_{before,after}_*.log)
- c115a 8/0 -> 8/0; c148 8/0 -> 8/0; headcmp 2/0 -> 2/0; stageplan 12/0 -> 12/0; c106e 14/1 -> 14/1; c114 15/1 -> 15/1; c114d 11/1 -> 11/1
- protocol 46/2 -> 46/2; protocol_wiring 66/0 -> 66/0; c128b 5/1 -> 5/1 (T4, already failing)
- c115c 9/1 -> 8/2 (fp-98 edit) -> 9/1 after the revert
- c103 0/4 before (558 s); TIMEOUT at 10 min after, while running alongside 6 parallel runs. c106c TIMEOUT before and after: not comparable.
- c128b before and c106c before started at 22:10-22:11, before the first stage_prerun edit (~22:15), so their child processes may have loaded edited code.

## Drain calls: none (the card returned at the first unexpected result, before step 4)
skipped: fp-98 (reverted), fp-99 and fp-100 drains (left for the judgement session), fp-101, fp-102, hook entries;
the labview:read self-tests (c110g, c128, graphload: the card's flag is labview none); c128b_mktrace (it writes a fixture).
