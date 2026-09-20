---
type: peer-review
status: historical
date: 2026-09-05
tags: [peer-review]
---

# com-run-hang-after-killed-client

- **agent:** codex
- **date:** 2026-09-05
- **outcome:** ANSWERED (90s)
- **why asked:** two 180 s COM Run hangs during overnight matrix prep (2026-09-05 00:08 revert, 00:27 report); my keystroke hypothesis was refuted by a discriminating test, the replacement hypothesis (killed/concurrent COM client) needed an adversary before driving the recovery design.
- **verdict:** accepted as 'unproven' — the killed-client mechanism has no documentary support; 180 s is gscript's own watchdog, not a LabVIEW timeout; hidden modal / VI-still-running / root-loop delay remain live alternatives.

## Question

REFUTE this diagnosis, do not confirm it. Setup: LabVIEW 2026 on Windows 10, driven from Python via ActiveX (VI Server: Application -> GetVIReference -> Run with wait). Twice tonight a Run call (of a small reporter/revert VI) blocked for 180 s with no modal dialog visible; both times a DIFFERENT python COM client had just been force-killed (taskkill /F /T) or was still running its own Run call. A controlled test afterwards (revert -> SendInput Alt/Esc focus -> Run, with and without a mouse click in between) returned instantly in all cases, so keystroke/menu-mode is ruled out. Claimed cause: a concurrent or abruptly killed ActiveX client leaves the LabVIEW VI Server busy (single-threaded UI/root loop serving the previous call, or an orphaned synchronous Run), so the next client Run blocks until that finishes/times out. Questions: (1) Is there documented or forum evidence that VI Server ActiveX calls are serialized through the LabVIEW UI thread/root loop such that a hung or killed client can block another client for minutes? (2) What ELSE could make Run block ~180 s with no dialog (e.g. a VI still running because its caller died, Wait Until Done semantics, a hidden dialog on another desktop, ExportVIStrings/other calls), and what cheap test discriminates each? (3) Is Application.Quit/restart the only recovery, or is there a lighter one (Abort VI, Application property, closing references)? Already ruled out: modal dialog (screenshot at hang shows none), keystroke menu-mode (test above), stray python processes at the time of the second hang (none listed). Answer with sources (NI docs/forums URLs).

## Answer

