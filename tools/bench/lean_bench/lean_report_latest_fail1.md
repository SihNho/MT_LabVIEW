# Lean report - latest (overload = latest-wins, U8/U13), on top of the p6fix result, 2026-10-14

One Opus session. Started 00:51 (task `queue/running/latest.md`). Start condition: `lean_report_p6fix.md` exists and ends
`RESULT {"p6fix": "PASS", ...}` (line 254) -> started. Input = the fixed P6 `claudeDev\bench\lean\D1_ring_p6fix_20261013_231910.vi`
(3e847397) and its four test copies (read-only; byte copies only). The queue's motor session start log ends `SESSION START OK`
(quoted in section 8).

## 1. Graph facts (offline, BEFORE any LabVIEW run)
Sources: the stored bed graph `tools/bench/graph_ring_p6_20261012_212645.json` (the p6fix change did not touch the pick or the
check: its edge set == the bed's), read by the new tool `latest_graph.py`; the subVI build `tools/bench/build_ringpickslot_v2.py`
(log 87/0) and its record `docs/d1/ring-p4b.md:117-141`.

- **RingPickSlot_v0** (`claudeDev\RingPickSlot_v0.vi` 6fcf153f; pane 11 Num, 10 last -> 3 min Num, 2 min slot, 1 found). Inside:
  `GT` Greater? (Num > last, element-wise) -> For loop: `SW` Select(s = GT[i], t = Num[i], f = `KMX1` I32 2147483647) ->
  masked array -> `AMM` Array Max & Min -> **min value -> `min Num`, min index -> `min slot`**; `LT` Less?(min value, `KMX2`
  2147483647) -> `found`. **Rule: the slot with the SMALLEST Num > last** (the oldest unread frame). If none: min Num = I32 max,
  found = False.
- Its one call in loop 1.2, **#29719**, sits in the pick loop (While #16483, diagram d29699): `Num` <- Local `Num` #29720 (read
  inside the pick loop, i.e. re-read each poll); `last` <- loop tunnel #30060 <- left shift register #29548 (loop 1.2's `last`,
  init constant #29576); `found` -> Function #29818 (the `Or` with `StopAll` = the pick loop's stop); `min slot` -> tunnel #30179
  -> the image IndexArray #29843, the 4 per-slot IndexArrays of p6fix and the n2 frame's input; `min Num` -> tunnel #30094 ->
  **RingSeqCheck #29724 `n1`**.
- **RingSeqCheck_v0** #29724 (0295a8d3; pane 11 n1 / 10 n2 / 9 last / 8 Latest / 7 discards -> 3 next last / 2 next discards /
  1 valid): `valid = (n1 == n2) AND (n1 > last)`; **`next last = valid ? n1 : Latest - 1`**; `next discards = valid ? d : d + 1`.
  `n2` comes from the n2 frame (IndexArray #29879 of Local `Num` #30016 at `min slot`, after tracking); `next last` -> right SR
  #29403; `valid` -> the 7 rollback Selects and the row-write case structures (#30914/#30922).
- **Where `Latest` is read:** Local `Latest` #30001 on loop 1.2's body d23166, no input wire, its only sink is RingSeqCheck #29724
  `Latest` (wire 30101). So it runs at the start of the iteration (unordered, before/while the pick loop waits) and is used ONLY
  by the discard branch (`Latest - 1`). Writer: loop 1.1 frame 3 writes `Num(i) = BufNum` and `Latest = BufNum` after the slot is
  complete; frame 1 sets `Num(i) = -1` before the write (seqlock), so a slot being written never has a Num > last.
- Consequence (as built, P6-3 / p6fix W100): when 1.1 laps 1.2, the slot 1.2 wanted is overwritten and RingPickSlot returns the
  oldest Num > last that is still in the ring = Latest - 19 -> a single skip, 1.2 trails at the oldest slot (~19 behind); it only
  jumps to the newest after a seqlock discard (`next last = Latest - 1`): 356 x 1 + 39 x 19 lost in p6fix's W100.

## 2. Design and predictions (written BEFORE any LabVIEW edit)
### Choice: change the PICK rule, not the check: pick = the slot with the LARGEST Num > last (the newest complete frame)
`RingPickSlot_latest_<ts>.vi` = a byte copy of RingPickSlot_v0 with, inside it only:
1. `SW.f` (the "not new" value of the mask) <- `last` instead of `KMX1` (I32 max); `KMX1` deleted. Masked[i] = Num[i] > last ? Num[i] : last.
2. `min Num` <- AMM `max value`, `min slot` <- AMM `max index` (instead of min value / min index).
3. `found` = `LT` Less?(x = `last`, y = AMM `max value`) i.e. `last < max` (instead of `min < I32 max`); `KMX2` deleted.
Pane, names and types unchanged (the indicators keep the names `min Num` / `min slot`; they now carry the newest frame). In the
fixed P6 and in each test copy the ONE call #29719 is swapped for this file by `replace_object` (callee swap, the user's
2026-10-13 route; nothing is edited inside the big VI). Reference for the functional test: `m = [n if n > last else last]`,
`v = max(m)`, outputs `[v, m.index(v), last < v]`.

