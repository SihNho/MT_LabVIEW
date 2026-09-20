---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# stall-record-sweep-false-positive

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (75s)
- **why asked:** mandatory stall-record review (user rule 2026-09-14): tools/bench/stall_pid9272_105613.log flagged the healthy `sweep_subvis_main.py` client (0.4 s CPU over 163 s) five seconds before it finished normally.
- **verdict:** diagnosis CONFIRMED (a COM client idles in LabVIEW's Run call; lifetime CPU is not a stall signature); design accepted with fixes: `$procs` IS populated from the same CIM snapshot in the file as it stands (the peer read an intermediate version); the log-freshness check runs BEFORE both CPU rules, so both are gated on progress; 90 s kept as the ordinary window. Not implemented (recorded): a `STALL_GRACE` phase line for genuinely long silent calls, heartbeat-line classification, and ancestor creation-time validation against PID reuse.

## Question

STALL RECORD review (mandatory by project rule). Record tools/bench/stall_pid9272_105613.log: 'STALL: 2026-09-14 10:58:56 pid 9272 alive 163s, CPU 0.41s lifetime' - pid 9272 was python.exe -u tools/bench/sweep_subvis_main.py (170 diagrams, one COM-driven op run per diagram ~1 s each, launched under tools/bgrun.py --log tools/bench/sweep_subvis_main.log). FACT: the sweep completed normally 5 s later (BGRUN END rc=0 after 168 s, 0 mismatches, its log file gained a line every ~1 s throughout). MY CLAIM: false positive of the lifetime-CPU rule in tools/lv_stallcheck.ps1 - a VI-Server COM client spends its time blocked in LabVIEW's Run call, so its own CPU stays tiny while it is making steady progress; lifetime CPU < 5 s over 163 s is the NORMAL profile of a healthy client here, not a stall signature. PROPOSED FIX (implementing now): treat the bgrun log as the progress signal - for each leaf suspect, find its ancestor whose command line carries 'bgrun.py ... --log <file>' and skip the suspect if that file's LastWriteTime is younger than 90 s; keep the lifetime and CPU-delta rules for clients with no log or a stale log. ATTACK: (1) is there a real stall this would now hide (a client that keeps writing heartbeat lines while blocked - e.g. a watchdog thread printing while the COM thread hangs; the earlier gscript _run watchdog prints?) and what is the cheapest discriminator (log content vs mtime? require the last line to change?); (2) is 90 s the right window given one op run on the main VI costs ~1-3 s and net_map purges ~12 s; what about a legitimately silent 5-minute phase (a long single COM call such as a 170-node Traverse or a save)? (3) the CPU-delta rule (+<0.5 s over >=60 s) would ALSO flag this healthy client - should the delta rule be gated on log staleness too, or on a much lower threshold (COM clients burn ~2.5 ms CPU per op run)? Read tools/lv_stallcheck.ps1 and tools/bgrun.py. Give concrete failure scenarios and the cheapest test for each; be brief.

## Answer

Your diagnosis is correct, but the proposed implementation currently does not work: `$procs` is never initialized or populated. `$row = $procs[[int]$anc]` throws under `$ErrorActionPreference='Stop'`; the outer catch then silently exits, potentially disabling the entire detector for that hook invocation.

Attack results:

1. **Fresh-log false negative**

   - `bgrun.py` itself emits no heartbeat. Its mtime advances only when the child produces a flushed line.
   - The present `gscript._run` watchdog does **not** print while polling, so it cannot conceal a hung `Run`.
   - A future watchdog/progress thread could print periodically while the COM worker is stuck, hiding the stall indefinitely until `bgrun`?셲 deadline.
   - ?쏳equire the last line to change??is equivalent to mtime here because `bgrun.out()` appends and flushes every received line.
   - Cheapest discriminator: classify lines. Ignore known heartbeat/status-only patterns and refresh progress only for recognized milestones?봮r record both `last_output` and `last_semantic_progress`. Test with a fixture whose COM worker blocks while another thread prints every 10 seconds.

2. **90-second window**

   - It is comfortably above normal 1??-second ops and the 12-second purge.
   - It deliberately reports a silent legitimate five-minute Traverse/save after 90 seconds. A single global window cannot distinguish that from a hang.
   - Cheapest solution: keep 90 seconds as the default, but let a job print a machine-readable phase line such as `STALL_GRACE seconds=360 phase=Traverse` immediately before a known long call. Test with a silent 100-second fixture and a silent 300-second fixture carrying explicit grace.
   - The existing `_run` cap is 180 seconds, and the sweep overrides it to 120 seconds, so no healthy `_run` call should require a five-minute exemption.

3. **CPU delta**

   - Gate **both** lifetime-CPU and delta-CPU rules on stale/no progress. Lowering `0.5s` is not robust: at the measured 2.5 ms/op and roughly one op/second, a healthy client gains only about `0.15s/60s`, still below the current threshold.
   - Test three fixtures: healthy low-CPU + fresh progress, blocked + silent log, and blocked + synthetic heartbeat. Expected: suppress only the first.
   - CPU should remain corroborating evidence, not the primary progress signal.

Two implementation cautions:

- Populate a process table from the same CIM snapshot, including every relevant ancestor?봭ot only Python command lines.
- Validate ancestor creation times because Windows may reuse PIDs and `ParentProcessId` can consequently identify an unrelated newer process. [Microsoft?셲 `Win32_Process` documentation](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process)
- Prefer `LastWriteTimeUtc`; timestamp reads can have OS-level update inaccuracies, although that is unlikely to matter at a 90-second scale. [Microsoft `LastWriteTimeUtc` documentation](https://learn.microsoft.com/en-us/dotnet/api/system.io.filesysteminfo.lastwritetimeutc)

Verdict: **accept the design after fixing `$procs`; gate both CPU rules on progress freshness; retain 90 seconds as the ordinary-operation threshold and add explicit phase-specific grace for genuinely long silent calls.**

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
