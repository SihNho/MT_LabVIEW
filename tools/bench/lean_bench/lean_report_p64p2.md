# Lean report - p64p2 RETRY 1 (2026-10-15): new 150 Hz wrapper with the log line finished BEFORE Configure Grab (Merge Errors), new A150 / B150 / BOBS150 / harness, 30 s camera-only check, fresh-open readback saved to a file

Task `tools/bench/lean_bench/queue/running/p64p2.md` (lean task 8, retry 1 of p64p2). One Opus session, lean rules (`CLAUDE.md`).
No beads, no motor command, no product VI run by this session. Started 01:48.

## 0. Start condition, retry, user notes
- `lean_report_p64p1.md:227` RESULT `"p64p1": "PASS"` -> started. p64p3 RESULT recorded: `lean_report_p64p3.md:126`
  `"p64p3": "PASS"`.
- **This is retry 1 of p64p2.** The first cycle (`lean_report_p64p2_fail1.md`, own result PASS) was judged FAIL by review
  `lean_review_p64p2_20261014_105444-c5.md:11-15,18-23`: (1) in wrapper d30c29b1 the log write and the Configure Grab call ran
  in parallel (`fail1.md:63-66`), so "line, then Configure Grab" was not met; (2) the fresh-open 90.0009 gate had no raw
  output on file. The old files (wrapper d30c29b1, A150 c6778e2c, B150 1eec9b69, BOBS150 008f786d, harness 0b0ed57c,
  `out_p64/p64p2/*`) are kept and pinned by md5 (start = end, section 9).
