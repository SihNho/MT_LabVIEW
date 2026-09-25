# Brief 89-1 (cycle 89 judgement): per-bead cost attribution in situ (`docs/d1-loop12-17-split-plan.md` Pre-decided 195(d))

Why: the kernel swap did not change frame loss at 15 picks (195(c), `tools/bench/m8_kswap_88.json`: 3,410 and 3,490
lost, against 3,776 for the same-session control). The t0 model (`docs/t0-instrumentation-plan.md:16`) predicts how big
the loss is, but not which per-bead work carries it. This card measures where each loop iteration's time goes.

## Build: an instrumented DIAGNOSTIC copy (never delivered, never a bed)
1. Make a byte copy `claudeDev\D1_s1_copy.vi` → `claudeDev\D1_s1_t0_<ts>.vi`. `D1_s1_copy.vi` stays byte-unchanged.
2. Bracket each per-bead group of `docs/t0-instrumentation-plan.md:96-104` that sits on the per-frame path with
   timing reads. The groups are: kernel call `#5058`, `check N bead pos v3-kimlab.vi`, Median/FIR filters, the display
   group (the Draw*/Flatten Pixmap nodes and the Z/dZ plots) and the file write (`save N xyz traces.vi` / `save trace.vi`).
   Also add one whole-iteration stamp for each While loop that holds any of them.
   Record which groups you could not bracket and why. Partial coverage with a written reason is acceptable.
3. Mechanism constraints (judgement, binding):
   - Add ONLY timing reads (Tick Count / High Resolution Relative Seconds) and the minimum sequencing they need. That
     means a flat-sequence wrap, OR a stamp helper spliced onto an existing error wire. Both are allowed.
   - A stamp helper must be REENTRANT (preallocated). It must NOT be a non-reentrant VI called from two loops, because
     that creates a new mutex (`docs/t0-instrumentation-plan.md:67-70`).
   - Do not add a queue wait, a UI property node or a front-panel Value read on the frame path.
   - Durations are accumulated inside each loop (shift register, array or sum+count) and written to ONE file after the
     loops stop. Nothing does per-iteration file I/O.
   - Record ms per iteration per group, preferably as the distribution (median and p90 over iterations). The loop
     iteration count per group also goes into the file.
4. Gates: `computation_diff(D1_s1_copy, t0 copy)` = 0 rows (only timing nodes and their wiring/structures added),
   ExecState 1 warm and cold, saved by script, md5 and bytes reported. A new verb or helper may be built under the
   2026-09-24 tool grant: ≤120 lines on stagekit, a negative self-test, handle count flat. If the launch gate asks for
   a dry run / pre-run, do it.

## Run (PRECONDITION: every build gate above passed; real hardware, rig 조립, 2026-09-24 motor grant)
The runner has already set the limits and referenced the PI stage.
- Use the `drive_m8_load83.py` pattern at 120 s and 90 Hz: `D1_s1_t0` at 15 picks ×1 and at 8 picks ×1.
- For each leg, record Total Lost Frames, frames acquired, the actual rate, and the per-group timing file.
  Close LabVIEW after every leg and verify it is gone.
- Write `tools/bench/t0_insitu_89.json`: per leg, per group ms/iteration (median, p90, count), whole-iteration
  ms per loop, and lost frames.
- Perturbation fact (report only, not a gate): compare lost frames at 15 picks with the uninstrumented S1 references
  (3,776 in cycle 88, 3,331/3,161 in cycle 83).
- There are no beads on the rig, so garbage tracking values are not a failure.

## Close
The md5s of `D1_s1_copy.vi`, `D1_s1_kswap_20260926_004935.vi` and the bed `D1_l2_a1_20260925_235224.vi` are unchanged,
and LabVIEW is gone. Return facts only. Name the group with the largest per-bead slope (15 vs 8 picks) as a
measured number; do not recommend a design.
