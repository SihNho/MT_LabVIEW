# P6-4 run plan - real-bead ABBA at 90 / 150 Hz (written 2026-10-14 by task p64prep; NOTHING here has been run)

Status: **PLAN ONLY.** No LabVIEW, no driver, no motor, no camera was used to write it. The real bead run waits for the
user at the rig (`user_notes.md:4`). Six `HOLD:` questions (section 10) must be answered before the step each one names;
the `ASSUME:` items are the method choices this plan takes unless the user says otherwise.
Revised 2026-10-14 by p64prep retry 1 (review FAIL 10:14, `lean_review_p64prep_20261014_095745-c1.md:11-17`): smoke
criterion without v5 L8 (section 5 item 4, section 9 item 2); C compared with a LOGGED start value, never fitted from a
saved row (section 6; observer route (b)); live claim limited to number consistency, the image-number pairing rests on
the replay (sections 6, 9); earlier A numbers labelled as `Total Lost Frames` indicator values (section 8); P-1 / P-3
wait for the user (section 11).

A = main checkout `../V6_ParallelLoop/`, B = this worktree `V6_lean/`. `CD` = `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`.

## 0. What P6-4 is, and what it is not
- P6-4 = "real ABBA at 90 / 150 Hz on the camera (PD238(f)); needs beads on the rig, so the user is asked before it is
  planned" (A `docs/d1/ring-p6.md:54`; A `docs/d1/ring-p6b.md:69`). Rule-1a acceptance = recorded-frame replay (done:
  P6-2 / P6-3 / p6fix / latest / p6close, B `lean_report_p6close.md:246-258`) **+** the real ABBA (A
  `docs/d1-loop12-17-split-plan.md:2259`).
- On a live run, X/Y/Z bit-identity between A and B cannot be the test: the two VIs see different frames (A
  `docs/m8-real-run-plan.md:323`, the live pair differs on every row). The live part is judged by frames lost under a
  criterion fixed before the run (A split-plan:1849, PD217(f)) plus acceptance #1 in two halves: number consistency
  read live against a logged start value (section 6), and the image-number pairing / per-slot values from the replay
  (`lean_report_p6close.md:251-254`; section 9 items 3-4).
- The product VI is **never edited** (user note `user_notes.md:2`). Every VI a leg runs is a byte copy; the two test
  variants (observer, 150 Hz) are small-subVI callee swaps on copies, built in their own tasks BEFORE the rig day.

