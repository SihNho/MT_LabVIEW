---
name: timeouts-must-be-mechanical-and-unbypassable
description: Every path that can wait on LabVIEW/COM must carry an enforced time limit (foreground hook, background runner with a kill deadline, every COM call in the watchdog thread) — a rule that can be bypassed by one code path is not a rule; when a bypass is found, fix the mechanism, not the prose
metadata:
  pinned: false
type: decision
status: in-force
date: 2026-09-05
source: memory/timeouts_must_be_mechanical_and_unbypassable.md
---

# Timeout checks must be mechanical on EVERY path — a bypass means the rule is broken

User, 2026-09-05, after a background keystone-discovery job sat hung for 3 h 48 min unnoticed:
*"Timeout 검사에서 우회된 내용이 있는 것 같은데 규칙 개선 필요할듯"* — the timeout check had been
bypassed, so the rule itself needed improving.

How it was bypassed (so the pattern is recognisable next time):
- The PreToolUse guard (`tools/hooks/guard_bash.py`) limits only FOREGROUND tool calls that touch
  LabVIEW; a `run_in_background` job had no ceiling at all, and "background it" had become the
  approved way to run anything long.
- gscript's COM watchdog wrapped only `Run`/`Invoke`; `GetVIReference`, `SetControlValue`,
  `GetControlValue` and the editor-driven `gui_save` waits ran unguarded on the main thread, so a
  wedged LabVIEW UI loop blocked the client forever with no screenshot and no exception.
- The "heartbeat while unattended work runs" rule existed only as prose in CLAUDE.md and was not
  executed.

Standing rule derived from the correction:
1. A limit must exist on every path that can block: foreground calls (hook), background jobs (a
   runner with a hard kill deadline that always writes a final line the monitor sees), and every
   COM call (one central guarded call helper — nothing touches the COM object directly).
2. When a rule is found bypassed, the fix is a mechanism (hook, wrapper, runner, watchdog), not a
   stronger sentence in a document. The same lesson as the GUI gate and the answer-first hook.
3. Silence from a background job is never "still running": the runner's deadline, not Claude's
   attention, is what ends a hang.
