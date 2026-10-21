---
type: rules
status: current
date: 2026-10-10
tags: [rules, hardware, motor, camera]
---

# Rules - hardware, the rig and the frame path

Restated briefly from `docs/rules/CLAUDE-full-2026-10-10.md` (cited line ranges hold the full wording and quotes).
Live numbers (envelope, rig state, grants) are in `STATUS.md`'s hardware banner and `tools/bench/motor_limits.json` -
never restated here.

## Rule 1b - permission follows the RIG STATE (re-issued 2026-09-16; the ASI is not a special case)

- **The table.** Disassembled: all motors, the ASI piezo and the camera allowed. Assembled: camera allowed; motors and
  ASI ONLY through `tools/motor_gate.py` inside the safe-motion envelope. Experiment running: nothing - no motor, no
  ASI, no camera. *Scope:* PI translation, rotor, magnet, ASI piezo, camera. `docs/rules/CLAUDE-full-2026-10-10.md:39-51`
- **Assembled = the single gateway and the envelope only** (user amendment 2026-09-17, envelope set at the rig
  2026-09-18: PI magnet 0-39 mm, ASI x/y inside `SL`/`SU` = live position +/-2 mm, never homed, z free). The envelope
  says what is SAFE, not when motors are allowed; it counts only while really enforced as refusing code.
  *Mechanism:* `tools/motor_gate.py`. `docs/rules/CLAUDE-full-2026-10-10.md:52-64`
- **Never give the ASI its own rule again** - the 2026-09-13 piezo-detached carve-out is retired; permission is by
  rig state, not instrument identity. `docs/rules/CLAUDE-full-2026-10-10.md:65-67`
- **Controller limits are SET at every cycle start and RELEASED at every cycle end, each verified by readback**, by the
  runner (`cycle_runner.py` `motor_limits_hook` -> `motor_gate.py --session start|end`); a start that does not verify
  stops the runner before the cycle, an end that does not verify stops it after. Nothing is sent in experiment/unknown
  state. **Session start = a real PI reference move first** (`SVO 1 1`, `RON 1 1`, `FNL 1`, `FRF? 1`, `POS 0`), then a
  2 mm commanded-vs-readback check within 0.05 mm, retried up to 3x (`REF_ATTEMPTS`); all fail -> no cycle. Never
  "restore" a reference by declaring the current counter (`RON 1 0` + `POS 1`) - that drove the magnet into the hard
  limit on 2026-09-23. `docs/rules/CLAUDE-full-2026-10-10.md:68-68`
- **Motor grant 2026-09-24 (until the user withdraws it):** motors may be driven by the gate and by a running main VI
  with the rig assembled; a newly assembled main VI's acceptance test is a REAL run (replay only when a real run cannot
  answer); reference check and limits set/released are never skipped. **Every cycle ends with LabVIEW CLOSED and
  verified gone** (camera acquisition must not keep running) - `cycle_runner.py` end hook. `docs/rules/CLAUDE-full-2026-10-10.md:69-69`
- **Only the user announces a state change**; never infer one from silence, quiet or session length. Inside a declared
  state, do not ask per incident. `docs/rules/CLAUDE-full-2026-10-10.md:70-73`
