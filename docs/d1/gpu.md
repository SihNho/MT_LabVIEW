---
type: decision
kind: topic
status: current
date: 2026-10-19
parent: docs/d1/INDEX.md
tags: [d1, gpu, mt_track.dll, tolerance, reference-bead, rotor, magnet]
---

# GPU tracking path and its acceptance (from PD419)

Background on the DLL and its interface: `docs/gpu-backend.md`. Rotor protocol: `docs/rotor-protocol.md`.

## Pre-decided

419. **(chat ingest, 2026-10-19 — lean runs 12-15, task gpuswap and its retries; user words in
     `V6_lean/tools/bench/lean_bench/user_notes.md`; offline Python harness + one diagnostic VI, bead-less images)**
     USER-RULES: U1 (the CPU's per-bead maths stays the reference); the DLL is our own file - "Dll은 애초에 만든 파일임.
     수정 자유롭게 허용함"; comparisons only with IDENTICAL inputs ("당연한거잖아").
     - **(a) Why GPU:** the user wants the GPU path in the end - tens of beads may be tracked later. CPU costs ~0.12 ms per
       pick (ceiling ~39 picks at 150 Hz); GPU in Python 15/30/50/100 picks = 1.64/1.65/2.50/3.20 ms.
     - **(b) DLL versions:** `mt_track.dll` eb19c9ac (old) -> v2 12b742a0 -> v3 a46a352e; recommended variant **v3d9**.
       rc -12 was an empty cal_path (fell back to a 5-bead default file). v3 copies the CPU rules: good rule
       (X>10, X<1280, Y>10, Y<1024, zi>1, zi<S-2, no 72-px term), pos -1, edge clip, low-stack zi.
     - **(c) Identical-input result (CPU's captured calibration bits, windows, images, starts):** good mismatch 0/3000;
       interior real beads x/y 800/800, z 796/800; pick-8 edge good/pos 200/200. v3d9 differences: edge dz max 0.51 nm,
       dxy 3.3e-6 px; interior dz max 0.10 nm.
     - **(d) Tolerances (user):** real-bead x/y 1e-6 px, z 1e-4 um; exceptions (i) near-tie gap < 1e-4, (ii) rows the CPU
       marks bad, (iii) A' edge rows and low-stack-end rows (CPU pos 0/1) x/y 1e-5 px, z 1 nm (10 nm refused: nucleosome
       unwrapping steps are 20-25 nm). good / pos / pos -1 must match. Bead-less picks: coordinates excluded, the good flag
       is judged; no bead-less picks in the coordinate set.
     - **(e) The identical-input comparison is a bug screen only. FINAL GPU acceptance = a real reference-bead CPU-vs-GPU
       ABBA experiment** (user: "cpu도 완벽하진 않을거임. 실제 실험으로 정하는게 좋겠음"): stuck reference beads should
       read fixed; use the two-stuck-bead difference; std and Allan deviation; GPU passes if not worse than CPU.
     - **(f) Same experiment adds:** a magnet-height artefact scan (apparent position vs PI magnet position, CPU and GPU)
       and a magnet-alignment check by rotation. The protocol goes to the user before any rig run (lean task `refprep`).
     - **(g) Runtime calibration route A:** pass the CPU's calibration clusters via a run-local .cal / array; any bead
       count works (15/30/50 tested). Productisation (in the VI) comes after the replay with P6L + GPU and 150 Hz legs.
     - **(h) Rotor (magnet rotation) through the gate only:** Autonics PMC-1HS/2HS, COM5 9600 8N1; X axis = rotor;
       0.72 deg/pulse (500 pulses/turn); `POS` reply is signed 8-hex. Envelope -5..+5 turns = +-2500 pulses relative to
       the session-start POS, speed 100 (user: "속도는 100 사용해"); `PAB` / `PIC` / `SPD` allowed, home / clear / save
       refused (motor_gate 36c870ac, sender blocked for direct use by guard_bash 24497ac0). First session start read POS
       100000 pulses -> window 97500..102500. Open: the tra file's RotPos reads 0 while the controller returns 100000
       (the VI's read path is suspect). The chat's first motion command was refused by the auto-mode classifier; the
       user runs the rotation check.

422. **(chat ingest, 2026-10-19 evening - rotation check, RotPos cause, lean run 17 task rotpos; report
     `V6_lean/tools/bench/lean_bench/lean_report_rotpos_fail1.md`, review `lean_review_rotpos_20261019_194933-c2.md`)**
     - **(a) Rotation check (user "지금 회전 확인해보자", chat through motor_gate):** session-start POS 100000 -> PIC 125 ->
       100125 (+90 deg, 1.1 s) -> PIC -125 -> 100000; session end OK, limits released and read back
       (`tools/bench/rotor_check_start.log`, `_end.log`).
     - **(b) RotPos cause (user):** the serial read returned wrong values for negative positions, so the user picked an
       arbitrary zero and shifted the rotation value linearly; the user wants it fixed. The original `SetCommand.vi` parses
       the POS hex unsigned; the signed copy `claudeDev\SetCommand_signed.vi` ec87a265 passed injection 16/16 and a
       hardware negative read (`docs/cycle27-plan.md:3718-3730`).
     - **(c) The shift, located (rotpos trace):** RotPos = Pos_degree = 0.72 x POS - Baseline Startpoint x 360, Baseline
       Startpoint = 200 turns (SetCommand panel default, not on the pane) = 0.72 x POS - 72000 deg, i.e. POS 100000 reads 0.
       This explains PD419(h)'s "RotPos 0 while the controller returns 100000".
     - **(d) P6R** `claudeDev\bench\lean\D1_ring_P6R_20261019_210453.vi` 333578bf = P6L byte copy + 9 x `replace_object`
       SetCommand.vi -> SetCommand_signed.vi, shift KEPT (the zero point is the user's choice). Injection 10/10; edges
       2421/2421, constants 303/303, nodes, tunnels, panel all equal. **Cycle FAIL by locked gate G7:** LabVIEW moved the 5
       swapped nodes at y = 32710 by 16 px and re-placed 25 objects beyond +-32767 on save (layout only; PD421 explains the
       coordinate limit); T9 expectation too narrow; scratch copies not deleted (E4). Retry parked in `queue/hold/rotpos.md`;
       the fix is redone on the tidied copy after PD421.
     - **(e) Open user choice - zero point:** (a) controller signed POS as is, (b) session-start POS = 0, (c) keep POS
       100000 = 0. Kept in one constant so any choice is a one-constant edit.

423. **(chat ingest, 2026-10-19 - gpuswap testcopy-16, the cycle stopped by the 01:41 STOP for the rotation check;
     report `V6_lean/tools/bench/lean_bench/lean_report_gpuswap.md`)** Steps 0-4 PASS (calibration identity byte-equal,
     CPU loader capture 15/15 bit-equal, CPU reference 5/5 and 75/75 equal to diag10, offline v3d9 reference 5/5).
     `gpuCall3` built, all gates PASS (`claudeDev\bench\lean\gpuswap_gpuCall3_20261019_013126.vi` b1310225, 28-terminal
     pane, 3 CLFNs, build peak 517 MB). Harness `gpuCall3H` attempt 1 FAILED gate B9 (`Image Name` default "untitled",
     locked ""); build fixed, attempt 2 refused by the STOP file. No GPU call, no CPU/GPU number yet; 148 pins unchanged.
     Next (not queued, user's word): harness attempt 2 (last allowed) -> cold read-back -> 5 calls -> A' judgement.
