---
name: rig_magnet_return_and_followups
description: "2026-10-21/22 - Q2 \"Q2 동의함\": every session end returns the PI magnet to 0 mm (verified) BEFORE the limits are released, also on a mid-job experiment; Q1 ASI release = original +-500; Q3 Arduino deferred; follow-ups 1-4 ordered \"V6 후속작업 실시\""
metadata:
  type: project
---

User, LabVIEW2Scr chat (`G:\Codes\rig\proposals\2026-10-21-labview2scr-decisions.md`, "More user decisions"):
- **Q1** answered by the record: the ASI X/Y limits were +-500 before the project's first write
  (`tools/bench/p2_asi_query_limits.log`, 2026-09-18 15:09), so the release value is the original state. ASI Z was
  +-0.075 then; the read-only check (2026-10-22) found no project write of Z anywhere (only SL/SU X/Y are ever sent).
- **Q2 "Q2 동의함":** at session end the PI magnet returns to **0 mm** (the ceiling, farthest from the sample) BEFORE
  the limits are released, verified by readback. Return fails or is not verified -> nothing released, lock kept. Also
  when an experiment is declared mid-job. The rotor is not decided (left where it is).
- **Q3 "Q3 동의함":** the Arduino end state is decided when the hardware is used.
- Follow-ups "후속작업은 제안과 같이" (brief `G:\Codes\rig\proposals\2026-10-21-followups-brief.md`, items 1-4), ordered
  2026-10-22 "V6 후속작업 실시". Applied: report appendix in `G:\Codes\rig\proposals\2026-10-21-apply-report.md`.

**Why:** experiments, which other lab users run without any chat, need everything motor-related exactly as before the
project; the gates exist to stop the LLM from breaking the program or the machine, never to restrict the user.
**How to apply:** `motor_gate.py --session end` does the return (send path, limits still set, POS within 0.01 mm), then
the release; every session-ending path calls it (rig_session, rig_recover, lean_cycle_hooks end, cycle_runner,
finish_orphan_cycle). It runs in the experiment state for the lock holder only. Cycle ends close only the cycle's own
LabVIEW (B4). Related: [[riglock_labview2scr_fixes_approved]], [[riglock_v6_wiring_approvals]].