- **Shared rig lock (user 2026-10-21, item 10 of debate `tools/bench/debate/riglock-v6/`):** when the chat receives a
  state change from the user (실험중 / 실험 마침 / 조립 / 분해), it ALSO runs
  `py G:\Codes\rig\riglock.py set-state experiment|assembled|disassembled --by chat --note "<the user's words>"`,
  besides the existing STOP-file write and the `STATUS.md` line. `G:\Codes\rig\rig_lock.json` was created 2026-10-21
  01:16 with `assembled` on the user's word "현재: 조립". **Shared rig rules for every project (V6 and LabVIEW2Scr):
  `G:\Codes\rig\RULES.md`** (user 2026-10-21). In V6 the lock is wired into the lean queue + cycle hooks, `motor_gate.py`
  (session / reference / execute need the lock; cleanup = ownership), `tools/rig_session.py` (chat / one-off rig jobs)
  and `tools/rig_recover.py` (dead holder, user's words only) - decision `docs/decisions/riglock_v6_wiring_approvals.md`.
  **Fixes approved 2026-10-21 ("승인", `docs/decisions/riglock_labview2scr_fixes_approved.md`):** new device work is
  refused while STATUS.md `rig-state:` and `rig_lock.json` disagree (motor_gate, rig_session); rig_session refuses to
  start while LabVIEW runs, kills its whole job (job object) before releasing limits, closes only its own LabVIEW;
  while `rig_lock.json` says experiment, `tools/hooks/guard_experiment.py` blocks device / LabVIEW / kill / lock-acquire /
  install commands and screen clicks (reads and screenshots pass) - `G:\Codes\rig\RULES.md` section 5.
  **Magnet return (Q2 "Q2 동의함", applied 2026-10-22, `docs/decisions/rig_magnet_return_and_followups.md`):**
  `motor_gate.py --session end` first sends `MOV 1 0` (0 mm = the ceiling, farthest from the sample) through the send
  path while the session limits are still set and verifies POS within 0.01 mm; not verified -> nothing released, the
  session file and the lock are kept. `--session end` runs in the experiment state too, for the lock holder only. Cycle
  ends (cycle_runner, lean hooks) close only the cycle's own LabVIEW, LabVIEW first, then the motor end.
- **While disassembled, hardware measurement is expected work** (VISA/serial latency, motor-read cost, rotor
  negative-angle check) - not deferred. `docs/rules/CLAUDE-full-2026-10-10.md:74-76`
- **The rotor is SIGNED** - the new VI uses `SetCommand_signed.vi` and follows the hardware number with its sign; the
  unsigned `SetCommand.vi` was a serial-path workaround; the sign round-trip on the real link is to be measured, not
  assumed. `docs/rules/CLAUDE-full-2026-10-10.md:77-81`
- **Superseded, never reinstated:** the 2026-08-27 blanket motor ban and the piezo-detached condition. **Hazard:** a VI
  run as a side effect - the broken-arrow and Run buttons are the same pixels; check the arrow state or use menus
  before clicking there on any VI that can reach an instrument. `docs/rules/CLAUDE-full-2026-10-10.md:82-88`

## Rule 1c - no serial on the frame path (2026-09-16)

- **No VISA/serial call anywhere on the frame acquisition path.** Not one frame may be lost to motor communication;
  focus re-adjustment is continuous (the stage drifts on its own). Serial lives in its own loop, owns its VISA session
  exclusively, reaches the frame path only by a non-blocking handoff. "The serial branch is conditional, so cheap on
  average" is refuted at the premise. `docs/rules/CLAUDE-full-2026-10-10.md:89-101`

## Rule 1c'' - control signals by LOCAL VARIABLE, the focus loop on its own clock (2026-09-25)

- **Control/trigger signals between loops (focus requests, setpoints, enable flags, counters) are locals; queues are
  for lossless DATA streams only** (e.g. the file writer's results FIFO). Never detect an EDGE on a polled boolean -
  publish a value the reader can compare (counter, position). **Autofocus copies the CODE, not the memory:** Case
  `#10407` has no threshold - every 25 frames it moves by `clamp(idx_bead0 - slices/2 + 'Focus Deviation from the
  Center', +/-0.2)` on bead index 0 (`docs/autofocus-case-10407.md`); a threshold trigger would be a new feature
  needing the user's decision. Design in force: the frame loop publishes the reference bead's z and the auto-reset
  counter as locals; the focus loop runs on its own cadence and applies the original arithmetic under `Auto-Focus` /
  `Limit of Auto-Focus`. *Mechanism:* `tools/stage_prerun.py` `control_path_lint` (X8) refuses a queue for a control
  signal or a cross-loop edge detector. `docs/rules/CLAUDE-full-2026-10-10.md:102-125`

## Rule 1c' - test runs are UNATTENDED until reassembly; the harness clicks the beads (2026-09-17)

- **Run sequence:** panel parameters -> configure -> a while loop waiting for clicks on the live image (first =
  reference bead, rest = magnetic beads) -> a button that ends it and runs calibration -> the experiment loop. The
  user chose **option 1**: scripted GUI clicks on the image, the done button and the save-path entry through
  `tools/lv_gui.ps1 -Exception Approved -Evidence "user 2026-09-17 bead-pick option 1"`; a `.cal`-loading substitute
  was rejected. Garbage tracking in a no-bead run is not a failure. GPU path first, CPU afterwards. `docs/rules/CLAUDE-full-2026-10-10.md:126-138`

Related decisions: `docs/decisions/hardware_operation_permission.md`, `docs/decisions/motor_safe_motion_envelope.md`,
`docs/decisions/motors_allowed_real_runs_close_labview.md`, `docs/decisions/no_serial_on_the_frame_path.md`,
`docs/decisions/locals_not_queues_focus_loop_own_clock.md`.
