---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opwiresource-fail4-report-per-object-on-5000-wires

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (60s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

BRIEF ATTACK (LabVIEW 2026 VI Scripting over COM, python). tools/recipes/build_opwiresource_v0.py run 4 (log tools/bench/build_opwiresource_v0.log): the BUILD finished and SAVED OpWireSource_v0.vi (all gates PASS, ExecState 1, labels written) - then the TEST phase produced no output for 18 minutes and bgrun killed the process tree at its 20-minute deadline (BGRUN TIMEOUT). The first statement of the test is g.report(MAIN, "Wire") on the 4-MB main VI. MY DIAGNOSIS: gscript.report() runs the reporter op ONCE PER OBJECT (its sibling report_all() returns all rows in ONE run; our own gscript.uids() docstring records that this O(n) behaviour was the hidden cost behind an earlier 12-minute timeout), and the main VI has on the order of several thousand wires, so the call cannot finish. Fix: take the uid list with gscript.uids(MAIN, "Wire") (report_all-based, one op run) and index into it. Questions (cite or reason from the evidence given): (1) any competing explanation for a silent 18-minute stall right at that call - e.g. Traverse on class Wire being intrinsically slow, or a COM/apartment stall - and what one cheap measurement separates them (I intend to time uids(MAIN,"Wire") alone with a 120 s watchdog and print the count)? (2) after bgrun kills the python client mid-COM-call, LabVIEW.exe survives (pid 14088 here): is it safe to reuse that instance for the next batch, or must it be restarted - our project rule says a killed client leaves its references alive inside LabVIEW and the handle count must be read; I intend to start the rerun with a forced restart plus a two-round-trip preflight. (3) is there any scripting-level way to find a wire by UID directly (e.g. VI.Block Diagram plus a UID lookup method) that avoids enumerating all wires at all - give the property/method ID if one exists. Read-only.

## Answer

Your diagnosis is the leading explanation, but question 3 reveals a better final implementation.

1. The stall

`report(MAIN, "Wire")` being O(number of wires) fits the evidence extremely well:

- Build and save completed.
- Silence began at the first test statement.
- `report()` invokes the reporter separately for each index.
- The prior 12-minute failure establishes the same scaling problem.
- No dialog/error output appeared.

A competing explanation is that each invocation repeatedly performs a full recursive `Traverse for GObjects`; NI describes Traverse as recursively searching nested containers, so thousands of complete traversals can readily become approximately O(n짼), rather than Wire traversal itself being unusually slow once. [NI discussion of recursive Traverse behavior](https://forums.ni.com/t5/LabVIEW/get-references-to-all-controls-on-front-panel/m-p/694003/highlight/true)

Your proposed measurement is the right discriminator:

```text
time uids(MAIN, "Wire") once; print elapsed time and count; 120 s watchdog
```

Interpretation:

- Completes quickly with thousands of UIDs ??the repeated-run `report()` design caused the timeout.
- Consumes most of 120 seconds ??the single Traverse itself is expensive on this VI.
- LabVIEW shows negligible CPU and no completion ??investigate modal/root-loop or COM dispatch blockage instead.

Strictly, timing alone does not separate ?쐓low Traverse??from a COM/apartment stall if it times out. The cheapest extra observation is LabVIEW CPU delta during the watchdog plus the project?셲 enabled-window/modal scan. Active CPU favors traversal; near-zero CPU plus a blocked-window pattern favors a modal/root-loop stall. This is consistent with your locally recorded failure history, not an external guarantee.

2. Reusing PID 14088

For this project: restart it.

Generic out-of-process COM normally maintains server-side object/reference counts, but the precise cleanup behavior after forcible client termination depends on the server implementation; Microsoft?셲 documentation does not establish that LabVIEW will promptly dispose of every internal VI/object reference. [Microsoft COM server reference-counting overview](https://learn.microsoft.com/en-us/windows/win32/com/out-of-process-server-implementation-helpers)

Moreover, your project already has a measured rule that a killed client leaves LabVIEW-side references/handles alive. Thus PID survival and two successful calls would prove responsiveness, not cleanliness. Forced restart followed by:

- PID identity check,
- two agreeing lightweight round trips,
- handle-count baseline check,

is the correct batch boundary. Restart is operationally required by your project evidence, even though killing a COM client does not universally imply that LabVIEW is wedged.

3. Direct UID lookup

Yes. Use:

```text
<LabVIEW>\vi.lib\VIServer\UID to GObject Reference.vi
```

It takes a VI reference and UID and returns the corresponding GObject reference, avoiding traversal entirely. NI community references identify that installed VI and note that it works in the development environment, not the runtime engine. [NI discussion and installed path](https://forums.ni.com/t5/LabVIEW/Unique-ID-for-all-front-panel-object/m-p/4302972)

It is not a VI Server property or invoke method, so there is no property/method ID to provide. Reportedly it wraps this internal call:

```c
int32_t UidToObjRef(
    const int32_t *VIReference,
    const int32_t UID,
    int32_t *LVObjReference
);
```

[Wrapper implementation discussion](https://forums.ni.com/t5/LabVIEW/Frame-Names-for-Disable-Structure/m-p/3965935)

Therefore the best production route is an Op around `UID to GObject Reference.vi`, followed by a cast to `Wire` and the existing `Terms[] ??source terminal ??Owner` chain. That removes both repeated traversal and the remaining one-time enumeration. Validate that an unknown UID returns a handled error/null reference without invoking automatic error handling.

## Sources

(extract from answer)

## What was done with it

Applied: the test takes the wire list with `gscript.uids()` (report_all — ONE op run) and prints its elapsed time
and count, so the discriminator the reviewer asked for runs as part of the rerun; `--test-only` now starts with a
forced LabVIEW restart plus the two-round-trip preflight, per the batch-boundary rule. The better route is
confirmed to exist on this machine — `C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\VIServer\UID to
GObject Reference.vi` (8 KB, alongside `NI_VI Scripting.lvlib`) — and is recorded in NAMES.md as the op to build
when a UID→object lookup is needed again, with the reviewer's caveat that an unknown UID must be shown to return a
handled error rather than tripping automatic error handling. Not built now: the one-run enumeration is enough for
four wires. Rerun: `tools/bench/build_opwiresource_v0.log` (`--test-only`).
