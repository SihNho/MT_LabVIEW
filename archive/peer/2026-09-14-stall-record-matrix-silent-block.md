---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# stall-record-matrix-silent-block

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (25s)
- **why asked:** mandatory review of stall record tools/bench/stall_pid1720_141314.log (fourth false positive of the day: silent 155-s block in handle_growth_matrix.py)
- **verdict:** unverified

## Question

STALL RECORD review (mandatory by project rule; one paragraph). Record tools/bench/stall_pid1720_141314.log: 'STALL: 14:16:33 pid 1720 alive 199s, CPU 0.41s lifetime' = python -u tools/bench/handle_growth_matrix.py (bgrun log tools/bench/handle_growth_matrix.log). FACT: the job completed normally (BGRUN END rc=0 after 456 s; five blocks all reported). CAUSE (from the script): block() prints ONE json row per block after the block ends; block B = 50 report_all runs on the main VI (~126 s) preceded by a 30-s idle sleep -> the bgrun log was silent ~155 s > the 90-s freshness window, and the lifetime-CPU rule (COM client, 0.41 s) fired - the fourth false positive of the same class today (silent phases: 167-s walk, this). FIX: block() now prints a progress line at every 10-run sample and before/after the 30-s idle wait. ATTACK: (1) is a per-sample line every ~25 s + an 'idle 30 s' marker enough, or should bgrun itself print a heartbeat while the child is alive (that would make a genuine hang invisible - the earlier review rejected side-thread heartbeats)? (2) given four false positives and zero true stalls today, is the lifetime-CPU rule (< 5 s) still worth keeping for COM clients, or should the detector require BOTH stale log AND zero CPU delta over 60 s? Cheapest change that keeps a real hang detectable within ~2 min.

## Answer

**STALL RECORD review:** This was a detector false positive, not a job failure. PID 1720 was reported alive after 199 seconds with 0.41 seconds lifetime CPU, but the job subsequently completed normally at 456 seconds with all five blocks reported. The 155-second silence is fully explained by block B?셲 buffered reporting pattern: approximately 126 seconds for 50 `report_all` calls plus the preceding 30-second idle. The new per-sample progress output and idle-boundary markers directly remove that ambiguity.

1. A progress line about every 25 seconds, plus markers before and after the 30-second idle, is enough for this workload. Do **not** add an unconditional `bgrun` heartbeat to the monitored log: it would continuously refresh the same signal used to detect a hung child and could conceal an indefinitely blocked COM call.

2. Remove the `<5 s lifetime CPU` rule for COM clients. Lifetime CPU is cumulative execution time, not evidence of recent activity; Windows explicitly defines process kernel/user times as accumulated amounts. [Microsoft GetProcessTimes documentation](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes)

Cheapest safe rule:

```text
stall candidate =
    child still alive
    AND log stale >= 90 s
    AND child CPU increase over the last 60 s <= measurement tolerance
```

Use a small tolerance rather than literal floating-point zero?봣or example, one timer/accounting quantum. At each poll, retain timestamp and CPU total; do not add a thread or modify the child.

This preserves detection within approximately 90?뱎oll-interval seconds when a COM call hangs immediately after the last progress line, comfortably under two minutes. If no 60-second CPU baseline exists when the log first becomes stale, wait only until that baseline is available. Given four false positives and zero true stalls, the lifetime-CPU predicate is presently harmful and should be replaced, not merely weakened.

## Sources

(extract from answer)

## What was done with it

Applied both recommendations in tools/lv_stallcheck.ps1: the lifetime-CPU predicate was removed; a stall now requires stale job log AND CPU delta <= 0.05 s over >= 60 s (state file tools/bench/.stall_samples.txt); handle_growth_matrix.py prints a line every 10 runs and around the idle wait. Verdict: adopted (design), no further false positive since.
