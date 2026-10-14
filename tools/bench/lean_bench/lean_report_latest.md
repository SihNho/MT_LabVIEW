# Lean report - latest RETRY 2 (latest-wins U8/U13: per-pick lag under W100, measured), 2026-10-14

One Opus session, started 03:26 (task `queue/running/latest.md`, retry 2, the last one the queue allows). Nothing was built.

## 0. Start condition and user notes
- `lean_report_p6fix.md:254` ends `RESULT {"p6fix": "PASS", ...}` -> started.
- `user_notes.md` has ONE note (2026-10-13 23:1x "넣어주자": do not edit inside the big P6 VI; copy a small subVI and swap only
  the call's callee). It contains no refusal of a second retry and no acceptance of "pick-rule test + end-lag estimate".
  So steps 4-5 are done. The task text does not contradict the note: this retry builds nothing and uses retry 1's observer,
  which already follows the callee-swap route.

## 1. Graph facts (offline, before any LabVIEW run)
- **Pick rule and observer (cited, unchanged):** fail1 section 1 (`lean_report_latest_fail1.md:8-33`): loop 1.2's pick loop calls
  the pick subVI once per poll, with `Num` = a fresh read of the 20 per-slot buffer numbers (a slot being written holds -1) and
  `last` = loop 1.2's shift register. `RingPickSlot_latest` picks the LARGEST Num > last. fail2 section 1
  (`lean_report_latest_fail2.md:8-22`): in the W100 observer copy, call #31367 -> `RingPickSlot_latestobs` (new uid 31207). The
  observer logs one line per found=True call: `Num[0..19], last, picked Num, picked slot, ms tick`.
- **Where column 0 (`BufDiff`) comes from (open item b).** I read the stored bed graph `tools/bench/graph_ring_p6_20261012_212645.json`
  with the new offline tool `latest3_bufdiff.py` (walks upstream from a node):
  - Loop 1.1 frame 2 writes `BufDiff` with Local #29683 <- Replace Array Subset #29396 (`index` = slot = count mod 20, Q&R #27373).
    Its `new element` comes through Flat Sequence tunnel #29566 <- case tunnel #29584 <- **Subtract #5119 `x - y`**:
    - `x` = **get-buff call #6810 `current image number`** (in the replay copies this call is `replay_get_buff_image_paced60.vi`).
    - `y` = loop tunnel #3363 <- **IMAQdx Property node #250 `LastBufferNumber`** on diagram d686, OUTSIDE loop 1.1. So it is
      read ONCE, before the loop starts. The same value also initialises `Buffer to extract` (left shift register #5351 -> #6810).
  - Loop 1.1 frame 3 writes `Num` with Local #28037 <- Replace Array Subset #29407 <- Select #10579 (`f` = the same #6810
    `current image number` via tunnel #28429; `t` = constant #28257 on an image-copy error) - the same value goes to `Latest`.
  - So **BufDiff = Num - LastBufferNumber(read once at start)**, and **Num - column 0 is one constant per run**. The first frame
    the loop asks for is buffer `LastBufferNumber` (#5351), so the constant is the first frame's buffer number. In the cut run it
    equals the first logged picked Num, **20642**, and row 0's column 0 = 0 (section 4).
- **What happens to a picked frame after the pick (open item c).** Loop 1.2 does not write the row itself:
  - Case #30726 (frames d30914/d30922), selector tunnel #30897 <- RingSeqCheck #29724 `valid`. In the `valid` frame it runs
    **Enqueue Element #30756** (row = BuildArray #2626) and the row counter (#31004 -> +1 #31078 -> right shift register #30996).
  - Loop 1.3 (While #23041, d23405) runs **Dequeue Element #31262** -> save subVI #376 and counts what it saves (#31666 -> +1
    #31697). It stops when that count == Local `records final (1.2 to 1.7)` (#12169 -> Equal? #12170).
  - `records final` is written ONLY by Local #31213, outside loop 1.2, from loop 1.2's right shift register #30996, i.e. the
    final number of rows loop 1.2 ENQUEUED.
  - **Release Queue #31266** runs only after loop 1.3 has ended (queue wire #31347 -> #31266; no force-destroy wired).
  - By this STRUCTURE, rows saved == rows enqueued == loop 1.2 iterations with `valid` True. A picked frame with no row was
    then never enqueued, i.e. `valid` was False in that iteration.
  - **Limit (found after the leg):** the stored graph does not hold constant VALUES (it has no value for the save counter's
    start #31674 or the dequeue timeout #31448; `latest3_bufdiff.py --obj`). So an off-by-one at the save loop's end condition
    cannot be ruled out offline. Section 7 has the measured end.
  - The leg stops gracefully: the harness writes `stop (end)` / `stop (end) 2` = True over VI Server, with no abort, and the VI
    is idle after 1.0 s (`out_latest/legs/W100_a1/m8_v5_replay_s1.json:159`).

## 2. U32 decode and the 6 build gates (offline, `latest3_offline.py gates` -> `out_latest2/latest3_gates.json`)
- **Stated decode:** the observer's Build Array came out U32 (I32 Num/last/picked/slot plus the U32 Tick Count). A logged value
  v >= 2^31 is read as **v - 2^32**. This is lossless: I32 -> U32 keeps the bits, buffer numbers are < 2^31, and the only
  negative value in the ring is the -1 marker.
- **"6 FAIL as recorded, 6/6 equal after the stated decode."** The build record `latestobs_build.json` gates are pass 96 / fail 6:
  warm and cold vectors 5, 9 and 10, each a log line holding a -1 written as 4294967295. Re-checked against fail1's Python
  reference (`latest_build.py:35-43`, copied):
  - The 6 recorded failures are exactly the 6 raw mismatches. **All 6 are equal after the decode.**
  - All 20 output triples are equal to the reference.
  - Lines per vector are right (1 on found=True, 0 otherwise).
  - The moved test log `out_latest2/picklog_functest_20261014_025316.txt` (14 lines) is equal after the decode.
- The build's recorded RESULT FAIL stays recorded. **Decision, in writing, made here before the leg:** the 3 saved files are
  used. The failures are the U32 representation of -1 only; the observer's outputs and line count are right on every vector,
  and its log is read with the decode above. (Retry 1 ran the leg without writing this down; that was review item a.)

## 3. Cut run of retry 1 (supplementary: **LabVIEW force-closed, not the acceptance run**)
- Run dir `out_latest2/run/replay_s1_20261014_030804`. The leg itself ran to the end: the log was last written at 03:14:41 and
  LabVIEW was force-closed at 03:17. The session ended before any post-processing.
- `out_latest2/picklog_w100.txt` was moved to **`out_latest2/picklog_w100_cut_20261014_0308.txt`** (1473 lines, 214924 bytes) by
  `latest3_offline.py move-cut`, so the new leg starts from an empty file.
- Ran `p6fix_align.py` (unchanged, mode `same`, through `latest3_offline.py run`) -> `out_latest2/align_W100OBS_cut.json`, plus the
  per-pick analysis -> `out_latest2/latest3_cut.json`:
  - rows 1472; **own number 1472/1472**; X/Y/Z matched 1472/1472; 0 damaged; strictly increasing.
  - span 0..2540; **lost 1069** (all 1-frame gaps); TransPos/RotPos post-init 0 differ.
  - lag at the pick (ring max - picked Num): **0 on all 1473 lines**.
  - unread: 1 x 403, 2 x 1070.
  - **lag at save (next line's ring max - picked Num): 1 x 402, 2 x 1070**, mean 1.727.
  - the slot holds the picked Num on every line; tick step 102..118 ms, mean 104.2.
  - **GPT's numbers checked: all equal** (1472/1472 own number, lost 1069, lag at pick 0 x 1473, lag to next pick 1 x 402 / 2 x 1070).
  - in-write (-1 slots): 0 on 1462 lines. The 11 other lines are the first ones, while the ring was still filling (19, 18, 16, ...,
    2 never-written slots). After the fill, no line saw a slot being written (the writer's seqlock window is short).
- **Constant join:** log picked Num - 20642 == column 0 for log lines 0..1471, in order, one-to-one (0 mismatches). One extra pick
  is left: **line 1472, picked 23184 = 2542, slot 2, no row**.
- **The unsaved last pick (item c), cut run:**
  - It was taken 104 ms after the previous pick (the median step, so a normal iteration).
  - Its lag at the pick is 0; its slot holds it.
  - The tra file was last modified 0.30 s after the log's last line, so the VI ended within a few iterations.
  - So it was picked in loop 1.2's final iteration, and its row is missing at the very end of the run (section 7).

## 4. Predictions (written BEFORE the LabVIEW run)
W100, 150 s, 15 picks, `p6fix_legs.py` unchanged, mode `same`, test copy `D1_ring_p6latestobs_replay_w100_20261014_025316.vi`:
| quantity | prediction |
|---|---|
| rows | 1440-1500 (+-3 % vs 1472 is not a change) |
| log lines | rows + 0..1; I predict **rows + 1** (the final iteration's pick is logged but not enqueued, as in the cut run) |
| lag at the pick (decoded ring max - picked Num) | **0 on every line** |
| unread per pick | 1 (~27 %) or 2 (~73 %), never >= 3 |
| in-write per pick | 0 or 1 after the ring has filled (the first <= 19 lines count never-written slots) |
| lag at save (next line's ring max - picked Num) | 1..2, mean ~1.7 |
| log picked Num - constant == column 0 | in order, one-to-one on every row; constant = first logged picked Num, row 0 col 0 = 0 |
| own-number rows / total | all |
| X/Y/Z bit-identical vs S1 | all |
| damaged / order | 0 / strictly increasing |
| lost | only 1-frame gaps, ~1050-1080, max step 2 |
| P62 / GAP / W40 / fail1 W100 (offline from `out_latest2/recompute_fail1.json`, `align_fail1_*.json`) | equal to fail1's accepted numbers: 2537/2537, 2538/2538, 2540/2540, 1472/1472; X/Y/Z all; lost 0/0/0/1069 |

(Sections 0-4 were written before the leg started. After the leg I changed only two passages, both marked: the "Limit" bullet
in section 1, and the last bullet of section 3, which had claimed "valid False" too firmly. The predictions were not changed.)

## 5. Timeline
| time | step |
|---|---|
| 03:26 | start. Read CLAUDE.md, the task, user_notes (one note, no refusal/acceptance), p6fix RESULT PASS, fail1/fail2 reports, the review and its round-1 files, `latestobs_build.json` |
| 03:28 | `lean_md5.py` +3 files (retry 1's saved files) -> `md5_latest3_start.json`: **132 files**, all 9 input pins equal (fail1's 6 + 9371c64b, 9504e0cf, e5810aec); the 129 shared with `md5_latest_start.json` unchanged |
| 03:28-03:31 | graph facts (`latest3_bufdiff.py`); U32 gate re-check (`latest3_offline.py gates`); cut log moved; cut run aligned and analysed |
| 03:32 | `tools/bench/motor_session.json` present; `tasklist` LabVIEW 0; report sections 0-4 written (predictions first) |
| **03:33:19** | **`BGRUN START 2026-10-14 03:33:19 limit 30.0 min: py -u tools/bench/lean_bench/p6fix_legs.py --out-root ...\out_latest2 --leg W100OBS=...\D1_ring_p6latestobs_replay_w100_20261014_025316.vi::9371c64b2fc32957bb430b48b4060ace::same --run-s 150 --picks 15`** (`latest3_legs.log`) |
| 03:33:21 | VISA precheck ok; run dir `replay_s1_20261014_033411` |
| 03:33-03:45 | the session blocked on foreground checks of the bgrun log (until-loop on `BGRUN END`); no reply was ended while the job ran |
| **03:45:23** | **`BGRUN END rc=0 after 724s`**; chain gates 9/9 PASS (H0, S, P1, V1, T3 LabVIEW gone after, T1 rc 0, T2 15 picks, P2 md5 unchanged, H LabVIEW gone at end); 1 attempt |
| 03:45-03:47 | `tasklist` LabVIEW 0; `latest3_offline.py run` on the new log + `align_W100OBS.json` (written by the leg chain) -> `out_latest2/latest3_new.json`; md5 end `md5_latest3_end.json`: **EQUAL 132/132** |
| 03:48 | report finished (~22 min, about $5); `tasklist` LabVIEW 0 |

## 6. The VIs (nothing built, nothing saved; the 9 inputs, read-only)
| file (`claudeDev\bench\lean\`) | md5 (start == end) | role |
|---|---|---|
| `RingPickSlot_latest_20261014_010104.vi` | 8fc2ec267b3919402124f23a40f9ffae | fail1's latest-wins pick subVI |
| `D1_ring_p6latest_20261014_010104.vi` | 15c664e3eed1c580e05b13e42c86566f | fail1's P6 with latest-wins (product candidate) |
| `D1_ring_p6latest_replay_20261014_010104.vi` / `_gap_` / `_w40_` / `_w100_` | d615e096... / f6566203... / 0eb42f73... / 04e54006... | fail1's test copies (their runs are re-computed here, not re-run) |
| `PickLog_latestobs_20261014_025316.vi` | e5810aecfc6f78aa1469c6061946b5b9 | retry 1's logger |
| `RingPickSlot_latestobs_20261014_025316.vi` | 9504e0cffe372cd6ad35ab6842ec089d | retry 1's observer = RingPickSlot_latest + a logging branch |
| **`D1_ring_p6latestobs_replay_w100_20261014_025316.vi`** | **9371c64b2fc32957bb430b48b4060ace** | **the leg's VI**: fail1's W100 copy with call #31367 -> the observer (callee swap only) |

## 7. Numbers vs predictions
### P62 / GAP / W40 / fail1 W100 (fail1's runs, re-computed offline; `out_latest2/recompute_fail1.json`, `align_fail1_*.json`, all present -> not re-run)
| condition | rows | own number | X/Y/Z matched | damaged | order | lost | vs fail1 accepted |
|---|---|---|---|---|---|---|---|
| P62 | 2537 | 2537/2537 | 2537 | 0 | strictly increasing | 0 | equal |
| GAP | 2538 | 2538/2538 | 2538 | 0 | strictly increasing | 0 | equal |
| W40 | 2540 | 2540/2540 | 2540 | 0 | strictly increasing | 0 | equal |
| W100 (fail1) | 1472 | 1472/1472 | 1472 | 0 | strictly increasing | 1069 (all 1-frame) | equal |
TransPos/RotPos post-init rows differ on 0 rows in all four.

### W100 side by side
| | fail1 W100 (no observer) | cut run (retry 1, force-closed, supplementary) | **new observer run (acceptance)** | prediction |
|---|---|---|---|---|
| run dir | `out_latest/run/replay_s1_20261014_020903` | `out_latest2/run/replay_s1_20261014_030804` | **`out_latest2/run/replay_s1_20261014_033411`** | |
| rows | 1472 | 1472 | **1474** | 1440-1500 |
| **own number** | 1472/1472 | 1472/1472 | **1474/1474** | all |
| X/Y/Z bit-identical vs S1 | 1472/1472 | 1472/1472 | **1474/1474** | all |
| damaged / order | 0 / strictly increasing | 0 / strictly increasing | **0 / strictly increasing** | 0 / strictly |
| span / lost | 0..2540 / 1069 | 0..2540 / 1069 | **0..2541 / 1068** | ~1050-1080 |
| gap pattern / max step | 1069 x 1 / 2 | 1069 x 1 / 2 | **1068 x 1 / 2** (steps: 1 x 405, 2 x 1068) | 1-frame only / 2 |
| TransPos/RotPos post-init differ | 0 | 0 | **0** (1415 rows) | - |
| pick log lines | (no log) | 1473 | **1475** | rows + 0..1 |
| **lag at the pick** (ring max - picked Num) | - | 0 x 1473 | **0 x 1475** | 0 on every line |
| unread per pick | - | 1 x 403, 2 x 1070 | **1 x 406 (27.5 %), 2 x 1069 (72.5 %)**, never >= 3 | 1 ~27 % / 2 ~73 % |
| in-write per pick | - | 0 x 1462; 11 fill lines | **0 x 1464; the first 11 lines count never-written slots (19, 18, 16, 14, 13, 11, 9, 7, 6, 4, 2)** | 0/1 after fill |
| slot holds the picked Num | - | all | **all 1475** | - |
| **lag at save** (next line's ring max - picked Num) | - | 1 x 402, 2 x 1070, mean 1.727 | **1 x 405, 2 x 1069, mean 1.725, max 2** | 1..2, ~1.7 |
| pick spacing (ms tick) | - | mean 104.2, 102..118 | **mean 104.1, 102..108** | - |
| constant (picked Num - col 0) | - | 20642 = first picked | **20896 = first picked**, row 0 col 0 = 0 | first picked |
| join: picked - constant == col 0 | - | lines 0..1471 == rows, in order, 0 mismatches | **lines 0..1473 == rows 0..1473, in order, 0 mismatches** | one-to-one |
| unsaved picks | - | 1: the last (23184 = 2542) | **1: the last (23439 = 2543)** | 0..1 |
| frame counter at stop (`stop_run1` detail) | 23431 | (json not kept) | **23439** | - |
| frames-counter delta | 2463 | - | 2464 | - |

All new-run quantities are inside the predictions. The observer did not change the result: same checks pass, same gap pattern
as fail1 (only 1-frame gaps, max step 2), and rows 1474 vs 1472 (+0.14 %).

### The per-pick lag, histogram (new run, all 1475 picks; `out_latest2/latest3_new.json` "per_pick")
| frames | lag at the pick | lag at save (1474 picks with a next line) | unread at the pick |
|---|---|---|---|
| 0 | **1475** | 0 | - |
| 1 | 0 | 405 | 406 |
| 2 | 0 | 1069 | 1069 |
| >= 3 | 0 | 0 | 0 |
- Lag at the pick = 0 on every pick. Loop 1.2 always takes the newest complete frame in the ring.
- Lag at save = 1-2 frames: the frames loop 1.1 wrote during one ~104 ms iteration of loop 1.2 (frame period ~59 ms). That is
  the overload cost; there is no backlog. Each later pick again starts at lag 0, dropping the 0-1 older unread frames
  (1069 dropped at the pick = the 1068 lost + the final pick's one).

### The constant (open item b) - closed
BufDiff = `current image number` - `LastBufferNumber`. The second term is read once by IMAQdx Property #250 before loop 1.1
(section 1), and is also the first buffer the loop requests. Measured:
- picked Num - column 0 is the same constant on every row of both runs: 20642 (cut) and 20896 (new).
- The constant = the first logged picked Num, and row 0's column 0 = 0.
- So column 0 (BufDiff) and the log's Num describe the same frame, one-to-one, in order.

### The unsaved last pick (open item c)
Both observer runs show the same thing:
- Exactly ONE pick has no row, and it is the LAST log line. Every earlier pick has its row, in order.
- It was taken at the normal spacing (104 ms after the previous pick) with lag 0.
- In the new run it IS the newest frame loop 1.1 ever wrote: the front-panel frame counter read at stop = **23439** =
  the picked Num.
- The stop is graceful (VI Server writes `stop (end)`, VI idle after 1.0 s, no abort). The tra file was last modified 0.30 s
  after the log's last line in both runs, i.e. the VI ended within ~3 iterations.

So: the final pick was taken in loop 1.2's final iteration, and its row did not reach the file before the end. It was not lost
to the pick rule, to a ring overwrite (no frame was written after it), or to a gap. No other picked frame is missing (all
1474 earlier picks have their row).

The exact place inside the stop path is **not determined**. By the graph's structure the save loop stops at loop 1.2's
enqueue count, which points to "not enqueued in the final iteration". But two constants whose values the stored graph does not
hold (save counter start #31674, dequeue timeout #31448) leave a save-end off-by-one possible. Either way, the effect is the
last frame of a run, at stop: <= 1 frame per run. I report it as a small open finding, not a data-accuracy defect: the saved
rows all carry their own number.

## 8. What failed and how it was fixed
- Nothing failed in this session. The leg ran once (1 attempt, rc 0, 9/9 gates).
- v5's own step `run1.L8` ("three `choose bandpass` panels", contract 3) reports 15 closed. It was the same in all of fail1's
  legs (`out_latest/legs/*/m8_v5_replay_s1.json:128-131`): it is the 15-pick replay's normal behaviour, and p6fix_legs does
  not gate on it.
- Retry 1's failures are handled: (a) the build's 6 FAIL lines are shown to be the U32 representation, and the decision to use
  the files is written in section 2 before the leg; (b) the 20642 basis is shown (sections 1 and 7); (c) the 1473-vs-1472 last
  pick is explained as far as the data and graph go (section 7). The SESSION RULE was kept: the session blocked on
  `BGRUN END` before doing anything else.
- Permission prompts refused a few compound shell commands; they were re-run as single commands or moved into the new scripts.
  No hook was routed around; no `*_GUARD_OFF` was set.

## 9. Shared scripts edited
- `tools/bench/lean_bench/lean_md5.py`: + retry 1's 3 saved files (PickLog / RingPickSlot_latestobs / the W100 observer copy)
  in the md5 list -> 38 pins + 94 `background VIs` files = 132.
- New (offline, read-only except the one rename): `latest3_bufdiff.py` (upstream walk / `--kids` / `--obj` on the stored
  graph) and `latest3_offline.py` (gates re-check, cut-log move, align + per-pick lag + constant join + last-pick facts; it
  imports `latest_picklag.py` and `p6fix_align.py` unchanged).
- Run unchanged: `p6fix_legs.py`, `p6fix_align.py`, `latest_picklag.py`, `p6fix_graph4.py`, `bgrun.py`.
- Not edited: `tools/hooks/**`, `tools/motor_gate.py`, `tools/bench/motor_limits.json`, `CLAUDE.md`. (`tools/gscript.py` shows
  as modified in git status from before this session; this session did not touch it.) Nothing committed.

## 10. Motor readback
- **The queue's session start** (`motor_session_start_latest.log`), last lines:
  - `PI  : PI controller limits match the file (TMN 0.0000 / TMX 39.0000, tol 0.001) (sender code=0)`
  - `PI  : reference {"FRF": 1.0, "POS": 0.0, "POS_BEFORE": 30.0, "RON": 1.0} -> REFERENCED at 0; verify OK (attempt 1/3)`
  - `LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402`
  - `position after (must be unchanged): X=4559 Y=-37898`
  - `ASI : ASI controller limits match the file (SL {'X': -3.8475, 'Y': -4.7744} / SU {'X': 0.1525, 'Y': -0.7744} mm, tol 0.001) (sender code=0)`
  - `SESSION START OK -> ...\tools\bench\motor_session.json`
  - `RESULT {"schema":"result-line/1","status":"PASS",...}`
- This session never ran the motor session verbs. `p6fix_legs.py` checked `motor_session.json` before the leg (gate S PASS),
  and the file was still present after (`session_json_after: true`).
- Same disclosure as fail1/p6fix: the replay leg's v5 runs its own built-in gate step before LabVIEW and a readback after.
  It re-writes the SAME limits and never runs `--session end`. This leg (`out_latest2/p6fix_legs.json`,
  `legs/W100OBS_a1/m8_v5_replay_s1.json:194`):
  - before: `POS?=1=0.00000 TMN?=1=0.00000 TMX?=1=39.00000 ERR?=0` · `LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0` ·
    `REFSTATE RON=1 FRF=1 POS=0 POS_BEFORE=0 ERR=0 travelled=0.000` · `SESSION START OK`
  - after: `TMX?=39.0 from 'PRELIMITS TMN=0 TMX=39'; gate exit=0; LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0; REFSTATE RON=1 FRF=1
    POS=-5E-05 POS_BEFORE=30 ERR=0 travelled=30.000` (the device init had moved the PI stage to 30 mm, inside 0..39).
- The release (`--session end`) is the queue's, after this session.

## 11. LabVIEW gone
`tasklist | grep -ic labview` -> `0`:
- at 03:32 (before the leg);
- inside the chain after the leg (gates T3 and H);
- at 03:45 and 03:46 after `BGRUN END`;
- again at the end of this report (03:47:58).

## 12. Input md5s, start (03:28) vs end (03:46): EQUAL 132/132
`py tools/bench/lean_bench/lean_md5.py --diff latest3_start latest3_end` -> `EQUAL 132 / 132`. The files are:
- the 29 old pins: the original `Min_Track N beads V6_ParallelLoop.vi` 2a78e17c, the bed c2d9c13c, the p6fix files,
  RingPickSlot_v0 / RingSeqCheck_v0, the replay files, the S1 reference cal/tra, manifests, motor_limits 65e9efae, motor_gate
  0f06dd0d, plan 170;
- the 9 inputs of section 6;
- all 94 files of `zz_LabView VI\background VIs\`.

The older `md5_latest_*` files were not overwritten. No VI was opened for writing and nothing was saved.

## 13. Verdict
- **latest: PASS.**
  - fail1's accepted numbers re-compute equal: P62 2537/2537, GAP 2538/2538, W40 2540/2540, W100 1472/1472, X/Y/Z all, lost
    0/0/0/1069.
  - The 6 build-gate failures are the U32 representation only: 6/6 equal after the stated decode.
  - The new W100 observer leg completed: BGRUN END rc 0, no force-close, LabVIEW gone. It gave own number 1474/1474,
    X/Y/Z 1474/1474, 0 damaged, strictly ordered, and only 1-frame gaps.
  - The log is matched one-to-one, in order, to the rows; the constant's basis was found in the graph and checked in the data.
  - **Per-pick lag at the pick was measured on every pick: 0 on all 1475.** Lag at save is 1-2 frames (mean 1.73).
  - Motor readback lines quoted; md5 132/132 equal.
- Limit, stated: the one unsaved pick per run is the final pick at stop (the newest frame, 23439 = the frame counter at
  stop). Its exact place in the stop path (not enqueued vs. save-loop end) is open, because two constant values are not in the
  stored graph.

RESULT {"latest": "PASS", "own_number": {"p62": "2537/2537", "gap": "2538/2538", "w40": "2540/2540", "w100_fail1": "1472/1472", "w100_obs": "1474/1474"}, "w100_lag": "per pick at pick: 0 frames on 1475/1475 picks (cut run 0 on 1473/1473); at save: 1 x 405, 2 x 1069, mean 1.73, max 2", "xyz": "w100_obs 1474/1474", "lost_w100_obs": 1068, "build_gates": "96/6 recorded; 6/6 equal after the U32 decode", "unsaved_picks": "1 per run, the final pick at stop (newest frame = frame counter 23439); mechanism open", "md5": "132/132 equal", "minutes": 22}
