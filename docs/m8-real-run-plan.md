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

## Pre-decided (cycle 74 judgement, 2026-09-25 — material sessions apply these without asking)

1. **Driver = a thin wrapper, not a fork.** `tools/bench/drive_m8.py` (≤120 lines) imports/parameterises
   `drive_original_copy_v5.py` (target VI path, run folder, log) rather than copying its 500+ lines; if v5 has no
   seam for the target path, add ONE parameter to v5 with its default unchanged (v5's own behaviour byte-identical).
2. **What runs is a dated byte copy** `claudeDev\D1_s4_loop17_run_<ts>.vi` (md5 == `4b621946…` checked before the
   launch). It is never saved; after the run the bed's md5 is re-read and must be unchanged. The copy is deleted at
   the end of the run (a run artefact, not a deliverable).
3. **Order in one LabVIEW session**: bed copy first (the deliverable), then the D0 baseline on a fresh original copy
   with the same driver. Each leg deadline 30 min under bgrun; LabVIEW restarted between legs.
4. **Known unwired rows are not an (a) failure**: loop 1.7's t5 (w4517) and t7 (w3268 frame index) are open by design
   (owed to QRT, `docs/d1-loop12-17-split-plan.md` Pre-decided 175/176). Record what the outputs they feed show
   (e.g. a frame-index column stuck at 0) as a FACT; only "does not reach the experiment loop / does not stop by its own
   control / writes no file / LabVIEW does not close" fails (a).
5. **Motors**: the VI may command magnet/rotor/ASI from its panel defaults under the 2026-09-24 grant; the controller
   limits set at cycle start fence them. No `motor_gate --execute` moves by the material session in this step. `TMX?`
   and position are read back only after LabVIEW has exited.
6. **(b) is measured before it is built**: the first (b) dispatch reports whether a recorded-frame harness that drives
   the WHOLE main VI (not only the kernel) exists, with file:line — it does not build one. Judgement decides the route.
7. The driver is not a `stage_*.py`, so RETRY_CAP does not apply; the material failure budget (2) does.
8. **Cycle-74 ruling on run 1 (`tools/bench/m8_run1.json`, result card 74-1): M8(a) on `D1_s4_loop17.vi` = PARTIAL.**
   Operation is proven (picks → done → bandpass → save dialog → ~3,070 frames → own-control stop → LabVIEW exits,
   5 lost frames, bed md5 unchanged). Data is NOT: `tra001-000` is header-only (0 of 2,000,000 points) and no TIFF is
   written, which is the designed consequence of the open t5 row (w4517 → `#376 'current frame data array in'`,
   `docs/d1-loop12-17-split-plan.md:430`). No diagnosis owed. The bed's data half is re-run after QRT/STOP make t5/t7.
9. **M8' = the same real run on `claudeDev\D1_s3_loop15.vi` (md5 `1a11d92a…`)**, the last bed with a whole data
   path, compared against the cycle-74 baseline leg (`tools/bench/m8_baseline.log`, fresh copy of
   `Min_Track N beads V6_ParallelLoop.vi` `2a78e17c`, the S1 source — accepted as THE baseline; the 4.5 D0 original
   is not the bed's source). Pass = run 1's pass plus tracking rows written (count comparable to baseline's 2,948 for
   a comparable frame count); garbage values allowed. No new baseline leg.
10. **(b) route**: no harness drives the whole main VI from saved frames (result 74-1 fact: only the kernel
    `docs/gpu-backend.md:122` and the display route). Building one is a tool decision for a later cycle (a replay
    frame source substituted for the camera grab in COPIES of both VIs); not started until M8' is in.
11. **Cycle-74 ruling on M8' (`tools/bench/m8s3_run.json`, result 74-4): M8(a) PASSES on `D1_s3_loop15.vi`** —
    3,514 tracking rows (header 3514/2,000,000), 3 lost frames, own-control stop, LabVIEW exited, md5s unchanged.
    The row count is comparable (baseline 2,948). **0 TIFFs is EXPECTED**: the fixture TIFF writer (#22700/#23020)
    exists only in `Min_Track N beads V6_ParallelLoop.vi`, not in S1 or any bed (`tools/bench/m8b_facts_74.log` F1),
    which also explains the baseline's 567 lost frames — the baseline's lost-frame count is NOT a clean comparison.
12. **(b) route, decided**: a replay STAGE, built as a tool under the 2026-09-24 grant. In dated COPIES of `D1_s1_copy.vi`
    and `D1_s3_loop15.vi`, replace the image feeding `#15403 IMAQdx Grab`'s `Image Out` t15412 (w19462 → `#15442
    ImageToArray` t15463 + LoopTunnel `#15188`) with an IMAQ ReadFile of frame i from the 2026-09-06 fixture set
    (10,044 TIFFs, `tools/gpu/fixture.py:15`), camera session left unconfigured/grab bypassed; bead positions from the
    same recorded clicks in both copies; run both on the same N frames and diff tra rows X/Y/Z (tolerance per
    `docs/gpu-backend.md` / N1 acceptance). Built through the simulator pipeline (stage plan file → dry → pre-run →
    run). The judgement session writes the stage's own Pre-decided (exact uids, whether `#22692 IMAQdx Get Image` in
    the Sequence #22650 must also be substituted) from a MEASUREMENT of where each grab's image is consumed first.

## Stop conditions

Any refusal from the motor gate, an Error List MISMATCH on the bed, a run that does not reach the experiment loop,
or LabVIEW not closing ⇒ stop, RESULT FAIL, judgement decides. Failure budget 2 for the material session.
