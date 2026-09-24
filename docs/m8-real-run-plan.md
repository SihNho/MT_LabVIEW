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

13. **Cycle-75 ruling — PD12's substitution point is WITHDRAWN; the replay swaps SUBVI NODES, not wires**
    (measured: `tools/bench/m8b_grab_consumers_75.json`, `tools/bench/m8b_frame_source_75.json`, results 75-1/75-2).
    `#15403 IMAQdx Grab` feeds only the bead-pick display (Flatten/Draw Pixmap) and never reaches a tra row. The ONLY
    pixel path into tra X/Y/Z is `#6810 'get buff image-lost frames.vi'` t6865 → `#5058` kernel t5089 on d639, and it
    is identical in S1 and S3. The ONLY pixel path into calibration is `#22692 IMAQdx Get Image` t22701 → Seq #22541
    local → the six `generate 1/2 I of r` nodes. The fixture holds tracking frames only (no calibration frames).
    (a) **Two replay subVIs in `claudeDev\replay\`**, each with the EXACT connector pane of the node it replaces, so the
        swap leaves every wire as it was: `replay_get_buff_image.vi` for #6810. It copies fixture frame
        `(Buffer to extract) mod 10044` (`tools/gpu/fixture.py:15`) into the `Image In` ref, returns `Buffer Number Out`
        = `Buffer to extract`, `Missed frames?` = False, and `current image number` = `Buffer to extract`. It passes
        `Session In`/error through untouched. `replay_get_image_cal.vi` for #22692 returns fixture frame
        k = its own call count since first call; frame k is the same in both VIs. Garbage calibration content is
        acceptable: equivalence needs IDENTICAL inputs, not physical ones.
    (b) The swap is made in dated COPIES of `D1_s1_copy.vi` and `D1_s3_loop15.vi` (never the beds; the copies are test
        instruments, not deliverables). It goes through the simulator pipeline: stage plan file → dry → pre-run → run.
        The per-copy prediction: `computation_diff(original, copy)` = exactly the two swapped nodes, and nothing else.
    (c) Camera, pick display and motors stay live under the grant. Both runs use the same driver and the same located
        clicks. Bead xy are read back from each run's cal file and must be EQUAL between the two runs, or the numbers
        comparison is void.
    (d) **Numbers pass**: join S1 and S3 tra rows on the frame/buffer number (frames skipped under load differ by run).
        Need ≥ 1,000 common frames, and X/Y/Z must be bit-identical (the same CPU kernel on the same pixels). A
        nonzero Δ is a failed prediction owing a review, not something to tune a tolerance for. Also diff the two cal
        files' profile stacks. If they differ (e.g. piezo readback in the z axis), report the fact before judging Z.
    (e) The seq-local link t22656→t22659 is off the substitution path (the swap sits upstream at #22692), so 75-2's
        OPEN about it is moot for this stage.
    (f) Build order: first MEASURE the connector panes of #6810's VI and of the #22692 instance (terminal names, types,
        connector pattern), and whether an existing op can replace a subVI node's callee in place (`Replace` /
        relink) with its wires intact, citing `docs/NAMES.md` / `docs/toolkit-capabilities.md`. Then prior-art-review
        this entry, then build.

14. **Cycle-75 ruling after the measurement and prior-art in PD13(f)** (`tools/bench/m8b_replay_prep_75.json`, result 75-3,
    `archive/peer/2026-09-25-priorart-m8b-pd13-replay-75.md`). This amends PD13 and wins over it where they differ.
    (a) **Pane corrected.** `#6810`'s callee has in: `Session In`, `Image In`, `Buffer to extract`, `error in`; and out:
        `Session Out`, `Image Out`, `Missed frames?`, `current image number`, `error out`. It has NO `Buffer Number Out`.
        The replay returns `current image number` = `Buffer to extract` and `Missed frames?` = False. The tra join key
        is the frame/buffer column the tra file actually carries; it is measured from a real tra file before (d) is run.
    (b) **Each replay VI is a byte COPY of its own callee, edited inside**, so its connector pane is identical by
        construction and no typedef is re-created. `replay_get_buff_image.vi` = a copy of
        `get buff image-lost frames.vi` (md5 `9aaaef21…`), with its inner `#529 IMAQdx Get Image` replaced by a fixture
        read of frame `Buffer to extract mod 10044` into `Image In`. `replay_get_image_cal.vi` = a copy of
        `IMAQdx.llb\IMAQdx Get Image.vi`, whose body returns fixture frame k (k = its own call count) and
        `Buffer Number Out` = k. Both copies live in `claudeDev\replay\`; vi.lib and `background VIs` are never written.
    (c) **Prediction re-cut (Pre-decided 132 desk-check).** `computation_diff` keys nodes without their callee
        (`tools/vigraph.py:205`), so it cannot see a swap. The per-copy predictions are:
        (i) wire-edge diff(original, copy) = ∅;
        (ii) callee census diff = exactly `{#6810 → replay_get_buff_image.vi, #22692 → replay_get_image_cal.vi}`;
        (iii) ExecState 1.
        Each of the three can fail.
    (d) **The swap route is a TOOL, built because the stage needs it and ROT will too (user 2026-09-24 tool grant).**
        It is `GObject.Replace` 632A402 (public), with `SubVI.Replace` 635E001 as the fallback. It is measured first on
        a dated scratch copy of `D1_s1_copy.vi`: swap `#6810` to a same-content copy of its callee under a new name,
        then check (c)(i)–(iii), with handles flat over 20 calls. It is never run on a bed or an original.

15. **Cycle-75 ruling on the swap verb (result 75-4, `tools/bench/swap_verb_75.json`, 21/0): ACCEPTED as the swap
    route.** The verb is `gscript.replace_object` (`tools/gscript.py:2896`) on `claudeDev\OpReplaceGObj_v0.vi`
    (md5 `a3723240…`, `GObject.Replace` 632A402, Path input only). It was measured on a scratch copy: callee read back
    = the probe, ExecState 1, and handles range 38 over 20 swaps. **Replace gives the node a NEW uid** (6810 → 23006).
    So every PD14(c) check is taken AFTER remapping new_uid → old uid, using the verb's returned uid, never a lookup.
    After the remap, the wire-edge diff was ∅ over 2,216 edges; without it, a raw diff shows −16/+16 rows and cdiff
    shows 9 rows. Both are the uid change, not a wiring change. From now on, "cdiff(original, copy) = 0 after the
    remap" is the predicted value for every swap, and a remapped nonzero row is a failed prediction. This also
    answers ROT's O6 (`docs/d1-loop12-17-split-plan.md:501-503`): the callee is invisible to cdiff, and the uid is
    not kept. The verb is verified only for a subVI → subVI swap with an identical connector pane; `#22692` (a vi.lib
    subVI → a byte copy of it) is that case.
    **Next build = the two replay VIs (PD14(b))**, then the swap in dated copies of S1 and S3, through the simulator
    pipeline (stage plan file → dry → pre-run → run). Each replay VI is its own saved artefact
    (`claudeDev\replay\replay_get_buff_image.vi`, `claudeDev\replay\replay_get_image_cal.vi`). Its prediction is
    ExecState 1, a connector pane identical to its source callee (terminal-list diff ∅), and a ≤120-line test that
    calls it with `Buffer to extract` = 5 and 10049 and gets fixture frame 5 both times (pixel md5 == frame 5 read
    independently in Python through `tools/gpu/fixture.py`'s own index → file mapping).

16. **Cycle-76 ruling on result 76-1 (BLOCKED, `tools/bench/replay_vis_76_measure.log`). This amends PD13(a)/14/15 and wins
    over them where they differ.** Three premises were measured false: the fixture is 10,044 files numbered 4..11825 with
    124 gaps (no `img00005`); inside `get buff image-lost frames.vi` `Missed frames?` = `Equal To 0?(Buffer to extract −
    Buffer Number Out)`, so it is TRUE whenever the camera returns the requested buffer; and a byte copy of
    `IMAQdx Get Image.vi` stays claimed by `NI_Vision_Acquisition_Software.lvlib` and loads with ExecState 0.
    (a) **Frame map = a contiguous replay folder.** Python builds `claudeDev\replay\frames\f00000.tif … f10043.tif`
        from the SORTED fixture list (hardlink if the same volume, else copy; manifest `frames_manifest.json` =
        index → source file → md5). Frame for a buffer or call number n = `f(n mod 10044)`. The test's "frame 5" means
        `f00005` = the 6th sorted fixture file, read independently in Python from the fixture list, not from the folder.
    (b) **Replace ONLY `#529` inside the copy of `get buff image-lost frames.vi`; everything else in it stays.** The
        Subtract and `Equal To 0?` are the original's logic (rule 1a); the replay stand-in returns
        `Buffer Number Out` = `Buffer Number In`, like a camera that delivered the requested buffer, so the unchanged
        logic yields `Missed frames?` = TRUE, the normal real-camera value. PD14(a)'s "`Missed frames?` = False" is
        WITHDRAWN; the test predicts TRUE.
    (c) **Stand-ins are VIs with `IMAQdx Get Image.vi`'s exact connector pane and NO library owner**, swapped in with
        `gscript.replace_object` (PD15): `replay_imaqdx_get_image_buf.vi` (frame `f(Buffer Number In mod 10044)`, Out =
        In) replaces `#529` in `claudeDev\replay\replay_get_buff_image.vi` (the get-buff copy); `replay_get_image_cal.vi`
        (frame `f(k mod 10044)`, k = its own call count from 0, `Buffer Number Out` = k) replaces `#22692`. Session and
        error pass straight through; `Image In` receives the frame (IMAQ ReadFile into the caller's image) and is
        returned as `Image Out`. How an unowned pane-identical VI is made is MEASURED first (candidates: Save-As-copy
        without the library by VI Server; library disconnect on the copy; a new VI whose pane is set by scripting) —
        the lvlib and vi.lib are never written. Pane identity is checked against the vi.lib original, terminal by
        terminal (name, type, direction, pattern position).
    (d) **Tool, under the 2026-09-24 grant:** the fleet has no verb that wires a front-panel control terminal to an
        indicator terminal (`gscript.py:2528`, `docs/toolkit-capabilities.md:25`). Build it now: the stand-ins need
        Session In→Session Out and error in→error out, and every later loop split meets the same class. Measured on a
        scratch VI before use (wire exists, ExecState 1, handles flat over 20 calls).
    (e) Predictions for the three saved VIs: ExecState 1 cold; pane diff ∅ vs the vi.lib `IMAQdx Get Image.vi` (stand-ins)
        and vs `get buff image-lost frames.vi` (the get-buff copy); get-buff copy called with `Buffer to extract` 5 and
        10049 → pixel md5 == `f00005`'s source file, `current image number` == `Buffer to extract`, `Missed frames?` ==
        TRUE; cal stand-in called three times → f00000, f00001, f00002, `Buffer Number Out` 0,1,2. The get-buff copy's
        callee census diff vs its source = exactly `#529 → replay_imaqdx_get_image_buf.vi`, wire-edge diff ∅ after the
        uid remap.

17. **Cycle-76 ruling on the PD16 review (`archive/peer/2026-09-25-m8b-pd16-replay-76.md`, verdict refuted on (a),
    result 76-3). ACCEPTED; this amends PD16 and wins over it.** Measured: `Buffer to extract` is seeded from the live
    `LastBufferNumber` (#250 → SR #5351, +1 per frame), and the cycle-74 runs started at 8217 / 8331 / 8227
    (`tools/bench/m8s3_run.json:22,111,200`); the kernel `#5058` carries x,y,z and SR #2972 from the previous frame. So
    keying the frame on the absolute buffer number gives the two VIs different pixel sequences.
    (a') **Frame = `f((n − n0) mod 10044)`, n0 latched at the stand-in's first call** (both stand-ins; for the cal one
        n is its call count, so n0 = 0). With `Buffer Number Out` = `Buffer Number In` the get-buff logic requests
        n0, n0+1, … with no skip, so iteration i gets `f(i)` in every run — a deterministic pixel sequence.
        `Buffer Number Out` stays = `Buffer Number In` (PD16(b) unchanged: `Missed frames?` TRUE).
    (a'') **Frames folder = HARDLINKS on G:** (same volume as the fixture, 0 bytes extra; claudeDev's C: would keep only
        ~16 GB after a 13 GB copy). Location: a new folder on G: outside this project folder and outside the fixture
        folder; the path is reported and is a constant in the stand-ins. Nothing is ever written through a link.
    (b') **S1 and S3 replay runs are separate LabVIEW launches** (the latch and the call counter live while the VI is in
        memory; PD3 already restarts LabVIEW between legs). The tra join key is the iteration index (row order after
        the first replayed frame), cross-checked against `current image number − n0` where the tra file carries it.
    (c') Pane identity is checked per connector SLOT by data TYPE and direction (names are informative only).
    (e') The pixel check is the md5 of the U8 pixel ARRAY (IMAQ image → array in the harness vs PIL/numpy array of the
        source file in Python), never the TIFF file md5. Tests: get-buff copy first call b=8217 then b=8218 → f00000,
        f00001; a fresh launch with b=5 → f00000 (latch). Cal stand-in: three calls → f00000, f00001, f00002, Out 0,1,2.

18. **Cycle-76 ruling on result 76-4 (FAIL on budget, 24 pass: `G:\m8_replay_frames\` 10,044 hardlinks,
    `gscript.connect_ctl_ind` on `claudeDev\OpConnectCtlInd_v0.vi`, the unowned pane base
    `claudeDev\replay\replay_imaqdx_pane_base.vi` md5 `65e999d9…`, whose `replace_object` onto `#529` kept all 9 wires).**
    (a) **Both stand-ins key the frame on their OWN call count k from 0: frame = `f(k mod 10044)`.** This replaces
        PD17(a')'s n0 latch for the buf stand-in. Call i gets `f(i)` whatever buffer number is requested, so the pixel
        sequence stays deterministic even if the requests are not consecutive. The two stand-ins differ only in
        `Buffer Number Out`: the buf one returns `Buffer Number In`, the cal one returns k. PD17(e')'s test becomes: after
        a fresh load, the get-buff copy called with b = 8217 then 8218 returns f00000 then f00001 (with b = 5 on a fresh
        load, f00000).
    (b) **Counter = an uninitialised shift register on a For loop with N = 1** (no DLL). Primitives that have no creator
        (Increment, Quotient & Remainder, Format Into String "f%05d.tif", Build Path) come from a GENERIC primitive
        creator if one can be built (tool grant; cycle 68 needed `Not Equal?`/`Select` too). The external search on
        New VI Object primitive styles is mandatory first. The fallback is `copy_by_index` from measured donors
        (S1 `#1978` Increment, `#2136` Q&R, `docs/frame-loop-wire-graph.md:67-68`). Each replay VI is its own saved
        file, built from a copy of the pane base.

19. **Cycle-76 ruling on result 76-5 (FAIL 61/6).** The three replay VIs exist, ExecState 1 cold, pane per slot ==
    source, and the get-buff copy's callee diff = exactly `#529`, with a wire-edge diff of 0. The pixels come back EMPTY and
    the cal `Buffer Number Out` reads 0,0,0 because two of the three constants were panel controls with saved
    defaults, and those defaults did not persist (`Control Names` N = [], `y` = 0.0;
    `tools/bench/replay_vis_76d_defaults.log`). `gscript.make_default` reads no op error (`gscript.py:2985-2995`).
    (a) **Scalar constants are DIAGRAM constants** (N = 1 and the modulus 10044), made with the fleet's constant verb.
        The 10,044-path array may stay a control default ONLY if its value is read back COLD after the save.
    (b) **Tool fix first:** `make_default` checks the op's error out and reads each value back after the save. It
        FAILS loudly on a mismatch. A self-test on a scratch VI covers scalar, numeric array and path array.
    (c) **Chain the error through IMAQ ReadFile** (error in → ReadFile → error out). The stand-ins are test
        instruments, not the original's computation, and a silent read failure would void the equivalence test.
        This amends PD16(c)'s "error passes straight through".
    (d) Tests unchanged (PD18(a)). The rebuilt files replace the 76-5 files of the same names. 76-5's md5s are
        superseded, not deliverables.

20. **Cycle-76 close, ruling on result 76-6 (FAIL 13/1; review `archive/peer/2026-09-25-76-6-makedefault-cold.md`).**
    `make_default` is now error-checked (`gscript.py:2990-3020`), but a panel default can still be lost at save/load
    without any error: an I32[4] came back empty cold. Only the 10,044-element String[] kept its default, and it
    kept it every time. The cause (not applied vs lost at save) is OPEN and **off the critical path**.
    (a) **Next build = a constant-on-ANY-terminal verb** (tool grant: loop N and conditional terminals recur in every
        loop split, as with cycle 68's loop `i` hole). The external search on `Terminal`-level Create Constant or
        equivalent comes first. The verb is measured on a scratch VI (For N, While conditional, a body-node terminal)
        with a COLD read-back of each constant's value. Then the stand-ins are rebuilt per PD19 with N = 1 and 10044 as
        diagram constants. The path list stays a String[] default, read back cold. Then the PD18(a) tests run.
    (b) The default-loss discriminating test (sizes 1/4/100/10044, panel open vs closed, reload) is a parallel-safe
        diagnostic. It is not a precondition for (a).
    (c) **After retrospective-cycle76 (accepted):**
        - The new verb is needed ONLY for loop-owned terminals (For N, While conditional). The modulus 10044 goes on
          Q&R's `y` with the existing `OpCreateConstOnTerm_v0`, which already handles body-node terminals
          (`build_opcreateconstonterm_v0.log:46-54`).
        - The replay VIs are rebuilt by a `tools/recipes/stage_replay_*.py` stage recipe (dry run, pre-run and
          prior-art gates), never as a `diag_*.py`.
        - Every value a stand-in depends on (constants, the path list default, the counter type) is read back COLD
          before the functional tests run.
        - The IMAQdx mode enum #581 value is read and recorded.
        - Review dispositions are made by judgement; a material session returns them as OPEN.

21. **Cycle-77 rulings (steer_77 FOLLOWED; outcome review `archive/peer/2026-09-25-outcome-review-20260925.md`).**
    (a) **M8(a) clean baseline DONE (card 77-6, 6 legs 8/0, INDEX rows 45–46, `tools/bench/m8_s1s3_77.json`).**
        `D1_s1_copy.vi` has no TIFF writer. Lost frames S1 vs S3 at 3/1/6 picks: 7/4, 2/2, 11/8 of ~3,075 (35 s);
        rows ≈ frames. The 567 lost of the cycle-74 base leg were the fixture TIFF writer's. At this load the split
        shows NO measurable lost-frame gain; one run per cell, spread unmeasured. M3 stays justified by CLAUDE.md
        1c (no serial on the frame path — structural), not by these numbers. Realistic load = user question
        `D-2026-09-25-01` (not blocking).
    (b) **Constant verb DONE:** `gscript.create_const_loop_term` (`OpCreateConstTop_v0` / `OpCreateConstLoopEnd_v0`),
        cold: For N = 1, ExecState 1, handles flat over 20 calls (`const_loopterm_77c.log`, clean rerun
        `const_loopterm_77d.log` 16/0). While conditional: class + wire only; its Boolean value reader stays OPEN.
    (c) **Stand-in stage READY, NOT RUN:** `tools/recipes/stage_replay_standins.py` (md5 `610a96a2…`, dry PASS,
        pre-run 7/0, prior-art released by FIXED lines) + `tools/bench/diag_replay_test77.py` (`330db8df…`). Q&R `y`
        = 10044 via the top-level constant op (Q&R is top level): ACCEPTED, cold-gated. `#581` Mode stays unread,
        not blocking; the gate instead checks each stand-in's `BN Out` wire SOURCE (buf: `BN In`; cal: count k).
    (d) **Order from now:** the deliverable run first (stand-in stage → PD18(a) → the S1/S3 swap and replay runs with
        bit-identical X/Y/Z, PD13(d)/15/17(b')), THEN tooling. Launch the stage as ONE non-compound PowerShell command
        (`$env:RETRY_CARD=…; $env:MATERIAL='1'; py tools\bgrun.py --material …`); compound Bash launches are refused
        by the permission layer AFTER the retry-cap recorder has counted them.

22. **Cycle-78 rulings on results 78-1 (BLOCKED) and 78-2 (FAIL 4/1).**
    (a) **Retry-cap recorder REPAIRED** (`tools/bgrun.py` records at child start; `selftest_retry_cap.log` 8/0;
        `docs/violation-decisions.md:1248`). Accepted launch form = Bash, non-compound, backgrounded:
        `py tools/bgrun.py --material --max-min N --log <log> -- py -u <script>`; a judgement retry = `--retry-card <card>`.
    (b) **Stand-ins ACCEPTED as built** (`stage_replay_78.log` 35/0; md5 buf `a89dafc1…`, cal `afce0d04…`,
        get-buff `842ecad9…`): ES 1 cold, constants cold, callee diff `#529` only, wire diff 0; image number == b,
        `Missed frames?` TRUE, cal `BN Out` 0,1,2 (`replay_test78b.log`).
    (c) **PD18(a) pixel identity: ACCEPTED on INTERIM evidence** — the harness's COM `GetControlValue` on the 2-D U8
        indicator returns only column 0, and that column's md5 == column 0 of source f0000k for k = 0,1,2 on BOTH
        stand-in paths (`diag_replay_slice78.log:3-8`). This rules out empty/stale/wrong-index frames, which is what
        the equivalence test needs. The FULL-frame check is still owed, NOT blocking: route = the harness writes the
        returned image with `IMAQ Write File 2` (PNG, lossless) to a scratch file and Python md5s the DECODED U8 array
        against the source's. Do it inside the next replay dispatch if it costs no extra LabVIEW launch, else later.
    (d) **Next = PD13(d)/15/17(b'): the swap stage + two replay runs.** A `tools/recipes/stage_replay_swap.py` makes
        dated copies of `D1_s1_copy.vi` and `D1_s3_loop15.vi` in `claudeDev\replay\`, replaces `#6810` with
        `replay_get_buff_image.vi` and `#22692` with `replay_get_image_cal.vi` (`gscript.replace_object`, uid remap per
        PD15), and gates: ES 1 cold, callee diff == exactly those two nodes, wire-edge diff 0 after the remap, sources
        md5 unchanged. Then each copy runs in its OWN LabVIEW launch through `drive_m8.py` (same picks, same
        durations; camera live only for the bead-pick display, motors under the grant with the session checks). Join the
        tra rows on iteration index; PASS = X/Y/Z bit-identical over the common prefix, with the row counts and the
        first differing row (if any) reported. An INDEX row in `archive/benchmarks/INDEX.md`.

23. **Cycle-78 ruling on result 78-3 (PASS 6/0). M8(b) is DONE for `D1_s3_loop15.vi`, at the FUNCTIONAL level.**
    (a) Swapped copies `claudeDev\replay\D1_s1_replay_20260925_075422.vi` (md5 `126f8497…`) and
        `D1_s3_replay_20260925_075422.vi` (`5e48e197…`), ES 1 warm + cold, callee diff == {#6810, #22692}, wire diff 0.
        Each ran in its own LabVIEW launch via `drive_m8.py --leg replay_s1|replay_s3` (8/0 each, lost 0/0). **All
        10,310 common tra rows have X/Y/Z bit-identical (max |d| 0.0)**; row counts 10,310 vs 10,585 (run length).
        trans/rot differ in 276 rows = motor READBACK, not computation. Table `tools/bench/m8b_replay_78.json`,
        INDEX row 47. Negative control: the same comparer on the live pair (row 46) finds every row different.
    (b) PD13(c) STANDS and is SATISFIED: the cal files differ only in the save-time string (3 bytes), so the bead xy
        are equal.
    (c) **The PD22(c) full-frame pixel check is DROPPED as a requirement.** Column 0 matched per frame on both
        stand-in paths, and the tracking output, which reads the whole frame, is identical and non-vacuous.
        Optional, never blocking.
    (d) **Scope:** this certifies the loop-1.5 split (S1 → S3). The current bed `D1_s4_loop17.vi` writes no tra rows
        by design (t5 w4517 and t7 w3268 are open until QRT, PD4/PD8), so its rule-1a numbers come from the SAME
        replay harness once M3 closes those rows. The swap stage is reusable: rerun `stage_replay_swap.py` on the new
        bed. **Goal map: M8 stays `active` — its done-when names the S4 bed, whose (b) needs M3's rows; evidence added
        to `docs/goalmap.json`. The next deliverable work is M3 (stage K), which is also what completes M8(b) on the bed.**

## Stop conditions

Any refusal from the motor gate, an Error List MISMATCH on the bed, a run that does not reach the experiment loop,
or LabVIEW not closing ⇒ stop, RESULT FAIL, judgement decides. Failure budget 2 for the material session.
