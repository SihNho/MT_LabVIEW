---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# stall-alert-wrappers-false-positive

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (130s)
- **why asked:** the PostToolUse stall hook flagged three idle WRAPPER pids (bgrun + two py.exe launchers) while the real client (pid 22008) was busy; the user made recurring alerts a mandatory peer-review trigger ("규율에 적용하도록"), so both the diagnosis and the new mechanical gate were put up for attack before relying on them. The same dispatch was asked whether the client's CPU was health or cost.
- **verdict:** ACTED ON - three real defects found (see below); the wrapper reading of the alert stands but was made subordinate to a progress measure

## Question

ATTACK this diagnosis and this mechanism; do not confirm, refute. CONTEXT: tools/lv_stallcheck.ps1 (PostToolUse hook) reported 'STALLED LabVIEW client(s): pid 7692 alive 330s CPU 0.02s; pid 12732; pid 9096' during a background probe launched as: py tools/bgrun.py --max-min 12 --log ... -- py -u tools/recipes/probe_attach_reader2.py. Process table at that moment: 7692 = py.exe launcher of bgrun, 9096 = python.exe bgrun.py, 12732 = py.exe launcher of the recipe, 22008 = python.exe recipe (kernel 68 s + user 64 s CPU, NOT listed by the hook). CLAIM 1: the alert was a false positive - the three flagged pids are wrappers that are idle by construction while their child works; the hook must only consider LEAF processes (no live child). Implemented today: build a set of ParentProcessId over all Win32_Process rows and skip any pid in it. CLAIM 2 (user rule 2026-09-14: recurring alerts must trigger mandatory peer review, enforced mechanically): the hook now writes tools/bench/stall_pid<leaf>.log with a 'STALL:' line, and tools/hooks/guard_peer.py treats '^STALL:' as a failing log so the next recipe/bench build is blocked until archive/peer/ holds a file newer than the record. Read both files. ATTACK: (a) cases where a wrapper legitimately IS the stalled COM client (e.g. bgrun itself calling COM? a leaf that spawns a helper?), (b) a leaf that is blocked on COM but shows CPU (spinning, busy-wait, marshalling) and so escapes detection, (c) ways the record/gate can be satisfied without a real review or can wedge the loop (record rewritten while stall persists; MAX_AGE 6h; PEER_GUARD_OFF; BENCH_CELL exit), (d) whether the recipe's 132 s of CPU in 8 min is itself evidence of a real problem (the net_map junk purge: per-object report() + delete_object per junk Invoke, O(junk) op runs) rather than health. ALREADY RULED OUT: no modal dialog (lv_gui.ps1 -Action dialogs = clear); LabVIEW pid 14088 responsive; only one COM client chain running. Answer with concrete failure scenarios and the cheapest discriminating test for each.

## Answer

The leaf-only rule is too strong, and the peer gate is mechanically bypassable. These are attacks, not a verdict on whether the reported event was real.

1. Wrapper can be the stalled COM owner

Failure scenarios:

- A Python process opens the LabVIEW COM object, then starts a helper for logging, timeout handling, conversion, or cleanup. The COM-owning parent is now excluded solely because it has a live child ([lv_stallcheck.ps1](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/lv_stallcheck.ps1:53)).
- A leaf blocked in COM may temporarily spawn an unrelated helper. During that helper?셲 lifetime, the actual blocked client becomes invisible.
- The present `bgrun.py` does not import or call COM, but the policy silently assumes that remains true forever. ?쏞urrently a wrapper??is not equivalent to ?쐇ncapable of owning COM.??- The `$parents` set records every reported `ParentProcessId` without verifying the parent?셲 creation time or relationship. Windows explicitly warns that a recorded parent PID can refer to a process that has terminated and that its PID may have been reused. [Microsoft?셲 `Win32_Process.ParentProcessId` documentation](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process) describes this ambiguity.

Cheapest discriminating test:

