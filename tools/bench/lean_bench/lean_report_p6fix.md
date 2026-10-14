# Lean report - p6fix (P6's one-lap-old per-row values), 2026-10-13

One Opus session. Started 22:22 (`start_p6fix.txt`); the queue's motor session start log `motor_session_start_p6fix.log`
ends `SESSION START OK` (22:22:15, PI referenced, limits read back, quoted in section 8).

## 1. Graph facts (offline, BEFORE any LabVIEW run; from the stored bed graph `tools/bench/graph_ring_p6_20261012_212645.json`, md5 of the VI c2d9c13c)
Tools (new, read-only): `p6fix_graph.py`, `p6fix_graph2.py`, `p6fix_graph3.py`, `p6fix_graph4.py`.

Loop 1.2 = While #10170, body diagram d23166. Every Local read under it (`p6fix_graph2.py`):

| local | node | where | its wire goes to | ordered after the pick? before n2? |
|---|---|---|---|---|
| `Num` | #29720 | inside the pick loop While #16483 (d29699) | RingPickSlot_v0 #29719 `Num` -> `min slot`, `min Num` (= n1) | it IS the pick |
| `Num` | #30016 | inside the ONE frame d29869 of Flat Sequence #29721 | IndexArray #29879 [min slot] -> n2 (RingSeqCheck #29724 `n2`) | yes: the frame's inputs are `min slot` (#30724) and the tracker's `Bead is good? array out` (#30710), so this read is AFTER tracking |
| **`BufDiff`** | #30294 | d23166, no input | IndexArray #30300 [min slot] -> BuildArray #2626 (the row) | **NO - a no-input Local; runs whenever the iteration starts** |
| **`TransPos`** | #30116 | d23166, no input | IndexArray #30119 [min slot] -> BuildArray #2626 + LoopTunnel #9503 (For Loop #1359 -> `Magnet position` #28083) | **NO** |
| **`RotPos`** | #30215 | d23166, no input | IndexArray #30216 [min slot] -> BuildArray #2626 | **NO** |
| **`FrameIdx`** | #30239 | d23166, no input | IndexArray #30240 [min slot] -> `x` of the two Quotient&Remainder #10068 / #29240 (the `# FD points` / `# DT points` schedule) | **NO** |
| `Latest` | #30001 | d23166, no input | RingSeqCheck #29724 `Latest` | no (by design: used only for the jump target; not a per-slot value) |
| `autofocus reseed flag`, `StopAll` | - | - | control signals, not ring slots | - |

- The image is NOT read by a Local: IndexArray #29843 [min slot] takes the image-reference array from loop tunnel #30194
  (wired once into loop 1.2); the tracker #5058 reads the pixels by reference while it runs, i.e. between n1 and n2. That is why
  X/Y/Z were always right.
