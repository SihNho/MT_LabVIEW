---
type: plan
kind: stage-plan
status: current
parent: docs/goalmap.json
date: 2026-09-24
tags: [m8, real-run, d1, acceptance]
---

# M8 — first REAL RUN of the current bed `D1_s4_loop17.vi` (goal map M8, before M3)

User, 2026-09-24: *"이제 메인 vi 조립시에는 실제 작동시켜야 할테니 그대로 해볼 것"* · *"코드 작동은 현재 테스트가 가능하나 내가
실제 채널을 현미경에 놓지 않아서 데이터는 이상한 숫자가 나올 것"* · *"사이클 종료하고서는 제대로 LabVIEW 끄는것 잊지 말것"*.
Motors are granted until withdrawn; reference + limits are verified by the session hooks.

## Two halves, two evidences

| half | proves | pass |
|---|---|---|
| **(a) operation** | the assembled VI runs | picks → done → bandpass panels → save dialog → experiment loop ≥ 2,000 frames → stop by the VI's own control (no Abort) → files written; `Total Lost Frames` reported; LabVIEW closed and verified gone; PI back at reference; limits released |
| **(b) numbers (rule 1a)** | computation unchanged | same recorded frames through a copy of the original and through the bed give the same X/Y/Z within the agreed tolerance (recorded-frame path from the D0/N1 harness) |

Garbage tracking values in (a) are NOT a failure (no sample channel on the microscope; rule 1c').

## What already exists (cite, do not rebuild)

- `tools/bench/drive_original_copy_v5.py` — the D0 driver: picks by template-located clicks, done button, three
  `choose bandpass` Yes buttons, save dialog answer, stop by the VI's own control (1.0 s), both legs 39/1
  (`archive/2026-09-18-status-cycle31-d0-delivered.md` §4–§5). Locating: `tools/bench/d0_locate.py` (template match,
  every click located live — Pre-decided 9).
- Session hooks: `motor_gate.py --session start/end` (reference FNL + 2 mm verify, limits set/released), runner
  `labview_close_hook` (COM Quit → taskkill → tasklist empty), `errorlist_hook` (Error List read before the cycle).
- Facts to respect (§4 of the D0 archive): no save-path control — the destination is a file dialog; stop controls
  live in the frame loop and act only once the experiment loop runs; `TMX?` is read only after LabVIEW has exited
  (COM ports busy while the VI runs).

## Steps (each leaves a file)

1. **P0 dry-run of the driver against the bed** (no LabVIEW): `stage_prerun.py --dry` on a copy of
   `drive_original_copy_v5.py` retargeted to `claudeDev\D1_s4_loop17.vi` (a byte-identical dated copy of the bed is
   what runs; the bed is never opened for writing). Template patches re-cut from a fresh panel capture of the bed
   (its front panel is the original's, but every click is located live).
2. **(a) run 1** under bgrun (deadline 30 min), full leg once: log = `tools/bench/m8_run1.log`, RESULT line, files
   `tra*/cal*` under the run folder, `Total Lost Frames`, frame count, stop latency. Then `labview_close_hook`.
3. **Compare with the D0 baseline** (`drive_original_copy_v5` on the ORIGINAL copy, same session): frames, lost
   frames, stop latency, files — a table in `tools/bench/m8_run1.json`.
4. **(b) recorded-frame equivalence**: the D0/N1 recorded-frame harness on (i) `D1_s1_copy.vi` and (ii) the bed;
   X/Y/Z diff table, tolerance from `docs/gpu-backend.md` / N1 acceptance. Log `tools/bench/m8_numbers.log`.
5. **Goal map**: M8 `done` with the four logs as evidence; M3 becomes current.

## Stop conditions

Any refusal from the motor gate, an Error List MISMATCH on the bed, a run that does not reach the experiment loop,
or LabVIEW not closing ⇒ stop, RESULT FAIL, judgement decides. Failure budget 2 for the material session.