## 1. VIs (all under `CD\bench\lean\`; md5 checked before and after every leg)
| id | file (to be made by byte copy / build) | from | md5 of the source | used in |
|---|---|---|---|---|
| A90 | `D1_s1_p64A_<ts>.vi` (byte copy) | `CD\D1_s1_copy.vi` (the original's copy, A arm of every earlier ABBA) | 3e3d23cefd3a334001aa9d6156bf1aee (B `tools/bench/diag_c104_abba.py:32`) | 90 Hz A legs |
| B90 | `D1_ring_p64B_<ts>.vi` (byte copy) | the final VI `D1_ring_p6latest_20261014_010104.vi` | 15c664e3eed1c580e05b13e42c86566f (`lean_report_p6close.md:21`) | 90 Hz smoke + B legs |
| BOBS90 | `D1_ring_p64Bobs_<ts>.vi` (BUILD task P-1, two callee swaps; waits for HOLD-5) | a byte copy of 15c664e3 with (1) call #31710 `RingPickSlot_latest_20261014_010104.vi` -> `RingPickSlot_latestobs_20261014_025316.vi` 9504e0cf (the pick observer already built and used in `latest`, `lean_report_latest.md:13-17,125-127`) and (2) call #6810 `get buff image-lost frames.vi` -> the new start-value wrapper `GetBuffFirst_<ts>.vi` (section 6.2; same callee route as the replay swap of #6810, `lean_report_p6close.md:29-30`) | 15c664e3 + 9504e0cf + PickLog e5810aec + the wrapper (pinned at build) | the OBS leg: acceptance #1's live half (section 6) |
| A150 / B150 / BOBS150 | the three above + ONE more callee swap: the camera `IMAQdx Configure Grab.vi` call (#13962 in S1, init frame 87, A `docs/main-vi-subvi-identity.md:106`; located by class + callee in the P6 lineage) -> a small wrapper `ConfigureGrab_rate150_<ts>.vi` (BUILD task P-2, only if HOLD-2 says yes) | | | 150 Hz cell |

- A legs run `A90` from `bench\lean\` (not `CD\D1_s1_copy.vi` itself): lean rule 2 saves only under `bench\lean\`, and
  `drive_m8.py:72-73` puts the per-leg `_run_<ts>.vi` copy BESIDE the source.
- The wrapper (P-2) has the connector pane of `IMAQdx Configure Grab` (`Session In`, `Number of Buffers`, `error in` ->
  `Session Out`, `error out`; A `docs/camera-acquisition-facts.md:655`): it writes `AcquisitionFrameRate` = 150 on the
  session, reads it back, then calls the real Configure Grab with the same inputs. Nothing else changes: the rate must be
  set inside the VI's own session because every camera open reloads the .icd at 90.0009 Hz
  (A `docs/camera-acquisition-facts.md:642-647`), which is the route the user chose (D-2026-09-25-05, A
  `tools/bench/decisions_pending.json:108-122`). 150 Hz fits the camera (ceiling 247.95 Hz, `camera-acquisition-facts.md:29-36`;
  measured 149.7-149.9 under a 5555 us exposure, :758). Exposure is left as the .icd sets it (1909 us, `ExposureAuto`
  Continuous, :26); the leg's own rate check (gate T5, section 5) tells whether 150 was reached.

## 2. Legs
Protocol of the earlier real ABBA, kept: order **A B B A**, 15 picks, 120 s experiment loop per leg, panel normal, both VIs
run as they are (A split-plan:1849; B `diag_c104_abba.py:1-3,28,35`).

**Day split (two tasks, each fits one session; ~12 min wall-clock per leg, `diag_c104_abba.py:34`, p6close legs 723-725 s):**

| task | leg | VI | rate | picks | run_s | purpose |
|---|---|---|---|---|---|---|
| p64run90 | S0 | B90 | 90 | 15 | 60 | smoke: the ring VI's LIVE camera path has never run (`lean_report_p6close.md:207`; every P6 run so far swapped #6810/#22692 to replay stand-ins, :29-30) |
| p64run90 | 1 A, 2 B, 3 B, 4 A | A90 / B90 | 90 | 15 | 120 | the ABBA (lost frames) |
| p64run90 | 5 OBS | BOBS90 | 90 | 15 | 120 | acceptance #1's live half: number consistency against the logged start value (section 6); not counted in the ABBA |
| p64run150 | 1 A, 2 B, 3 B, 4 A | A150 / B150 | 150 | 15 | 120 | the ABBA at 150 Hz (only if HOLD-2 = yes) |
| p64run150 | 5 OBS | BOBS150 | 150 | 15 | 120 | the same live half at 150 Hz |

- Totals: 90 Hz 6 legs ~72 min; 150 Hz 5 legs ~60 min; offline analysis ~10 min per task.
- Picks: per HOLD-4. Default in this plan (ASSUME, only if the user answers "machine picks"): the 15 fixed fractions of
  `drive_m8.py:33-38` (FRACS6 + grid), identical in every leg.

## 3. Driver and its changes (DESCRIBED, not made)
Base: `tools/bench/diag_c104_abba.py` (sequencer) -> `diag_c104_leg.py` (one leg) -> `drive_m8.py --leg replay_s1 --src <vi>`
(byte copy + run) -> `drive_original_copy_v5.py` (G0 motor session start, VISA precheck, picks, Done, bandpass, save
dialog, L11, stop, G92/G93). A new copy, not an edit of the shared files:
1. **`tools/bench/lean_bench/p64_abba.py`** = `diag_c104_abba.py` with parameters instead of constants: `--a-src/--a-md5`,
   `--b-src/--b-md5` (today B and its pin are hard-wired to `D1_s1_disp_*`, :31-32), `--hz 90|150` and `--run-s` (today
   `HZ, RUN_S = 90, 120`, :28), `--order ABBA|B` (smoke), `--out-root tools/bench/lean_bench/out_p64` (M8_OUT_DIR /
   M8_RUN_ROOT as `p6fix_legs.py` sets them), `--pick-mode fixed|beadmap`.
   - B-only gates F1/F2 (#8323 plot non-empty, `Display period (ms)` a number, :174-177) become RECORDED facts: in P6
     t8323 is an unfed display row by design (A `ring-p6.md:119-121`, PD405(d)).
   - The `archive/benchmarks/INDEX.md` append (:207-221) is removed (lean writes only under `tools/bench/lean_bench/`);
     the json goes to `out_p64/`.
   - Before each leg: stop if `tools/bench/lean_bench/STOP` exists, if `tools/bench/motor_session.json` is missing, or if
     the rig-state key is not 조립.
2. **`diag_c104_leg.py` copy (`p64_leg.py`)**: `FRAME_MS = 1000/hz` (:189 has 90 fixed, proxy only); gate D1 (plot read
   without ERR, :228) recorded only, because the label may not exist on the P6 panel.
3. **Lost-frame metric computed offline (`p64_sum.py`), the same formula for both arms (ASSUME-2):** lost = (last col0 -
   first col0 + 1) - rows of the leg's tra file. The VI indicator `Total Lost Frames` is recorded beside it but is NOT
   the metric: in P6 it counts only camera-loop gaps - p6close W100 read `"0"` (`out_p6close/legs/W100_a1/m8_replay_s1.json:102`)
   while 1068 frames had no row (`lean_report_p6close.md:112`).
4. **Bead-map picks (only if HOLD-4 = aimed by machine):** before leg 1, LabVIEW closed, one C-API snapshot of the camera
   (`imaqdx_limits` as in `diag_c104_abba.py:46-60`; camera use is allowed in 조립) -> 15 bead centres found in the image ->
   fractions of 1280 x 1024 -> `out_p64/beadmap_<hz>.json` + PNG; every leg of that cell clicks the SAME 15 fractions of its own
   located display rect (v5 L3, `drive_original_copy_v5.py:353-376`, via `v5.PICK_FRACS`). The user checks the PNG once.
5. **Observer leg:** after the leg the PickLog file is moved to `out_p64/picklog_<hz>.txt` (as `latest3_offline.py
   move-cut` did, `lean_report_latest.md:64-65`) and the wrapper's one-line file to `out_p64/getbuff_first_<hz>.txt`;
   before the leg the driver checks that neither file exists (a stale line would be read as this leg's start value).
   `p64_own.py` runs the section-6 check. Values are read with the stated U32 decode (`lean_report_latest.md:47-49`).
6. Unchanged and kept: v5 G0 per-leg `motor_gate --session start` (approved, `user_notes.md:3`); the VISA precheck of
   `Rotor` / `ASRL5::INSTR` before every leg, a refused leg ends the ABBA (A split-plan:1864); a failing A leg before pick 1
   ends the loop (`diag_c104_abba.py:181-186`, LG.leg_loop); v5's G92 forced exit after its 240 s wait (normal ending,
   `lean_report_p6close.md:147-153`); the queue's cycle hooks (session start before the task, LabVIEW close + session end after).
7. Each new script gets a `--dry` run (stubs, no LabVIEW, no port) in its own build task before the rig day.

## 4. Every motor move per leg (read from the files; nothing new is commanded)
| when | who | what moves | source |
|---|---|---|---|
| before LabVIEW | v5 G0 `motor_gate --session start` | limits re-written (PI TMN 0 / TMX 39; ASI SL/SU X -3.8475..0.1525, Y -4.7744..-0.7744 mm); PI reference move to the negative switch (0 mm = ceiling, the safe direction) + verify | `drive_original_copy_v5.py:549-561`; `motor_limits.json:3-12`; A `STATUS.md:56,66`; `lean_report_p6close.md:171-187` |
| VI start | the VI's device init | PI magnet to 30 mm (inside 0..39); ASI initialised; rotor port opened by `Configure.vi` | `lean_report_p6close.md:186-189` (POS 30 before the G93 reference); A split-plan:1850 |
| after Done Picking | the VI's z-stack calibration (~2 min) | focus steps 60 x 0.1 um (panel `# images in stack`, `z step (um)`); the device carrying it was not re-read here | `drive_original_copy_v5.py:71-74`; panel record `out_p6close/legs/P62_a1/m8_v5_replay_s1.json:295-298` |
| experiment loop | the VI's autofocus #10407 (`Auto-Focus` = True on the panel) | the ASI, inside the gate's limits | A split-plan:1890; panel record :278 |
| experiment loop | panel magnet / rotor controls | **nothing**: `Send to Trans`, `Start Cycles`, `Send to Rot`, `HOME`, `1 L-Turn`, `1 R-Turn` read False and `Trans Step`/`Rot Step` 0 before and after the leg, and v5 writes no panel parameter (section 7, item d) | `m8_v5_replay_s1.json:264-307,539-582`; `drive_original_copy_v5.py:278-285,596-600` |
| after LabVIEW exits | v5 G93 `motor_gate` readback | PI reference move 30 -> 0 mm (`travelled=30.000`), TMX? 39 | `lean_report_p6close.md:186-189` |
- With beads on the rig this is: magnet 0 -> 30 mm -> 0 once per leg (11 times over the two tasks), autofocus steps, and one
  z-stack per leg. All rotor motion is refused by the gate (A `STATUS.md:58`). Part of HOLD-3.

## 5. Stop conditions (any one ends the task; the session writes its report and the queue closes LabVIEW)
1. The user says 멈춰 or announces 실험중, or `tools/bench/lean_bench/STOP` exists (checked before every leg).
2. `tools/bench/motor_session.json` missing; v5 G0 exit != 0 (leg refused, `drive_original_copy_v5.py:558-561`); G93 TMX? != 39.
3. VISA precheck refused (any leg) -> the ABBA ends (A split-plan:1864).
4. The smoke leg S0 fails any of the following -> no ABBA (the live camera path of the ring VI is not working):
   - the leg gates: `drive_m8.py` M1-M8 with M2 = L7 + L9 + L11, the form `drive_m8.py:103` already uses for `--picks N`
     (`drive_m8.py:88-90`), and the leg script's own gates (`diag_c104_leg.py:222-228`, with F1/F2/D1 recorded only, section 3);
   - v5 L1-L7 and L9-L13 (`drive_original_copy_v5.py:60-88`);
   - panels closed (FACTS `bandpass_run1.answered`, `drive_original_copy_v5.py:467`) == picks registered (the tra file's
     `(cols - 3) / 3`, `picks_registered_tra`, `diag_c104_leg.py:216`) == 15;
   - tra file written with 3 + 3 x 15 columns and column 0 strictly increasing; LabVIEW gone after.
   **v5 L8 is NOT a criterion:** it is the 3-panel contract (`l8 = save dialog present and answered == 3`,
   `drive_original_copy_v5.py:466`; contract text :76-77), so it is false on every normal 15-pick leg - the p6close W100
   leg records `"ok": false`, "15 closed (contract 3) ... terminal=save dialog appeared after 15 panel(s)"
   (`out_p6close/legs/W100_a1/m8_v5_replay_s1.json:128-131`) with `bandpass_run1.answered` = 15 (:419-420), and that leg
   passed every chain gate (`lean_report_p6close.md:116`). The panel count it was meant to check is the "== 15" line above.
5. An A leg fails before pick 1 (LG.leg_loop), or a leg registers != 15 picks after its one rerun.
6. Rate gate T5: measured fps (frame-counter delta / run_s) outside +-15 % of the cell's rate (`diag_c104_abba.py:168`) ->
   that rate cell stops; at 150 Hz this also tells that the wrapper did not take.
7. Any pinned md5 changes (the final VI 15c664e3, S1 3e3d23ce, the leg copies) or LabVIEW not gone after a leg.
8. Memory: MEMSTOP 695 MB private (CLAUDE.md rule 4).
9. The user at the rig sees beads lost, a magnet or stage problem, or anything unsafe -> 멈춰 (rule 1).

## 6. Acceptance #1 on a live run (item b) - design (revised: a LOGGED start value, observer route (b))
Acceptance #1: every saved row's buffer number (and each per-slot value written with it) is its own frame's (A
`ring-p6b.md:59-61`). In a replay this was read against S1's column 0 on the same recorded frames. Live, there is no S1.

### 6.1 What column 0 is (graph facts already written; nothing re-run)
- `BufDiff` = Subtract #5119 `x - y`. `x` = get-buff call #6810 `current image number`; `y` = loop tunnel #3363 <- IMAQdx
  Property #250 `LastBufferNumber`, outside loop 1.1, so read ONCE before the loop starts. **The same #250 value
  initialises `Buffer to extract` (left shift register #5351 -> #6810).** `Num` in the ring is the same #6810
  `current image number` (`lean_report_latest.md:20-27`). In the original the same wire exists (#250 t4 -> #6810 t7
  `Buffer to extract`, A `docs/frame-loop-wire-graph.md:447`); the shift register is seeded from the live
  `LastBufferNumber` and advances +1 per frame (A `docs/m8-real-run-plan.md:204-205`).
- So for every row, `Num - col0` = #5119's `y` = the `Buffer to extract` value #6810 receives on its FIRST call.
- **C is NOT fitted from a saved row.** "C = first picked Num - col0 of row 0" (the earlier step 2) would absorb any constant
  offset between a row and its pick, and the smallest Num of the first ring lap is not proven to be the start value (the
  ring is still filling during the first picks, `lean_report_latest.md:75-76`; and the camera may return a buffer other
  than the one requested, which is what `Missed frames?` compares, A `docs/m8-real-run-plan.md:171`). That step is removed.

### 6.2 The reference: the start value, logged once by a callee-swap wrapper on #6810 (choice (b))
- **Why not (a), the camera's own frame counter:** it is not exposed in the files. The attribute dump of this camera and
  driver has `ChunkDataDecodingEnabled = False` (B `tools/bench/imaqdx_attributes.txt:14`), `ReceiveTimestampMode = 'None'`
  (:179), and its camera features (:16-171) fall in DeviceControl, ImageFormatControl, AcquisitionControl,
  DigitalIOControl, AnalogControl, PulseGenerators, LUTControl, TransportLayerControl, UserSetControl and
  JAICustomControl - no chunk, FrameID / BlockID, event or timestamp feature. A `docs/camera-acquisition-facts.md` has no
  frame-ID entry (its only `LastBufferNumber` line is the shift register that drives `Total Lost Frames`, :614-615). The
  IMAQdx `LastBufferNumber` (`StatusInformation`, dump :196) is the driver's buffer number - the value #250 reads, which
  is what (b) logs; whether the driver takes it from the USB3 Vision block ID is not in the files.
- **Why the wrapper sits on #6810:** #5119 is a primitive and #250 a property node - neither has a callee to swap; #6810 is
  the only subVI whose inputs carry the start value (6.1). Its callee was already swapped in every replay copy
  (`get buff image-lost frames.vi` -> `replay_get_buff_image_paced60.vi`, `lean_report_p6close.md:29-30`), so the route
  is proven on this VI lineage. User note `user_notes.md:2`: nothing inside the big P6 VI is edited.
- **The wrapper `GetBuffFirst_<ts>.vi`** (new small VI in `CD\bench\lean\`, built in P-1 - described only):
  - connector pane = `get buff image-lost frames.vi`'s, slot by slot (type, direction): IN `Session In`[0], `Image In`[5],
    `Buffer to extract`[7], `error in`[11]; OUT `Session Out`[4], `Image Out`[6], `Missed frames?`[8],
    `current image number`[10], `error out`[15]; same execution settings, reentrant preallocated clone, Time Critical
    (A `docs/NAMES.md:84-87`);
  - body: ONE call of the unchanged `get buff image-lost frames.vi` - the file the product already calls (A
    `docs/main-vi-subvi-identity.md:160`, `background VIs`, md5 pinned in `lean_md5.py`; never opened for edit, Don't
    Save on any prompt naming it) - with every input passed through and every output returned unchanged; AFTER that call,
    and only when `First Call?` is True, ONE line is appended to a fixed file `CD\bench\lean\obs\getbuff_first.txt`:
    requested `Buffer to extract`, returned `current image number`, `Missed frames?`, ms tick. Nothing else on any later
    call; no serial / VISA (rule 1c, U3). The single file write at the first call is the only extra on the frame path.
  - used ONLY in BOBS (the OBS leg); the A legs and the B90 / B150 ABBA legs never contain it.
- **Cost:**
  - builds: no new build task - it joins P-1 (the BOBS build): one new small VI, its unit test, and the second swap in the
    BOBS copy. Reference size: the pick observer build (one new subVI + one swapped copy) ran 816 s
    (`latestobs_build_run2.log`, `BGRUN END rc=1 after 816s`); estimate 15-30 LabVIEW minutes for P-1, no camera, no motor.
  - unit test without the camera: a TEST copy of the wrapper whose inner call is swapped to
    `replay\replay_get_buff_image_paced60.vi` (returns `Buffer Number Out` = `Buffer Number In`, A
    `docs/m8-real-run-plan.md:180,226-229`), called 3 times after a fresh load with 8217, 8218, 8219 -> exactly ONE line
    `8217, 8217, True, <tick>`, outputs equal to the inner VI's on all 3 calls, pane diff empty, ExecState 1 cold. BOBS:
    callee diff == exactly {#31710, #6810}, wire edges equal after the uid remap, ExecState 1, md5 pinned.
  - extra load on the live leg: loop 1.1 (the camera loop, frame path) gets one more subVI call level per frame, plus one
    file open / append / close at its first call, after the first frame is already in hand (the camera keeps filling the
    driver's buffers, `Number of Buffers` of Configure Grab, A `docs/camera-acquisition-facts.md:655`; nothing gates the
    camera, U6). Loop 1.2 gets the pick observer's line per pick (as in `latest`).
  - saved: the one-line file and the pick log, moved per leg into `out_p64/` (section 3 item 5). The product VI saves
    nothing new.
- **If the P-1 build or its unit test fails:** fall back to (c) - the live claim shrinks to "number consistency only" (rows
  vs picks under one fitted C, lag at the pick inside the ring) and the acceptance says so; nothing else in the plan moves.

### 6.3 The check (`p64_own.py`, offline, on the OBS leg)
Let S = the logged requested `Buffer to extract` and R = the logged returned `current image number` (U32 decode,
`lean_report_latest.md:47-49`). Missing or more than one line in the wrapper file -> the check is NOT RUN (stated, never
replaced by a fitted C).
1. **Start value from the log, not from the rows:** S is taken from the wrapper's line. R - S is recorded (expected 0: the
   camera delivered the requested buffer, `Missed frames?` True, A `docs/m8-real-run-plan.md:171,180-181`).
2. **Every row against its own pick, with S:** for every row k, `col0[k] + S` == the picked Num of the pick that produced
   the row; rows and picked Nums one-to-one, in the same strictly increasing order; picks with no row are listed (a seqlock
   discard, or the last pick at the stop, `lean_report_latest.md:185-196`) and their count <= (log lines - rows). No
   constant is fitted: a constant offset d between a row and its pick shows as `col0 + S - picked = d != 0` on every row.
3. **No row older than the first frame:** `col0[0] >= R - S`.
4. **Each picked Num inside the ring at its pick:** `max(Num[0..19]) - 19 <= picked <= max(Num[0..19])` ("lag at the pick",
   0 on 1475/1475 in `latest`, `lean_report_p6close.md:123-126`).
5. A one-lap-old row (the p6fix defect: col0 = frame k-20, A `ring-p6b.md:54-58`) fails (2) on every row >= 20.
- Recorded, not judged: the end lag = frame counter at stop (v5 L12 detail `frame=`) - (S + last col0). It becomes
  computable here because S is logged (p6close could not compute it without the constant, `lean_report_p6close.md:127-130`).
- The join `latest` ran on the replay W100 observer leg used a FITTED constant ("picked - constant == col 0", constant 20896 =
  the first picked Num, `lean_report_latest.md:151,157-159`); step 2 is that join with the logged S instead.

### 6.4 What the live OBS leg shows, and what it does not
- **Shows (live camera, real beads):** for every saved row, column 0 + the start value actually subtracted (logged, not
  fitted) == the camera buffer number that loop 1.1 stored for the frame loop 1.2 picked, one-to-one and in order; every
  pick was inside the ring (lag at the pick); and the first frame loop 1.1 received relative to that start value. That is
  **number consistency, rows <-> picks <-> start value**.
- **Does not show:** that the IMAGE in slot i is frame Num(i) (the camera-loop write under the n1 == n2 seqlock, U9), that
  the per-slot TransPos / RotPos values are the slot's own (the magnet does not move during a leg, so they are constant
  live), or that the driver's buffer number is the camera's own frame count. These rest on the **replay proof** (p6close:
  own number 9089/9089 rows, X/Y/Z bit-identical vs S1 9089/9089, TransPos/RotPos 0 rows differ, `lean_report_p6close.md:251-254`).
  Accepting that split as P6-4's evidence is HOLD-6.
- **What the VI or driver must save extra:** BOBS only - the pick log and the wrapper's one line; the driver moves both per
  leg and keeps the tra file + the frame counter at stop (already saved). The product VI saves nothing new.
- **Why a separate OBS leg (ASSUME-1):** the pick log writes a file from loop 1.2 on every pick and the wrapper adds a call
  level to loop 1.1, which adds work to the measured loops; the ABBA's B legs run the product bytes unchanged, so their
  lost frames are the product's. (In the replay
  W100 leg the observer did not change any result, `lean_report_latest.md:163`, but that was not a live load.)

## 7. Answers found in the files (item d and the others)
- **d. Panel magnet controls during a leg: they move nothing.** v5 resets only `stop (end)`, `stop (end) 2`, `Done Picking`
  and writes "no panel PARAMETER" (`drive_original_copy_v5.py:278-285`); the panel record is read, "never set" (:596-600).
  In the p6close P62 leg (same lineage as 15c664e3, test swaps only) `Send to Trans`, `Start Cycles`, `Send to Rot`,
  `HOME`, `1 L-Turn`, `1 R-Turn` are False and `Trans Step (mm)` / `Rot Step (deg)` 0 both before and after the leg
  (`out_p6close/legs/P62_a1/m8_v5_replay_s1.json:264-307` and `:539-582`). The A arm's panel is recorded the same way
  in each leg (gate G4). Motion that DOES happen is in section 4.
- **The per-leg G0 session start: approved** (`user_notes.md:3`; `questions_for_user.md:9`).
- **The 150 Hz route in principle: decided by the user** - rate set inside the VI (copy only), later saved as metadata
  (D-2026-09-25-05, A `tools/bench/decisions_pending.json:108-122`; A `docs/decisions/camera_settings_in_vi_cal_out_of_scope.md:22-25`).
  The callee-swap form follows `user_notes.md:2`. Applying it to the A arm (a copy of the original) is HOLD-2.
- **Live run of 15c664e3: none exists** (`lean_report_p6close.md:207`) -> smoke leg S0 first.

## 8. Predictions (written before any run; per leg, 120 s, 15 picks)
### 8.1 What the earlier "lost" numbers were (re-read: A split-plan :874-877, :1912)
| source | numbers | what was measured | the new metric (column-0 gaps, ASSUME-2)? |
|---|---|---|---|
| A split-plan :874-877 (cycle 83 load measurement, 120 s, ~89 frames/s) | S1 copy, 15 picks: **3,331** and (repeat) **3,161**; `D1_s3_loop15.vi` 3,493 / 3,269; 8 picks 16 vs 12, 12 vs 14 | the **`Total Lost Frames` indicator** - named at :874 ("Total Lost Frames, 120 s ...") | **No.** No column-0 count is given at those lines |
| A split-plan :1912 (cycle 110 ABBA, the 217(f) criterion) | A15 **3,359** / **5,860**; B (display-loop VI) 16 / 12; frames 10,665-10,681 per leg; tra rows A 7,773 / 5,268, B 11,129 / 11,126 | the **`Total Lost Frames` indicator** as read by the leg tool: `lost` = `m8.total_lost_frames` (`diag_c104_leg.py:216`), parsed from v5 L11's `(lost=...)` (`drive_m8.py:113-114`), read "AFTER L11 has read `Total Lost Frames`" (`diag_c104_leg.py:2`) | **No.** Column-0 gaps were not counted |
| p6close W100 (replay, P6 lineage) | indicator `"0"` vs **1068** column-0 gaps | both (`out_p6close/legs/W100_a1/m8_replay_s1.json:102`; `lean_report_p6close.md:112`) | the only earlier column-0 count, and it shows that in P6 the indicator is NOT the metric |
- The earlier plan text "3,161 - 3,493" mixed two VIs: 3,493 and 3,269 are `D1_s3_loop15`, not the A arm. The A arm's
  indicator values are 3,331 / 3,161 (cycle 83) and 3,359 / 5,860 (cycle 110).
- **Inference, not a measurement:** in the cycle-110 legs rows + indicator = 7,773 + 3,359 = 11,132 and 5,268 + 5,860 =
  11,128 for A, 11,129 + 16 = 11,145 and 11,126 + 12 = 11,138 for B (:1912). The near-constant sum fits "the indicator
  counts exactly the frames that got no row" in those single-camera-loop VIs, so for the A arm the indicator and the
  column-0 gap count are expected to agree within ~0.2 %. That is why the A prediction below keeps the indicator's range;
  the A legs record both numbers, and a difference > 1 % between them is reported as a failed inference.

### 8.2 The predictions (column-0 gaps unless the row says otherwise)
| cell | A legs | B legs (product copy) | OBS leg | basis |
|---|---|---|---|---|
| 90 Hz frames per leg | ~10,800 (90.0009 Hz x 120 s) | same | same | A `camera-acquisition-facts.md:25` |
| 90 Hz lost, column-0 gaps | **no earlier measurement in this metric**; predicted 2,500 - 7,000 per leg | **no earlier live measurement in this metric**; predicted < the lower A leg in both legs, <= 10 % of frames (central guess <= 3 %) | not judged on lost | A: the indicator values 3,331 / 3,161 / 3,359 / 5,860 (8.1) + the rows-sum inference. B: the Force plot that cost >= 7.94 ms/frame is unfed in P6 (A `ring-p6.md:119-121`; split-plan:1849); the display-loop VI, same tracking with the plot moved out, lost 16 / 12 by its indicator (:1912; ~ column-0 gaps by the inference); replay legs of the P6 lineage: 0 gaps at the replay pace, 1068 under the 100 ms load (`lean_report_p6close.md:112`) |
| 90 Hz `Total Lost Frames` indicator | recorded; ~ equal to the A gap count (8.1) | recorded only; NOT comparable (P6 counts camera-loop gaps only) | recorded | 8.1 |
| 150 Hz frames per leg | ~18,000 | same | same | |
| 150 Hz lost, column-0 gaps | **no earlier measurement at 150 Hz in any metric** (no VI run has reached 150 Hz, A split-plan:878-883); estimate 55 - 75 % of frames from A's row rate at 90 Hz (7,773 / 5,268 rows per leg, :1912, i.e. ~40-65 rows/s against 150 frames/s) | < the lower A leg; 0 - 45 % (wide: P6's loop 1.2 cost per frame live is unmeasured) | - | 6.67 ms budget per frame, A `camera-acquisition-facts.md:36,51-56` |
| functional | 15/15 picks; L11 advances; stopped by VI Server; G92 forced exit after 240 s (as every earlier leg); TMX 39 after | same | same | `lean_report_p6close.md:147-153` |
| acceptance #1 (OBS, section 6.3) | - | - | wrapper file: exactly 1 line, R - S = 0; `col0 + S == picked` on 100 % of rows with NO fitted constant; lag at the pick 0 on >= 99 % of picks at 90 Hz, <= 19 always | `lean_report_latest.md:157-158,166-172` (replay, fitted constant) |
| rate check T5 | 90: within 15 %; 150: within 15 % only if the rate wrapper took | same | same | |
Real beads add autofocus work and real tracking in both arms equally; the A numbers above came from legs without beads
(A `STATUS.md:54` "No beads on the rig"), so A may lose more than before.

## 9. Acceptance (final words, to be confirmed by HOLD-1 before any run)
**P6-4 PASSES at a rate when, at that rate, all of these hold:**
1. **Frames:** both B legs lost fewer frames than the lower A leg by at least 25 % of the A legs' mean (PD217(f)'s GAIN
   form, A split-plan:1849), lost = column-0 gaps of the saved tra file, the same formula for both VIs.
2. **Functional, every B leg:** the leg gates (`drive_m8.py` M1-M8 with M2 = L7 + L9 + L11, `drive_m8.py:103`; the leg
   script's gates, `diag_c104_leg.py:222-228`), v5 L1-L7 and L9-L13 (L8, the 3-panel contract, excluded: section 5 item 4),
   panels closed (`bandpass_run1.answered`) == picks registered (`picks_registered_tra`) == 15, rows strictly increasing in
   column 0, 0 damaged rows, stopped by its own stop control, LabVIEW gone after, md5 unchanged.
3. **Live number consistency on the OBS leg (section 6.3, steps 1-4):** the wrapper logged exactly one start value S; for
   every saved row, column 0 + S equals the camera buffer number of the pick that produced the row, one-to-one and in order,
   with no fitted constant; no row is older than the first frame (`col0[0] >= R - S`); every picked number was inside the
   ring at its pick. This is what the live leg proves - **number consistency, rows <-> picks <-> the start value actually
   subtracted**. It does NOT prove live that the image in a slot is frame Num(i), nor the per-slot TransPos / RotPos
   values (section 6.4).
4. **Image-number pairing and per-slot values (acceptance #1's other half, U9): from the replay, not from this run.** Every
   saved row's buffer number is its own frame's and X/Y/Z are bit-identical on the same recorded frames (9089/9089 rows over
   the four p6close legs), and TransPos/RotPos differ on 0 rows (`lean_report_p6close.md:251-254`). P6-4 adds no live
   evidence for this half; it relies on the replay (HOLD-6). A pick with no row is listed and counted (step 2), never
   matched to another row.
5. **Safety:** every leg's G0 exit 0, G93 TMX 39, no gate refusal routed around.
**Acceptance #1 for P6-4 = item 3 (live) + item 4 (replay).** If the P-1 wrapper cannot be built, item 3 becomes
"number consistency under one fitted constant" (section 6.2 fallback (c)) and the report says so.
**P6-4 is DONE** when 90 Hz passes and 150 Hz either passes or is recorded as NOT RUN by the user's answer to HOLD-2.
At 150 Hz a NO-DIFFERENCE result is reported with its numbers, not re-run. Rule 1a stays met by the replay part
(p6close); nothing in P6-4 changes the per-bead maths (U1).

## 10. Questions for the user (in `questions_for_user.md`; HOLD-1 and ASSUME-1 revised 2026-10-14 by retry 1, HOLD-5/6 are the review's lines :17-18)
- **HOLD-1 (a, 합격 기준) (revised):** P6-4 합격 기준을 실행 전에 이렇게 정해도 될까요? 90 Hz 와 150 Hz 각각, 원본 복사본(A)과 새 VI(B)를 A-B-B-A 순서로 2분씩 돌려 저장 파일 0번 열(버퍼 번호)의 빈칸 수를 셉니다. 두 B 가 모두 A 중 적은 쪽보다 A 평균의 25 % 이상 적게 놓치고, B 가 15개 비드를 모두 잡고(닫은 패널 수 = 등록된 픽 수 = 15) 정상 종료하며, 별도 확인 레그에서 저장된 모든 줄의 0번 열 + 기록해 둔 시작 번호(맞춰 구한 값이 아님)가 그 줄을 만든 픽의 버퍼 번호와 순서대로 일치하면 합격입니다. 이미지와 번호의 짝, 칸별 TransPos/RotPos 는 실시간이 아니라 리플레이 결과(9089/9089 줄)로 인정합니다. (B 가 "덜 놓침" 대신 "더 놓치지 않음"이면 충분한지도 알려 주세요.)
- **HOLD-2 (c, 150 Hz):** 150 Hz 는 VI 가 카메라를 열 때마다 .icd 파일 값(90 Hz)으로 돌아갑니다. 결정하신 대로(VI 안에서 설정, 사본만) 카메라 설정 호출 하나를 "150 Hz 를 쓰고 읽어 확인한 뒤 원래 설정을 부르는" 작은 subVI 로 바꾼 사본을 만들려고 합니다. 이 방식을 원본 복사본(A)에도 똑같이 적용해 150 Hz ABBA 를 해도 될까요, 아니면 150 Hz 는 이번에 빼고 90 Hz 만 할까요?
- **HOLD-3 (e, 리그·비드):** 비드 준비(샘플, 개수: 15개가 한 화면에 보이는지), 장착, 초점 맞춤은 사용자께서 해 주셔야 합니다. 언제 가능하신가요? 그 동안 상태는 "조립(실험중 아님)"으로 두고, 레그마다 자석이 0 → 30 mm → 0 으로 한 번씩 움직이고(총 11번) 자동초점과 z-스택 보정이 돕니다. 비드가 있는 상태에서 이 움직임이 괜찮은지도 알려 주세요.
- **HOLD-4 (e, 픽 방법):** 비드 고르기를 (1) 지금처럼 화면의 정해진 15곳 기계 클릭, (2) 첫 레그 전 카메라 사진에서 비드 위치 15곳을 자동으로 찾아 모든 레그에서 같은 곳 클릭(사진은 사용자 확인), (3) 레그마다 사용자가 직접 클릭(11번) 중 어느 것으로 할까요? 추천은 (2) 입니다.
- **ASSUME-1 (b) (revised):** 실시간 실행에서 버퍼 번호 확인은 ABBA 와 별도인 확인 레그(레이트마다 1번)에서 합니다. 그 레그의 VI 사본은 호출 대상 두 개만 바꿉니다: (1) 이미 만든 픽 기록용 subVI(픽마다 번호를 파일에 남김), (2) 새로 만들 작은 감싸기 subVI - 카메라 루프의 프레임 가져오기 호출(#6810)을 원래 VI 그대로 부르고, 첫 호출 때 한 번만 시작 번호(뺄셈에 실제로 쓰이는 LastBufferNumber)와 받은 번호를 파일 한 줄로 남깁니다. 이 시작 번호로 저장된 줄들을 비교하므로 첫 줄에서 상수를 맞춰 구하지 않습니다. 카메라 자체 프레임 번호(FrameID 등)는 이 카메라 설정 파일에 나와 있지 않아 쓰지 않습니다. ABBA 의 B 레그는 제품 VI 를 그대로 복사해 돌립니다.
- **ASSUME-2 (a, 측정 방법):** 놓친 프레임은 두 VI 모두 저장 파일 0번 열(버퍼 번호)의 빈칸 수로 셉니다. P6 의 `Total Lost Frames` 표시는 카메라 루프에서 빠진 것만 세어 비교할 수 없기 때문입니다(W100: 표시 0, 실제 1068).
- **ASSUME-3 (진행 방식):** 레그는 2분, 15픽, A-B-B-A(이전 ABBA 와 같음). 90 Hz 날에 먼저 B 를 1분 시험 실행(새 VI 가 실제 카메라로 돈 적이 없음)하고, 150 Hz 는 다른 작업으로 나눕니다. 실행 전에 빌드 작업 두 개(기록용 사본, 150 Hz 사본)와 드라이버 사본(p64_abba.py, 모의 실행)을 먼저 합니다.
- **HOLD-5 (review 10:14, `questions_for_user.md:17`, unchanged):** 계획 보완 뒤 P-1(관찰용 VI 사본 callee swap 빌드, LabVIEW 사용·모터 없음)과 P-3(드라이버 사본 작성 + 모의 실행)을 준비 작업으로 허용합니까? 이 두 작업만 답까지 보류합니다. (This retry adds the #6810 start-value wrapper to P-1; still LabVIEW only, no camera, no motor.)
- **HOLD-6 (review 10:14, `questions_for_user.md:18`, unchanged):** 실시간 검사가 번호 일관성만 확인하고 이미지·번호 짝은 리플레이 근거에 의존하는 증거 범위를 P6-4 받아들임으로 인정합니까? 해당 받아들임에 기대는 실행만 답까지 보류합니다. (The plan now states exactly this split: section 6.4, section 9 items 3-4.)

## 11. Order of work after the answers
1. P-1 (LabVIEW, no rig change) - **waiting for the user's answer (`questions_for_user.md:17`, HOLD-5).** BOBS90 = a byte
   copy of 15c664e3 with two callee swaps: #31710 -> the pick observer (the `latest` route) and #6810 -> the new
   start-value wrapper `GetBuffFirst_<ts>.vi` (section 6.2: a callee-swap build, described only; unit test on the replay
   inner callee, no camera); ExecState 1; md5 pinned. P-2 (if HOLD-2 = yes): the rate wrapper + A150 / B150 / BOBS150
   swaps, each a callee swap; a 30 s camera-only check that the wrapper's readback says 150 (no beads needed).
2. P-3 (offline) - **waiting for the user's answer (`questions_for_user.md:17`, HOLD-5).** `p64_abba.py`, `p64_leg.py`,
   `p64_sum.py`, `p64_own.py` (+ bead-map picker if HOLD-4 = 2), each with `--dry`; `p64_own.py` implements section 6.3
   with the logged S.
3. Rig day, user present at the start: beads, focus, 조립 confirmed -> task p64run90 -> (answer at the end) -> p64run150.
   The ABBA's acceptance #1 claim waits for HOLD-6 (and HOLD-1).