- `user_notes.md` (11 notes + 1 chat fact) read. Note 2 (no edit inside the big P6 VI; callee swap only) and note 5 (HOLD-5:
  P-2 allowed incl. a 30 s camera-only check without beads; motors only by the queue's hooks / v5 G0) are what this task does.
  Note 8 (the ASI XY change of the failed cycle was the user's joystick) answers the open question the task text calls a
  HOLD (`questions_for_user.md:43-46`) - the note wins: it is not a HOLD any more; it never blocked this camera-only task anyway.
  No other contradiction between the task text and a note.
- `tools/bench/motor_session.json` exists; no `tools/bench/lean_bench/STOP` (only the renamed `STOP_run1_20261014_095740.txt` and
  `STOP_run3_20261015_014703.txt` - the latter's text: `run limit 5 reached (5 cycles since 2026-10-14 10:54:44) - evaluation
  discussion, then the user's check`, written by the queue at 2026-10-14 15:34; the queue started this cycle after it).
- LabVIEW processes at start: 0. `obs\configgrab_rate150.txt` does not exist at start.

### Motor session start log (queue's hook): `motor_session_start_p64p2_20261015_014711.log`, last lines
```
PI  : reference {"FRF": 1.0, "POS": 0.0, "POS_BEFORE": 0.0, "RON": 1.0} -> REFERENCED at 0; verify OK (attempt 1/3)
before SL: :A X=-500.000000 Y=-500.000000   SU: :A X=500.000000 Y=500.000000
SL write -> :A
SU write -> :A
LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402
position after (must be unchanged): X=-52899 Y=-41518
RESULT: controller limits set (mode limits-set)
ASI : ASI controller limits match the file (SL {'X': -3.8475, 'Y': -4.7744} / SU {'X': 0.1525, 'Y': -0.7744} mm, tol 0.001) (sender code=0)
SESSION START OK -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_lean\tools\bench\motor_session.json
RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}
```
**ASI XY of this cycle's start: X=-52899 Y=-41518** - different from both earlier values (X=4559 Y=-37898 before the failed
cycle; X=284 Y=-30522 during it, the user's joystick move per `user_notes.md:8`). Read from the log only; no `motor_gate` /
stage command was used to check it. The end log of this cycle is written by the queue after this session ends, so this
session cannot read it. **For the user:** the ASI stage stands at a third position (X -52899, Y -41518) at this cycle's start;
if that was not your joystick, please say so before any rig / bead work (this task uses no motor).

### Inputs by md5 (start, `md5_p64p2r1_start.json`, 01:5x)
A source `D1_s1_copy.vi` 3e3d23ce...; B source 15c664e3...; BOBS90 257fb852...; GetBuffFirst 4cd87cb4...; vi.lib
`IMAQdx Configure Grab.vi` 306a6f92c10e66ff419b3e74a315c20e; `.icd` 2ea8512c57d734e76b02e91ced996d08; old wrapper d30c29b1...;
A90 / A150 / B150 / BOBS150 of 20261014_140059 3e3d23ce / c6778e2c / 1eec9b69 / 008f786d; old harness 0b0ed57c...; old outputs
`out_p64/p64p2/configgrab_rate150_check.txt` f95e3d39..., `rate150_frames.txt` ab95c034...; also pinned: vi.lib `Merge Errors.vi`
2369e859..., `Write Delimited Spreadsheet (string).vi` c6b042c7..., `IMAQdx Read Attributes From String.vi` 6d269590...; the
original main VI 2a78e17c... - all equal to the task table where it gives one.

## 1. Predictions (written 01:5x, before any LabVIEW run)
1. **New wrapper body** (`CD\bench\lean\ConfigureGrab_rate150_<newts>.vi`, EMPTY_v0 copy, built by `p64p2r1_build.py` part
   `w` = `p64p2_build.py` part wh with one change): `IMAQdx Read Attributes From String` (one-attribute string, rate "150") ->
   property node ActiveAttribute = AcquisitionFrameRate -> ValueString -> ActiveAttribute = ExposureTime -> ValueString (= the
   readback chain; its last node is the 2nd ValueString node, "P4"). Log branch as d30c29b1: Unbundle(P4 error out) -> code;
   Tick Count; Number To Decimal String x3; Build Array chain ["150", rate ValueString, exposure ValueString, code, tick] ->
   `Write Delimited Spreadsheet (string)` (append, `obs\configgrab_rate150.txt`). **Merge Errors wiring:** `Merge Errors.vi`
   (vi.lib `error.llb`) input 1 (`error in 1`, first) <- P4 `error out`; input 2 (`error in 2`) <- the logger's `error out`;
   the logger's `error in (no error)` UNWIRED; Merge Errors `error out` -> Configure Grab `error in`, and nothing else feeds
   Configure Grab's `error in`. Configure Grab `Session In` <- P4 session; `Number of Buffers` <- pane control (default 5);
   `Session Out` / `error out` -> the pane indicators. Pane == Configure Grab's slot by slot (11 Session In, 10 Number of
   Buffers, 8 error in, 3 Session Out, 0 error out); execution settings == Configure Grab's {ReentrancyType 0, IsReentrant
   True, ExecPriority 2, PreferredExecSystem 7, AllowDebugging True}; ExecState 1 warm and cold; census = {Read Attributes
   From String, Configure Grab, Write Delimited Spreadsheet (string), Merge Errors}; defaults hold COLD after a restart (F1;
   may need the fixdef re-apply, which the build now does on its own after the save).
2. **Readback** 150 (+- 0.01; the camera's text, set value 149.993, facts :758); exposure ~1909 us; line error code 0.
3. **30 s harness:** 4500 frames, 149.7-150.0 frames/s, 0 buffer gaps with `Next`, 0 Get Image2 errors; the wrapper's own
   `error out` is not an indicator of the old harness (it feeds Get Image2's `error in` through the loop tunnel), so the
   evidence that it is 0 = the line's code 0 + 0 Get Image2 errors (a wrapper error would make every Get Image2 return it).
4. **Each copy's callee diff exactly 2 rows** (#13962 Configure Grab gone, one new uid -> the NEW wrapper); edges after the
   uid remap A 2216, B 2431, BOBS 2431, warm and cold; ExecState 1 warm and cold; source md5s unchanged.
5. **Harness** (byte copy of 0b0ed57c + one swap): callee diff exactly {#44 old wrapper gone, one new uid -> new wrapper};
   edges equal after the remap; ExecState 1 cold.
6. **Fresh open** (C API, LabVIEW closed): AcquisitionFrameRate 90.0009; `.icd` md5 2ea8512c... before = after.
7. LabVIEW gone at the end; refs opened == closed; md5 diff `p64p2r1_start` vs `p64p2r1_end` EQUAL.

## 2. Timeline
| time | step |
|---|---|
| 01:48 | start; task, CLAUDE.md, user_notes, fail1 report, review c5, `p64p2_build.py`, `p64p2_fresh.py`, old state |
| 01:5x | `lean_md5.py` + `--r1` / `--r1new` switches -> `md5_p64p2r1_start.json`; LabVIEW 0; motor_session.json present; no STOP |
| 01:5x | sections 0-1 written (this text) |
| 01:54-01:58 | wrapper run 1 (`p64p2r1_build.py w`): STOP at my own gate W8a - vi.lib Merge Errors' inputs are named `error in 1 (no error)` / `error in 2 (no error)` / `error in 3 (no error)` / `error array in`, my match wanted names ending in "1"/"2". Nothing saved (the unsaved EMPTY_v0 work file `ConfigureGrab_rate150_20261015_015418.vi` left, removed at the end); LabVIEW gone, refs 9 == 9; `RESULT ... 32/2` |
| 01:58-02:17 | wrapper run 2: **96/0**, `BGRUN END rc=0 after 1142s`; build save 43193359, defaults lost on the build save again (COLD before: all empty / 0) -> re-applied once on the saved file -> **F1 COLD PASS**, final md5 **1419d4c6**; all cold structure gates PASS; refs 47 == 47; H9 LabVIEW gone |
| 02:17-02:42 | copies + harness run (`p64p2r1_build.py copies`): **65/0**, `BGRUN END rc=0 after 1497s`; refs 28 == 28; H9 LabVIEW gone |
| 02:42-02:45 | camera run (`p64p2r1_build.py run`): **20/0**, `BGRUN END rc=0 after 150s`; refs 7 == 7; H9 LabVIEW gone |
| 02:45 | `tasklist | grep -ic labview` = 0; fresh open (`p64p2r1_fresh.py`, once) -> `out_p64/p64p2_r1/fresh_open.json` |
| 02:45 | tidy (`p64p2r1_tidy.py --do`): run 1's unsaved work file removed (md5 = EMPTY_v0 6544be40); md5 end + `--r1new` outputs; diff EQUAL 159 / 159; LabVIEW 0 |

## 3. The new wrapper `CD\bench\lean\ConfigureGrab_rate150_20261015_015820.vi` (md5 **1419d4c679bd2e68d4962e0ff3ad39d1**)
Built by `p64p2r1_build.py w` run 2 (`p64p2r1_build_w.log`, 96/0). EMPTY_v0 copy; body = d30c29b1's (same donors, same
attribute string, same reads, same line) with ONE change, the Merge Errors join:
| uid | node | wired |
|---|---|---|
| #43 | `IMAQdx Read Attributes From String.vi` | `Session In` / `error in` <- pane; `Attributes String In` <- control default (one line `...AcquisitionFrameRate = "150"`) |
| #44 -> #137 | IMAQdx property nodes: ActiveAttribute = `...AcquisitionFrameRate` -> ValueString (rate readback) | session + error from #43 |
| #166 -> #219 | ActiveAttribute = `...ExposureTime` -> ValueString (exposure) | session + error chain; **#219 = the readback chain's last node** |
| #45, #221, #294 / #313 / #332, #351, #368-#428 | Unbundle(#219 `error out`) -> code; Tick Count; Number To Decimal String x3; Build Array chain ["150", #137 ValueString, #219 ValueString, code, tick] | as d30c29b1 |
| #448 | `Write Delimited Spreadsheet (string).vi` (append, `obs\configgrab_rate150.txt`) | `1D data` <- #428; **`error in (no error)` UNWIRED** |
| **#46** | **vi.lib `Merge Errors.vi`** | **`error in 1 (no error)` <- #219 `error out`; `error in 2 (no error)` <- #448 `error out`; `error in 3`, `error array in` unwired** |
| #248 | vi.lib `IMAQdx Configure Grab.vi` (unchanged) | `Session In` <- #219 session; **`error in` <- #46 `error out` only**; `Number of Buffers` <- pane control (default 5); `Session Out` / `error out` -> pane |

So Configure Grab #248 cannot start until #46 has both inputs, i.e. until the logger #448 has returned (the line written or its
own error); a camera error of the reads (#219) still reaches the logger's line (code column) and, through Merge Errors input 1
(first, it wins), Configure Grab and the caller.

**Structure gates, COLD (LabVIEW restarted, read from the saved final file; `p64p2r1_build_w.log` [WC]):**
- (a) WC.a1 Merge Errors #46 inputs == exactly {`error in 1` <- #219 `error out`, `error in 2` <- #448 `error out`}; WC.a2 #46
  output -> #248 `error in` and nothing else; WC.a3 #248 `error in` has exactly one source (#46); WC.a4 #248 inputs exactly
  {Session In <- #219, Number of Buffers <- pane, error in <- #46}; WC.a5 #219 `error out` feeds exactly #46 input 1 and the
  Unbundle #45 - PASS.
- (b) WC.b the logger's inputs are only `append`, `file path`, `1D data` - `error in` unwired - PASS.
- (c) WC.c1 census = {Read Attributes From String #43, Configure Grab #248, Write Delimited Spreadsheet (string) #448, Merge
  Errors #46} (+ primitives: owner classes SubVI 4, BuildArray 5, Function 4, Unbundler 1, Property 4); WC.c2 one each; WC.c3 no
  serial / VISA (no such class or callee; the 4 `Function` nodes are Tick Count + 3 Number To Decimal String); the only written
  attribute is the one line of the attribute string (AcquisitionFrameRate) - PASS. WC4 cold edges == warm edges (36).
- (d) **F1 defaults COLD**: the build save lost the value defaults again (COLD before: all empty, number 0, append True) - the
  run re-applied them once on the saved file (as fixdef) and the COLD read after a restart holds them: attribute text, both
  ActiveAttribute names, number 150, log path `...\bench\lean\obs\configgrab_rate150.txt`, append True; WC0 Number of Buffers 5
  (== Configure Grab's). md5 build save 43193359 -> final **1419d4c6** (all cold gates and every later step use 1419d4c6).
- (e) WC2 pane == Configure Grab's slot by slot {0 error out (out), 3 Session Out (out), 8 error in, 10 Number of Buffers,
  11 Session In}; WC3 execution settings == Configure Grab's {ReentrancyType 0, IsReentrant True, ExecPriority 2,
  PreferredExecSystem 7, AllowDebugging True}; WC1 ExecState 1 - PASS.

## 4. The built VIs (`C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean\`, `p64p2r1_build_copies.log` 65/0)
| file | md5 | source (md5 unchanged) | the ONE swap (old -> new uid) |
|---|---|---|---|
| `ConfigureGrab_rate150_20261015_015820.vi` (wrapper) | **1419d4c679bd2e68d4962e0ff3ad39d1** | EMPTY_v0 6544be40 | - (new small VI, section 3) |
| `D1_s1_p64A_20261015_015820.vi` (A90 byte copy) | 3e3d23cefd3a334001aa9d6156bf1aee | `D1_s1_copy.vi` 3e3d23ce | none (byte copy; the A source itself never opened) |
| **`D1_s1_p64A150_20261015_015820.vi`** (A150) | **65b409a8c44f9140b26f70135fb89b99** | A90 = 3e3d23ce | #13962 `IMAQdx Configure Grab.vi` -> **#23006** -> new wrapper |
| **`D1_ring_p64B150_20261015_015820.vi`** (B150) | **d3953cd6e96cc225ac0ed3f8ec3eaca0** | 15c664e3 | #13962 -> **#31524** -> new wrapper |
| **`D1_ring_p64Bobs150_20261015_015820.vi`** (BOBS150) | **35e7e973c93d1aa56bd6344fab1db8c1** | BOBS90 257fb852 | #13962 -> **#31381** -> new wrapper (observer #31524 and GetBuffFirst #4092 kept: callee diff = only the swap) |
| **`Rate150Harness_p64p2r1_20261015_015820.vi`** (harness, test only) | **75024d3f11e419b901184f3bcf9b2fdd** | old harness 0b0ed57c | #44 old wrapper d30c29b1 -> **#723** -> new wrapper |

**Gates per copy (warm / cold):**
| copy | Configure Grab calls | callee diff | edges after remap warm / cold | ExecState warm / cold | md5 unchanged by cold load; source md5 unchanged |
|---|---|---|---|---|---|
| A150 | [#13962] | exactly {#13962 gone, #23006 -> new wrapper} | 2216 = 2216 / 2216 = 2216 | 1 / 1 | yes / yes |
| B150 | [#13962] | exactly {#13962 gone, #31524 -> new wrapper} | 2431 = 2431 / 2431 = 2431 | 1 / 1 | yes / yes |
| BOBS150 | [#13962] | exactly {#13962 gone, #31381 -> new wrapper} | 2431 = 2431 / 2431 = 2431 | 1 / 1 | yes / yes |
| harness | old wrapper at [#44] | exactly {#44 old wrapper gone, #723 -> new wrapper} | 23 = 23 / 23 = 23 | 1 / 1 | yes / old harness + old wrapper unchanged |
Each copy: the new wrapper at exactly one call site, no Configure Grab call left. Copies LOADED only, never run. Harness cold
(HC4): its panel carries the labels the run uses (`Session In`, `Image Name`, `Array`, `Array 2`, `Array 3`, `error out`).
**Acceptance #1:** the edge diff after the remap is empty in every copy, warm and cold, so the frame-get call (#6810 in A150 /
B150, GetBuffFirst #4092 in BOBS150), #250 `LastBufferNumber`, #5119 `BufDiff` and all their wires are unchanged; column 0 is
formed exactly as in each source. Only the init-frame Configure Grab callee changed.

## 5. The 30 s camera-only check (`p64p2r1_build_run.log`, 20/0; no beads, no motor, no product VI)
- R0 motor_session.json present, no STOP; R1 wrapper 1419d4c6 / harness 75024d3f as saved; **R2 `obs\configgrab_rate150.txt`
  did not exist before**; R3 harness ExecState 1 cold; wrapper defaults read COLD before the run (attribute text, names, 150,
  log path, append True); R3b camera control `('cam1', ...)` read back; R3c no modal dialog.
- **The line** (moved to `out_p64/p64p2_r1/configgrab_rate150_check.txt`, md5 8cc1daea...; `obs\configgrab_rate150.txt` does not
  exist at the end): `150	150	1909	0	24904580` = requested 150, **readback 150** (camera ValueString), **exposure 1909 us**,
  **error code 0**, **tick 24904580**. R5 exactly one line; R6 readback within 150 +- 0.1 and code 0 - PASS. (The line's tick is
  212 ms before the first frame's tick 24904792; the ordering itself is proven by the wiring of section 3, not by the tick.)
- **Frames** (`out_p64/p64p2_r1/rate150_frames.txt`, md5 eccbf84e...; columns i, buffer number, ms tick, error status, code):
  **4500 frames**, buffer numbers 0 .. 4499, steps {+1: 4499} -> **0 gaps**; R7 **4500 / 4500 Get Image2 without error**; span
  30.004 s -> **149.947 frames/s** (buffer delta / tick delta) - R8 within 150 +- 1 %: PASS. Harness wall 35.4 s; Close error
  (False, 0, '').
- **The wrapper's own `error out` as seen by the harness:** the harness has no indicator on it (it feeds Get Image2's `error in`
  through the loop tunnel; not changed - the harness is the byte copy + one swap only). Evidence it was 0: the line's code 0
  (the readback chain) and 0 Get Image2 errors in 4500 calls (Get Image2 passes an incoming error through, so a non-zero
  wrapper `error out` - from the reads, the logger or Configure Grab - would have shown in every row's error column).

## 6. Fresh open/close, raw output on file (`out_p64/p64p2_r1/fresh_open.json`, md5 0d2f0f47...)
Run once with LabVIEW closed (`tasklist` 0). Quoted from the file:
- `"run_start": "2026-10-15 02:45:12"`, `"run_end": "2026-10-15 02:45:21"`, `"exit_code": 0`, `"stderr": ""`
- `"command_line": "C:\\Users\\KimLab\\AppData\\Local\\Programs\\Python\\Python310\\python.exe -u \"...\\tools\\bench\\lean_bench\\p64p2r1_fresh.py\" --child"`
- `"stdout": "RESULT {\"open_rc\": 0, \"AcquisitionFrameRate\": [0, 90.0009], \"AcquisitionFrameRateRaw\": [0, 11111], \"ExposureTime\": [0, 1909.0], \"ExposureAuto\": [0, \"Continuous\"], \"close_rc\": 0}\n"`
- `"open_rc": 0`, **`"AcquisitionFrameRate": [0, 90.0009]`**, `"close_rc": 0`
- **`"icd_md5_before": "2ea8512c57d734e76b02e91ced996d08"`, `"icd_md5_after": "2ea8512c57d734e76b02e91ced996d08"`**
Gate: 90.0009 (the 150 Hz setting does not persist) and `.icd` unchanged - PASS.

## 7. Predictions vs results
| prediction (section 1) | result |
|---|---|
| wrapper body + Merge Errors wiring (input 1 <- #P4, input 2 <- logger, output -> Configure Grab only; logger error in unwired) | **as predicted** (WC.a1-a5, WC.b); input names are `error in 1 (no error)` / `error in 2 (no error)` (cost build run 1) |
| pane / execution settings == Configure Grab's; census of 4 subVIs; defaults COLD | **as predicted**; the defaults were again lost by the build save and re-applied once (F1 COLD PASS) |
| readback 150 +- 0.01; exposure ~1909; code 0 | **150, 1909, 0** |
| 149.7-150.0 frames/s, 0 gaps, 0 Get Image2 errors, ~4500 frames | **149.947, 0, 0, 4500** |
| wrapper `error out` not exposed by the harness; evidence = code 0 + 0 Get Image2 errors | **as predicted** |
| callee diff exactly 2 rows; edges A 2216 / B 2431 / BOBS 2431 warm and cold; ExecState 1 | **as predicted** |
| harness: diff exactly the wrapper swap, edges equal, ExecState 1 cold | **as predicted** (23 edges) |
| fresh open 90.0009, `.icd` unchanged | **as predicted**, quoted from `fresh_open.json` |
| LabVIEW gone; refs opened == closed; md5 EQUAL | **as predicted** (section 9) |

## 8. Deviations from the task, stated
1. **Build run 1 failed at my own name gate** (W8a, section 2): nothing saved; its unsaved EMPTY_v0 work file was removed by
   `p64p2r1_tidy.py` only after its md5 matched EMPTY_v0 (6544be40).
2. **The wrapper was re-saved once by the defaults step** (43193359 -> 1419d4c6) inside the same build run, BEFORE any copy
   was built and before every cold gate - so all copies, the harness and the run use the final 1419d4c6 (no re-save after).
3. **A90 byte copy** `D1_s1_p64A_20261015_015820.vi` (3e3d23ce) made in bench\lean as the A150 source (the task's "byte-copy the
   A source first"); it is an extra file identical to the A source.
4. **Harness `error out` of the wrapper**: not exposed (section 5); I did not edit the harness beyond the one swap.
5. **`lean_md5.py`**: new switches `--r1` (adds the failed cycle's 6 VIs, `out_p64/p64p2/*`, vi.lib `Merge Errors.vi`,
   `Write Delimited Spreadsheet (string).vi`, `IMAQdx Read Attributes From String.vi`) and `--r1new` (lists ONLY the retry's
   new outputs, for the end pin `md5_p64p2r1_end_outputs.json`). The `p64p2r1_start` / `p64p2r1_end` diff covers inputs + old
   files; the new outputs do not exist at start, so they are pinned separately at the end (section 4 md5s = that file).
6. **Fresh script**: `p64p2r1_fresh.py` = `p64p2_fresh.py`'s camera code (unchanged reads) + an outer process that runs it
   once as `--child` and writes the file; it refuses to run if `fresh_open.json` exists (run once only).

## 9. Approval prompts / hook refusals (first message verbatim), LabVIEW, md5s, motors
- Permission prompts (not approved; I used single-command forms or dedicated tools, never another route to the same effect):
  - `This Bash command contains multiple operations. The following part requires approval: grep -i -E "p64p2|p64p1|p64p3|review_p64p2|lean_md5|STOP$" ; ls tools/bench/motor_session.json tools/bench/lean_bench/STOP 2>&1; ls -t tools/bench/lean_bench/motor_session_start_p64p2_*` (also for later compound lines and a `py -c` / `py -m py_compile` one-off)
  - `This command requires approval` (my peek script called with absolute paths; re-run with relative paths)
  - Tool message: `Blocked: sleep 25 followed by: tail -n 25 tools/bench/lean_bench/p64p2r1_build_w.log. To wait for a condition, use Monitor with an until-loop ...` (waited instead with the existing text-log waiter `p64p2_wait.py`, which carries `# labview: none`).
- Hook refusals: none.
- **LabVIEW gone**: H9 PASS at the end of every LabVIEW run (w run 1, w run 2, copies, run); `tasklist | grep -ic labview`
  -> **0** at 02:45 (before the fresh open) and at the end. VI-Server refs opened == closed (H5) in every run: 9 == 9,
  47 == 47, 28 == 28, 7 == 7.
- **md5 `p64p2r1_start` (01:5x) vs `p64p2r1_end` (02:45): `EQUAL 159 / 159`** (`lean_md5.py --diff p64p2r1_start
  p64p2r1_end`): A source 3e3d23ce, 15c664e3, BOBS90 257fb852, GetBuffFirst 4cd87cb4, vi.lib Configure Grab 306a6f92,
  Merge Errors 2369e859, the `.icd` **2ea8512c57d734e76b02e91ced996d08 (start = end)**, the old wrapper d30c29b1 and old A90 /
  A150 / B150 / BOBS150 / harness, the old outputs `out_p64/p64p2/*`, the original main VI 2a78e17c, motor_limits, motor_gate,
  every `background VIs` file. The failed cycle's `md5_p64p2_*.json` untouched. New outputs: `md5_p64p2r1_end_outputs.json`.
- **Motors**: no `motor_gate` verb, no stage / PI / ASI command, no driver, no product VI was run by this session. Camera used in
  조립 for the 30 s check and the fresh open (both allowed by HOLD-5, `user_notes.md:5`).

## 10. Files
- New scripts (copies; the old ones unchanged): `p64p2r1_build.py` (parts w / copies / run / wcold), `p64p2r1_fresh.py`,
  `p64p2r1_tidy.py`, `p64p2r1_peek.py` (read-only JSON printer). State `p64p2r1_state.json`. Logs `p64p2r1_build_w.log`
  (runs 1-2), `p64p2r1_build_copies.log`, `p64p2r1_build_run.log` (+ their `.json`). md5: `md5_p64p2r1_start.json/.txt`,
  `md5_p64p2r1_end.json/.txt`, `md5_p64p2r1_end_outputs.json`.
- Data: `out_p64/p64p2_r1/rate150_frames.txt`, `configgrab_rate150_check.txt`, `fresh_open.json`.
- Edited: `lean_md5.py` (`--r1`, `--r1new`). Not edited: `tools/hooks/**`, `tools/motor_gate.py`, `motor_limits.json`,
  `CLAUDE.md`, `gscript.py`, `p64p2_build.py`, `p64p2_fresh.py`, any P-3 script, any pre-existing .vi. Nothing under
  `out_p64/p64p2/` written. Nothing committed. No bead / rig task queued.

## 11. Verdict
**p64p2 retry 1: PASS.** The review's two causes are fixed: (1) the new wrapper's Configure Grab takes its only `error in` from
Merge Errors, whose input 2 is the logger's `error out` (logger `error in` unwired) - proven cold from the saved file - so the
line is written before Configure Grab starts, and a camera error is still logged and still reaches the caller; (2) the
fresh-open readback 90.0009 and the `.icd` md5 before / after are on file in `out_p64/p64p2_r1/fresh_open.json`. The new 150 Hz
wrapper gave readback 150, exposure 1909 us, code 0; 4500 frames at 149.947 frames/s, 0 gaps, 0 Get Image2 errors; A150 /
B150 / BOBS150 / harness are byte copies with exactly one callee swap each, edges equal warm and cold, ExecState 1.
For the user: the ASI stage read X -52899 Y -41518 at this cycle's start (a third position, section 0) - please confirm it was
you before any rig / bead work.

RESULT {"p64p2": "PASS", "retry": 1, "rate_readback_hz": 150, "fps_30s": 149.947, "gaps_30s": 0, "fresh_open_hz": 90.0009, "md5": {"wrapper": "1419d4c679bd2e68d4962e0ff3ad39d1", "a150": "65b409a8c44f9140b26f70135fb89b99", "b150": "d3953cd6e96cc225ac0ed3f8ec3eaca0", "bobs150": "35e7e973c93d1aa56bd6344fab1db8c1", "harness": "75024d3f11e419b901184f3bcf9b2fdd"}, "minutes": 60}
