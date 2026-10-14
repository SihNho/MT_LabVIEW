# Lean report - p64p1 (2026-10-14): P6-4 preparation P-1, the 90 Hz observer copy BOBS90

Task `tools/bench/lean_bench/queue/running/p64p1.md`. One Opus session, lean rules (`CLAUDE.md`). No camera, no rig change, no
motor command by this session.

## 0. Start condition and user notes
- `lean_report_p64prep.md:177` RESULT `"p64prep": "PASS"` -> started (10:55).
- `user_notes.md` (4 notes): note 1 = never edit inside the big P6 VI, use a small subVI + callee swap; note 4 (10:4x "전부 동의함")
  = HOLD-5 answered: P-1 allowed, LabVIEW may be used, motors only through the queue's hooks / v5 G0. The task text agrees
  with the notes; nothing had to be overridden.
- The review of p64prep (`lean_review_p64prep_20261014_095745-c2.md:13,17`) added two instructions for P-1, taken here:
  (가) the First Call? test calls ONE wrapper node (one clone) 3 times inside ONE run of a top-level test VI and must give
  exactly 1 line; the BOBS call list must show the wrapper at exactly one call site; (나) if the wrapper fails, do NOT switch to
  the fitted-C fallback (c) by myself - ask HOLD-1/6 again.
- `tools/bench/motor_session.json` exists. Queue's session start (`motor_session_start_p64p1_20261014_105444.log`), last lines:
  - `PI  : reference {"FRF": 1.0, "POS": 0.0, "POS_BEFORE": 0.0, "RON": 1.0} -> REFERENCED at 0; verify OK (attempt 1/3)`
  - `LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402`
  - `position after (must be unchanged): X=4559 Y=-37898`
  - `ASI : ASI controller limits match the file (SL {'X': -3.8475, 'Y': -4.7744} / SU {'X': 0.1525, 'Y': -0.7744} mm, tol 0.001) (sender code=0)`
  - `SESSION START OK -> ...\tools\bench\motor_session.json`
  - `RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}`

## 1. Predictions (written before the build run)
Order note, stated: one READ-ONLY LabVIEW probe (`p64p1_lvprobe.py`, 11:00, nothing saved) ran before this section was
written; it read the get-buff VI's body and pane and searched for primitive donors. It tests none of the predictions below.

### 1.1 The two swaps (BOBS90 = byte copy of the final VI 15c664e3)
| call in 15c664e3 | callee now | callee in BOBS90 |
|---|---|---|
| #31710 (loop 1.2 pick loop) | `bench\lean\RingPickSlot_latest_20261014_010104.vi` 8fc2ec26 | `bench\lean\RingPickSlot_latestobs_20261014_025316.vi` 9504e0cf (calls `PickLog_latestobs_20261014_025316.vi` e5810aec), unchanged files |
| #6810 (loop 1.1 frame get) | `zz_LabView VI\background VIs\get buff image-lost frames.vi` 9aaaef21 | new `bench\lean\GetBuffFirst_<ts>.vi` |

### 1.2 Expected diffs and states
- Callee census diff (15c664e3 -> BOBS90) = exactly 4 rows: #31710 and #6810 gone, two NEW uids that call the observer and
  the wrapper (replace gives new uids). Nothing else.
- Wire-edge diff after the uid remap {new1 -> 31710, new2 -> 6810} = 0 of 2431 edges (the count of every earlier P6 copy).
- The wrapper is called at exactly ONE call site of BOBS90; the original get-buff VI keeps any other call it has in 15c664e3
  (expected: none - #6810 is the only get-buff call of the P6 lineage).
- ExecState 1 warm and cold for BOBS90, the wrapper, its test copy and the test harness. Cold edges of BOBS90 (remapped) == cold
  edges of 15c664e3. md5 of 15c664e3 and of every input unchanged.
- Wrapper: connector pane == the get-buff VI's, slot by slot (label + direction); execution settings equal (reentrancy type,
  priority, exec system); its census = exactly one call, to the original get-buff file.

