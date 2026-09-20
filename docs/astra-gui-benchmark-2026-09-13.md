---
type: reference
status: current
date: 2026-09-13
tags: [docs, benchmark, gui]
---

# Astra GUI benchmark — infrastructure failure, no performance result

The user requested direct screenshot-guided mouse wiring, permitting an exception to the read-only and scripting-first rules for isolated benchmark VIs.

Historical comparison: docs/benchmark-report-2026-09-04.md section 8. Four GUI micro-operations repeated three times: move Invoke (+100,+50), place Index Array, Change To Write, close Find using Cancel. Opus-low: 12/12, 9.3 minutes; Sonnet-low: 12/12, 15.8 minutes. These did not test direct wiring.

Prepared ASTRA_GUIBENCH_20260913.vi as a copy of GUIBENCH_v0.vi in claudeDev. No benchmark GUI input was issued. Computer Use sky.list_windows successfully located the front panel, but get_window_state failed twice, including fresh window selection, with:

    SetIsBorderRequired failed: 해당 인터페이스를 지원하지 않습니다. (0x80004002)

Classification: infrastructure failure before first timed trial. No accuracy, action-time, or model comparison can be reported. Computer Use guidance requires stopping after unsuccessful capture recovery and forbids mixing PowerShell UI automation in the same turn.

Earlier scripting attempt is excluded: it did not match the user's requested method. That attempt incorrectly mixed Traverse order and Nodes creation order. Reporter evidence in tools/bench/astra_diagnose.log confirms array wire reached UID54 instead of UID51. The target was never executed. Do not run ASTRA_WIRING_20260913_v1.vi: the disk file is an unchanged template copy and unsaved edits may remain in memory.

No hardware or original VI was executed or saved. Scratch panels were left open. No benchmark Python process remained at the start of GUI preparation; preparation exited normally. Execution lock released. Scripts/logs retained for reproducibility; actual GUI trials remain outstanding.
