ATTACK this claim about a failed self-test row (card 121-3, offline, no LabVIEW).

FAILURE: tools/bench/c121_3reg_selftest_launch_gate.log:7 `FAIL L4 a FAILED run newer than the records -> refused (decision 4)`
(27 pass / 1 fail). Script: tools/bench/selftest_launch_gate.py:77-84.

CHANGE THAT PRECEDED IT (gate-fp fp-1/fp-6): tools/stage_prerun.py `last_failed_run_after` now skips a bgrun segment of an
appended log when its END is proven <= t_min (segment_ended_by: START stamp + the `after Ns` of its END/TIMEOUT line + 1 s);
a segment with no stamp or no END line still counts. Before, every segment of any log whose MTIME > t_min counted.
Evidence for fp-1: tools/bench/stage_d1_l2r2_prerun.log:1-133 is a FAIL prerun segment 07:54:30 (+27 s) older than its PASS
records (prerun_records.jsonl, 08:00:25); the log's mtime came from the later PASS segment, so the launch was refused.

CLAIM: L4 fails because its FIXTURE, not the gate, is wrong. selftest_launch_gate.py:77 writes the pre-run records at
time.time()-100 (2026-09-28), and :81-82 writes the "newer" failing run with a hard-coded START stamp `2026-09-24 20:00:00`
and `BGRUN END rc=1 after 3s` - i.e. a run that by its own stamp ENDED four days BEFORE the records. The old gate only saw
the file mtime (fresh), so it passed; the new gate reads the stamp. A real bgrun writes the real local time, so a genuinely
newer failed run still has end > t_min and is still refused (tools/bench/selftest_c121_3_gatefp.py N1/N2/N3: 21/0,
tools/bench/selftest_c121_3_gatefp.log). The fix would be to stamp the fixture with the current time, not to change the gate.

Attack: is there a REAL launch path where a failed run that happened after the pre-run records carries a START stamp +
duration <= the records' time (clock skew, bgrun writing local vs UTC, protocol.segments parsing with time.mktime, DST, a run
whose END line reports a shorter duration than it lasted, appended logs written by two bgrun processes, records written with
a stale `t`)? If one exists the gate change widens decision 4 and must not be kept.