- During a harmless scratch probe, have the actual recipe create a long-lived non-COM helper before deliberately waiting at a known point. Run the detector against the resulting tree. If the recipe disappears because it became a parent, leafness is disproved as a safe exclusion rule.
- Even cheaper: statically inventory which PID imports `win32com`, `pythoncom`, or `tools/kb_com.py`, and compare that PID with the leaf decision. Classification should be ?쐏ossible COM owner,??with wrapper/leaf status only supporting evidence.
- For reused-parent ambiguity, record `(PID, CreationDate, ParentPID, parent CreationDate, command line)` in one CIM snapshot. A parent relationship that cannot be validated should not suppress an alert.

2. CPU detection has a permanent false-negative mode

`$p.CPU` is cumulative lifetime processor time, not recent utilization. Microsoft defines `TotalProcessorTime` as the sum of user and privileged CPU consumed by the process. [Microsoft documentation](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.totalprocessortime).

Therefore:

- Once a recipe has accumulated more than five CPU seconds, it can subsequently block in COM forever and never satisfy `$p.CPU -lt 5`.
- A COM-related busy retry, marshalling loop, polling loop, or Python-side spin can remain genuinely stuck while continuing to accrue CPU.
- The reported recipe?셲 approximately 132 CPU seconds already makes it permanently undetectable by the current predicate, regardless of what it does afterward.

Cheapest discriminating test:

- Sample each candidate twice, 10??5 seconds apart. Alert on low CPU delta plus no progress, not lifetime CPU:
  `?CPU`, log-file `LastWriteTime`, and ideally the current logged phase.
