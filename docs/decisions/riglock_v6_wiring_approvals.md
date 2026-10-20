---
name: riglock_v6_wiring_approvals
description: "2026-10-21 - shared rig lock (G:\\Codes\\rig\\riglock.py) wiring into V6: item-by-item approvals after debate riglock-v6; mid-cycle experiment must still return the rig to its initial condition"
metadata:
  node_type: memory
  type: project
  originSessionId: 352cf43e-6115-43ef-a77e-e8ccfae2d90c
  modified: 2026-10-20T16:31:58.421Z
---

User answers (2026-10-21 ~01:1x) to the 12-item list from debate `tools/bench/debate/riglock-v6/` (7 rounds, converged):
- 0 rig state = 조립 (assembled) -> `G:\Codes\rig\rig_lock.json` created 01:16 by the chat.
- 3 queue + cycle-hook wiring: APPROVED (queue process = holder, per-cycle acquire/release; other live holder = WAIT; stale / corrupt / module error = StopRun; experiment = STOP; failed end hook keeps the lock; end hook checks state + ownership first).
- 5 worktree motor_gate synced to master: APPROVED, done (V6_lean d6ef8038; rotor sender not synced - guard blocks its name).
- 7 guard_lean refuses riglock write commands from lean sessions: APPROVED.
- 9 REJECTED as proposed: "안되지. 초기 조건으로 돌려줘야 원활한 실험이 가능." - an experiment declared mid-cycle must still close LabVIEW and release limits (return to the initial condition), then release the lock.
- 10 chat also runs `riglock.py set-state` on every user state word: APPROVED, written into docs/rules/hardware.md.
- Second answer (~01:3x): 1 APPROVED, 2 APPROVED, 6 APPROVED; asked about 4 (does an experiment stop chat motor requests? what is "all at once"), 8 (does rig_session.py go through motor_gate - yes), 11 (does recovery read the rig state - yes, and it does not start in experiment). Still open: 4, 8, 11.
- APPLIED 2026-10-21 ~02:xx: 1 (riglock.py, backups *_before_v6.py.bak, self-test 38/0), 6 (motor_gate master 0033aec6 + worktree), 3 + 9-revised (lean_queue.ps1 / lean_cycle_hooks.py, V6_lean c8ed9451), 7 (guard_lean 17/17), 2 (mock 27/27). Effect: motor_gate now refuses session / reference / execute without the lock - chat motor work needs item 8 first; the runner holds the lock per cycle.

**Why:** two programs (V6 and LabVIEW2Scr) share one rig; the user wants a machine-checked lock but approves each wiring step separately.
**How to apply:** apply only approved items; 3 and 7 use item 1's functions, so they wait for item 1; never let a mid-cycle experiment leave LabVIEW open or limits set. Related: [[lean_operation_and_buffer_number_accuracy]].