### 1.2b Revision before the build (written 11:30, before build run 1 at 11:31), stated: the "once" mechanism
The probe found no `First Call?` node in any file a donor copy could come from (section 2), and the GUI route (Quick Drop) is
refused by this session's permissions. So the wrapper logs once with an **uninitialized shift register** instead: a
one-iteration While loop (stop <- Boolean constant True), its shift register's left side selects a Case, the right side is
fed the same True; the logger is in the FALSE frame. The register is False until the clone's first call, True afterwards.
Difference from First Call?: First Call? re-arms on every top-level RUN; the register re-arms only when the VI is LOADED
again. Each P6-4 leg starts a fresh LabVIEW (plan 6.2, v5), so a leg still gives exactly one line; a second run in the same
LabVIEW gives NO line, and plan 6.3 then says "check NOT RUN" (never a fitted C) - the safe direction.
Also stated: the line holds requested `Buffer to extract` S, returned `current image number` R and a ms tick, not `Missed
frames?`. Inside get buff, `Missed frames?` = `Equal To 0?(Buffer to extract - Buffer Number Out)` and `current image number`
= `Buffer Number Out` (probe: #76 x-y, #65 x=0?, wire 99), so `Missed frames?` = (S == R), exactly, from the line.
Predictions 1.3 below are revised for the register (warm run 2: 0 lines).

### 1.3 Unit test (no camera)
Revised (11:30): harness inputs `Buffer to extract` = 8217, 8218, 8219 from an I64[] control (auto-indexed For loop); two
test copies - inner = the paced replay VI (R = S) and inner = the P6-3 gap wrapper (R = S + 1, so the line's S/R order is
visible). Per test copy: warm run 1 -> exactly 1 line `8217, 8217|8218, tick`; warm run 2 (same LabVIEW) -> 0 lines; cold run
(fresh LabVIEW) -> exactly 1 line; outputs = the inner VI's own outputs on every run (paced: [8217, 8218, 8219], Missed
[T,T,T]; gap: [8218, 8219, 8220], Missed [F,F,F]). The text below (First Call?, values 0/1/2) is superseded.
Original text:
- Test copy = byte copy of the wrapper with its inner call swapped to `replay\replay_get_buff_image_paced60.vi` (59ec66b6, which
  returns `current image number` = `Buffer to extract`; `Missed frames?` = True).
- Harness: ONE For loop (parallelism off), N = 3, ONE test-wrapper node, `Buffer to extract` = the loop index i (0, 1, 2).
- Per harness run: the log file grows by exactly **1** line = `0, 0, <tick>` (requested 0, returned 0); the harness outputs
  `current image number` = [0, 1, 2] and `Missed frames?` = [T, T, T] = the inner VI's own outputs for 0, 1, 2 (read by direct
  calls). A second run in the same LabVIEW: again exactly 1 more line (First Call? is True once per top-level run).
  A run cold (fresh LabVIEW): exactly 1 more line.

