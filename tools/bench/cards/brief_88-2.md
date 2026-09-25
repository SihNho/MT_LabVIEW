# Brief 88-2 (cycle 88 judgement) — kernel-swap load test (PD194(d); outcome review `archive/peer/2026-09-25-outcome-review-20260925.md:162,184`)

Why: cycle 83 measured the S1 copy (INDEX row 48, `tools/bench/m8_load_83.json`). At 15 picks it lost 3,331 of
~10,680 frames (3,161 on the repeat); at 8 picks it lost about 0.1 %. The per-bead tracking cost is the lever. The
swap is one call-site repoint of a subVI that has already been verified.

## PRECONDITION (rule 1a) — before any edit
Cite `INDEX` rows 12 and 17 (file:line). Together they must show two things:
- the parallel kernel is bit-identical to the kernel the S1 call uses, on the recorded fixture;
- it has the same connector pane: every terminal the S1 call site wires exists on it with the same type.

If either citation is missing, return BLOCKED and say what is missing. Do not swap.

## Build
1. Make a byte copy `claudeDev\D1_s1_copy.vi` → `claudeDev\D1_s1_kswap_<ts>.vi`.
2. Exactly ONE node changes callee. Every wire of the old call site must sit on the same terminal of the new node
   (read back by uid).
3. ExecState must be 1. Save by script. Report md5 and bytes. `D1_s1_copy.vi` must stay byte-unchanged.
4. If no scripting verb replaces a subVI callee in place, you may build one (user 2026-09-24 tool grant): ≤120
   lines on stagekit, a self-test with a negative case, handle count flat over 20 calls.

## Run (real hardware: rig 조립, motors driven by the running VI under the 2026-09-24 grant)
The runner has already set the limits and referenced the PI stage.
- Run `drive_m8_load83.py` legs at 15 picks, 120 s, 90 Hz: kswap ×2, then `D1_s1_copy.vi` ×1 as the same-session
  control.
- For each leg record Total Lost Frames, frames acquired and the actual frame rate. After each leg, close LabVIEW and
  verify it is gone.
- Put every leg in `tools/bench/m8_kswap_88.json`.
- There are no beads on the rig, so the tracking values are garbage and that is not a failure. The measurement is
  lost frames.

## Close
The md5s of `D1_s1_copy.vi` and of the bed `D1_l2_a1_20260925_235224.vi` are unchanged, and LabVIEW is gone.
