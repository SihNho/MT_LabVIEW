---
type: negative-search
status: current
date: 2026-09-26
card: 89-3
tags: [profiler, gui-exception, negative-search]
---
# Negative-search record: LabVIEW's Profile Performance and Memory window has NO scripted route

Cited by every profiler GUI act as `lv_gui.ps1 -Exception NegativeSearch -Evidence tools/bench/diag_c89_profiler_search.md`
(CLAUDE.md §3 "GUI only where scripting is VERIFIED unreachable"; §5 "External search is MANDATORY").
The operation CLASS is "start / snapshot / save the built-in profiler". Each concrete use below is a click on that
window or its Tools-menu entry; no scriptable alternative construction exists for any of them.

## External search (peer `-Role fact`, fable/low + web, `archive/peer/2026-09-26-c89-profiler-fact.md`, ANSWERED 249 s)

| route asked | result | evidence |
|---|---|---|
| public VI Server Application/VI method or property that starts/snapshots/saves profiling | **not found**; NI employee: "there is no way to programmatically set up your memory profiler in LabVIEW", keystroke automation suggested | https://forums.ni.com/t5/LabVIEW/programmatically-profile-memory-usage-on-multiple-VIs/td-p/564225 (fact.md:31,33) |
| private / scripting methods | not found for the profiler; the hidden scripting tokens expose DETT (`DTT.Setup`, `DTT.GetTraceData`), not the Profile window | https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Desktop-Execution-Trace-Toolkit-DETT-programmatic-API/idi-p/3220955 (fact.md:34) |
| `LabVIEW.ini` token that starts or auto-saves profiling | **none found** (LAVA hidden-ini list; LabVIEW Wiki Debugging / Performance / Execution System / Miscellaneous pages) | https://lavag.org/topic/18469-i-found-some-more-hidden-ini-keys/ , https://labviewwiki.org/wiki/LabVIEW_configuration_file/Debugging (fact.md:35, fact2.md:45) |
| vi.lib / resource VI backing the Profile window | only a hidden, password-protected `project\_ProfileBufferAllocations.llb` ("Turn On LV Profiling.vi", writes a cryptic binary BAP file, "blocks execution") | same 564225 thread (fact.md:32) |
| command-line switch | not found | fact.md:36 |
| threads that ended without a programmatic solution | "Profiling in executable" (unresolved), "How can I profile part of an application?" (manual workarounds only) | https://forums.ni.com/t5/LabVIEW/Profiling-in-executable/td-p/231908 , https://forums.ni.com/t5/LabVIEW/How-can-I-profile-part-of-an-application/td-p/638131 (fact.md:37) |

## Local search (this machine, 2026-09-26 01:5x, read-only)

| where | query | result |
|---|---|---|
| `docs/vi-server-ids.json` | `[Pp]rofil`, `Debug` | 0 hits (no registered property/method ID touches the profiler) |
| `tools/gscript.py`, `tools/lv_gui.ps1`, `docs/toolkit-capabilities.md` | `profil` (case-insensitive) | only `-NoProfile` PowerShell flags; no verb |
| `C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.ini` | `[Pp]rofil|[Dd]ebug` | 0 hits |
| `…\LabVIEW 2026\resource\**` | `*rofil*`, `*Perf*` | no profiler VI (only AutoRecover/CreateSubVI/RemoteWindows `Perform_*.vi`) |
| `…\LabVIEW 2026\vi.lib\**` | `*rofil*` | only `pid.llb\PID Setpoint Profile.vi` (unrelated) |
| `…\LabVIEW 2026\project\` | `*rofile*` | **`_Profile Buffer Allocation.vi`** exists (the 2026 form of the hidden llb the forum names). It is NI-private, password-protected per the thread, writes a binary BAP file and "blocks execution" — not a route to the per-VI timing table, and not one this project may reverse-engineer (rule 1 hygiene: a LabVIEW-private VI is an original). |
| `archive/peer/**` | `Profile|Performance and Memory|Snapshot` | no earlier exchange on the profiler (only `-NoProfile` hits) |

## Conclusion

Start / Snapshot / Save of the Profile Performance and Memory window are reachable only through its GUI (Tools menu +
three buttons + one Save dialog). Every act is enumerated with capture → locate → act → capture → confirm in
`tools/bench/profiler_run_plan_89.md`. The Save dialog is answered by keyboard (`d0.answer_save_dialog` pattern,
`drive_original_copy_v2.py:522-560`), which is the same verified-unreachable class as the cal-file save dialog.
What IS scriptable and is used instead of GUI: loading/running/stopping the VI (COM), reading `AllowDebugging`,
`ExecState` (ActiveX `VirtualInstrument` properties, fact2.md:30-31), the lost-frame counter (VI Server), and the
saved tab-delimited file (Python).
