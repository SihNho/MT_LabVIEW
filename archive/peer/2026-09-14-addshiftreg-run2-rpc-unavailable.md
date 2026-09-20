---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# addshiftreg-run2-rpc-unavailable

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (110s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS DIAGNOSIS. Do not confirm it. A background batch died unpredictably and I must not act on my own explanation unchallenged.

SEQUENCE (all times 2026-09-14):
- 22:35:2x I killed the running LabVIEW.exe (pid 7148) from PowerShell with Stop-Process -Force, then Start-Sleep 6, then confirmed "killed" (Get-Process returned nothing).
- 22:35:43 a Python batch started: tools/recipes/build_opaddshiftreg_v0.py, driving LabVIEW 2026 over COM (win32com Dispatch) via tools/gscript.py.
- The batch's first phase A0 SUCCEEDED: it read node labels and terminals of OpExitWhile_v0.vi over COM.
- It then copied OpWhileCast_v0.vi to OpAddShiftReg_v0.vi, opened its front panel, and printed a successful census line ("start: Property=3 Invoke=0 Wire=16 ExecState=1").
- The very next COM call, SetControlValue on an op VI's "vi path" control inside gscript.node_labels, raised pywintypes.com_error -2147023174 "The RPC server is unavailable". Batch died at 34 s.
- Afterwards a LabVIEW.exe process EXISTS with StartTime 22:36:01 (i.e. started AFTER the batch began) and a fresh handle count of 30651.

MY EXPLANATION, which you must try to refute:
H1 - a kill/Dispatch RACE. Killing LabVIEW and immediately COM-Dispatching in the same few seconds attached the client to an instance that was still tearing down (or whose COM/ActiveX registration still pointed at the dying process); the first few calls worked against it, then it exited and the RPC endpoint vanished. The 22:36:01 process is a second, later launch.

COMPETING EXPLANATION I also need attacked:
H2 - LabVIEW CRASHED while handling the freshly copied OpAddShiftReg_v0.vi (copied on disk, then OpenFrontPanel'd, then traversed). Note node_labels had just worked on a different VI seconds earlier, so whatever it was would be specific to the new copy.

QUESTIONS:
1. Which of H1/H2 does the evidence actually favour, and what evidence would distinguish them? Note the log shows the census on the NEW copy already succeeding before the failure - does that weaken H2?
2. Is "RPC server is unavailable" (-2147023174 / 0x800706BA) diagnostic of the SERVER PROCESS having exited, or can it also be raised by a still-live server that is busy, marshalling across apartments, or by a client-side proxy that went stale? Cite documentation.
3. What is the correct, documented way to wait for LabVIEW to be fully ready for ActiveX/VI Server automation after a forced kill and relaunch - is there a readiness signal better than "Dispatch succeeded" (this project has been burned before by calls that succeed and then hang)? Is repeatedly Dispatching until a cheap round-trip call succeeds the right preflight?
4. Does killing LabVIEW with Stop-Process -Force risk leaving a stale ActiveX/ROT registration that a later Dispatch can bind to? How would a client detect that?
5. Name the single cheapest DISCRIMINATING test between H1 and H2, runnable in under a minute.

Context files to read in this project directory: tools/bench/build_opaddshiftreg_v0_run2.log (the failure), tools/bench/build_opaddshiftreg_v0.log (the earlier run), tools/recipes/build_opaddshiftreg_v0.py, tools/gscript.py (the lv()/op()/_run() COM layer), and docs/NAMES.md for the recorded "changed on disk" modal trap. Cite file paths and documentation URLs you actually read. Read-only: change nothing, do not open LabVIEW.


## Answer

The evidence favors neither H1 nor H2 as stated. It most strongly favors a third explanation:

**H3 ??the cached `OpNodeLabels_v0.vi` COM proxy became disconnected while the LabVIEW process remained alive.**

H1?셲 ?쐁lient attached to the killed, still-tearing-down process??is difficult to reconcile with the timestamps. H2?셲 ?쐍ew copy crashed LabVIEW??is difficult to reconcile with both the successful census and the apparently surviving process.

## 1. What the evidence favors

### Why H1 is weak

The killed PID 7148 was confirmed absent before the batch began. The LabVIEW process found afterward had `StartTime 22:36:01`, approximately 18 seconds after the 22:35:43 batch start. Unless the process observations missed another LabVIEW instance, the successful A0 calls almost certainly caused or used the 22:36:01 instance?봭ot PID 7148.

More importantly, H1 predicts that the process serving the successful calls subsequently disappeared. You have not shown that:

- the PID serving A0 differed from the PID present afterward;
- the 22:36:01 process exited;
- another LabVIEW process replaced it.

A StartTime alone cannot establish ?쐓econd launch.??You need PID and StartTime sampled during the successful calls and again after the failure.

### Why H2 is also weak

The copied `OpAddShiftReg_v0.vi` had already survived:

- `OpenFrontPanel`;
- three separate censuses?봒roperty, Invoke, and Wire;
- an `ExecState` read returning 1.

Only then did the failure occur on:

```python
vi = op(OP_NODE_LABELS)
vi.SetControlValue("vi path", target)
```

That is a call on the cached **reporter VI reference**, before the reporter ran or traversed the copied target. See [gscript.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/gscript.py:383>) and the traceback in [build_opaddshiftreg_v0_run2.log](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/build_opaddshiftreg_v0_run2.log>).

Therefore the successful census materially weakens H2. It does not completely exclude delayed target-specific corruption, because the earlier counts and `ExecState` do not exercise `Node.Label`. But the repository records `node_labels` successfully covering 626 nodes across 170 diagrams without crashing, which also makes ?쐎rdinary label traversal crashes on this small copy??a poor prior; see [NAMES.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/NAMES.md:227>).

The strongest discriminator would be:

- same PID survived ??no process crash; investigate a disconnected proxy, VI unload/reload, endpoint failure, resource exhaustion, or internal LabVIEW subsystem failure;
- serving PID exited and Windows/WER records a fault ??H2/crash family;
- serving PID changed between readiness probes and failure ??H1/restart family.

The reported handle count of 30,651 is suspicious, but without a baseline or time series it proves nothing.

## 2. What `0x800706BA` actually means

`-2147023174` is `HRESULT_FROM_WIN32(1722)`, namely `RPC_S_SERVER_UNAVAILABLE`. It is **not diagnostic proof that the server process exited**.

Microsoft says RPC 1722 occurs when a lower transport reports a connectivity failure; possible causes include resource limitations, the higher-level protocol not running, or the higher-level protocol itself returning the error. RPC ?쐆as no special insight??into the underlying failure. [Microsoft?셲 RPC 1722 documentation](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/replication-error-1722-rpc-server-unavailable)

A dead server or stale proxy is compatible with 1722, but not uniquely identified by it. Conversely:

- A normally busy COM STA should ordinarily produce `RPC_E_SERVERCALL_RETRYLATER` (`0x8001010A`).
- A message-filter rejection ordinarily produces `RPC_E_SERVERCALL_REJECTED` (`0x8001010B`).
- A disconnected COM object has the more specific `RPC_E_DISCONNECTED` (`0x80010108`).
- Wrong-apartment use has `RPC_E_WRONG_THREAD` (`0x8001010E`).

Those are distinct documented COM results. [Microsoft COM/RPC error-code table](https://learn.microsoft.com/th-th/windows/win32/com/com-error-codes-3)

Thus ?쐌erely busy??or ?쐌erely marshalled across apartments??is not the best reading of this exact code. But endpoint loss, server-side RPC failure, resource exhaustion, a stale proxy, or a server that remains as a Windows process while its automation endpoint is gone are all still compatible.

## 3. Readiness after forced termination

I found no NI-documented LabVIEW ActiveX readiness event stronger than successfully creating the Application object and completing real VI Server operations.

NI documents that:

- `LabVIEW.Application` creates an Application automation object;
- `GetVIReference` creates the dependent VirtualInstrument object;
- loading a VI from disk may wait until LabVIEW?셲 UI is idle.

[NI ActiveX documentation](https://www.ni.com/en/support/documentation/supplemental/06/converting-visual-basic-activex-examples-to-equivalent-labview.html) and [NI VI Server documentation](https://www.ni.com/docs/tr-CY/csh?context=lvcore_lvhowto_vi_server)

`WaitForInputIdle` is not a sufficient ActiveX readiness signal. Microsoft defines it only as the GUI message loop reaching an idle state, principally useful for waiting until a main window exists. It says nothing about LabVIEW?셲 ActiveX class factory, VI Server, compilation, or scripting subsystems. [Microsoft `WaitForInputIdle`](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.waitforinputidle)

Therefore repeated cheap round trips with an unchanged PID are a reasonable **project-specific health check**, but not a documented LabVIEW guarantee. A good preflight would:

1. `Dispatch`;
2. obtain PID/StartTime;
3. `GetVIReference` to one fixed, known-good tiny VI;
4. read a cheap property such as `ExecState`;
5. release every obtained proxy;
6. wait briefly;
7. create a completely new Application and VI reference and repeat;
8. require the same PID/StartTime.

Do not merely repeat calls through cached proxies.

There is also a defect in the currently added `com_preflight`: it sets `g._lv = None` but does not clear `g._cache`. Since `op()` returns cached VirtualInstrument proxies, later attempts can continue testing an old disconnected proxy rather than the newly dispatched Application. See [build_opaddshiftreg_v0.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_opaddshiftreg_v0.py:52>) and [gscript.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/gscript.py:61>).

## 4. Forced termination and stale ROT registrations

Abrupt termination prevents LabVIEW from performing its orderly shutdown, including explicit revocation of ActiveX registrations. Microsoft documents that strongly registered active objects must be explicitly revoked, and that orderly shutdown should revoke the active object and disconnect external clients. [Microsoft `RegisterActiveObject`](https://learn.microsoft.com/en-us/windows/win32/api/oleauto/nf-oleauto-registeractiveobject)

That establishes a theoretical stale-registration window, but it does **not** establish that LabVIEW uses a strong ROT registration in precisely this way or that a stale entry persisted here.

Also distinguish:

- COM class registration in the registry: persistent configuration identifying how to launch LabVIEW;
- ROT/active-object registration: runtime association with an existing automation object.

A forced kill does not normally make the registry ?쐏oint at the dying PID.??H1 currently conflates these mechanisms.

A client cannot prove freshness from `Dispatch` alone. It should:

- record PID/StartTime before and after activation;
- make a real call on both Application and a newly obtained VI proxy;
- discard all old Application and VI references after any RPC failure;
- perform a fresh activation;
- confirm the PID/StartTime is stable.

If an old proxy returns 1722 while a freshly activated proxy immediately works against the same live PID, that is strong evidence of a stale/disconnected proxy?봭ot a process crash.

## 5. Cheapest discriminating test

Run one read-only probe against the already-running, stable LabVIEW instance:

> Record PID/StartTime; create a **new, uncached** Application reference and a **new, uncached** `OpNodeLabels_v0` reference; call `SetControlValue("vi path", copied_path)` and run `node_labels` once; record PID/StartTime again.

Interpretation:

- New uncached call succeeds, while the old cached reference fails ??stale/disconnected proxy; refutes H2 and the dying-process form of H1.
- PID disappears or changes exactly when traversing the copy ??crash/restart; favors H2.
- It fails with 1722 but the identical fresh probe against the original donor succeeds in the same PID ??target-specific H2 family.
- Both targets fail while the PID remains unchanged ??server/endpoint/resource problem, not copy-specific H2.

This is more discriminating than repeating the entire build, takes seconds, and directly tests the operation at the failure boundary.

## Sources

(extract from answer)

## What was done with it

**The reviewer's H3 was right and both of my hypotheses were wrong.** It located the failure precisely: the call that
raised `0x800706BA` was `SetControlValue` on the **cached reporter-VI proxy** inside `node_labels`, *before* the
reporter ran or touched the copied target — which weakens H2 (the copy had already survived OpenFrontPanel, three
censuses and an `ExecState` read) and leaves H1 unsupported (I never sampled the serving PID during the successful
calls, so "a second launch replaced it" was never evidence, only a story that fitted).

**Root cause, found from that pointer — my own recipe bug.** `a0()` runs first and caches op-VI references; `build()`
then executed `g._lv = None`, re-Dispatching the Application *underneath* those already-cached VI proxies. The next
call against a cached proxy hit a disconnected endpoint. The idiom `g._lv = None` is copied from recipes where it is
the FIRST statement of `main()`; in this recipe it sat after a phase that had already cached references.

Fixes applied to `tools/recipes/build_opaddshiftreg_v0.py`:
- `g._lv = None` happens **once**, at the top of `main()`, before anything caches a proxy; removed from `build()`
  and from the preflight loop.
- Added `com_preflight()`: require two spaced round-trips that agree, against an **unchanged pid**, before building —
  because "Dispatch succeeded" and even two working calls were not readiness (the reviewer confirmed NI documents no
  stronger ActiveX readiness signal, and that `WaitForInputIdle` is not one).

Also recorded from the answer: `0x800706BA` = `RPC_S_SERVER_UNAVAILABLE` and is **not** proof the server exited;
a merely-busy STA would give `RPC_E_SERVERCALL_RETRYLATER` (`0x8001010A`) and a disconnected object
`RPC_E_DISCONNECTED` (`0x80010108`). Rerun as a new batch: `build_opaddshiftreg_v0_run3.log`.
