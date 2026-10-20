---
name: riglock_v6_wiring_approvals
description: "2026-10-21 - shared rig lock (G:\\Codes\\rig\\riglock.py) wiring into V6: item-by-item approvals after debate riglock-v6; mid-cycle experiment must still return the rig to its initial condition"
metadata:
  node_type: memory
  type: project
  originSessionId: 352cf43e-6115-43ef-a77e-e8ccfae2d90c
  modified: 2026-10-20T16:16:57.567Z
---

User answers (2026-10-21 ~01:1x) to the 12-item list from debate `tools/bench/debate/riglock-v6/` (7 rounds, converged):
- 0 rig state = 조립 (assembled) -> `G:\Codes\rig\rig_lock.json` created 01:16 by the chat.
- 3 queue + cycle-hook wiring: APPROVED (queue process = holder, per-cycle acquire/release; other live holder = WAIT; stale / corrupt / module error = StopRun; experiment = STOP; failed end hook keeps the lock; end hook checks state + ownership first).
- 5 worktree motor_gate synced to master: APPROVED, done (V6_lean d6ef8038; rotor sender not synced - guard blocks its name).
- 7 guard_lean refuses riglock write commands from lean sessions: APPROVED.
- 9 REJECTED as proposed: "안되지. 초기 조건으로 돌려줘야 원활한 실험이 가능." - an experiment declared mid-cycle must still close LabVIEW and release limits (return to the initial condition), then release the lock.
- 10 chat also runs `riglock.py set-state` on every user state word: APPROVED, written into docs/rules/hardware.md.
- Asked to explain, not yet decided: 1 (riglock fixes: permitted(), process creation time, no mutex auto-delete, Korean names), 2 (mock stage), 4 (enforcement timing (a) per path / (b) all at once), 6 (motor_gate wiring), 8 (rig_session.py wrapper), 11 (stale recovery path).

**Why:** two programs (V6 and LabVIEW2Scr) share one rig; the user wants a machine-checked lock but approves each wiring step separately.
**How to apply:** apply only approved items; 3 and 7 use item 1's functions, so they wait for item 1; never let a mid-cycle experiment leave LabVIEW open or limits set. Related: [[lean_operation_and_buffer_number_accuracy]].
