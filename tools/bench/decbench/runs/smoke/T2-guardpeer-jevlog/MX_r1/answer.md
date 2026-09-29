The two symptoms are one chain. guard_peer treats a Jev test log as a LabVIEW failure, and the self-test crash only supplied that log's first failure line.

**Symptom 1.** In the 08:42 run, the self-test moved `guard_peer.BENCH/PEER` to TEMP on C: but left `ROOT` on G:. So `os.path.relpath(path, ROOT)` raised a cross-drive ValueError (tools/hooks/guard_peer.py:370; tools/bench/jev_discharge.log:21-25). jev_run_all turned that into rc=99 and a `  FAIL` row (tools/bench/jev_run_all.py:32-36; jev_discharge.log:26). In real use BENCH sits under ROOT (guard_peer.py:51-53). The test now moves ROOT too (tools/bench/selftest_guard_peer_jev.py:126-130), and the 09:06 rerun passed 15/0 (jev_discharge.log:276).

**Symptom 2.** guard_peer skips a log only by its file name: the review-tool names (tools/logclass.py:46-71) and `selftest_*` (guard_peer.py:124,138). The user's Jev exemption (CLAUDE.md:363) was coded only for commands (guard_peer.py:62,316). The self-test runs inside the jev_run_all process (jev_run_all.py:47-53), whose log is `jev_discharge.log` (jev_run_all.py:8). Run on its own, the same test logs to `selftest_*` and is skipped (selftest_guard_peer_jev.log:1). So line 26 made jev_discharge.log the newest failing log (guard_peer.py:127-159).

**Most plausible alternative:** a legitimate one-off block that clears once the self-test passes.

**Evidence against it:**
- Case C0b calls the gate without capturing stderr (selftest_guard_peer_jev.py:142), and bgrun merges stderr into the log (tools/bgrun.py:183). So the block message copies the test's fake `STOP:` line into jev_discharge.log:245.
- The `STOP:` pattern in FAILURE_RE is not tied to the start of a line (guard_peer.py:96), and only the last run in a log counts (guard_peer.py:156). So the passing 09:06 run still arms the gate. Whether the 09:0x refusal came before or after that rerun, the log matched (line 26 or 245).
- Changing the fake marker from `FAIL` to `STOP:` (selftest_guard_peer_jev.py:51-57) got past bgrun's failure scan but not guard_peer's.
- That run's `BGRUN END rc=1` comes from bgrun.py:215 matching `rc=2` in four PASS rows (jev_discharge.log:480). FAILURE_RE has no `rc=` term, so the gate ignores it.

**Cheapest discriminating test:** apply FAILURE_RE only to the text after the last `BGRUN START` (jev_discharge.log:230). It is a file read with no LabVIEW. A match means a passing self-test still blocks LabVIEW work; no match supports the alternative. Searching the whole file with that pattern (ripgrep) returns exactly lines 26 and 245. Line 245 is in the last run, so the result already supports the root cause.

ROOT CAUSE: guard_peer.py exempts logs only by file name and applies the Jev exemption only to commands, so the Jev self-test's output in tools/bench/jev_discharge.log (first the FAIL row from its own cross-drive relpath crash, then, even on a passing run, the copied `STOP:` line from the test's fake log) is read as an unreviewed LabVIEW failed prediction.
TEST: Run guard_peer.FAILURE_RE over only the last `BGRUN START` section of tools/bench/jev_discharge.log (the 09:06 run that passed 15/0); a match on line 245's copied `STOP:` shows the gate stays armed after the crash is fixed, ruling out "only the one-off rc=99 FAIL row".