The diagnosis overreaches. NI evidence supports ??Run` must briefly enter the UI/root loop,??but I found no NI documentation or forum evidence that force-killing an external ActiveX client leaves an orphaned COM call that owns LabVIEW?셲 VI Server for about 180 seconds.

## 1. What the evidence actually supports

An NI employee explains that starting a top-level VI with the VI Server `Run` method posts work to LabVIEW?셲 UI thread. Modal windows, menus, drop-downs, and other UI activity can therefore delay `Run`. [NI forum: Mouse activity blocks Call by Reference](https://forums.ni.com/t5/LabVIEW/Mouse-activity-blocks-call-by-reference/td-p/422389)

NI?셲 current knowledge base likewise says some VI Server operations require the UI thread/root loop and may wait until the UI is idle. In particular, loading a VI by path with `Open VI Reference` can hang there; using the name of an already-loaded VI avoids that loading step. [NI: Open VI Reference hangs while selecting a menu](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001Dd6ISAS&l=en-US)

There is also older NI documentation saying LabVIEW handles ActiveX communication through its UI execution system, in the context of avoiding a circular LabVIEW?봗estStand synchronous-call deadlock. [NI TestStand manual](https://download.ni.com/support/manuals/375070a.pdf)

But none of those sources says:

- ActiveX requests from independent external clients are globally serialized for the full duration of `VI.Run`.
- Killing a client leaves its synchronous `Run` registered as an orphan.
- LabVIEW waits 180 seconds to reclaim a dead client.
- A dead client?셲 COM reference keeps the UI/root loop locked.

Thus the temporal correlation?붴쏿nother Python client was killed immediately before the hang?앪봡oes not establish the proposed mechanism. It may instead mean that the killed client successfully started a VI whose execution continued, or that both clients encountered an already-existing blocked LabVIEW state.

The exact 180-second duration is especially suspicious: the ActiveX signature is `Run([async])`, with `async` defaulting to false, so an omitted or incorrectly marshalled argument makes the call wait for VI completion. [NI forum quoting the ActiveX signature](https://forums.ni.com/t5/LabVIEW/Different-ActiveX-methods-appear-when-referencing-a-VI-inside-or/m-p/1879201/highlight/true) I found no NI source identifying 180 seconds as a LabVIEW VI Server dead-client timeout.

## 2. Competing explanations and cheap discriminating tests

| Explanation | Why it fits | Cheap discriminator |
|---|---|---|
| Synchronous `Run` waited for the reporter itself | ActiveX `Run()` defaults to synchronous; `Run(True)` is the non-waiting form. [NI forum](https://forums.ni.com/t5/LabVIEW/Different-ActiveX-methods-appear-when-referencing-a-VI-inside-or/m-p/1879201/highlight/true) | Log the exact Python argument and call `Run(True)` explicitly. If that returns immediately while `Run(False)` hangs, the delay is VI completion, not general VI Server congestion. |
| The previous client successfully launched a top-level VI before dying | A VI started with `Run VI` is a separate top-level VI; losing or closing the client reference does not inherently prove that execution stopped. [NI: Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html) | Before another `Run`, query that exact VI?셲 `Execution.State` through a fresh, untyped reference. NI defines `Idle`, `Run top level`, and `Running`. [NI: Check whether a VI is running](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YIEJCA4&l=en-US) |
| A non-reentrant VI or dependency was already executing | NI says non-reentrant VIs serialize simultaneous calls. [NI execution properties](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/dialog-boxes/execution-page-vi-properties-dialog-box.html) | Query the reporter and its relevant subVIs??execution states. Also run a distinct already-loaded no-op VI: if that starts but the reporter does not, this is VI-specific serialization, not a globally busy VI Server. |
| A blocking node inside the reporter/revert VI | I/O, DLL, automation, network, file access, or an internal wait can keep a VI from completing. NI notes that abort/reset can itself wait when a thread is in I/O or another blocking operation. [NI: Causes of ?쏳esetting VI??(https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019M50SAE&l=en-US) | During the hang, inspect `Execution.State`; after aborting, note whether LabVIEW enters ?쏳esetting VI.??A persistent reset strongly implicates a blocking execution node rather than COM-client ownership. |
| The delay happened before `Run`, such as `GetVIReference`/loading | Opening a VI by path can wait for the root loop to become idle. [NI knowledge base](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001Dd6ISAS&l=en-US) | Timestamp every individual COM boundary: application acquisition, `GetVIReference`, each control set, `Run` entry, and `Run` return. Preload once, then obtain it by in-memory name. Do not classify the event as a `Run` hang merely from the last coarse log line. |
| `ExportVIStrings` or another scripting call occupied the root loop | Many VI Server operations have per-method ?쏮ust wait until user interface is idle??metadata; root-loop dependence must be established method by method. [NI knowledge base](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001Dd6ISAS&l=en-US) | Time every method independently and repeat without export/scripting operations. A concurrently executing `ExportVIStrings` is only supported as the cause if removing it removes the hang or its call interval overlaps the stall. |
| A hidden modal window existed despite the screenshot | A screenshot of visible windows cannot exclude an invisible/off-screen/behind-owner modal. NI users report dialogs on another monitor and modal windows hidden behind other windows. [NI forum: second-monitor dialogs](https://forums.ni.com/t5/LabVIEW/dialog-box-blocks-all-activities/td-p/589271), [NI forum: modal windows not frontmost](https://forums.ni.com/t5/LabVIEW/Modal-windows-not-frontmost/td-p/2513658) | Enumerate all top-level and owned windows for the LabVIEW PID, including invisible windows; record class, title, visibility, enabled state, owner and desktop. Disabled LabVIEW frames plus an enabled owned window is stronger evidence than a screenshot. |
| Python?셲 180-second watchdog produced the duration | No NI material I found assigns 180 seconds to `VI.Run` or dead-client recovery. | Record both the actual COM return time and the watchdog-kill time. Repeat with 60/120/240-second client limits. If the apparent duration follows the configured limit, 180 seconds is observational, not LabVIEW?셲 timeout. |
| Genuine root-loop obstruction | Even `Run(True)` must get through the UI/root-loop launch step. [NI employee explanation](https://forums.ni.com/t5/LabVIEW/Mouse-activity-blocks-call-by-reference/td-p/422389) | While the suspect call is blocked, use a second client to read a cheap property documented not to require UI-idle, then attempt an already-loaded no-op `Run(True)`. Property success plus `Run(True)` failure supports a root-loop-specific obstruction. If all calls block, it indicates broader COM/server trouble. |

The strongest first test is therefore:

1. Preload a unique no-op reporter.
2. Explicitly call `Run(True)`.
3. Immediately poll its execution state through a separate reference.
4. Time every COM call separately.
5. Repeat while killing a different synchronous client.

That distinguishes ?쐋aunch was blocked,???쐋aunch succeeded but execution did not finish,??and ?쐔he delay was actually in another ActiveX method.??
## 3. Recovery short of restarting LabVIEW

Restarting is not the only documented recovery.

- The ActiveX VI object exposes `Abort()`, equivalent to LabVIEW?셲 Abort Execution button. [NI ActiveX `VI.Abort`](https://www.ni.com/docs/fa-AF/bundle/labview-api-ref/page/properties-and-methods/activex/vi/abort.html)
- NI explicitly documents opening a reference to a running VI and invoking `Abort VI` programmatically. [NI: Abort LabVIEW VI programmatically](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YI57CAG&l=en-US)
- A cooperative stop mechanism remains safer than aborting. NI warns that aborting can leave resource state uncertain and recommends designing a programmatic stop path. [NI: Causes of ?쏳esetting VI??(https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019M50SAE&l=en-US)
- Closing leaked references can prevent memory retention and stale VI state, but closing a reference is not a general substitute for stopping an independently running top-level VI. NI specifically classifies a VI started by `Run VI` as a separate top-level VI. [NI: Closing References](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)

A practical escalation order is:

1. Query the target?셲 `Execution.State`.
2. Request its cooperative stop, if available.
3. Invoke `Abort()` on that exact VI.
4. Close and reacquire the Python COM references.
5. Only then quit/restart LabVIEW.

Caveat: if the UI/root loop itself cannot service ActiveX requests, an ActiveX `Abort()` may also be unable to enter LabVIEW. In that state, try LabVIEW?셲 local abort mechanism; if the VI is stuck in non-interruptible I/O or abort/reset itself never completes, NI?셲 documented last resort is terminating the LabVIEW process, with possible loss of unsaved work. [NI: Abort a stuck VI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P9hASAS&l=en-US)

Bottom line: the observations are consistent with a root-loop delay, but they do not specifically implicate a killed COM client. The leading alternatives are a synchronous `Run(False/default)` waiting on a VI that remained active, a delay in `GetVIReference` or another scripting call misattributed to `Run`, or an invisible modal/owned window. The explicit `Run(True)` plus per-call timestamps and execution-state polling should settle most of this in one controlled reproduction.

## Sources

(extract from answer)

## What was done with it

bench_prep.com_alive now probes a real Run in a child process (60 s) and restarts LabVIEW on timeout (standing permission); the matrix driver no longer force-kills cells while they may be inside a COM call except on the 40 min cell timeout; per-call timing instrumentation of gscript is queued as a follow-up. Recorded in the skill reference (vi-scripting.md, 'COM Run hangs').
