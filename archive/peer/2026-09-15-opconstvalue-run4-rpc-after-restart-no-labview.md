---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvalue-run4-rpc-after-restart-no-labview

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (76s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026 VI Scripting over COM, python win32com). Recipe tools/recipes/build_opconstvalue_v1.py run 4, log tools/bench/build_opconstvalue_v1.log: the BUILD phase fully PASSED and OpConstValue_v1.vi was saved runnable (ExecState 1, donor md5 unchanged). Then the TEST phase called fresh() (Stop-Process LabVIEW -Force; sleep 8; g.reset() which clears _lv AND the op-proxy _cache - the fix accepted in archive/peer/2026-09-15-opconstvalue-fail1-stale-op-cache.md) and the very next COM work raised 0x800706BA RPC_S_SERVER_UNAVAILABLE (no traceback captured - the handler prints only str(e)).
NEW EVIDENCE vs the earlier two RPC incidents (also archive/peer/2026-09-14-addshiftreg-run2-rpc-unavailable.md): ~2 minutes after the script exited, tasklist shows NO LabVIEW.exe process at all; the Windows Application event log for the last 20 min has NO LabVIEW entry (no crash), and Documents\LabVIEW Data\lvfailurelog has nothing newer than 2025. The identical fresh_labview() in tools/recipes/build_track_v6_queue.py (kill + sleep 8 + g.reset()) worked in 3 runs, but there the next call was g.op(...) on a small op VI; here the first calls after the restart are g.op(OP) then g.report(MAIN, 'StringConstant') where MAIN is the 4-MB main VI with a large subVI hierarchy (NI Vision, VISA, instrument drivers).
PREDICTION THAT FAILED: reset() + 8 s suffice after a kill.
Candidates: (H1) Dispatch('LabVIEW.Application') launched a new LabVIEW still initializing (splash / add-on loading) when the first call arrived -> RPC unavailable; the COM-launched instance then EXITED because its only client disconnected when the script died on the exception (a COM local server started by activation quits when its last external reference is released and it has no windows) - this explains 'no LabVIEW process' without a crash; (H2) LabVIEW crashed loading MAIN (no log entry found - weak); (H3) bgrun's taskkill /T on exit killed a LabVIEW child - but bgrun kills only on TIMEOUT and this was END rc=1, and a COM-activated server is not the script's child; (H4) a stale proxy held OUTSIDE gscript's cache (a local alias, the B helper module's globals, or the watchdog thread used by g._run) was invoked - would be a cache hit that never Dispatched.
Questions: (1) rank, and name the cheapest discriminating test. My plan: print the full traceback; after fresh() and before g.op(), run com_preflight() (two spaced Application round-trips against an unchanged PID, as in tools/recipes/build_opaddshiftreg_v0.py); log LabVIEW's PID before the kill, after the Dispatch, and at exit. (2) Does a COM-activated LabVIEW.exe exit when its client process dies with no VI window open? cite. (3) Is loading a large VI hierarchy through GetVIReference on a just-started instance a known cause of RPC_S_SERVER_UNAVAILABLE (vs RPC_E_SERVERCALL_RETRYLATER 0x8001010A)? (4) Anything in my plan that would MASK rather than fix the cause? Read-only; cite what you read.


## Answer

