---
name: riglock_labview2scr_fixes_approved
description: "2026-10-21 - user \"승인\" (LabVIEW2Scr chat) for groups A, B, C of G:\\Codes\\rig\\proposals\\2026-10-21-labview2scr-decisions.md: riglock CR-1..4, V6 rig_session/motor_gate fixes B1-B4, RULES.md preamble / CR-5 final / AI add-on / experiment-time chat hook"
metadata:
  type: project
---

User 2026-10-21, LabVIEW2Scr chat: "승인" - ALL of groups A, B and C as listed in
`G:\Codes\rig\proposals\2026-10-21-labview2scr-decisions.md` section "USER APPROVAL". Debates: `tools/bench/debate/riglock-cr1/`,
`tools/bench/debate/l2s-conflict-01/`. Applied 2026-10-21 (report `G:\Codes\rig\proposals\2026-10-21-apply-report.md`):
- A1-A4 in `G:\Codes\rig\` (break serialization, CLI --pid, no token in status/set-state, README).
- B1 `tools/rig_session.py`: the command runs in a Windows job object; a `permitted()` exception is a stop; the whole job
  is killed and verified gone before cleanup. B3: limits are released only after that; a mid-job experiment ends with a
  "CLEANUP COMPLETE" notice. B4: refused at start while LabVIEW runs; only LabVIEW proven to be the job's own (started
  after the job began and COM-launched `/Automation` or a job member) is closed; anything else -> INCOMPLETE, lock kept
  (also `tools/rig_recover.py`).
- B2 `tools/motor_gate.py` `rig_state_agree`: session start / reference / execute refused while STATUS.md `rig-state:`
  and rig_lock.json disagree; `rig_session.py` checks it before acquiring.
- C1-C4 in `G:\Codes\rig\RULES.md`; C4 hook `tools/hooks/guard_experiment.py`, called first in `guard_bash.py` and
  wired in `.claude/settings.json` for desktop-control tools.

NOT answered by the user, not decided here: Q1 ASI release target (a readback before the first write shows +/-500, see the
report), Q2 magnet return, Q3 Arduino end state.

**Why:** two projects share one rig; the gates exist to stop the LLM from breaking the program or the machine, never to
restrict the user; after the project no LLM runs.
**How to apply:** the lean worktree (`V6_lean`: motor_gate copy, lean_queue.ps1, guard_lean) does NOT have B2/C4 yet - a
separate sync step. Related: [[riglock_v6_wiring_approvals]].
