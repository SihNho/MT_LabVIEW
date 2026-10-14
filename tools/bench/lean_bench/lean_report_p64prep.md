# Lean report - p64prep RETRY 1 (2026-10-14 10:15-10:27): repair of the P6-4 plan, read and plan only

Task `tools/bench/lean_bench/queue/running/p64prep.md` (retry 1 of the review FAIL 10:14). One Opus session, lean rules
(`CLAUDE.md`). **No LabVIEW, no driver, no analysis script, no `motor_gate.py`, no camera, no rig; no new script.**
Files written: `p64_plan.md` (repaired, not rewritten), this report, 2 lines appended to `questions_for_user.md`.
Nothing else edited; nothing committed. A = main checkout `../V6_ParallelLoop/`, B = this worktree.

## 0. Start condition, user notes, safety record
- `lean_report_p6close.md:262` RESULT `"p6close": "PASS"` -> started.
- `user_notes.md` (3 notes): (1) no edit inside the big P6 VI, small subVI copy + callee swap - this decides the form of
  the new start-value wrapper (callee swap of #6810); (2) v5 G0 per-leg session start approved - kept; (3) P6-4
  PREPARATION approved, read + plan only - this task stays read + plan. **The task text contradicts no note.**
- Motor: not used by this task. The queue's session start for this cycle (`motor_session_start_p64prep_20261014_101529.log`),
  last lines: `LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402` · `position after (must be unchanged): X=4559 Y=-37898`
  · `ASI : ASI controller limits match the file (...) (sender code=0)` · `SESSION START OK -> ...\tools\bench\motor_session.json`
  · `RESULT {"schema":"result-line/1","status":"PASS",...}`. `tools/bench/motor_session.json` exists (10:15).
- `tasklist | grep -ic labview` -> `0` at 10:24 (no LabVIEW was started by this session).
- md5: **no md5 snapshot was taken in this cycle** and none was compared (that would mean running `lean_md5.py`, a script
  the task excludes). Nothing this session wrote is a VI.

## 1. What was read (each cited line re-read by this session)
- B: `CLAUDE.md`; the task; `user_notes.md`; `lean_review_p64prep_20261014_095745-c1.md` (all); `lean_report_p64prep_fail1.md`
  (all); `p64_plan.md` (all, before and after editing); `questions_for_user.md` (all); `lean_report_latest.md:1-104, 139-204`
  (section 1 graph facts, the observer join, the constant, the unsaved last pick); `lean_report_p6close.md` (all);
  `drive_original_copy_v5.py:1-104` (G0-G93 / L1-L13 contract) and `:436-475` (L8 code); `out_p6close/legs/W100_a1/m8_v5_replay_s1.json:60-170, 415-439`;
  `drive_m8.py:10-134`; `diag_c104_leg.py:195-234`; `tools/bench/imaqdx_attributes.txt` (lines 1-14, the Chunk / timestamp /
  StatusInformation lines, the camera-feature categories 16-171); `latestobs_build_run2.log` (head / tail).
- A: `docs/camera-acquisition-facts.md:590-670` (+ grep of the whole file for FrameID / BlockID / Chunk / Timestamp /
  LastBufferNumber); `docs/d1-loop12-17-split-plan.md:866-885, 1843-1917`; `docs/d1/ring-p6b.md:50-70`; `docs/user-rules.md`
  (all); `docs/NAMES.md:80-109`; `docs/m8-real-run-plan.md:160-232`; `docs/stage2-plan.md` (LastBufferNumber lines);
  grep of `docs/` for `get buff image-lost frames` (incl. `frame-loop-wire-graph.md:447`, `main-vi-subvi-identity.md:160`);
  `tools/bench/m8s3_run.json:15-28`.

## 2. The six fixes
Predictions: written into this file at 10:17 (section P at the end, unchanged), BEFORE the settling sources were read.

### Fix 1 - smoke criterion without L8
- **Prediction:** L8 checks exactly 3 answered panels; the W100 record shows L8 false with 15 answered.
- **Finding (as predicted):** `drive_original_copy_v5.py:466` `l8 = d0.win_present(SAVE_TITLE) and answered == 3` (contract
  text :76-77 "EXACTLY 3 `choose bandpass` panels"); the W100 leg: `"ok": false`, "15 closed (contract 3) ... terminal=save
  dialog appeared after 15 panel(s)" (`m8_v5_replay_s1.json:128-131`), `bandpass_run1.answered` = 15 (:419-420); that leg
  passed all chain gates (`lean_report_p6close.md:116`). The leg tool already drops L8 for N picks: M2 = L7 + L9 + L11
  (`drive_m8.py:103`, comment :88-90).
- **Plan changed:** section 5 item 4 (`p64_plan.md:114-125`): leg gates (drive_m8 M1-M8 with that M2; the leg script's gates)
  + v5 L1-L7 and L9-L13 + panels closed (`bandpass_run1.answered`) == picks registered (`picks_registered_tra`,
  `diag_c104_leg.py:216`) == 15 + tra / LabVIEW checks, with the L8 reason and citations. Same wording in section 9
  item 2 (`:275-278`). No other place in the plan required L8 or "all of L1-L13" (grep after editing: none).

### Fix 2 - an independent reference for C
- **Prediction:** (a) not in the files; (b) #5351 is seeded from #250, the same value as #5119's `y`, and #6810 is a proven
  swap point -> choose (b).
- **Finding (as predicted):**
  - (a) camera counter: not in the files. `ChunkDataDecodingEnabled = False` (`imaqdx_attributes.txt:14`),
    `ReceiveTimestampMode = 'None'` (:179); the camera features listed (:16-171) are DeviceControl, ImageFormatControl,
    AcquisitionControl, DigitalIOControl, AnalogControl, PulseGenerators, LUTControl, TransportLayerControl,
    UserSetControl, JAICustomControl - no chunk, FrameID / BlockID, event or timestamp feature. A
    `camera-acquisition-facts.md` has no frame-ID entry (its only LastBufferNumber line is :614-615). The IMAQdx
    `StatusInformation::LastBufferNumber` (:196) is the driver's number, the one #250 reads.
  - (b) graph facts: `y` of Subtract #5119 = tunnel #3363 <- Property #250 `LastBufferNumber`, read once outside loop 1.1;
    "The same value also initialises `Buffer to extract` (left shift register #5351 -> #6810)"; `x` and the ring's `Num` are
    #6810's `current image number` (`lean_report_latest.md:20-27`). Original: #250 t4 -> #6810 t7 `Buffer to extract`
    (A `frame-loop-wire-graph.md:447`); seeded from the live LastBufferNumber, +1 per frame (A `m8-real-run-plan.md:204-205`).
    #6810's callee `get buff image-lost frames.vi` was swapped in every replay copy (`lean_report_p6close.md:29-30`).
    #6810 is on the frame path (loop 1.1): rule 1c / U3 (no serial/VISA) holds; the one file write at the first call is
    the only extra.
  - Side fact, not used: the "8217 / 8331 / 8227" starts in A `m8-real-run-plan.md:205` are the first FRONT-PANEL frame
    counter samples (`m8s3_run.json:21-22` `frame_counter_series`), not a logged start value.
- **Choice: (b) observer.** See section 3 for its cost.
- **Plan changed:** section 6 rewritten (`p64_plan.md:133-228`): 6.1 what column 0 is and why C is not fitted (old step 2
  removed); 6.2 the reference and its cost, with fallback (c) if the build fails; 6.3 the check (steps 1-5 with the logged S,
  no fitted constant; end lag now computable); 6.4 what the live leg shows / does not. Section 1 BOBS row (`:32`) now has two
  swaps; section 3 item 5 (`:88-91`) moves the wrapper file and refuses a stale one.

### Fix 3 - section 9 items 3 / 4 wording
- **Prediction:** the live leg shows only number consistency against the logged start value + the pick inside the ring; the
  pairing rests on `lean_report_p6close.md:251-254`.
- **Finding (as predicted):** `lean_report_p6close.md:251-254`: own number 2540/2539/2538/1472 (9089) rows, X/Y/Z
  bit-identical vs S1 9089/9089, TransPos/RotPos post-init 0 rows differ - all replay legs.
- **Plan changed:** section 9 items 3-4 (`p64_plan.md:279-291`): item 3 = live number consistency (rows <-> picks <-> the
  start value actually subtracted), with what it does NOT prove; item 4 = image-number pairing and per-slot values from the
  replay, "P6-4 adds no live evidence for this half" (HOLD-6); the fallback wording if the wrapper is not built. Also section 0
  (`:19-23`) and the leg table (`:56,58`) no longer say "acceptance #1 on a live run" without the split.

### Fix 4 - section 8 predictions: indicator vs column-0 gaps
- **Prediction:** all earlier A numbers are `Total Lost Frames` indicator values; no column-0 measurement exists for A.
- **Finding (as predicted):** split-plan :874-877 names the indicator ("Total Lost Frames, 120 s ..."): S1 copy 3,331 / 3,161;
  3,493 / 3,269 are `D1_s3_loop15` (the old plan's "3,161 - 3,493" mixed the two VIs). Split-plan :1912 (A 3,359 / 5,860;
  B 16 / 12) is the leg tool's `lost`, i.e. the indicator: `diag_c104_leg.py:216` (`"lost": m8.get("total_lost_frames")`),
  `drive_m8.py:113-114` (parsed from v5 L11 `(lost=...)`), `diag_c104_leg.py:2` ("L11 has read `Total Lost Frames`").
  Not predicted: the same line gives tra rows, and rows + indicator = 11,132 / 11,128 (A) and 11,145 / 11,138 (B) - an
  inference (not a measurement) that in those single-camera-loop VIs the indicator ~ the column-0 gap count.
- **Plan changed:** section 8 (`p64_plan.md:242-270`): 8.1 table of every earlier number with "what was measured" and "new
  metric? No"; 8.2 A at 90 Hz = "no earlier measurement in this metric", predicted 2,500 - 7,000 with the basis; B "no earlier
  live measurement in this metric"; a separate indicator row (recorded, B not comparable); 150 Hz "no earlier measurement at
  150 Hz in any metric", A estimate 55 - 75 % from A's row rate; the OBS acceptance prediction with no fitted constant.

### Fix 5 - questions
- Kept all 7 (HOLD-1..4, ASSUME-1..3). Text changed only in **HOLD-1** (column-0 metric, panels == picks == 15, logged start
  value, pairing from the replay) and **ASSUME-1** (two callee swaps incl. the #6810 wrapper; no fitted constant; no camera
  frame ID) - plan section 10 `:298, :302`.
- The two review HOLDs added to section 10 as **HOLD-5** (P-1 / P-3 as preparation) and **HOLD-6** (live-evidence scope),
  citing `questions_for_user.md:17-18` (`p64_plan.md:305-306`); NOT appended again.
- `questions_for_user.md`: appended exactly 2 lines, `HOLD-1 ... (revised)` and `ASSUME-1 ... (revised)` (10:24). No duplicates.

### Fix 6 - order of work
- Section 11 (`p64_plan.md:308-318`): P-1 and P-3 marked "waiting for the user's answer (`questions_for_user.md:17`, HOLD-5)";
  P-1 now includes the #6810 start-value wrapper as a callee-swap build, described only; P-3's `p64_own.py` implements 6.3
  with the logged S; the run's acceptance #1 claim waits for HOLD-6 and HOLD-1.

## 3. The step-2 choice and its cost: (b) observer, `GetBuffFirst_<ts>.vi` on #6810, BOBS only
- **What:** a new small VI with `get buff image-lost frames.vi`'s exact pane (A `NAMES.md:84-87`) that calls the unchanged
  original once per call and, on the first call only, appends one line: requested `Buffer to extract` (= #5119's `y`),
  returned `current image number`, `Missed frames?`, tick. Swapped into the OBS copy at #6810 beside the existing pick
  observer swap at #31710.
- **Builds:** joins P-1 (no extra task): 1 new VI + its unit test (on a test copy whose inner call is the replay stand-in,
  `Buffer Number Out` = In, A `m8-real-run-plan.md:180,226-229`) + the second swap in BOBS. Reference: the pick observer build
  ran 816 s (`latestobs_build_run2.log`); estimate 15-30 LabVIEW minutes; no camera, no motor.
- **Extra load:** loop 1.1 (camera loop, frame path) - one more subVI call level per frame + one file open/append/close at
  the first call, after the first frame is in hand (no serial/VISA; the camera is never gated, U6). Loop 1.2 - the existing
  pick observer's line per pick. Only in the OBS leg; A and B ABBA legs never contain it.
- **Saved:** one line in `CD\bench\lean\obs\getbuff_first.txt` + the pick log, moved per leg to `out_p64/`. Product VI: nothing.
- **Fallback:** if the build or unit test fails, (c) "number consistency only" under one fitted constant, said in the acceptance
  (plan 6.2 last bullet, section 9).

## 4. Section-14 open items (`lean_report_p6close.md:201-237`) -> answer or question
| item | outcome | where in the plan |
|---|---|---|
| 14.2 live run of 15c664e3 | **answered:** none exists, every P6 run swapped #6810/#22692 (`lean_report_p6close.md:29-30,207`) -> smoke leg S0, criterion now without L8 (`drive_original_copy_v5.py:466`; `m8_v5_replay_s1.json:130`) | sections 2, 5 item 4 |
| 14.4 P6-4 pass criterion | **HOLD-1 (revised)** + **ASSUME-2** (metric = column-0 gaps). Earlier A numbers are indicator values (A split-plan:874, :1912; `diag_c104_leg.py:2,216`) | sections 8, 9, 10 |
| 14.5 150 Hz route | **answered in principle** (D-2026-09-25-05, A `decisions_pending.json:108-122`); **HOLD-2** for the A arm / 90-only | sections 1, 7, 10 |
| 14.6 panel magnet controls | **answered: they move nothing** (`drive_original_copy_v5.py:278-285,596-600`; `out_p6close/legs/P62_a1/m8_v5_replay_s1.json:264-307,539-582`) | sections 4, 7 |
| 14.7 beads / focus / picks | **HOLD-3**, **HOLD-4** (not in the files: A `STATUS.md:54` "No beads on the rig"; picks are fixed fractions, `drive_m8.py:33-38`) | sections 2, 3.4, 10 |
| 14.8 acceptance #1 live | **ASSUME-1 (revised)** + **HOLD-6**: live = number consistency against the logged start value (route (b)); pairing from the replay | sections 6, 9 |
| 14.9 v5 G0 per-leg session start | **answered: approved** (`user_notes.md:3`; `questions_for_user.md:9`) | sections 3.6, 7 |
| (review) P-1 / P-3 as preparation | **HOLD-5** (`questions_for_user.md:17`) | sections 10, 11 |
Answered from the files: 4 (14.2, 14.5 in principle, 14.6, 14.9). Questions: HOLD 6 (HOLD-1..6), ASSUME 3.
Plan path: `tools/bench/lean_bench/p64_plan.md`.

## 5. Acceptance #1 (every saved row's buffer number is its own frame's)
- **As the plan now checks it LIVE (OBS leg, plan 6.3 / section 9 item 3):** with S = the start value logged by the #6810
  wrapper (the `y` actually subtracted by #5119, not fitted): for every saved row, `col0 + S` == the buffer number of the
  pick that produced the row (pick observer log), one-to-one and in order; `col0[0] >= R - S`; every pick inside the ring.
  This proves **number consistency (rows <-> picks <-> start value)** on live frames; a constant row-to-pick offset would
  show on every row. It does not prove live that slot i's image is frame Num(i), nor the per-slot TransPos / RotPos values.
- **As the replay proved it (section 9 item 4):** own buffer number on every row and X/Y/Z bit-identical vs S1 on the same
  recorded frames, 9089/9089 rows over P62 / GAP / W40 / W100; TransPos/RotPos 0 rows differ
  (`lean_report_p6close.md:251-254`). P6-4 relies on this half (HOLD-6).

## 6. Limits
- The wrapper's pane, execution settings and the BOBS swap are designed from the files only; P-1 verifies them in LabVIEW
  (after HOLD-5). Whether the #6810 call in the P6 lineage still has uid 6810 in the final VI is taken from the stored graph
  facts (`lean_report_latest.md:22`, `lean_report_p6close.md:29`), not re-read.
- The A-arm "indicator ~ column-0 gaps" link is an arithmetic inference from :1912, labelled as such; the A legs record both.
- 150 Hz predictions have no earlier measurement in any metric.

## P. Predictions written before reading the settling sources (10:17, unchanged)
- **Fix 1 (L8):** `drive_original_copy_v5.py:466` checks that exactly 3 bandpass panels were answered (the 3-panel
  contract of the old M8 leg); on a 15-pick leg the answered count is 15, so the W100 record
  `m8_v5_replay_s1.json:130` shows L8 false while every other L-gate is true and the answered count is 15.
- **Fix 2 (C reference):** (a) the camera's own frame counter is NOT usable from the files (chunk data off, no FrameID /
  BlockID attribute, receive timestamp mode None - already seen in `imaqdx_attributes.txt` by the failed run);
  `camera-acquisition-facts.md` will not list a per-frame ID either. (b) `Buffer to extract` shift register #5351 is
  initialised from the same IMAQdx property read #250 (LastBufferNumber) that feeds #5119's y input, and feeds the
  buffer-number input of get-buff #6810; #6810 returns the buffer number actually delivered, which is what goes into
  the ring's Num. #6810 was already callee-swapped in every P6 replay leg (to the replay stand-in), so a callee swap of
  #6810 in the OBS copy is a proven route. Expected choice: **(b) observer**.
- **Fix 3:** the live leg can only show number consistency against the logged start value + the pick inside the ring;
  `lean_report_p6close.md:251-254` holds the replay proof of slot pairing and TransPos/RotPos.
- **Fix 4:** split-plan :874-877 (A15 3,359 / 5,860) and :1912 (3,161 - 3,493; display-loop VI 12 - 16) are values of
  the VI's `Total Lost Frames` indicator, not column-0 gaps. Expected: no earlier measurement in the column-0 metric for
  the original on a live run, unless the original's indicator is itself the sum of BufDiff steps (then it equals the
  column-0 gap count only when every acquired frame is saved).
- **Fix 5/6:** only HOLD-1 and ASSUME-1 change text; P-1 / P-3 become "waiting for the user's answer".
- (Afterwards: all held. One detail of the Fix-4 prediction was misplaced - 3,359 / 5,860 are at :1912 and 3,331 / 3,161 at
  :874-877, not the other way round; the plan cites them correctly.)

RESULT {"p64prep": "PASS", "answered": 4, "questions": {"hold": 6, "assume": 3}, "plan": "tools/bench/lean_bench/p64_plan.md", "c_reference": "observer", "minutes": 13}