My ranking is **H1 > H4 > H2 > H3**, but H1 should be narrowed to ?쐍ewly activated LabVIEW process became unavailable during or immediately after activation,??not yet ?쏮AIN overloaded it.??
1. **H1 ??most likely.** The fixed 8-second delay is not a readiness test. `0x800706BA` means the RPC server endpoint was unavailable, whereas a live STA application declining a call because it is busy normally produces `0x8001010A RPC_E_SERVERCALL_RETRYLATER` ([Microsoft COM error table](https://learn.microsoft.com/en-us/windows/win32/com/com-error-codes-3)). The later absence of a process is consistent with an activation/startup failure or orderly exit, although it does not distinguish those cases.

2. **H4 ??plausible but substantially weakened.** [`gscript.reset()`](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:80) clears both `_lv` and `_cache`. In `_run`, the worker?셲 marshaled interface is consumed with `CoGetInterfaceAndReleaseStream`, the worker is joined, and its local proxy dies when the thread returns. I found no persistent VI proxy in the imported `build_track_v6_core` helpers used here. H4 remains possible only through an unlocated global/closure or an abandoned still-running timeout thread?봭ot the normal completed `_run` path.

3. **H2 ??weak.** A large hierarchy can make Open/Get VI Reference synchronous and slow: it loads and links dependencies before returning, and does so through LabVIEW?셲 UI thread ([NI Community explanation](https://forums.ni.com/t5/LabVIEW/Open-VI-Reference-prevents-execution-of-other-parallel-threads/m-p/1838409)). That supports ?쐋ong/busy loading,??but I found no NI evidence that ordinary large-hierarchy loading is a known cause of `RPC_S_SERVER_UNAVAILABLE`. With no process/event/failure log, an undocumented hard crash remains possible but unsupported.

4. **H3 ??effectively ruled out by the supplied runner evidence.** Nothing externally sourced is needed for this ranking: an `END rc=1`, rather than timeout cleanup, contradicts the proposed `bgrun` kill path.

### Cheapest discriminating test

Your traceback/PID instrumentation is right, but first run one deliberately *un-preflighted* diagnostic:

```python
fresh_kill_and_reset()

mark("before Dispatch", pid())
app = g.lv()
mark("after Dispatch", pid())

mark("before Application.Version", pid())
print(app.Version)
mark("after Application.Version", pid())

mark("before g.op(OP)", pid())
vi = g.op(OP)
mark("after g.op(OP)", pid())

mark("before report MAIN", pid())
rows = g.report(MAIN, "StringConstant")
mark("after report MAIN", pid())
```

Log `repr(e)`, `e.args`, `traceback.format_exc()`, elapsed time, and PID/process creation time at every boundary.

Interpretation:

- Failure at `Dispatch`: activation/startup failure; MAIN is exonerated.
- `Dispatch` succeeds but `Version` fails and PID disappears: startup/early server termination.
- Cheap application calls and `g.op(OP)` succeed, but `g.report(MAIN, ??` fails: MAIN hierarchy becomes the leading trigger.
- Failure occurs before any new Dispatch, or the traceback invokes an old object: H4.
- PID remains alive while the HRESULT is `0x8001010A`: ordinary busy/rejected-call behavior, not unavailable RPC. Microsoft defines that HRESULT specifically as the application message filter reporting busy ([Microsoft](https://learn.microsoft.com/en-us/windows/win32/com/com-error-codes-3)).

Use process creation time as well as PID because Windows may reuse PIDs.

### Does COM-activated LabVIEW exit with its last client?

**I cannot substantiate that as a LabVIEW-specific fact.**

For a generic out-of-process COM server, release of the last server object *can* drive the server-process reference count to zero, at which point the server is expected to initiate shutdown?봟ut that is a choice made by the server implementation, not a universal automatic guarantee ([Microsoft?셲 out-of-process server lifetime documentation](https://learn.microsoft.com/en-us/windows/win32/com/out-of-process-server-implementation-helpers)). NI documents that LabVIEW acts as an ActiveX server and exposes its Application and VI objects, but the NI material I found does not document LabVIEW.exe?셲 last-client shutdown policy ([NI ActiveX documentation](https://www.ni.com/docs/ar-SD/csh?context=lvcore_lvconcepts_using_activex_with_labview), [NI Python/ActiveX example](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU0000002VZB0A2&l=en-US)).

Therefore the statement ?쐔he script died, released its only reference, so LabVIEW exited normally??is **possible but presently unproven**. A cheap direct test would activate LabVIEW from a minimal Python process, perform only `Application.Version`, record PID, exit normally, and observe the PID for several minutes. Repeat with a VI reference and with a front panel open. That tests LabVIEW?셲 actual policy without loading MAIN.

### Large hierarchy versus the two HRESULTs

The defensible distinction is:

- Opening a top-level VI can synchronously load and link its dependency hierarchy, blocking LabVIEW?셲 UI thread until completion ([NI Community](https://forums.ni.com/t5/LabVIEW/Open-VI-Reference-prevents-execution-of-other-parallel-threads/m-p/1838409)).
- A live automation server refusing work because it is busy maps to `RPC_E_SERVERCALL_RETRYLATER` (`0x8001010A`) ([Microsoft](https://learn.microsoft.com/en-us/windows/win32/com/com-error-codes-3)).
- `0x800706BA` is `RPC_S_SERVER_UNAVAILABLE`, meaning the RPC server could not be reached ([Microsoft](https://learn.microsoft.com/en-us/answers/questions/525306/failed-when-request-a-cert-0x800706ba)).

I found **no documented NI precedent** connecting a large `GetVIReference` hierarchy directly to `0x800706BA`. If MAIN really triggers it, the stronger inference is process termination, COM endpoint loss, or an internal LabVIEW failure during load?봭ot merely ?쏬abVIEW was busy.??
### What could mask the cause

`com_preflight()` is suitable as a production readiness gate, but it can mask the diagnostic:

- Its two calls plus the four-second spacing give LabVIEW additional startup time.
- It loads/runs small op infrastructure before MAIN, warming LabVIEW and some shared libraries.
- Its retry loop discards the first failing call and can convert a reproducible startup race into an eventual pass.
- Calling `g.count(probe, "Wire")` is not a pure Application-level probe; it loads and executes a VI, so it changes the state you are trying to observe.

Keep it for the eventual fix, but first capture one raw run with `Dispatch ??cheap Application property ??g.op(OP) ??MAIN`, without retries. Then run the preflight version as the controlled comparison.

One additional correction: in the failed run, the log does **not** prove MAIN was reached. After `fresh()`, [`vi = g.op(OP)` precedes `g.report(MAIN, cls)`](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opconstvalue_v1.py:201). Until the traceback identifies the failing line, the MAIN-size correlation is premature.

## Sources

(extract from answer)

## What was done with it

Accepted in full. Correction taken: the log never proved MAIN was reached (`g.op(OP)` precedes it), so the
"4-MB hierarchy" story was premature. The reviewer's raw discriminator is run first, unmodified, as
`tools/bench/diag_rpc_restart.py` (kill → reset → Dispatch → Version → op(OP) → report MAIN, pid + process start time
and elapsed time at every boundary, repr/args/traceback of the first failure, then a 60 s pid watch — the
"COM-activated LabVIEW exits with its last client" claim is tested by that watch rather than assumed). Only after
that raw run does the recipe's `com_preflight()` version (already written into `fresh()`, plus a traceback handler
and a `--test-only` entry so the PASSED build is not rebuilt) run as the controlled comparison. Log:
`tools/bench/diag_rpc_restart.log`.