- The four IndexArrays' `index` input IS the pick's `min slot` (wire 30763 from loop tunnel #30179 of the pick loop), so the
  INDEXING happens after the pick; but the ARRAY each one indexes is the value its Local copied when the Local executed, and a
  Local with no input runs at the start of the iteration, i.e. while 1.2 is still waiting in the pick loop for the next frame.
  When 1.2 keeps up, frame k's slot then still holds frame k-20's values -> the row gets frame k-20's numbers.
- **The row (tra) is BuildArray #2626 = [BufDiff, TransPos, RotPos, x/y/z...]** (inputs in that order), so **column 0 is BufDiff**
  (column 1 TransPos, column 2 RotPos). P6-3 named the column-0 read `FrameIdx`; the graph shows FrameIdx feeds the FD/DT
  schedule (#10068/#29240), and BufDiff is the column-0 source. Both have the same read form, so both are fixed here.
- Writer side (loop 1.1, Flat Sequence #27509, frames left to right d27641 | d32464 | d27722, `p6fix_graph4.py`):
  frame 1 `Num(i) = -1` (#28902 read / #29175 write); frame 2 writes BufDiff (#29683), FrameIdx (#29380), RotPos (#29312),
  TransPos (#29095) by Replace Array Subset; frame 3 `Num(i) = BufNum` (#28037) and `Latest` (#29096). So all four per-slot
  arrays are inside the writer's seqlock; only the reader side is out of order.

## 2. Fix design and predictions (written BEFORE any LabVIEW edit)
### What changes (one structural edit, no new computation)
In a byte copy of the bed: Flat Sequence #29721 (today one frame, d29869 = the n2 read) gets ONE NEW FRAME BEFORE its frame
(`gscript.fs_add_frame(#29721, 0, after=False)`, the FlatSequence `Add Frame` method on the existing structure - no node copy).
The eight existing nodes Local BufDiff #30294, TransPos #30116, RotPos #30215, FrameIdx #30239 and their IndexArrays #30300,
#30119, #30216, #30240 are MOVED (OpMoveIn, `build_d1_v0.move_in`; the same nodes, nothing copied) into the new frame, and
every wire they had is re-made by `gscript.connect_term_uid` (Terminal.Connect Wire; LabVIEW makes the Flat Sequence tunnels):
- Local -> IndexArray `array` (4 wires, inside the new frame);
- pick loop tunnel #30179 `min slot` -> the 4 IndexArray `index` (in through ONE new input tunnel of the new frame);
- IndexArray `element` -> the same sinks as before (BuildArray #2626 x3, LoopTunnel #9503, Q&R #10068 `x`, #29240 `x`) through
  new output tunnels of the new frame.
Nothing else is touched: the pick, RingPickSlot/RingSeqCheck, the n2 frame, the discard/jump logic, loop 1.1 and every maths
node are unchanged (the user has not decided U8 latest-wins; the pick/discard behaviour stays as built).

### Why it is the order only (rule 1a)
The values come from the same slot arrays (the same Locals) at the same index (`min slot`) into the same sinks. Only WHEN the
Locals execute changes: the new frame cannot start before its input `min slot` exists (= after the pick, i.e. after n1), and the
n2 frame (now frame 1) cannot start before frame 0 has finished (Flat Sequence order) - so every per-slot value is read
**after n1 and before n2**, inside the seqlock, exactly like the image. No per-bead maths node, constant or wire of the tracker
changes; X/Y/Z cannot change.

### Gates for the build (`p6fix_build.py`, run once LabVIEW is allowed)
B1 copy md5 == c2d9c13c; B2 ExecState 1 before; B3 FS #29721 frames = [new, 29869] after the add; B4 the 8 nodes' owner = the
new frame (uids unchanged by the move); B5 every re-made wire lands; B6 ExecState 1 warm; B7 callee census unchanged;
B8 (gate, COLD, as P6-3 learned the warm read can mis-attribute calibration pass-through terminals) the wire-edge set of the
saved file with the new frame's tunnels collapsed to pass-throughs == the bed's cold edge set, i.e. **edge diff = exactly the
intended change** (the only new objects are the frame and its tunnels); cold ExecState 1; md5 unchanged by the cold load.
Then the test copies, all by `replace_object` callee swaps only (the P6-2 / P6-3 routes): replay copy (plan 170: #6810 ->
`replay_get_buff_image_paced60.vi`, #22692 -> `replay_get_image_cal.vi`), and from it the gap copy (get-buff call -> the P6-3 gap
wrapper a885a8fb) and the W40 / W100 copies (RingSeqCheck #29724 -> the P6-3 `RingSeqCheck_w40/_w100` files 581e2953 / 429cdc5d);
each: callee diff == the swap, cold edge diff 0 after the uid remap, ExecState 1 warm and cold.
If moving nodes into this big VI breaks it as copying did in P6-3, the gates stop before any save; the fallback is decided then.

### Predictions for the re-runs (S1 reference = P6-2's S1 leg `out_20261013d/run/replay_s1_20261013_142928`, 6321 rows)
- **P6-2 re-run (P6 leg, 150 s):** ~2540 rows (P6-2 had 2538), all X/Y/Z bit-identical to S1 row-for-row (0 lost); **column 0 ==
  S1's column 0 of the matched frame on EVERY row, rows 0-19 included** (before: 0/2538 own, rows 0-19 = -1); cal differs only in
  the date field; trans/rot identical on every post-init row. Init rows are facts: row 0's trans will now be the PI readback taken
  with frame 0 (no longer the array's initial 0.0); its value depends on how far the init move had gone and is not predicted.
- **GAP** (number 2k+1 for frame k): ~2537 rows, 0 lost, 0 damaged, strictly ordered; **column 0 == 2k+1 of the row's own frame
  on every row** (before: 2(k-20)+1 and -1); Total Lost Frames as before (+1 per frame).
- **W40:** ~2540 rows, 0 lost, 0 damaged; **column 0 == own number on every row** (before 0/2540).
- **W100 (overload):** ~1430 rows (P6-3: 1431), 0 damaged, strictly ordered, ~1090 lost in the same two gap classes (single
  skips while trailing, 19-frame jumps after a discard) because pick/discard are unchanged; **column 0 == own number on every
  row** (before 1430/1431, row 0 = -1). Discards may come out slightly differently because the four reads now run in parallel
  with tracking (a few us), not before the pick.
- The fix adds no wait: a frame that holds four Local reads and four IndexArrays costs microseconds per iteration.

## 3. Timeline
| time | step |
|---|---|
| 22:22 | start; read CLAUDE.md, task, lean_report.md, lean_report_p63.md, tools |
| 22:24-22:33 | graph facts offline (section 1); design + predictions written (section 2), before any LabVIEW run |
| 22:34 | md5 start snapshot `md5_p6fix_start.json` (24 files); `tools/bench/motor_session.json` present; LabVIEW 0 processes |
| 22:35-22:38 | build run 1 (`p6fix_build_run1.log`): frame added (d31550 first), 8 nodes moved; STOP at F7 (RBW removed the inner wire of loop tunnel #9503); nothing saved |
| 22:39-22:49 | build run 2 (`p6fix_build_run2.log`): F7 passes (relink planned); STOP in (c): loop tunnel #9503's outer terminal no longer exists; nothing saved |
| 22:49-23:03 | build run 3 (`p6fix_build_run3.log`): tunnel #9503 found GONE, its inner sink wired instead; all connects clean; STOP at F12 ExecState 0; nothing saved |
| ~23:05 | offline `p6fix_reach.py` on the bed graph: no same-iteration data path from the 4 moved reads to the tracker, the n2 frame or the pick (so not a structure cycle) |
| 23:04-23:19 | build run 4 (`p6fix_build_run4.log`): warm edge set with the new/gone tunnels collapsed == bed's EXACTLY (+0 / -0), but ExecState 0 and **8 new unwired Invoke nodes** = one junk Invoke per OpMoveIn call; (the Error List read crashed in my helper); nothing saved |
| 23:19:10-23:50:18 | **build run 5** (`p6fix_build_run5.log`, `p6fix_build.json`): + purge of the moves' junk Invokes (F6b). **85 pass / 0 fail**, 5 files saved, all cold-checked, H9 LabVIEW gone |
| (runs 1-4) | each failed run's unsaved work copy (md5 == bed c2d9c13c, never saved) removed by `p6fix_tidy.py --rm-unsaved` after an md5 check; LabVIEW 0 processes after every run |
| 23:50:25-00:38:53 | legs `p6fix_legs.py` (`p6fix_legs.log`, `out_p6fix/`): P62 23:51-00:03, GAP 00:03-00:15, W40 00:15-00:27, W100 00:27-00:39; **30/30 chain gates**; each leg 1 attempt, 15 picks, rc 0, LabVIEW gone after |
| 00:03-00:40 | offline per leg: `p6fix_align.py` (inside the chain), `p6fix_cmp.py` (P6-2's full compare, P62 leg), `p6fix_cal.py` |
| 00:40 | md5 end snapshot `md5_p6fix_end.json`: **EQUAL 24/24** with the start; `tasklist` LabVIEW 0 |
| ~00:50 | report finished (~148 min after the start; about $13 spent) |

## 4. The fixed VI and its test copies (all under `claudeDev\bench\lean\`, built by `p6fix_build.py` run 5, 85/0)
| file | md5 | what it is |
|---|---|---|
| **`D1_ring_p6fix_20261013_231910.vi`** | **3e847397eb120860adb2e868792345f7** | **the fixed P6** (byte copy of the bed c2d9c13c + the one edit below) |
| `D1_ring_p6fix_replay_20261013_231910.vi` | ae83d1aa088ba4546c65e039c6b4d16d | fixed P6 + plan 170's swaps: #6810 -> `replay_get_buff_image_paced60.vi` (new uid 31710), #22692 -> `replay_get_image_cal.vi` (new uid 6829) |
| `D1_ring_p6fix_replay_gap_20261013_231910.vi` | 2c499c7ba1a38c813d784efe7eacee76 | replay copy + #31710 -> P6-3's gap wrapper `gap_get_buff_image_paced60_20261013_161639.vi` (a885a8fb) |
| `D1_ring_p6fix_replay_w40_20261013_231910.vi` | db5e2e958201df1f1de928558aeff3ac | replay copy + RingSeqCheck #29724 -> P6-3's `RingSeqCheck_w40_20261013_161639.vi` (581e2953) |
| `D1_ring_p6fix_replay_w100_20261013_231910.vi` | ae8474bc8b33506c3659af407c2e7696 | replay copy + RingSeqCheck #29724 -> P6-3's `RingSeqCheck_w100_20261013_161639.vi` (429cdc5d) |

**The exact change in the fixed P6** (route: a structure method + node MOVES + Remove Bad Wires + Terminal.Connect Wire; no node
was copied into the VI, so P6-3's copy breakage did not arise):
1. Flat Sequence #29721 `Add Frame` before its only frame: frames are now **[d31550 (new), d29869 (n2 read, unchanged)]** (warm F4, cold CF).
2. The 8 nodes Local BufDiff #30294, TransPos #30116, RotPos #30215, FrameIdx #30239 and IndexArray #30300, #30119, #30216,
   #30240 moved into d31550 (uids kept; F6 warm, CO cold). OpMoveIn leaves one unwired junk Invoke per call: the 8 were deleted (F6b).
3. Wires re-made (all `broken False`, no op error): Local -> IndexArray `array` x4 (inside d31550); `min slot` (pick loop tunnel
   #30179) -> new input tunnel #28684 of d31550 -> the 4 `index`; each `element` -> a new output tunnel of d31550 (#30270, #31529,
   #31634, #31692) -> its old sinks (BuildArray #2626 x3, Q&R #10068 / #29240 `x`, `Magnet position` #28083).
4. One side effect, handled and gated: For Loop #1359's input tunnel #9503 (TransPos -> `Magnet position` #28083) lost both its
   wires in the move + Remove Bad Wires and LabVIEW deleted it; the TransPos element now reaches `Magnet position` through a NEW
   For Loop tunnel #31600 (it carries a scalar, which cannot be auto-indexed, so it is a plain tunnel like #9503).
- Gates: ExecState 1 warm (F12) and cold (C1); callee census unchanged (F13); **edge set with the new tunnels (and the gone #9503)
  collapsed as pass-throughs == the bed's, warm (F14, 2425 edges, +0/-0) and cold (CE, the bed read cold in a fresh LabVIEW:
  +0/-0)**; no new object other than the 6 tunnels (F12b); md5 unchanged by the cold load (C2). So every data edge is the bed's;
  only the owner (the new frame) of the 8 nodes changed, plus the tunnels the frame boundary needs.
- Test copies: each `replace_object` swap: callee diff == exactly the swap(s), wire-edge diff 0 after the uid remap (2431 edges),
  ExecState 1 warm and cold, cold edges == the source's cold edges, md5 unchanged by the cold load.
- Pins unchanged during the build (Stage H2/H3: bed, original, paced get-buff, replay cal, gap wrapper, both W subVIs, S1 replay
  copy, RingSeqCheck_v0); VI-Server refs opened 40 / closed 40 (H5); LabVIEW gone (H9).

## 5. Re-run numbers vs predictions
Reference A = P6-2's S1 leg `out_20261013d/run/replay_s1_20261013_142928` (6321 rows, every frame, lost 0). Alignment = X/Y/Z
(45 cells, f64 bits) per row (`p6fix_align.py` = `p63_align.align` + column 0 + trans/rot). Outputs `out_p6fix/align_<leg>.json`.
"Before" = the same tool on the unfixed P6's legs (P6-2 `out_20261013d`, P6-3 `out_p63`), files `base_*.json`.

### First PASS/FAIL item: column 0 = the row's OWN buffer number (U7/U9)
| condition | rows | **own-number rows / total** | before the fix | lost | damaged | order |
|---|---|---|---|---|---|---|
| normal load (P6-2 re-run) | 2537 | **2537 / 2537 PASS** | 0 / 2538 (rows 0-19 = -1, then k-20) | 0 | 0 | strictly increasing (X/Y/Z and col 0) |
| gapped source (number 2k+1) | 2537 | **2537 / 2537 PASS** (= 2k+1; also equal to the S1-gap leg's col 0 on all 2189 frames it has) | 0 / 2537 | 0 | 0 | strictly increasing |
| W40 (normal load + 40 ms) | 2540 | **2540 / 2540 PASS** | 0 / 2540 (P6-3 col-0 finding) | 0 | 0 | strictly increasing |
| W100 (overload) | 1432 | **1432 / 1432 PASS** | 1430 / 1431 (row 0 = -1) | 1097 | 0 | strictly increasing |

TransPos / RotPos (columns 1, 2), read with the same fix: post-init rows identical to S1's row of the SAME frame on every row of
every leg (P62 2436/2436, GAP 2436/2436, W40 2439/2439, W100 1363/1363; boundary = row after S1's last change, row 101 as in
P6-2's B3). Init rows (facts; a hardware readback, different between any two runs): row 0 trans is now the readback taken with
frame 0 - **P62 21.6943, GAP 21.6665, W40 21.6123, W100 21.6394 mm vs S1 21.6852** (before the fix: 0.0 = the array's initial value,
P6-2 B4); init trans range e.g. P62 [21.6943, 30.0055] mm, inside PI 0..39, 0 non-finite.

### P6-2 re-run (task step 4) - `out_p6fix/cmp_P62.json` (P6-2's compare_p6, unchanged, D = 20) + column 0 + `p6fix_cal.py`
| item | result | vs prediction |
|---|---|---|
| tra rows | 2537 (P6-2: 2538) | ~2540 predicted: as predicted |
| X/Y/Z bit-identical per row (B1 MATCH) | 2537 / 2537, 0 differ, no drop signature | as predicted |
| DISTINCT (C1, D = 20) | PASS on all common rows | - |
| **column 0 == S1's column 0 of the matched frame** | **2537 / 2537** (0 lost, so row k = frame k = number k) | as predicted |
| cal outside the date/time field | **identical**: `p6fix_cal.py` - walk consumed exactly on both; bytes before the field equal; bytes after the field equal (72 = 72) when each side is aligned at its own field end. compare_p6's B2 item says FAIL because it compares by absolute offset and this run's field is ONE byte longer (`오후 11:55:22` vs `오후 2:33:18`), which shifts the 34 following bytes - not a content difference | PASS (reported with the reason B2's raw flag fails) |
| trans/rot post-init (B3) | 0 differ | as predicted |
| init rows in PI range, rot finite (B6) | PASS (101 rows, trans 21.6943..30.0055) | - |
| B4 (init first+last equal S1, not a task item) | FAIL as in P6-2: first trans 21.6943 vs 21.6852 (two hardware readbacks); last rows equal | fact |
| run-dir files / leg files present (B5, B7) | PASS | - |
| Total Lost Frames / frame-counter delta | 0 / 2459 | as P6-2 (0 / 2460) |

### GAP / W40 / W100 (task step 5) vs predictions
- **GAP:** 2537 rows, X/Y/Z all matched (0 damaged), frames 0..2536 consecutive (0 lost), column 0 = 2k+1 on every row,
  Total Lost Frames 2526 and frame-counter delta 4918 (P6-3: 2526 / 4918). **As predicted.**
- **W40:** 2540 rows, all matched, 0 lost, column 0 own on every row. **As predicted.**
- **W100:** 1432 rows, all matched (0 damaged), strictly increasing, frames 0..2528 spanned, **1097 lost** = 356 single skips + 39
  jumps of 19 (P6-3: 1431 rows, 1090 lost = 311 x 1 + 41 x 19). Counted two independent ways: X/Y/Z alignment and the rows' own
  column-0 numbers - both 1097. Column 0 own on all 1432 rows. **As predicted** (~1430 rows, ~1090 lost, same two gap classes; the
  discard count, 39 vs 41, moved a little as predicted).

## 6. What failed and how I fixed it
1. **Build run 1 - F7:** after the moves, Remove Bad Wires also removed the INNER wire of For Loop tunnel #9503 (its outer source,
   IndexArray #30119, had been cut by the move). My gate allowed no lost non-member edge. Fix: a lost edge is allowed only when it
   starts at a tunnel that a moved node fed, and it is re-made afterwards (gated by the final edge-set compare).
2. **Build run 2 - exception:** the tunnel #9503 itself no longer existed (LabVIEW deletes a tunnel with no wires). Fix: when a
   sink's owner tunnel is gone, wire its own inner sink (`Magnet position`) instead; LabVIEW makes a new For Loop tunnel (#31600);
   the gone tunnel is collapsed as a pass-through on the BEFORE side of the edge gate.
3. **Build run 3 - ExecState 0** after clean connects. Offline reachability (`p6fix_reach.py`) ruled out a dependency cycle through
   the Flat Sequence. **Build run 4** read the state instead: warm edge set exactly the bed's, but **8 new unwired Invoke nodes**
   = one junk Invoke left by every OpMoveIn call (the project's own case-frame mover `gscript._move_into_frame` purges them; I had
   called the lower-level `build_d1_v0.move_in` without that purge). My Error List helper crashed (`'dict' object is not callable`);
   not pursued since the cause was found. Fix: `gscript._purge_new_invokes` after the moves (gate F6b). **Run 5: 85/0.**
4. **P6-2 compare B2 (cal) flag:** an absolute-offset compare after a one-byte-longer date field; resolved by the aligned compare
   (`p6fix_cal.py`), see section 5.
No leg failed or needed a second attempt.

## 7. Shared scripts edited
- `tools/bench/lean_bench/lean_md5.py`: added this task's read-only inputs (P6-3 gap wrapper, `RingSeqCheck_w40/_w100`, and the
  S1 reference leg's `cal001` / `tra001-000`) to the md5 list (24 files now).
- No other shared script was edited. New files (all `tools/bench/lean_bench/`): `p6fix_graph.py`, `p6fix_graph2.py`, `p6fix_graph3.py`,
  `p6fix_graph4.py`, `p6fix_reach.py` (offline graph readers), `p6fix_build.py`, `p6fix_legs.py`, `p6fix_align.py`, `p6fix_sum.py`,
  `p6fix_cmp.py`, `p6fix_cal.py`, `p6fix_tidy.py`; `p6fix_report_s4.md` is a superseded draft of section 4 (deleting it needs a
  shell `rm` that was not pre-approved; it can be removed).
- Not edited: `tools/hooks/**`, `tools/motor_gate.py`, `tools/bench/motor_limits.json`, `CLAUDE.md`, any recipe or driver
  (`p6fix_legs.py` calls `m8_legs.leg` / `keep_leg_files` unchanged). No `*_GUARD_OFF` was set. Nothing was committed.

## 8. Motor readback
- **The queue's session start** (`motor_session_start_p6fix.log`, 22:22:15), last lines:
  `LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0` · `PI  : PI controller limits match the file (TMN 0.0000 / TMX 39.0000, tol 0.001) (sender code=0)` ·
  `PI  : reference {"FRF": 1.0, "POS": -5e-05, "POS_BEFORE": 0.0, "RON": 1.0} -> REFERENCED at 0; verify OK (attempt 1/3)` ·
  `LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402` · `position after (must be unchanged): X=4559 Y=-37898` ·
  `ASI : ASI controller limits match the file (SL {'X': -3.8475, 'Y': -4.7744} / SU {'X': 0.1525, 'Y': -0.7744} mm, tol 0.001) (sender code=0)` ·
  `SESSION START OK` · `RESULT {"schema":"result-line/1","status":"PASS",...}`.
- **This session never ran the motor session verbs** (CLAUDE.md 1b; `p6fix_legs.py` has no session call and checked that
  `tools/bench/motor_session.json` existed before every leg: 4/4 PASS). **Disclosure for the judgement:** the replay leg itself
  (`diag_c104_leg.py` -> v5, unchanged since P6-2) runs its own built-in `motor_gate --session start` before LabVIEW opens and once
  after the run, i.e. it re-writes the SAME limits and repeats the gate's PI reference move; it never runs `--session end`, so the
  limits stayed set for the whole cycle. Its readback per leg (`out_p6fix/legs/<leg>_a1/m8_v5_replay_s1.json`):
  - before the run, all 4 legs: `exit=0; LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0; REFSTATE RON=1 FRF=1 POS=0 (GAP -5E-05) POS_BEFORE=0 ERR=0; SESSION START OK`
  - after the run, all 4 legs: `TMX?=39.0 from 'PRELIMITS TMN=0 TMX=39'; gate exit=0; LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0; REFSTATE RON=1 FRF=1 POS=0 (GAP/W100 -0.0001) POS_BEFORE=30 ERR=0 travelled=30.000`
    (the device init had moved the PI stage to 30 mm, inside 0..39).
  The release (`--session end`) is the queue's, after this session.

## 9. LabVIEW gone
- 00:40 `tasklist | grep -ic labview` -> `0` (after the last leg). Also verified after every build run (H9 run 5; 0 processes
  checked after runs 1-4), after every leg (T3 x4) and at the end of the leg chain (H).

## 10. Input md5s, start (22:34) vs end (00:40): EQUAL 24/24 (`md5_p6fix_start.json` / `md5_p6fix_end.json`)
| file | md5 |
|---|---|
| D1_ring_p6_20261012_212645.vi (bed) | c2d9c13cb40c0a5cab7433896d1df157 |
| D1_ring_p5_20261010_172913.vi / D1_ring_p5s01_20261009_124542.vi | 75773b0ded2a08586bb1a542ddda5af6 / 7f2582ae54dc5bc42c3df0bdf3c72d2e |
| D1_s1_copy.vi | 3e3d23cefd3a334001aa9d6156bf1aee |
| RingPickSlot_v0.vi / RingSeqCheck_v0.vi | 6fcf153f7b8fecda727f5dcf944faab9 / 0295a8d349a3b61151cd87797119b9b1 |
| replay\D1_s1_replay_20260925_075422.vi | 126f84975fca9f6124432a7e4decd0c8 |
| replay\replay_get_buff_image.vi / replay_get_image_cal.vi | 842ecad9a6674a5060ebb3d5522751a9 / afce0d04346fc58234d28bcc0fc42e55 |
| replay\replay_imaqdx_get_image_buf.vi / ..._paced60.vi | a89dafc1db03feef7b528f0dd4fcc692 / e40ec86722948812d155d6e4047a3ef9 |
| replay\replay_get_buff_image_paced60.vi | 59ec66b61f3518b049a3c532a8e65482 |
| bench\lean\D1_ring_p6_replay_20261013_135743.vi (P6-2 replay copy) | 09a23608c223a9a31ea6ca3638c1241c |
| bench\lean\gap_get_buff_image_paced60_20261013_161639.vi | a885a8fbc06351ab789d539af460a8d7 |
| bench\lean\RingSeqCheck_w40 / _w100_20261013_161639.vi | 581e2953c10b91439eedcaa18656b13f / 429cdc5dc55cbc861a609b9249c9347d |
| S1 reference leg cal001 / tra001-000 | 08fbaff8cf13155210f6fddd0ae1f009 / b3c7fcb2020abb4195d28ce2bedfb1a3 |
| original `Min_Track N beads V6_ParallelLoop.vi` | 2a78e17c449cacdaf5da389818526859 |
| G:\m8_replay_frames\frames_manifest.json | f9032ae5510e96126d9f53fc92f69cfe |
| p6_replay_frames_manifest.txt (worktree) | 73877ae04bd5386cac8b6aeed2d9716d |
| motor_limits.json / motor_gate.py | 65e9efae189ff0a911c9b109b19d0e69 / 0f06dd0dc937bf2959a336fb0ea23c7d |
| plans/plan_replay_swap_170.json | f3175f66039bf30a9c671caeac48582a |
No original was opened for writing; every LabVIEW save went to `claudeDev\bench\lean\` (the 5 files of section 4). The four
failed runs saved nothing; their byte-identical work copies were removed.

## 11. Verdict
- **p6fix: PASS.** One structural edit - the four per-slot Local reads (BufDiff = column 0, TransPos, RotPos, FrameIdx) and their
  IndexArrays moved into a new first frame of the n2 Flat Sequence, so they run after the pick (n1) and before n2 - with every data
  edge identical to the bed's (warm and cold) and no maths node touched.
- **Buffer-number accuracy (first item), per condition: P6-2 2537/2537, gap 2537/2537, W40 2540/2540, W100 (overload)
  1432/1432** - every saved row now carries its OWN frame's buffer number (before: 0/2538, 0/2537, 0/2540, 1430/1431).
  TransPos/RotPos follow the same frame (post-init identical on every row; row 0 trans now a real readback instead of 0.0).
- **X/Y/Z bit-identical per row: 10046/10046** over the four legs (P62 2537, GAP 2537, W40 2540, W100 1432), 0 damaged, strictly
  ordered; cal identical outside the date field; pick/discard behaviour unchanged (W100 gap classes 1 and 19 as in P6-3).
- Not decided here (unchanged by design): U8 latest-wins - under overload the ring still trails at the oldest slot between discards.

RESULT {"p6fix": "PASS", "col0_own": {"p62": "2537/2537", "gap": "2537/2537", "w40": "2540/2540", "w100": "1432/1432"}, "xyz": "10046/10046", "minutes": 148}