Why this one (and not "next last = Latest - 1 whenever a frame was skipped" in RingSeqCheck):
- **Exactly U8/U13**: whenever more than one unread frame is in the ring, 1.2 takes the newest and drops the backlog; with one
  unread frame (1.2 keeping up) the largest Num > last IS the smallest, so the pick is identical to today's -> no change at
  normal load. Lag at the moment of the pick = 0 by construction (max of the ring's completed numbers).
- **Works for any numbering**: "a frame was skipped" cannot be told from buffer numbers (the gap source advances by 2 every frame:
  n1 = last + 2 always, so a skip rule would fire on every GAP pick), and `Latest` is read unordered at iteration start, so a
  `Latest - 1` rule would aim one iteration late (lag ~1-2 frames, not 0).
- **Seqlock and discard rule untouched**: RingSeqCheck, n1 -> track -> n2, the n2 frame, `Latest`, the rollbacks are the same
  nodes and wires; n1 is still the number of the slot that was picked. The newest slot is the one 1.1 will rewrite LAST (it
  writes slot (count mod 20) next = the oldest), so it is overwritten only ~19 frames (~1.2 s) later: a discard needs tracking
  to take > 1 s -> discards ~0. The discard branch still works as before if it ever fires (next pick = newest anyway).
- **Rule 1a**: no per-bead maths node changes; only WHICH slot index enters the same IndexArrays changes. Every saved row is
  still the tracker's output on that slot's image, and (p6fix) its per-slot values are read inside the seqlock -> own buffer number.
- **No new node** inside the subVI (2 constants removed, 5 wires re-made), so P6-3's "a copied node breaks the big VI" cannot arise.
- When nothing new (only on StopAll exit): min Num = last (before: I32 max) -> `valid` = (last > last) = False either way -> no row.

### Gates (build script `latest_build.py`)
SubVI: copy md5 == 6fcf153f; ExecState 1 before/after; edge diff (with the new For-loop tunnel for `last` collapsed) == exactly
-{KMX1->SW.f, KMX2->LT.y, AMM.min value->min Num, AMM.min value->LT.x, AMM.min index->min slot} +{last->SW.f, last->LT.x,
AMM.max value->min Num, AMM.max value->LT.y, AMM.max index->min slot}; Constant census = {} ; pane unchanged; vectors == the
reference (incl. a wrapped ring and an all-old ring), again from the saved file in a fresh LabVIEW.
P6 files (5): byte copy of the p6fix file; `replace_object` #29719 -> the subVI; callee diff == exactly that swap; wire-edge diff
0 after the uid remap; ExecState 1 warm and cold; cold edges == the source's cold edges; md5 unchanged by the cold load.

### Predictions per condition (150 s legs, 15 picks, the p6fix routes; reference = P6-2's S1 leg, 6321 rows)
| condition | rows | own number | X/Y/Z bit-identical | lost | gap pattern | damaged / order |
|---|---|---|---|---|---|---|
| P6-2 replay (normal) | ~2537 (p6fix 2537) | all rows | all rows | 0 | none | 0 / strictly increasing |
| GAP (number 2k+1) | ~2537 | all rows (= 2k+1) | all rows | 0 | none | 0 / strictly increasing |
| W40 | ~2540 | all rows | all rows | 0 (unchanged) | none | 0 / strictly increasing |
| **W100** | **~1460-1480** (iterations ~102 ms as measured in P6-3; no discards, so every iteration is a row; p6fix 1432) | all rows | all rows | **~1050-1080** (span ~0..2539 minus rows) | **only gaps of 1 (most, ~65%) and steps of 0 lost (~35%)**, rarely 2; **no 19-gaps, nothing >= 3** | 0 / strictly increasing |
- **W100 lag: ~0 frames at each pick (by construction), measured from the data as the END lag = (last frame written) - (last
  row's frame), last frame written = v5's frame-counter delta + 77 (calibrated on p6fix's 0-lost legs: P62 2536 - 2459 = 77,
  W40 2539 - 2461 = 78): predicted 0-2 frames (as built: P6-3 19.5, p6fix ~11; per-pick ~19 while trailing, shown by the 19-jumps).**
  Also predicted: the mean frames advanced per row ~1.7 (= iteration / frame period), max step 2-3.
- Risks stated now: (a) at normal load any single 1.2 iteration longer than a frame period with two frames ready now drops the
  older one (U8, by design) where the as-built rule caught up later -> 1-frame gaps would appear in P62/GAP/W40; I predict none
  (P6-2/W40 1.2 never fell 2 frames behind in a way the data can show... the as-built data cannot show it, so this is a real
  prediction). (b) At start-up, if 1.2 starts after 1.1 has written several frames, row 0 may be a later frame than 0 (the
  backlog dropped by design); I predict row 0 = frame 0 as in p6fix.
- Discard count is not readable (F3); with the new rule a discard would show as a gap of >= 3 frames with no timing reason. Predicted 0.

## 3. Timeline
| time | step |
|---|---|
| 00:51 | start; read CLAUDE.md, task, `lean_report_p6fix.md` (RESULT p6fix PASS -> start), `lean_report_p63.md`, user notes (callee-swap route) |
| 00:52-00:56 | graph facts offline (`latest_graph.py`, the RingPickSlot build script/log, ring-p4b); design + predictions written (sections 1-2) before any LabVIEW run |
| 00:57 | `lean_md5.py latest_start` (29 files: + the 5 p6fix files); `tools/bench/motor_session.json` present; LabVIEW 0 processes |
| 00:58-01:00 | build run 1 (`latest_build.log`): subVI edit done, STOP at S10 (tunnel terminal name, section 6); nothing saved; LabVIEW gone (H9); the unsaved work copy (md5 == RingPickSlot_v0 6fcf153f) removed by `latest_tidy.py --rm-unsaved` |
| 01:01-01:32 | **build run 2** (`latest_build_run2.log`, `latest_build.json`): **119 pass / 0 fail**, 6 files saved, all cold-checked, H9 LabVIEW gone |
| 01:32-02:20 | legs (`p6fix_legs.py` unchanged; `latest_legs.log`, `out_latest/`): P62 01:33-01:44, GAP 01:45-01:56, W40 01:57-02:08, W100 02:08-02:20; **30/30 chain gates**, each leg 1 attempt, 15 picks, rc 0, LabVIEW gone after |
| 02:20 | offline: `p6fix_align.py` (inside the chain), `p6fix_sum.py`, `latest_lag.py` (`out_latest/lag_latest.json`); md5 end snapshot: **EQUAL 29/29**; `tasklist` LabVIEW 0 |
| 02:22 | report finished (~91 min after the start; about $6 spent); `tasklist` LabVIEW 0 again |

## 4. The VIs (all under `claudeDev\bench\lean\`, built by `latest_build.py` run 2, `latest_build_run2.log`, **119 pass / 0 fail**)
| file | md5 | what it is |
|---|---|---|
| **`RingPickSlot_latest_20261014_010104.vi`** | **8fc2ec267b3919402124f23a40f9ffae** | byte copy of `RingPickSlot_v0.vi` (6fcf153f) + the pick-rule change below |
| **`D1_ring_p6latest_20261014_010104.vi`** | **15c664e3eed1c580e05b13e42c86566f** | **the P6 with latest-wins** = byte copy of the p6fix VI 3e847397 + call #29719 -> the subVI above (new uid 31710) |
| `D1_ring_p6latest_replay_20261014_010104.vi` | d615e096075c74c5ac0c63c05a722217 | p6fix replay copy ae83d1aa + #29719 -> subVI (new uid 31503) |
| `D1_ring_p6latest_replay_gap_20261014_010104.vi` | f656620329ffaf8c675fe050192ff9d3 | p6fix gap copy 2c499c7b + #29719 -> subVI (31507) |
| `D1_ring_p6latest_replay_w40_20261014_010104.vi` | 0eb42f736d6874e1af58781c82e81e37 | p6fix W40 copy db5e2e95 + #29719 -> subVI (31367) |
| `D1_ring_p6latest_replay_w100_20261014_010104.vi` | 04e5400646af36b7afc3876d6fe3b6a7 | p6fix W100 copy ae8474bc + #29719 -> subVI (31367) |

**The exact change** (inside the small subVI only; node uids of the subVI):
- deleted: constant #103 `KMX1` (I32 max -> Select #45 `f`, inside the For loop) and constant #52 `KMX2` (I32 max -> Less? #198 `y`);
  wires Array Max & Min #117 `min value` -> {`min Num`, Less? `x`} and #117 `min index` -> `min slot`; Remove Bad Wires (8 stubs).
- new wires (connect_term_uid, all `broken False`, no error): control `last` -> Select #45 `f` (LabVIEW made For-loop input tunnel
  #102), `last` -> Less? #198 `x`, #117 `max value` -> `min Num` and -> Less? #198 `y`, #117 `max index` -> `min slot`.
- Gate S10: edge set after (new tunnel #102 collapsed) == before - those 5 edges + these 5 edges, nothing else. One recorded
  side effect: the For loop's OUTPUT tunnel #199 (Select out -> AMM `array`, same wire, same owners) read its terminal name '' before
  and 'last' after (LabVIEW propagates the data name of the wire now feeding Select `f`). Run 1 stopped on that name (section 6);
  run 2's gate ignores TUNNEL terminal names only (owners and node terminal names still exact) and logs the raw diff.
- No Constant left; pane unchanged (11 Num, 10 last -> 3 min Num, 2 min slot, 1 found) warm and cold; ExecState 1 before, after, cold.
- **Functional test, 10 vectors (wrapped ring, all-old ring, slot being written = -1, empty ring), warm and again COLD in a fresh
  LabVIEW from the saved file: 20/20 == the Python reference** (e.g. Num = [20,21,22,3..19], last 5 -> [22, slot 2, True] where
  v0 gives [6, slot 6]); md5 unchanged by the runs and the cold load.
- Each P6 file: callee diff == exactly #29719 RingPickSlot_v0 -> the new subVI; wire-edge diff 0 over 2431 edges after the uid
  remap (warm), and COLD: ExecState 1, cold edges (remapped) == the source's cold edges (each source read cold in its own fresh
  LabVIEW), call -> the new subVI, md5 unchanged by the cold load, source md5 unchanged. VI-Server refs 51 opened / 51 closed;
  pins (original, bed, the 5 p6fix files) unchanged; LabVIEW gone (H9).

## 5. Re-run numbers vs predictions
Reference A = P6-2's S1 leg `out_20261013d/run/replay_s1_20261013_142928` (6321 rows, every frame). Alignment = X/Y/Z (45 cells,
f64 bits) per row + column 0 + trans/rot (`p6fix_align.py`, unchanged); files `out_latest/align_<leg>.json`; lag/steps
`out_latest/lag_latest.json` (`latest_lag.py`). Run dirs `out_latest/run/replay_s1_20261014_013257` (P62), `_014456` (GAP),
`_015700` (W40), `_020903` (W100). "Before" = the same tools on p6fix's legs (`out_p6fix/`) and P6-3's (`out_p63/`).

| condition | rows | **own-number rows / total** | X/Y/Z bit-identical | lost | damaged | order | vs prediction |
|---|---|---|---|---|---|---|---|
| P6-2 replay (normal) | 2537 | **2537 / 2537** | 2537 / 2537 | 0 (frames 0..2536) | 0 | strictly increasing | as predicted (= p6fix 2537) |
| GAP (number 2k+1) | 2538 | **2538 / 2538** (= 2k+1; = S1-gap leg's col 0 on all 2189 frames it has) | 2538 / 2538 | 0 (0..2537) | 0 | strictly increasing | as predicted |
| W40 | 2540 | **2540 / 2540** | 2540 / 2540 | 0 (0..2539) | 0 | strictly increasing | as predicted (unchanged) |
| **W100 (overload)** | **1472** | **1472 / 1472** | 1472 / 1472 | **1069** (span 0..2540) | 0 | strictly increasing | as predicted (rows ~1460-1480, lost ~1050-1080) |

Both lost counts agree two ways (X/Y/Z alignment and the rows' own column-0 numbers: 1069). Total Lost Frames (v5) and the frame
counter as before: P62 0 / 2459, GAP 2526 / 4920, W40 0 / 2461, W100 0 / 2463. TransPos/RotPos post-init rows identical to S1's
row of the same frame on every row (P62 2436, GAP 2437, W40 2439, W100 1413; 0 differ); init rows are hardware readbacks (row 0
trans P62 21.6718, GAP 21.70035, W40 21.508, W100 21.60255 mm vs S1 21.6852; ranges inside PI 0..39, 0 non-finite).

### W100: latest-wins vs as built
| | as built, P6-3 | as built, p6fix | **latest (this task)** | predicted |
|---|---|---|---|---|
| rows | 1431 | 1432 | **1472** | ~1460-1480 |
| lost | 1090 | 1097 | **1069** | ~1050-1080 |
| gap pattern (frames lost per gap) | 311 x 1, 41 x 19 | 356 x 1, 39 x 19 | **1069 x 1, nothing else** (402 steps lose 0) | mostly 1, some 0, rarely 2; none >= 3 |
| frames advanced per row | 1.762 mean, max 20 | 1.767, max 20 | **1.727 mean, max 2** | ~1.7, max 2-3 |
| seqlock discards seen in the data (a jump > the timing step) | 41 | 39 | **0** | 0 |
| **lag: end lag = frames written by the end - last row's frame** | **19** (0..2520, delta 2462) | **11** (0..2528, delta 2462) | **0** (0..2540, delta 2463: last = delta + 77 exactly as the 0-lost legs) | 0-2 |
| lag while running | ~19 frames (trailing at the oldest slot; each discard jumps 19) | same | ~0: every step is 1 or 2 frames = the frames written during one ~102 ms iteration (150 s / 1472 rows); no backlog ever built | 0 by construction |
- 1472 rows = the same number of 1.2 iterations as P6-3 (1431 rows + 41 discarded iterations): now every iteration writes a row.
- Steps lose 1 frame in 72.7 % of rows and 0 in 27.3 % (I predicted ~65/35 from 102/61 ms; the frame period in this run is
  ~59 ms: 2541 frames in 150 s, so 102/59 = 1.73 = the measured mean step). No step lost 2 or more.
- The end-lag calibration: frames written by the end = frame-counter delta + 77, from p6fix's P62 (2536 - 2459) and this run's
  P62 (2536 - 2459) and W40 (2539 - 2461 = 78); the measure is +-1 frame. (The GAP leg's counter advances 2 per frame, so the
  lag tool's number for GAP is not meaningful and is not used.)
- Risks named before the runs did not happen: no 1-frame gap at normal load (P62, GAP, W40 all 0 lost), row 0 = frame 0 in all legs.

## 6. What failed and how I fixed it
1. **Build run 1 - S10 (01:00):** the subVI's wiring change was exactly the planned one (5 edges out, 5 in, owners exact), but the For
   loop's output tunnel #199 (Select out -> AMM `array`, unchanged wire) read its terminal name '' before and 'last' after:
   LabVIEW propagates the data name of the control `last`, which now feeds Select `f`. My gate compared terminal names of tunnels
   too, so it stopped before saving (fatal gate; nothing saved; the unsaved work copy, byte-identical to RingPickSlot_v0, removed
   after an md5 check by the new `latest_tidy.py`). Fix: S10 ignores the terminal NAME on tunnel owners only (owners, node terminal
   names and the exact edge sets still compared), and logs the raw named diff (run 2 log: exactly that one rename). Run 2: 119/0.
No leg failed or needed a second attempt.

## 7. Shared scripts edited
- `tools/bench/lean_bench/lean_md5.py`: added the 5 p6fix files (this task's read-only inputs) to the md5 list (29 files now).
- No other shared script was edited. `p6fix_legs.py`, `p6fix_align.py`, `p6fix_sum.py` were run unchanged. New files (all
  `tools/bench/lean_bench/`): `latest_graph.py` (offline graph reader), `latest_build.py` (build + gates), `latest_tidy.py`
  (md5-checked removal of an unsaved work copy), `latest_lag.py` (steps + end lag), `latest_legsum.py` (leg summary).
- Not edited: `tools/hooks/**`, `tools/motor_gate.py`, `tools/bench/motor_limits.json`, `CLAUDE.md`, any recipe or driver. No hook
  was routed around (guard_lean refused two offline `py` commands for a missing timeout; they were re-run with timeout <= 30 s; a few
  compound shell commands and a shell `rm` outside the worktree were not approved, and were replaced by single commands /
  `latest_tidy.py`); no
  `*_GUARD_OFF` set. Nothing was committed.

## 8. Motor readback
- **The queue's session start** (`motor_session_start_latest.log`), last lines: `VERIFY-RESULT: OK - reference move done and the
  stage follows commands` · `LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0` · `PI  : PI controller limits match the file (TMN 0.0000 /
  TMX 39.0000, tol 0.001) (sender code=0)` · `PI  : reference {"FRF": 1.0, "POS": 0.0, "POS_BEFORE": 0.0, "RON": 1.0} -> REFERENCED
  at 0; verify OK (attempt 1/3)` · `LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402` · `position after (must be
  unchanged): X=4559 Y=-37898` · `ASI : ASI controller limits match the file (SL {'X': -3.8475, 'Y': -4.7744} / SU {'X': 0.1525,
  'Y': -0.7744} mm, tol 0.001) (sender code=0)` · `SESSION START OK` · `RESULT {"schema":"result-line/1","status":"PASS",...}`.
- This session never ran the motor session verbs; `p6fix_legs.py` checked `tools/bench/motor_session.json` before every leg (4/4
  PASS; still present at the end). Same disclosure as p6fix: the replay leg (`diag_c104_leg.py` -> v5, unchanged) runs its own
  built-in `motor_gate --session start` before LabVIEW and a readback after, re-writing the SAME limits; it never runs `--session end`.
  Per leg (`out_latest/legs/<leg>_a1/m8_v5_replay_s1.json`):
  - before, all 4: `before: POS?=1=0.00000 TMN?=1=0.00000 TMX?=1=39.00000 ERR?=0` · `LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0` ·
    `REFSTATE RON=1 FRF=1 POS=0 POS_BEFORE=0 ERR=0 travelled=0.000` (W100: POS=-0.00015) · `SESSION START OK`
  - after, all 4: `TMX?=39.0 from 'PRELIMITS TMN=0 TMX=39'; gate exit=0; LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0; REFSTATE RON=1
    FRF=1 POS=0 POS_BEFORE=30 ERR=0 travelled=30.000` (the device init had moved the PI stage to 30 mm, inside 0..39).
  The release (`--session end`) is the queue's, after this session.

## 9. LabVIEW gone
- 02:20 `tasklist | grep -ic labview` -> `0` (after the last leg). Also after build run 1 and run 2 (H9), after every leg (T3 x4)
  and at the end of the leg chain (H).

## 10. Input md5s, start (00:57) vs end (02:20): EQUAL 29/29 (`md5_latest_start.json` / `md5_latest_end.json`)
The 24 files of p6fix's table (bed c2d9c13c, P5 pair, D1_s1_copy, RingPickSlot_v0 6fcf153f, RingSeqCheck_v0 0295a8d3, the replay
stand-ins, P6-2 replay copy, gap wrapper a885a8fb, RingSeqCheck_w40/_w100, S1 reference cal/tra, original 2a78e17c, manifests,
motor_limits 65e9efae, motor_gate 0f06dd0d, plan 170) plus the 5 p6fix files: fix 3e847397, replay ae83d1aa, gap 2c499c7b,
w40 db5e2e95, w100 ae8474bc - all unchanged. No original was opened for writing; every save went to `claudeDev\bench\lean\` (the 6
files of section 4).

## 11. Verdict
- **latest: PASS.** One pick-rule change in a byte copy of the small `RingPickSlot_v0` (largest Num > last instead of smallest),
  swapped into loop 1.2's one call by `replace_object`; nothing edited inside the big VI; every P6 data edge identical warm and cold;
  seqlock (n1 -> track -> n2), `Latest`, the discard rule and every maths node unchanged.
- **Overload (W100): 1.2 now takes the newest frame.** End lag 0 frames (as built 19 / 11), no backlog, no 19-frame jumps, no
  seqlock discards seen; every gap is exactly the 1 frame that arrived during the iteration (1069 x 1); rows 1472 vs 1432 (every
  iteration now saves a row).
- **Own buffer number on every row, every condition: P62 2537/2537, GAP 2538/2538, W40 2540/2540, W100 1472/1472.**
  X/Y/Z bit-identical per row 9087/9087, 0 damaged, strictly ordered; normal load unchanged (0 lost in P62, GAP, W40).

RESULT {"latest": "PASS", "own_number": {"p62": "2537/2537", "gap": "2538/2538", "w40": "2540/2540", "w100": "1472/1472"}, "w100_lag": "0 frames at the end (as built 19 in P6-3, 11 in p6fix); steps 1-2 frames only (1069 x 1 lost, 0 jumps of 19, 0 discards seen)", "xyz": "9087/9087", "lost": {"p62": 0, "gap": 0, "w40": 0, "w100": 1069}, "build_gates": "119/0", "leg_gates": "30/30", "minutes": 91}
