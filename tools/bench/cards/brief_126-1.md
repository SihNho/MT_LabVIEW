# Brief 126-1 — shared hygiene runner, OpFsAddFrame_v0 hygiene rerun, Flat Sequence scratch run

Decisions this card applies (do not re-open): `docs/d1-loop12-17-split-plan.md` PD253(b)(c)(e) and the
violation decision `docs/violation-decisions.md` "repeated-failure-class — 2026-10-01 (cycle 126 judgement ...)".

PD242(b)'s equal-state clause, VERBATIM (it binds every hygiene check from now on):
> "For a CREATOR the probe may delete each created constant+indicator after its call, or recycle the scratch VI without
> saving at fixed call counts, measuring handles at the same VI state each time."

## STEP 1 — build `gscript.hygiene_run(op, workload, recycle=True)` (the device; first)
- Wraps the existing `hygiene_probe` (`tools/gscript.py:240`). `workload(target)` is a callable that makes ONE op call on an
  open scratch VI copy. With `recycle=True` the runner opens a fresh byte copy, runs a fixed number of calls, closes the copy
  WITHOUT saving, and repeats until the requested total (>= 2,000).
- Reads LabVIEW's handle count (and GDI/USER object counts) at the SAME VI state each round: before the calls, after the
  calls, after the close. Pass band = the existing device rule: 0 errors AND handles flat +-100 across rounds (judge the
  after-close reads against each other / the first one), refs closed.
- Writes the `op-hygiene/1` record exactly as the existing records do (`tools/bench/op_hygiene/*.json`), plus the three
  handle series and GDI/USER.
- Offline self-test (no LabVIEW, stubbed COM like the other offline self-tests): copy count returns to the start value after
  every round; a record carries all three handle reads; a workload that raises is counted as an error. <= 120 lines.

## STEP 2 — rerun `claudeDev\OpFsAddFrame_v0.vi` (md5 `cfaa304f…`) hygiene THROUGH `hygiene_run`
- Same workload as `diag_c125_5_opfs.py`'s hygiene part (Add Frame on the donor FS), now with copies recycled. 2,000 calls.
- Measurement only: report h_pre / h_post / h_closed series, GDI/USER, errors, PASS/FAIL by the band. Do NOT change the op.
  If it FAILS, record it, close LabVIEW, return (first unexpected result).

## STEP 3 — the written scratch run `tools/bench/diag_c125_5_fsscr.py` (only if STEP 2 PASSes)
- On a P3a BYTE COPY (never the bed): 3 frames in case `#22694`'s False frame (`27219`), a frame-1 -> frame-2
  sequence-tunnel wire; read back frame count/order (`fs_frames`), per-frame diagram uid, tunnel class, `Is Broken?`,
  `wire_joints` free ends (prediction 0), class-count census delta.
- Record a census sample (`tools/bench/census_samples.json`) and a `tools/bench/scratch_verify/` record. List what the
  stagexec route / stagesim model / self-tests will need (names, measured classes) — the offline card builds them.
- `gscript.fs_donor` / `fs_frames` / `fs_add_frame` are being machine-tested for the first time here: if one misbehaves,
  that is the first unexpected result — finish the step cleanly and return.

## Always
- Close LabVIEW at the end and verify it is gone. Bed `D1_ring_p3a_20261001_180540.vi` md5 unchanged.
- No stage recipe launched; no whole-VI Remove Broken Wires; `connect_term_uid` unchanged.
- Facts in `result_126-1.json`; the stagexec/stagesim/self-test needs as `open` lines.
