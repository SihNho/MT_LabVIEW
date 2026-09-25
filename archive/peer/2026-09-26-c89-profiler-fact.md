# c89-profiler-fact

- **agent:** claude
- **role:** fact
- **model:** fable (effort low; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $3.6264  in 258 / out 15414 / cache-create 66916 / cache-read 467724  (247s, 71 turn(s))
- **date:** 2026-09-26 01:57:52
- **outcome:** ANSWERED (249s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

API-fact question (LabVIEW 2026, Windows). Answer from NI documentation and forums with URLs for every claim; say "not found" where nothing exists. No project context needed.

1. Is LabVIEW's built-in profiler (Tools » Profile » Performance and Memory) controllable programmatically — any VI Server Application/VI method or property (public or private/scripting, e.g. 'Profile', 'Start Profiling'), any LabVIEW.ini token that starts profiling or auto-saves it, any vi.lib/resource VI that backs the Profile window, or any command-line switch? Cite the URL where each route is documented or discussed; list forum threads that concluded it is NOT programmable.
2. The Profile window's "Save" button: what file format is written (text? tab-delimited?), what columns (VI Time, Sub VIs Time, Total Time, # Runs, Average, Shortest, Longest, memory columns), what units (ms), and whether "Snapshot" is needed before Save.
3. Does a VI need "Allow debugging" (VI Properties » Execution) enabled to appear in the profiler with timing statistics? What does NI say about the profiler's own overhead and about "Timing statistics" / "Timing details" / "Memory usage" checkboxes and the timer resolution (ms, per-thread)?
4. Are subVIs called inside reentrant/inlined/parallel-For-loop contexts reported, and how (per clone, aggregated)? Are VIs inside an executable or an .llb reported?
Return a compact list of facts, each with its URL.


## Answer

**Summary:** NI has no public API, ini token, or command-line switch for the Profile window. The only known programmatic hook is a hidden, password-protected library that writes a binary profiling file. The Save button writes a tab-delimited text file. NI's docs say nothing about Allow debugging gating the profiler, and nothing about per-clone reporting. Details with URLs below.

## 1. Programmatic control

- **NI employee answer, not programmable.** In the thread "programmatically profile memory usage on multiple VIs", NI employee Nadim R wrote "there is no way to programmatically set up your memory profiler in LabVIEW" and suggested only keystroke automation. https://forums.ni.com/t5/LabVIEW/programmatically-profile-memory-usage-on-multiple-VIs/td-p/564225
- **Hidden library, same thread (2020).** wiebe@CARYA found `LabVIEW 20xx\project\_ProfileBufferAllocations.llb` containing "Turn On LV Profiling.vi" (takes a path to a BAP file), "Turn Off LV Profiling.vi", and "Read PBA Bin File API.vi". The main VI is password-protected and obfuscated, output is a cryptic binary, and the approach blocks execution. This is the only vi.lib/resource route found. Same URL as above.
- **Public VI Server methods:** not found. No `Profile` or `Start Profiling` Application or VI method appears in NI docs or forums.
- **Private/scripting methods:** not found for the Profile window. The hidden scripting tokens (`server.viscripting.showRiskyScriptingItems`, `enableSecretPopups`, `SuperPrivateScriptingFeatureVisible`) expose Desktop Execution Trace Toolkit methods (`DTT.Setup`, `DTT.IsTracingEnabled`, `DTT.GetTraceData`), not profiler methods. https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Desktop-Execution-Trace-Toolkit-DETT-programmatic-API/idi-p/3220955
- **LabVIEW.ini token:** not found. The LAVA hidden-ini-key list has no profiling key. https://lavag.org/topic/18469-i-found-some-more-hidden-ini-keys/
- **Command-line switch:** not found.
- **Other threads with no programmatic solution:** "Profiling in executable" ended unresolved, https://forums.ni.com/t5/LabVIEW/Profiling-in-executable/td-p/231908. "How can I profile part of an application?" got only manual workarounds, https://forums.ni.com/t5/LabVIEW/How-can-I-profile-part-of-an-application/td-p/638131

## 2. Save button

- **Format.** NI: "Saves the currently displayed data to disk as a tab-delimited text spreadsheet file." https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/dialog-boxes/profile-performance-and-memory-window.html
- **Columns, same page.** Base: VI Time, Sub VIs Time, Total Time, Project Library. Timing statistics: # Runs, Average, Shortest, Longest. Timing details: Diagram, Display, Draw, Tracking, Locals. Memory usage: Avg Bytes, Min Bytes, Max Bytes, Avg Blocks, Min Blocks, Max Blocks.
- **Units, same page.** A "Time unit" selector (microseconds, milliseconds, seconds) and a "Size unit" selector (bytes, KB, MB) control the displayed values. Milliseconds is not fixed.
- **Snapshot before Save.** Save writes "the currently displayed data". Snapshot "gathers profile times for all the VIs in memory" into the display, and Stop "retains the last snapshot". The NI knowledge article's procedure is Start, run, Snapshot, stop the VI, Snapshot again, then Stop. No page states Save auto-snapshots, so take a Snapshot first. https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019LT1SAM

## 3. Allow debugging, overhead, checkboxes, timer

- **Allow debugging requirement:** not found. NI's Allow Debugging description covers breakpoints, probes, highlighting, and stepping only. https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/allowdebugging.html
- **Inlined VIs cannot have debugging.** "You cannot inline a VI on which you enable debugging." https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/inlining-and-debugging-enabled.html
- **LabVIEW 2026 Q1** adds per-target override of Allow Debugging via Project Environment Settings. The profiler is not mentioned. https://forums.ni.com/t5/LabVIEW-Public-Beta-Program-in/New-2026-Q1-Feature-Enable-Disable-VI-Debugging-Without-File/td-p/4458707
- **Overhead.** "Collecting information about VI memory use adds a significant amount of overhead to VI execution, which affects the accuracy of any timing statistics." NI advises profiling memory separately from time. https://www.ni.com/docs/en-US/bundle/labview/page/profiling-vi-execution-time-and-memory-usage.html
- **CPU time only.** "The Profile Performance and Memory window measures only CPU usage time." Wait functions register only the small time to enter and return from the wait. Same URL.
- **Checkboxes.** Memory usage is only available if Profile memory usage was checked before the session began. Timing statistics adds run statistics. Timing details adds the category breakdown. https://www.ni.com/docs/en-US/bundle/labview/page/using-the-profile-performance-and-memory-window.html
- **Remote debugging** is not supported. Start profiling while the application is not running to measure only complete runs. https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/dialog-boxes/profile-performance-and-memory-window.html
- **Timer resolution.** NI docs state none. Forum users saw 15.625 ms granularity on Windows XP-era systems. https://forums.ni.com/t5/LabVIEW/profile-performance-and-memory-for-a-simple-program/td-p/2129734 and https://forums.ni.com/t5/LabVIEW/Profile-Performance-and-memory/td-p/2503504. An NI comment on LAVA says LabVIEW 2017 or 2018 switched to QueryPerformanceCounter, fixing negative-delta overflow. https://lavag.org/topic/15007-profile-performance-and-memory-inaccurate-numbers/
- **Per-thread accounting:** not found.

## 4. Reentrant, inlined, parallel, executables, llb

- **Per-clone vs aggregated reporting:** not found in NI docs. The reentrant profiling thread only concludes reentrant VIs cannot be debugged on RT. https://forums.ni.com/t5/LabVIEW/Problems-Profiling-re-entrant-VIs/td-p/1512380
- **Inlined subVIs.** Inlining copies the code into the caller and forces preallocated clones. https://forums.ni.com/t5/LabVIEW/Shared-clone-reentrancy-and-inlining/td-p/2372022. Whether the profiler still lists them: not found.
- **Parallel For loops.** Not found in profiler docs.
- **Dynamically loaded VIs.** An NI engineer confirmed subpanel-loaded VIs show 0.0 in the profiler. Static references fix it. https://forums.ni.com/t5/LabVIEW/Performance-Profiler-with-Sub-Panel-linked-VI-s/td-p/778154
- **Executables.** The profiler runs only in the development environment. The runtime-only question was never solved. https://forums.ni.com/t5/LabVIEW/Profiling-in-executable/td-p/231908
- **.llb.** Not found. The profiler lists "all the VIs in memory" per application instance, with no file-container exclusion stated. https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/dialog-boxes/profile-performance-and-memory-window.html

Note: the ni.com docs pages were readable only through a text proxy. The quoted wording is from the current LabVIEW help, which is not version-tagged for 2026.

## Sources

(extract from answer)

## What was done with it

Card 89-3 (material, fable/low). ACCEPTED as the external half of the negative search: no VI Server / ini / CLI route
to the Profile window (fact.md:31-37) → `tools/bench/diag_c89_profiler_search.md` (the record every profiler GUI act
cites as `-Exception NegativeSearch`). Local check added: this install has `LabVIEW 2026\project\_Profile Buffer
Allocation.vi` (the 2026 form of the hidden llb) — NI-private, not a route. F2 (tab-delimited Save, Snapshot first,
Time unit not fixed) and F3 (CPU time only, memory profiling OFF) are written into `tools/bench/profiler_run_plan_89.md`
§0 and §4. The "Allow debugging" precondition question is answered by the measurement in
`tools/bench/diag_c89_profiler_lvsr.log` (DebugCapable set), not by this answer's "not found".
