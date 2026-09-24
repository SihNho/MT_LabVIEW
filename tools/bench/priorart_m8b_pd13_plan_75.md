# Plan under review: docs/m8-real-run-plan.md entry 13 (PD13, cycle-75 ruling) — replay stage by SUBVI-NODE SWAP

Source: `docs/m8-real-run-plan.md:98-126` (md5 4a202784562dfecff83a13a0019162e3). Verbatim:

13. **Cycle-75 ruling — PD12's substitution point is WITHDRAWN; the replay swaps SUBVI NODES, not wires**
    (measured: `tools/bench/m8b_grab_consumers_75.json`, `tools/bench/m8b_frame_source_75.json`, results 75-1/75-2).
    `#15403 IMAQdx Grab` feeds only the bead-pick display (Flatten/Draw Pixmap) and never reaches a tra row. The ONLY
    pixel path into tra X/Y/Z is `#6810 'get buff image-lost frames.vi'` t6865 → `#5058` kernel t5089 on d639, and it
    is identical in S1 and S3. The ONLY pixel path into calibration is `#22692 IMAQdx Get Image` t22701 → Seq #22541
    local → the six `generate 1/2 I of r` nodes. The fixture holds tracking frames only (no calibration frames).
    (a) Two replay subVIs in `claudeDev\replay\`, each with the EXACT connector pane of the node it replaces, so the
        swap leaves every wire as it was: `replay_get_buff_image.vi` for #6810. It copies fixture frame
        `(Buffer to extract) mod 10044` (`tools/gpu/fixture.py:15`) into the `Image In` ref, returns `Buffer Number Out`
        = `Buffer to extract`, `Missed frames?` = False, and `current image number` = `Buffer to extract`. It passes
        `Session In`/error through untouched. `replay_get_image_cal.vi` for #22692 returns fixture frame
        k = its own call count since first call; frame k is the same in both VIs. Garbage calibration content is
        acceptable: equivalence needs IDENTICAL inputs, not physical ones.
    (b) The swap is made in dated COPIES of `D1_s1_copy.vi` and `D1_s3_loop15.vi` (never the beds). Simulator pipeline:
        stage plan file → dry → pre-run → run. Per-copy prediction: `computation_diff(original, copy)` = exactly the two
        swapped nodes, and nothing else.
    (c) Camera, pick display and motors stay live. Both runs use the same driver and the same located clicks. Bead xy
        read back from each run's cal file must be EQUAL between the two runs, or the comparison is void.
    (d) Numbers pass: join S1 and S3 tra rows on frame/buffer number; ≥ 1,000 common frames; X/Y/Z bit-identical.
        Also diff the two cal files' profile stacks.
    (e) The seq-local link t22656→t22659 is off the substitution path.
    (f) Build order: first MEASURE the connector panes of #6810's VI and of the #22692 instance, and whether an
        existing op can replace a subVI node's callee in place (`Replace` / relink) with its wires intact, citing
        `docs/NAMES.md` / `docs/toolkit-capabilities.md`. Then prior-art-review this entry, then build.

## Facts already measured by this material session (card 75-3), for the reviewer

- `#6810`'s callee in both beds is the ORIGINAL `zz_LabView VI\background VIs\get buff image-lost frames.vi`
  (`docs/wiki/subvi/D1_s1_copy.json:89810-89813`). Its connector pane (`docs/wiki/subvi/get buff image-lost frames.json`
  `connector_pane`): Session In(0,in) Session Out(4,out) Image In(5,in) Image Out(6,out) Buffer to extract(7,in)
  Missed frames?(8,out) current image number(10,out) error in(11,in) error out(15,out); 7 unassigned slots.
  **There is NO `Buffer Number Out` terminal on #6810** — PD13(a)'s wording names one.
- `#22692`'s callee is `NI_Vision_Acquisition_Software.lvlib:IMAQdx Get Image.vi` in `IMAQdx.llb`; node terminals
  (`docs/wiki/subvi/D1_s1_copy.json:57445-57563`): in Session In, Image In, Buffer Number In, Buffer Number Mode (Next),
  error in, 3 unnamed; out Session Out, Image Out, Buffer Number Out, error out. Whether it is a polymorphic instance
  is being measured.
- No op/verb in `tools/gscript.py` swaps a SubVI node's callee. `SubVI.Replace` 635E001 is recorded only as
  UNVERIFIED at `docs/vi-server-ids.json:117` and was never built; D1 plan ROT row (`docs/d1-loop12-17-split-plan.md:76,250`)
  planned to measure it on a scratch copy — not done.

Question for prior art: has this project already built, measured, refuted or decided anything that this entry
repeats or contradicts (replay harnesses, fixture frame sources, SubVI.Replace, connector-pane copying, calibration
frame handling, computation_diff expectations)?
