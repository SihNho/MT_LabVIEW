# hyp-ctsrc82-timeout

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.7414  in 40 / out 18766 / cache-create 113338 / cache-read 2177617  (219s, 27 turn(s))
- **date:** 2026-09-25 15:08:27
- **outcome:** ANSWERED (222s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** ctsrc_l2a1_82.log ended BGRUN TIMEOUT after all measurement gates passed (guard_peer, Jev ladder new-problem p=0.526)
- **verdict:** location confirmed by test 4 (pid 9968 start 15:02:51); ~150 s of extra run time unexplained

## Question

ATTACK this claim about tools/bench/ctsrc_l2a1_82.log (script tools/bench/ctsrc_l2a1_82.py, card tools/bench/cards/task_82-2.json).

CLAIM: the run ended "BGRUN TIMEOUT killed after 1802s (limit 30.0 min)" because the 30-minute bgrun budget I chose was
too short for the work, NOT because anything hung. Every measurement gate had already passed (P0, R1-R3 for both rows, R4,
H5 refs 13/13 closed; log lines 451-508 of the second run). The kill landed inside stagekit.Stage.close() ->
bench_prep.restart_labview() (tools/bench/bench_prep.py:74-79: Stop-Process, sleep 5, Start-Process, sleep 45), right
after "LabVIEW handle count AFTER the work: 46081". Evidence offered: after the kill a LabVIEW.exe (pid 9968) was still
running, i.e. the NEW instance restart_labview had started; the scratch D1_k_scratch_ctsrc82_20260925_143307.vi was left
on disk (close never reached its delete loop). The 30 real ops before op 31 each re-read the whole graph
(wiki_build.read_live, ~20 s each) plus node censuses and purges, which by itself approaches 25 min.

Already ruled out: a hang in the executor (the P0 gate and all row gates printed), an unclosed VI reference (H5 13/13).

What I want from you: the strongest reason this claim is wrong (e.g. restart_labview's Start-Process with
capture_output blocking on inherited pipe handles; labview_handles() PowerShell without timeout; close_panel's com_error),
an alternative explanation, and the cheapest discriminating test. Read tools/stagekit.py:1097-1148 (close),
tools/bench/bench_prep.py:64-79, and the log tools/bench/ctsrc_l2a1_82.log (second BGRUN block).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict:** the claim's conclusion probably holds: the kill most likely landed inside `restart_labview()`, and nothing hung in that function. But two parts of how it is argued are wrong. The "~25 min" breakdown doesn't match the measured timings, and a gap of about 2–4 minutes is left unexplained. None of the records settle whether that gap was a stall or ordinary variation.

**1. Strongest reason it is wrong: the timing argument is invented, and the real comparison run leaves time unexplained.**
- The log has no timestamps. The JSON was last written at `t: 56.6` (`ctsrc_l2a1_82.json:15`), and the per-op `secs` were lost because `dump()` never ran. The "~20 s per read" figure comes from a docstring (`stagexec.py:19`), not from this run.
- There is a direct baseline: `stage_d1_l2a1_r3.log` ran the same 30 ops on the same D1_k through the same `close()`, and it did the same restart inside close.
  - The 30 ops took **753 s in total** (sum of `"secs"` in `stage_d1_l2a1.json:1726–2641`, 22–28 s each), which is about 12.5 min, not about 25.
  - The whole run took **1562 s** (`r3.log:461`), with the same 56.6 s to reach "after open".
- In r3, "AFTER the work" printed at about 1505 s: 1562 s minus about 57 s for the close-time restart, deletes and pins (`r3.log:446–457`).
- For ctsrc82 to be killed inside `restart_labview` (Stop-Process, sleep 5, Start-Process, sleep 45; about 52 s in all), `ctsrc_l2a1_82.log:516` must have printed between about 1750 s and 1802 s. That makes ctsrc82's work before close **about 245–300 s longer than r3's**.
- The extra work (two rows, their second passes and one R4 `read_live`) is about four op-equivalents plus one read. At the measured per-op cost that is about 125 s.
- That leaves **about 2–3 minutes unaccounted for**. "The budget was too short" is true, but it doesn't explain those minutes.

**2. Alternative explanations for the same evidence**
- **(a) A slow step before close, not a hang.** The ctsrc82-only work (the PRIME route for 4 ControlTerminal ends, `wire_control`, `OpWireSource_v5`, the R4 compare) or a COM call that stalled for minutes and then returned would produce exactly this log. So would a slow phase between open and op 1: in r3 that phase already took about 700 s, and nothing records its breakdown.
- **(b) Stop-Process failed silently, so pid 9968 is the old instance.** Output is captured and `-ErrorAction SilentlyContinue` discards errors (`bench_prep.py:75–76`). Nothing in the evidence shows 9968 is the new instance.

What I checked against your suggested hangs:
- **A Start-Process pipe hang or a `labview_handles()` hang is unlikely.**
  - The same `restart_labview` finished inside `close()` in r3 with LabVIEW running (`r3.log:446→457`, handles 46059 → 33955).
  - The taskkill tree (`ctsrc_l2a1_82.log:518`) shows only two direct children of pid 16056 and no grandchildren. With `py -u` under bgrun (`bgrun.py:207`), 16056 is most likely the `py.exe` launcher, whose children are `python.exe` and, probably, `conhost` ([Python docs: launcher](https://docs.python.org/3/using/windows.html#python-launcher-for-windows); [launcher spawns interpreter as a child](https://github.com/Senkichi/charlie-work/issues/1851)).
  - So `python.exe` probably had no live PowerShell child when it was killed, which means it was in a `time.sleep` and not blocked in `subprocess.run`. This rests on my guess of what 15104 and 6080 are; neither was recorded.
- **The `close_panel` com_error (0x47D) is harmless.** r3 shows the same error at `r3.log:443` and still completed.

**3. What would falsify the claim**
- If pid 9968 **started before about 15:02:15** (kill ≈ 14:33:07 + 1802 s ≈ 15:03:09), it is not the new instance restart_labview launched. Either Stop-Process failed, or the kill was not in the restart window.
- If it started **around 14:33–14:34**, it is the original instance, and the "LabVIEW gone" chain failed.
- If it started **around 15:02:20–15:03:09**, the location is confirmed, and its start time gives the moment line 516 printed to within a few seconds.

**4. Cheapest test (read-only, one command)** — run it if pid 9968 is still alive:
`Get-CimInstance Win32_Process -Filter "ProcessId=9968" | Select ProcessId,CreationDate,ParentProcessId`
- A start time in about 15:02:20–15:03:09 confirms the claim's location. Subtracting about 6 s gives the time line 516 printed, and comparing that with r3's about 1505 s gives the true extra time.
- If the extra time is well over about 150 s, the rerun needs per-phase timestamps (and `dump()` called before `close()`), not just a larger `--max-min`.

If 9968 is gone, the next rerun should do three things: print a wall-clock time on every phase header, `dump()` before `close()`, and use `--max-min 45`.

**Bottom line:** "killed inside `restart_labview`, not in a hang there" is well supported. The budget claim is right in direction: r3 shows this pipeline needs about 26 min, so 30 min left about 4 min of margin. But this pipeline was about 2–3 min slower than the extra rows explain. Until pid 9968's start time or a timestamped rerun accounts for that gap, it shouldn't be closed as "budget only".

Sources:
- [Python docs — Python Launcher for Windows](https://docs.python.org/3/using/windows.html#python-launcher-for-windows)
- [charlie-work #1851 — py launcher + interpreter child pairs on Windows](https://github.com/Senkichi/charlie-work/issues/1851)

## Sources

(extract from answer)

## What was done with it

- Test 4 RUN (card 82-2, `tools/bench/ctsrc_l2a1_82_cleanup.log`): the leftover LabVIEW was pid 9968, started
  **2026-09-25 15:02:51**, inside the predicted 15:02:20-15:03:09 window => it is the instance `restart_labview` launched,
  the kill landed in its `sleep(45)`; the claim's LOCATION is confirmed. "AFTER the work" printed at ~15:02:45 = ~1778 s
  after start vs r3's ~1505 s => ~273 s extra, of which ~125 s is the two extra rows; **~150 s stays unexplained**
  (the review's point 1 accepted: "budget only" is not closed).
- Accepted for the next run of this pipeline: `--max-min 45`, not 30. Per-phase wall-clock stamps and `dump()` before
  `close()` are a stagekit/stagexec change outside card 82-2's scope -> reported as OPEN to the judgement session.
- Hygiene the kill skipped was completed by `tools/bench/ctsrc_l2a1_82_cleanup.py` (4/0): LabVIEW gone, scratch
  deleted, D1_k md5 6cf5b077 unchanged. The measurement gates (P0, R1-R4, H5) had all passed before the kill and stand.