### 1.4 Acceptance #1 (data accuracy) unchanged
The wrapper passes every input through and returns every output of the unchanged get-buff VI, so `current image number`,
`Buffer to extract` and thus column 0 (`BufDiff` = #5119 x - y) are the same values as in 15c664e3. BOBS90 is only for the OBS
leg; the product VI 15c664e3 is not touched.

(Sections 0-1 were written before the build. After it I changed only the two "11:35" time stamps to 11:30, the time they were
written; no prediction was changed.)

## 2. What the read-only probe found (`p64p1_lvprobe.py`, log `p64p1_lvprobe.log`, json `p64p1_lvprobe.json`)
- **Inside `get buff image-lost frames.vi`** (the claudeDev byte copy, md5 9aaaef21 == the original's): 4 body nodes only -
  #529 `IMAQdx Get Image.vi` (mode constant #581 `Buffer Number Mode (Next)`), #76 Subtract `x-y` (x = `Buffer to extract`,
  y = `Buffer Number Out`), #65 `Equal To 0?` -> `Missed frames?`; `current image number` = `Buffer Number Out` (wire 99).
- Pane (slot: label, direction): 0 Session In (in), 4 Session Out, 5 Image In (in), 6 Image Out, 7 Buffer to extract (in),
  8 Missed frames?, 10 current image number, 11 error in (in), 15 error out; slots 1-3, 9, 12-14 free. `Buffer to extract` and
  `current image number` are I32 (type code 0x03).
- Execution properties: ReentrancyType 1, IsReentrant True, ExecPriority 5 (time critical), PreferredExecSystem 7 (same as
  caller), AllowDebugging False.
- **No `First Call?` donor anywhere I could copy from.** The stored bed graph has none (offline). Scan 1: 80 of the 94
  `background VIs_COPY` files (the 14 largest not reached in the 600 s budget), 0 hits. Scan 2 (`p64p1_lvprobe_scan2.log`): NI
  examples (Structures, Synchronization, Asynchronous Call By Reference, TDMS speed tests), `vi.lib\Utility`, `LVClass`,
  `Erdos Miller`: 75 of 159 read (many vi.lib VIs are locked, error 1040), 0 hits. gscript has no creator for it (primitives
  come only by donor copy). The GUI route (Quick Drop, `tools/lv_gui.ps1`) was refused by this session's permission
  settings twice; I did not route around that. Hence the shift-register latch (section 1.2b).

## 3. Timeline
| time | step |
|---|---|
| 10:55 | start; task, CLAUDE.md, user_notes (4 notes), p64_plan 1 / 6.2 / 11, p64prep report + review c2 (the two P-1 instructions), latest report |
| 10:59 | `lean_md5.py` + 3 inputs (claudeDev get-buff copy, EMPTY_v0, DonorCase_v0) -> `md5_p64p1_start.json`, 139 files; LabVIEW 0; `motor_session.json` present |
| 11:00-11:14 | read-only probe + donor scan 1 (`BGRUN END rc=0 after 818s`, 10/0) |
| 11:06 | report section 1 (predictions) written |
| 11:15-11:26 | donor scan 2: first try had `/` path separators (error 7 on every file, 67 s); re-run `BGRUN END rc=0 after 653s`, 0 hits |
| 11:26-11:28 | Quick Drop route prepared (`p64p1_fcdonor.py open`: EMPTY_v0 copy, panel open, rc 0); the GUI helper refused by permissions -> abandoned, the copy deleted later |
| 11:30 | section 1.2b / 1.3 revised (shift-register latch), before build run 1 |
| 11:31-11:42 | build run 1: 66 pass / 1 fail - `loop_kernel` raised "expected 1 new wires, got 2" at the first harness (the loop-border tunnel makes two Wire objects); LabVIEW gone (H9). Its 4 saved files (timestamp 113106) are superseded and were deleted (section 9) |
| 11:42-12:05 | build run 2 (same script + an own check around `loop_kernel`): **141 pass / 1 fail**; the 1 fail = the script's LAST step, `os.replace` of the test log from C: to G: (WinError 17), after every gate; H9 LabVIEW gone. `BGRUN END rc=1 after 1359s` |
| 12:05 | `p64p1_tidy.py`: test log copied to `out_p64\getbuff_first_functest_20261014_114246.txt` (bytes equal), source deleted -> the wrapper's log path is empty for the leg; superseded files removed |
| 12:06 | md5 end: inputs EQUAL 139/139; LabVIEW 0 |

## 4. The built VIs (all `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean\`)
| file | md5 | what it is |
|---|---|---|
| **`D1_ring_p64Bobs_20261014_114246.vi` (BOBS90)** | **257fb8522d557305ab6fe2aa11a04b61** | byte copy of 15c664e3 + exactly two callee swaps: #31710 `RingPickSlot_latest_20261014_010104.vi` -> new #31524 `RingPickSlot_latestobs_20261014_025316.vi` (9504e0cf); #6810 `background VIs\get buff image-lost frames.vi` -> new #4092 `GetBuffFirst_20261014_114246.vi` |
| **`GetBuffFirst_20261014_114246.vi`** | **4cd87cb4fbe1a9a46675896397ec7a5f** | byte copy of get buff (pane, labels, execution settings by construction); its 4 body nodes deleted; ONE call (#43) of the original `G:\...\background VIs\get buff image-lost frames.vi` (the file 15c664e3's #6810 calls, md5 9aaaef21), all 4 inputs / 5 outputs wired straight through; log branch: Tick Count + Build Array [S, R, tick] -> one-iteration While loop (stop <- True #417), uninitialized shift register (left #455 -> case #77 selector; right #427 <- True), logger #97 in the FALSE frame d500 |
| `GetBuffLog_20261014_114246.vi` | b13444fe2dafa96c65525ebc79eb7323 | byte copy of `PickLog_latestobs` e5810aec (Write Delimited Spreadsheet (I64), pane {11: 1D data}); only change: path default -> `...\bench\lean\obs\getbuff_first.txt` (append True) |
| `GetBuffFirst_test_paced_20261014_114246.vi` | 37e4019c138c3081437a5ecea9b9e8a4 | TEST copy: wrapper with inner #43 -> `replay\replay_get_buff_image_paced60.vi` (59ec66b6) |
| `GetBuffFirst_test_gap_20261014_114246.vi` | 47d1316631bc7f7f4e6490019781a7fa | TEST copy: inner #43 -> `gap_get_buff_image_paced60_20261013_161639.vi` (a885a8fb; R = S + 1) |
| `GetBuffFirst_harness_paced_20261014_114246.vi` / `_gap_` | 00613eb52db7b217be5662b47a5fd8e6 / e708cba2113e9339081c49f58a691b24 | test harnesses (EMPTY_v0 copies): I64[] control -> ONE For loop (parallelism off, read back) -> ONE test-wrapper node; 3 output tunnels -> indicators |

Swap facts (build gates B0-B8, C7-C11): source 15c664e3 has exactly one RingPickSlot_latest call (#31710) and exactly one
get-buff call (#6810); callee diff = exactly 4 rows {6810, 31710 gone; 31524 observer, 4092 wrapper}; the wrapper at exactly
ONE call site, the observer at one, no direct get-buff call left (review (가), second half); wire-edge diff 0 of 2431 after
the remap {31524 -> 31710, 4092 -> 6810}, warm and cold (cold edges == 15c664e3's cold edges); ExecState 1 warm and cold;
md5 unchanged by the cold load.

## 5. Gates (build run 2, `p64p1_build.log` from `BGRUN START 2026-10-14 11:42:45`, json `p64p1_build.json`)
141 pass / 1 fail. The fail is "the run completed without an unhandled exception": `os.replace` across drives (WinError 17),
the script's last line, after C13; done by `p64p1_tidy.py` (section 3). No VI gate failed. Groups:
- S0-S3 source read; G0-G4 logger (pane only slot 11, default read back, ES 1);
- W0-W30 wrapper: 4 body nodes deleted (each verified gone), only the 9 pane terminals left, one get-buff call, **edges ==
  exactly the 9 pass-through edges** (W8), ES 1; then the log branch: stop constant read back True (W17), one shift register
  with its initializer unwired (W18), case frames {False, True} (W22), logger in the FALSE frame (W23b), edge diff: nothing
  removed, every added edge from a planned source, the logger's only source = the Build Array (W25-W26), the 9 pass-through
  edges unchanged (W27), ES 1 (W28), census = {get buff, logger} (W29), execution properties unchanged (W30);
- T (both test copies): callee diff = exactly the inner swap, edge diff 0 of 18 after remap, ES 1;
- H (both harnesses): one For loop + one kernel (own check H.1b/1c in place of `loop_kernel`'s wire count), parallelism OFF
  read back, ES 1, md5 unchanged by the runs;
- U (unit tests, section 6); B0-B8 BOBS90; C1-C13 cold (harness ES 1 + cold run, wrapper ES 1 / pane / properties / census,
  BOBS90 ES 1 / edges / callees, md5s, 4 test lines);
- H2-H6, H9 hygiene: input md5 unchanged, pins held, VI-Server refs opened 63 == closed 63, no stray file in claudeDev root,
  LabVIEW gone.

## 6. Unit-test numbers (no camera; the null image makes every call return error -1074396120 from the replay stand-in, the same in the wrapper and the direct calls)
| test copy | run | outputs `current image number` / `Missed frames?` | direct calls of the inner VI | log lines added | line |
|---|---|---|---|---|---|
| paced (R = S) | warm 1 | [8217, 8218, 8219] / [T, T, T] | same | **1** | `8217 8217 172743352` |
| paced | warm 2 (same LabVIEW) | same | same | **0** | - |
| paced | cold (fresh LabVIEW) | same | same | **1** | `8217 8217 173093207` |
| gap (R = S + 1) | warm 1 | [8218, 8219, 8220] / [F, F, F] | same | **1** | `8217 8218 172912502` |
| gap | warm 2 | same | same | **0** | - |
| gap | cold | same | same | **1** | `8217 8218 173147627` |
- 3 calls of ONE clone inside ONE run of the top-level harness -> exactly one line, and it is the FIRST call's (8217, not 8218
  or 8219): review (가) first half, met.
- Column order read back: [requested S, returned R, tick] (the gap copy makes S != R).
- The file `out_p64\getbuff_first_functest_20261014_114246.txt` holds exactly these 4 lines; `...\bench\lean\obs\getbuff_first.txt`
  does not exist now.

## 7. Predictions vs results
| prediction (section 1) | result |
|---|---|
| callee diff = exactly the two swaps (4 rows) | **as predicted** (B5, C10) |
| edge diff 0 of 2431 after remap | **as predicted**, warm (B7) and cold (C8) |
| wrapper at one call site; #6810 the only get-buff call of 15c664e3 | **as predicted** (S2, B6) |
| ExecState 1 warm and cold (BOBS90, wrapper, test copies, harnesses) | **as predicted** |
| wrapper pane == get buff's; execution properties equal; census = one get-buff call (+ the logger) | **as predicted** (C3-C5; the logger is the planned second callee) |
| unit test (revised 1.3): 1 / 0 / 1 lines per copy, outputs == inner VI's | **as predicted** |
| original 1.3 (First Call?, 1 line also on warm run 2) | not testable: superseded by 1.2b before the build |

## 8. Deviations from the task / plan, stated
1. **"Once" by an uninitialized shift register, not `First Call?`** (plan 6.2). Reason: no donor and no creator for the
   primitive (section 2); GUI refused. Effect: the latch re-arms per LOAD, not per top-level RUN. Every P6-4 leg launches a
   fresh LabVIEW, so the OBS leg still writes exactly one line; if the OBS VI were run twice in one LabVIEW, the second run
   writes nothing and plan 6.3 reports the check NOT RUN (never a fitted C). **P-3 must keep "fresh LabVIEW per OBS leg" and
   "refuse the leg if the wrapper file exists"** (plan section 3 item 5 already says the second).
2. **The line has no `Missed frames?` column.** It is S, R, tick; `Missed frames?` = (S == R) exactly, by get buff's own graph
   (section 1.2b). R - S (plan 6.3 step 1) is computed directly.
3. **Test values**: 8217-8219 as planned, through two test copies (paced and gap) instead of one; the gap copy is extra (proves
   the column order).
4. Review (나) was not triggered: the wrapper was built and tested; nothing fell back to the fitted-C route (c).
5. Extra files: `GetBuffLog_*` (the logger copy - the observer's PickLog writes to a fixed default path, so the wrapper needs its
   own copy with a different default) and the 2 test copies + 2 harnesses (test only; never called by BOBS90).

## 9. Notes for P-3 / the OBS leg (facts found here, nothing changed)
- BOBS90's pick observer writes to its PickLog's default path `tools\bench\lean_bench\out_latest2\picklog_w100.txt`, and that
  file EXISTS now (the `latest` W100 run's 1475 lines). The driver must move it away before the OBS leg (plan section 3 item 5
  checks for stale files - this one is stale today).
- The wrapper's file: `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean\obs\getbuff_first.txt`
  (absent now); format `S<TAB>R<TAB>tick` (U32 tick; S, R I32 written as I64 text).
- Files removed this session (all created by this session, never used by anything else): build run 1's
  `GetBuffLog_20261014_113106.vi` 4afa7e6d, `GetBuffFirst_20261014_113106.vi` 32255390, `GetBuffFirst_test_paced_20261014_113106.vi`
  663b8a46, `GetBuffFirst_harness_paced_20261014_113106.vi` 6544be40 (= EMPTY_v0, never saved); `FirstCallDonor_20261014_112649.vi`
  6544be40 (= EMPTY_v0); the probe's 3 `scratch_p64p1_probe_gb_*.vi` 9aaaef21 (= get buff, never saved).

## 10. LabVIEW gone, md5s, motors
- LabVIEW gone: H9 PASS at the end of every LabVIEW run (probe, scan 2 x2, build runs 1 and 2); `tasklist | grep -ic labview`
  -> `0` at 12:06 and again at the end of this report.
  The Quick Drop prep (`p64p1_fcdonor.py open`) left LabVIEW running on purpose (11:27); the next run's restart closed it.
- **Input md5s, start (10:59) vs end (12:06): `EQUAL 139 / 139`** (`lean_md5.py --diff p64p1_start p64p1_end`): the final VI
  15c664e3, the observer 9504e0cf, PickLog e5810aec, RingPickSlot_latest 8fc2ec26, the original get buff 9aaaef21 and its claudeDev
  copy, the replay / gap callees, EMPTY_v0, DonorCase_v0, the bed, the original main VI 2a78e17c, motor_limits 65e9efae,
  motor_gate 0f06dd0d, and all 94 `background VIs` files. `md5_p64p1_end_outputs.json` adds the 7 new files (146 entries; the
  7 differ from the start only as new entries, md5s as in section 4).
- Motors: this session ran no motor command and no `motor_gate` verb; nothing it ran calls v5 or the rig. Queue's session start
  quoted in section 0. No camera was opened (the replay stand-ins read files from `G:\m8_replay_frames`).

## 11. Shared scripts edited / new
- Edited: `tools/bench/lean_bench/lean_md5.py` (+3 inputs, +7 outputs).
- New: `p64p1_probe.py` (offline graph read), `p64p1_lvprobe.py` (read-only probe + donor scans), `p64p1_scan2_globs.txt`,
  `p64p1_wait.py` (log waiter, no LabVIEW), `p64p1_fcdonor.py` (Quick Drop prep, only its `open` step ran), `p64p1_build.py`,
  `p64p1_tidy.py`. Logs: `p64p1_lvprobe.log`, `p64p1_lvprobe_scan2.log`, `p64p1_fcdonor.log`, `p64p1_build.log` (runs 1 and 2;
  run 1 also as `p64p1_build_run1.log` / `.json`).
- Not edited: `tools/hooks/**`, `tools/motor_gate.py`, `tools/bench/motor_limits.json`, `CLAUDE.md`, `tools/gscript.py` (shows
  modified in git status from before this session). Nothing committed.

## 12. Verdict
**p64p1: PASS**, with the deviations of section 8.
- BOBS90 `D1_ring_p64Bobs_20261014_114246.vi` **257fb8522d557305ab6fe2aa11a04b61** = byte copy of 15c664e3 + exactly the two
  callee swaps; edges 2431/2431 after remap; ExecState 1 warm and cold; wrapper at one call site.
- Wrapper `GetBuffFirst_20261014_114246.vi` **4cd87cb4fbe1a9a46675896397ec7a5f**: calls the unchanged original get buff, passes all
  9 terminals straight through (outputs == the inner VI's in every test call), pane and execution settings identical, logs the
  start value once per load: 3 calls of one clone -> exactly one line holding the FIRST call's requested and returned numbers.
- Acceptance #1 not touched: the product VI 15c664e3 is unchanged (md5), and BOBS90's frame values are the original get buff's.
- For the user / review: the latch is per load (section 8.1) - accept it, or say if a true `First Call?` is required (it then
  needs one GUI Quick Drop in an approved session, or a donor file the user points to).

RESULT {"p64p1": "PASS", "bobs90_md5": "257fb8522d557305ab6fe2aa11a04b61", "getbufffirst_md5": "4cd87cb4fbe1a9a46675896397ec7a5f", "minutes": 73}