- Test two controlled states: one recipe that consumes ten CPU seconds and then waits indefinitely, and one that spins without advancing its log. Both should be detected.
- A thread snapshot can provide additional evidence about whether any thread is progressing; Windows supports system-wide thread enumeration through a read-only snapshot. [Microsoft Tool Help documentation](https://learn.microsoft.com/en-us/windows/win32/toolhelp/traversing-the-thread-list).

3. The review gate does not establish causal review

Concrete bypasses:

- Any newer `archive/peer/*.md` satisfies any failing record, even if it reviews a different failure ([guard_peer.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/hooks/guard_peer.py:77)). There is no PID, record path, failure hash, or review subject linkage.
- Copying, restoring, or touching an old peer file gives it a newer mtime. The comment says mtime avoids content gaming, but mtime is itself the easiest field to game.
- A blank or perfunctory Markdown file passes; the script explicitly concedes this.
- `PEER_GUARD_OFF=1` unconditionally bypasses the gate ([guard_peer.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/hooks/guard_peer.py:87)).
- `BENCH_CELL` disables stall detection completely, so no stall record is produced in that environment ([lv_stallcheck.ps1](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/lv_stallcheck.ps1:32)).
- `EXEMPT_RE` is applied to the whole command before `RUNS_RE`. A recipe command containing an otherwise harmless matching word such as `dir`, `type`, `head`, or `peer.ps1` anywhere in its arguments becomes exempt ([guard_peer.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/hooks/guard_peer.py:47)).
- The command matcher misses alternate launch forms such as `python -m ...`, variables holding the script path, wrappers other than `bgrun.py`, and potentially quoted executable/path arrangements.
- Malformed or missing hook JSON fails open ([guard_peer.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/hooks/guard_peer.py:90)).
- After six hours, an unresolved failure automatically ceases to gate ([guard_peer.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/hooks/guard_peer.py:53)).

Concrete wedge:

- The detector rewrites the stall record after every qualifying PostToolUse event ([lv_stallcheck.ps1](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/lv_stallcheck.ps1:87)).
- A legitimate review completed while the process remains flagged is immediately made older by the next rewrite. The loop cannot close until the process exits, stops matching, the detector is disabled, or alerts cease for six hours.
- Conversely, after six hours the exact same unresolved record becomes irrelevant. The system moves directly from ?쐇mpossible to close while alerts continue??to ?쏿utomatically open.??
Cheapest discriminating tests:

- Table-test the pure gate with temporary timestamps: unrelated newer review, touched old review, blank review, persistent record rewrite, age `5:59` versus `6:01`, `PEER_GUARD_OFF`, malformed JSON, and commands containing `dir` or using `python -m`.
- Give every stall event a stable ID/hash. Require a peer artifact to name that ID. Record only the transition into stalled state, or preserve a fixed `first_seen` timestamp while separately updating `last_seen`; compare the review against the event ID rather than the most recent rewrite.

4. The recipe?셲 CPU is evidence of cost, not health

The 132 CPU seconds over roughly eight minutes is about 27.5% of one CPU core averaged across the interval. It proves that substantial computation occurred; it does not prove continued progress or exclude a later COM block.

There is also a plausible self-inflicted cost explosion in `net_map`:

- Each `report()` performs one initial `_run`, followed by another `_run` for every discovered object ([gscript.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:251)).
- Purging each junk Invoke calls `delete_object()` ([gscript.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:1500)).
- Each `delete_object()` obtains the complete UID set both before and after deletion, and each UID set uses `report()` ([gscript.py](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:1206)).
- Thus deleting `J` junk objects is not merely `O(J)` LabVIEW operation runs. Because each deletion repeatedly enumerates the shrinking object collection, the purge can approach quadratic work in `J`, in addition to the work that created the junk.

Cheapest discriminating test:

- Add phase timings and counters only: walk time, junk count, initial Invoke enumeration, per-delete elapsed time, total purge time, remove-bad-wires time, and log heartbeat.
- Plot cumulative purge time against junk count for two or three small scratch sizes. Linear growth supports ordinary `O(J)` cleanup; a rising per-delete cost supports the repeated-enumeration/quadratic diagnosis.
- Most decisive: replace only the two per-delete `report()` verifications with one pre-purge UID snapshot and one post-purge snapshot in an isolated benchmark. If runtime collapses while the final UID-set verification remains equivalent, the CPU was tooling overhead rather than evidence of LabVIEW health.

The cheapest robust direction is: track plausible COM owners, sample CPU deltas and progress rather than lifetime CPU, and bind each review to an immutable stall-event ID. Leafness can remain a confidence signal, but it is unsafe as an exclusion rule.

## Sources

(extract from answer)

## What was done with it

1. **Lifetime CPU is a permanent false negative (s2) - accepted, fixed.** `lv_stallcheck.ps1` now samples CPU per (pid, start time) into `tools/bench/.stall_samples.txt` and flags a leaf whose CPU grew < 0.5 s over the last >= 60 s, in addition to the old lifetime-< 5 s rule.
2. **Gate satisfied by any newer archive file; record rewritten while the stall persists wedges the loop (s3) - accepted, fixed.** `guard_peer.py` now requires the newer peer file to NAME the failure (log basename or a recipe/bench script named in the log); the read-word exemptions no longer apply to a command that runs a build (the `dir`/`type` hole); the stall record is one file per stall EVENT (pid + start time), written once on the transition, never rewritten. MAX_AGE 6 h, PEER_GUARD_OFF and BENCH_CELL are kept as documented limits.
3. **Leaf-only exclusion is unsafe if a COM owner spawns a helper (s1) - noted, not changed.** No recipe in this fleet spawns a child while holding COM (bgrun and py.exe launchers never touch COM); the exclusion stays, with the progress rule from (1) as the primary signal. Re-visit if a recipe ever spawns helpers.
4. **CPU is cost, not health; the purge is ~O(J^2) (s4) - CONFIRMED by reading the code:** `delete_object` took a `report()` snapshot (one op run PER OBJECT) before and after every delete. Fixed in gscript.py: `uids()` uses `report_all` (one run), `delete_object(verify=False)` for bulk, one snapshot around the batch, and `net_map` prints walk/purge phase times so the next slow walk is diagnosable from its log. This is the working explanation for the 12-min `BGRUN TIMEOUT` in `tools/bench/probe_attach_reader2c.log` (recipe `tools/recipes/probe_attach_reader2.py`); the discriminating test is the phase-timed re-run.
