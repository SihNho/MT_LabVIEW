---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvalue-fail1-stale-op-cache

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (57s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

BRIEF ATTACK (Python win32com client of LabVIEW 2026). Log tools/bench/build_opconstvalue_v1.log run 1 (script tools/recipes/build_opconstvalue_v1.py): phase D read the NI example fine; the recipe then called fresh() = Stop-Process LabVIEW + 8 s + g._lv = None, and the next COM call raised 0x800706BA "RPC server is unavailable" (winerror -2147023174).
MY DIAGNOSIS: the same defect class as archive/peer/2026-09-14-addshiftreg-run2-rpc-unavailable.md (your H3 then): gscript caches op-VI references in a module dict (_cache, filled by op(path) = lv().GetVIReference(...)); resetting only _lv leaves those proxies bound to the killed instance, and the first cached-op call after the kill dies. Fix: gscript.reset() clears _lv AND _cache; both recipes' fresh-instance helpers now call it.
Attack: (1) any other reading (e.g. the 8-s sleep too short for the new instance to register its class factory, so Dispatch itself failed)? The traceback shows the error at a SetControlValue on a cached VI - consistent with a stale proxy; confirm that distinguishes the two. (2) Is clearing the cache sufficient, or must the dead proxies be explicitly released (pythoncom) to avoid a later crash on GC? (3) A guard: should op() verify the cached proxy's Application is alive (e.g. compare a pid captured at Dispatch time) before use? Cheapest robust pattern. Read-only; cite what you read (tools/gscript.py lv()/op()/reset()).


## Answer

Your diagnosis is the best reading, with one evidentiary caveat: the saved log omits the traceback, so the failing `SetControlValue` line must come from the fuller console traceback.

1. The traceback distinguishes stale proxy from failed activation.

`op(path)` returns `_cache[path]` without calling `lv()` when cached. Only a cache miss reaches `dynamic.Dispatch("LabVIEW.Application")` via `lv()` ([gscript.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:66)). Therefore:

- Failure inside `dynamic.Dispatch`: supports ?? seconds was too short/class factory unavailable.??- Failure at `cached_vi.SetControlValue(...)`: Dispatch was never attempted on that path; the cached VI proxy was invoking the killed server.

That is strong discrimination, not merely consistency. `0x800706BA` is Win32/RPC error 1722, indicating that the contacted RPC server was unavailable; it does not itself identify why, but the call site does. [Microsoft?셲 error description](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/replication-error-1722-rpc-server-unavailable)

The recipe sequence also fits exactly: phase D populated `_cache`; `fresh()` killed LabVIEW; the old implementation reset only `_lv`; the next `op(...)` reused `_cache` ([recipe](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opconstvalue_v1.py:49)). The eight-second/startup hypothesis could cause a later, separate activation failure, but cannot explain a `SetControlValue` made through a cache hit.

2. Clearing `_cache` is sufficient for correctness; explicit `pythoncom` teardown is unnecessary.

The revised `reset()` clears both `_lv` and `_cache` ([gscript.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:80)). Removing those Python references releases their wrappers when no other references remain. COM lifetime is reference-counted through `IUnknown::AddRef/Release`. [Microsoft COM reference-counting documentation](https://learn.microsoft.com/en-us/windows/win32/com/implementing-reference-counting)

Do not use `pythoncom.CoUninitialize()` as an object-release mechanism: it uninitializes COM for the calling thread, not individual cached proxies. [pywin32 documentation](https://mhammond.github.io/pywin32/pythoncom__CoUninitialize_meth.html)

Likewise, manually invoking `_oleobj_.Release()` is riskier than useful because the Python wrapper still believes it owns the interface. If deterministic cleanup is desired, the safe pattern is:

```python
_cache.clear()
_lv = None
# optional gc.collect(), mainly if cycles are suspected
```

Any proxy copied into a local variable remains independently live, so `reset()` cannot revoke arbitrary aliases. That is not a reason to force-release them; it is a reason not to retain op proxies across `fresh()` boundaries. A dead proxy?셲 eventual cleanup should not produce a Python-level ?쐋ater crash?? the meaningful hazard is accidentally invoking it.

3. Do not add an `Application` liveness call to every `op()` cache hit.

That check would itself be an RPC call through potentially dead state, adds overhead, and still has a check/use race. PID comparison is better as a restart-boundary invariant than a hot-path guard.

Cheapest robust pattern:

- Clear `_cache` and `_lv` at every intentional restart boundary.
- Kill/restart.
- Poll `dynamic.Dispatch` plus one harmless Application round-trip until ready; preferably require two successful, spaced checks against the same PID, as your existing `com_preflight()` convention does.
- Only then permit `op()` to populate the new cache.
- Optionally store a monotonically increasing connection generation with each cache entry; increment it in `reset()` and reject entries from older generations.

A generation guard catches internal lifecycle mistakes essentially for free. A PID guard is useful in `fresh()`/preflight for detecting an external restart, but checking the OS PID on every `op()` call is unnecessary. COM activation depends on a registered class object/class factory, so a fixed sleep alone is weaker than retrying an actual activation and round-trip. [Microsoft `CoCreateInstance`](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocreateinstance), [class-factory/ROT behavior](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/automat/implementing-a-class-factory)

Verdict: accept the diagnosis and `reset()` fix. Add a startup readiness poll if absent; do not add manual `Release`, `CoUninitialize`, or per-op liveness RPCs.

## Sources

(extract from answer)

## What was done with it

Confirmed: the failing call was a cache-hit `SetControlValue` (no Dispatch attempted), which discriminates the
stale proxy from a too-short restart wait. `gscript.reset()` (clear `_cache` + `_lv`) is the fix; no pythoncom
teardown, no per-call liveness check — the rule is "reset at every intentional restart boundary, never retain op
proxies across it" (both recipes' fresh-instance helpers). Rerun: `tools/bench/build_opconstvalue_v1.log` (run 2).
