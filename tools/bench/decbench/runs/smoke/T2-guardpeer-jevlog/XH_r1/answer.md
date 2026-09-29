**Root cause:** the Jev bundle writes its self-test's failure-shaped text into `jev_discharge.log`. `guard_peer` only exempts self-test output when the log's *filename* starts with `selftest_`, so it counted that bundle log as a real failed prediction. The Jev exemption was coded for commands, not for the logs they write.

**Symptom 1 (rc=99).** The test puts its fixture in the system temp folder on C:, while the project root is on G: (`selftest_guard_peer_jev.py:107`). `guard_peer.main()` builds its block message with `os.path.relpath(path, ROOT)` (`guard_peer.py:370`). On Windows that call raises `ValueError` when the two paths are on different drives (`jev_discharge.log:21-26`). The 09:06 rerun passes because `ROOT` was moved along with `BENCH` and `PEER` (`selftest_guard_peer_jev.py:126-130`; `jev_discharge.log:276`).

**Symptom 2 (the refusal).**
- `jev_run_all.py` runs the self-test in its own process and logs everything to `jev_discharge.log` (`jev_run_all.py:47-53`).
- `newest_failing_log()` skips only review-machinery logs and names starting `selftest_` (`guard_peer.py:124,138`). The review-log list has no `jev_` entry (`logclass.py:46-71`).
- The user's "Jev는 면제" exemption (`CLAUDE.md:363`) was added only to `RUNNER_RE` (`guard_peer.py:62`). That lets commands that *run* Jev scripts through, but does not stop *their logs* from arming the gate against other commands.
- Only two lines in the log match `FAILURE_RE`, and both come from the self-test:
  - Before 09:06:39, the gate saw the crash row `  FAIL  SELF-TEST ... raised ValueError` (`jev_discharge.log:26`).
  - After it, the gate saw the fixture's `STOP: A2 …` line (`:245`). Test C0b calls `run_main(cmd)` without `capture=True` (`selftest_guard_peer_jev.py:142`), so the block message leaks into the bundle log (`jev_discharge.log:243-260`). `FAILURE_RE` matches `STOP:` anywhere on a line (`guard_peer.py:96`).
- So the fixture's "use `STOP:`, not `FAIL`" workaround (`selftest_guard_peer_jev.py:51-57`) got past bgrun's scanner but not `guard_peer`. Even the passing 15/0 run left the log armed. Separately, bgrun still ended that run `rc=1` (`jev_discharge.log:480-481`).

**Most plausible alternative:** the Jev trials themselves recorded a real failed prediction, which would mean the refusal was correct. Evidence against it: none of the Trial A/B lines match `FAILURE_RE`. That includes the `XX` disagreement rows (`jev_discharge.log:89,92,152…`) and the `BGRUN INNER FAILURE` line.

**Cheapest discriminating test (offline, no LabVIEW, about a second):** copy `jev_discharge.log` into a temporary `BENCH` twice, then call `guard_peer.newest_failing_log()` on each copy:
- copy (a): delete only the self-test block, `jev_discharge.log:236-278`;
- copy (b): delete only the Trial A/B blocks.

If (a) returns `None` and (b) still returns the log, the leaked self-test output alone armed the gate. If (a) still returns the log, a Trial line is the cause and the refusal was legitimate.

ROOT CAUSE: `guard_peer` exempts self-test output by filename only (`selftest_`) and exempts Jev scripts only as commands, so self-test text written into `jev_discharge.log` armed the gate: first the cross-drive `relpath` crash row, then the fixture's `STOP:` line leaked through the uncaptured stderr in C0b.
TEST: Call `guard_peer.newest_failing_log()` on two temporary copies of `jev_discharge.log`, one without the self-test block (lines 236-278) and one without the Trial A/B blocks; if only the copy without the self-test block comes back `None`, the self-test leak is confirmed.