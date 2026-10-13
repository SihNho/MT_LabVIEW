# Lean report - P6-3 (the two ring tests: frame-number gap; overload with a test delay in loop 1.2), 2026-10-13

One Opus session. Started 15:45:20 (`start_p63.txt`).

## 1. Predictions (written 16:30, BEFORE any LabVIEW run of this session)

### What I read first (facts the predictions rest on)
- Ring design PD238(c)/(e) (`docs/d1-loop12-17-split-plan.md:2256-2258`), PD246(c) (`:2408-2425`), RingSeqCheck
  (`docs/d1/ring-p4b.md:140-141`), user rules U8/U9/U11/U13 (`docs/user-rules.md:24-38`), STATUS.md:131 (2026-09-28 overload
  order: no corruption > latest-wins > sequential fallback), the debate that created the two tests
  (`tools/bench/debate/plan-overall-02/relay/round_04_claude.md:5-7`, `round_05_gpt.md:11-12`).
- Loop 1.1 writes, per NEW buffer number (selector #26879 `x = y?` against the previous BufNum), slot i = (new-frame
  count) mod 20: `Num(i) = -1` -> image copy + TransPos/RotPos/FrameIdx -> `Num(i) = BufNum`, `Latest = BufNum`.
  So the ring's `Num` holds the CAMERA buffer number; the slot index does not.
- Loop 1.2: `last` in a shift register; RingPickSlot = slot with the smallest `Num > last`; RingSeqCheck: `n1` before and
  `n2` after tracking, valid = n1 == n2 AND n1 > last; next last = valid ? n1 : Latest - 1; discards += 1 when invalid.
  The discard counter is NOT readable by a leg (F3, `tools/bench/p6_replay_facts.md`), and a frame overwritten before 1.2
  picks it is skipped without being counted (F3).
- Replay frame source (`tools/bench/diag_replay_standins.py:1-12`): the buf stand-in returns image = paths[k mod 10044],
  k = its own call counter, and `Buffer Number Out = Buffer Number In`. The paced copy waits 60 ms per call
  (P6-2: 2460 frame-counter steps in 150 s = one frame per ~61 ms). The get-buff wrapper (`get buff image-lost frames.vi`
  layout, `docs/wiki/subvi/get buff image-lost frames.json`): BN Out (wire 99) -> `current image number` and `#76 x-y`
  (y input; x = `Buffer to extract`) -> `#65 x = 0?` -> `Missed frames?`. Loop 1.1 asks for `Buffer to extract` =
  previous number + 1 (#1978, F2).
- P6-2 data (re-read now by my new offline tool `p63_align.py`, `p63_align_p62.json`): the 2538 P6 rows match S1 rows
  0..2537 one-to-one by X/Y/Z bits (S1 has no repeated X/Y/Z key in 6321 rows, so each P6 row names exactly one input frame).
  New fact: P6's tra column 0 = (matched S1 frame index) - 20 for rows 20..2537 and -1 for rows 0..19; S1's column 0 =
  its frame index. So P6's column 0 carries the FrameIdx of the slot's PREVIOUS occupant (one ring lap old). It is a second,
  independent frame label per row, which I use below as a cross-check. (This one-lap lag is also what B4 of P6-2 saw in
  trans row 0. It is a finding about P6 itself; it is not a P6-3 item, and I change nothing for it.)

### Test copies I will make (all under `claudeDev\bench\lean\`, none touches the maths)
- **T-gap:** a byte copy of `replay\replay_get_buff_image_paced60.vi` (59ec66b6) with ONE Increment node put on the wire
  from the stand-in's `Buffer Number Out` to its two sinks (`current image number`, `#76 x-y` y). The frame source then
  returns number r+1 when r is asked: every delivered frame skips exactly one buffer number (1, 3, 5, ...). Images are
  unchanged (paths[k], k = call counter), so the delivered images are the same frames as in P6-2. Then a P6 replay copy made
  by the same recipe as P6-2 (`stage_replay_swap.py`, byte copy of the bed c2d9c13c) whose #6810 calls this gap wrapper.
- **T-load:** two byte copies of the P6 replay copy 09a23608, each with ONE `Wait (ms)` node on loop 1.2's body diagram
  (While #10170), its input fed by a constant, its output unwired: W = 40 ms (normal load) and W = 100 ms (overload). No
  wire touches any existing node, so data flow and maths are unchanged; only the 1.2 iteration time becomes >= W.

### T-gap predictions
- G1 rows: ~2538 rows in 150 s (as P6-2). Every row matches an S1 row of P6-2's S1 leg bit-for-bit (0 damaged), the matched
  S1 indices are consecutive from 0 (0 lost frames in the data), the same as P6-2: the number gap changes no image and
  RingPickSlot's "smallest Num > last" finds the next frame whatever its number.
- G2 every pick is the "n1 > last + 1" case; it is valid (valid needs n1 > last only), so no discard and no jump.
- G3 column 0 = matched index - 20 (FrameIdx is the loop-1.1 new-frame count, not the buffer number).
- G4 counter: loop 1.1's `Total Lost Frames` (the original's own nodes, unchanged in P6) is non-zero and grows by about one per
  frame; my best guess is (frames delivered while it counts) ~ the frame-counter delta (~2460). The exact formula
  (#3162 x-y in Case #3191) is the original's, not read by me before the run, so G4 is a weak prediction.
  - G4 refined ~16:05 (build running, before ANY leg; offline read of `docs/wiki/subvi/D1_s1_copy.json` by
    `p63_wires.py`): Total Lost Frames = (#2347: `current image number` - `LastBufferNumber`) - i, with i = loop 1.1's
    iteration count (wire 3268, the same wire that feeds `#376 'frame index'`). With the gap wrapper the number advances by
    2 per frame while i advances by 1, so Total Lost Frames = i + a constant: it rises by exactly 1 per loop-1.1 frame
    and its end value is about the number of 1.1 iterations at the moment v5 reads it (same order as the frame-counter end
    value minus its start). In P6 the same nodes sit in loop 1.1, so the same value is expected.
- What "as the original would" means here: the original (S1) tracks every delivered frame whatever its number and records
  the skipped numbers only in `Total Lost Frames`; P6 must do the same (rows = every delivered frame, in order, unchanged
  numbers). Since the gap changes no image, P6-2's S1 leg is the reference for the rows. I will run an S1 leg with the gap
  wrapper only if time allows (it would show S1's counter on the same gapped numbers).

### T-load predictions
Timing model: 1.1 writes one frame per P ~ 61 ms; 1.2 needs T_track (a few ms .. ~20 ms) per pick and, with the test node, at
least W per iteration.
- **W = 40 (normal load, W < P):** 1.2 is never behind by more than 1 frame. Rows ~2538, all matched, consecutive (0 lost),
  0 damaged, no gap of any size. The discard path does not fire (nothing is overwritten before or during its read).
- **W = 100 (overload, W/P ~ 1.64 frames written per 1.2 iteration):** per the ring design (my reading of RingPickSlot +
  RingSeqCheck), the run has cycles:
  1. after a jump, 1.2 takes consecutive frames (gap 0) while its backlog grows by ~0.64 frame per iteration;
  2. after ~30 iterations the backlog reaches the 20 slots: the next wanted frame is overwritten before it is picked, and the
     pick takes the OLDEST slot still in the ring: a skip of 1 (sometimes 2) frames, not counted by any counter (F3);
     1.2 then trails ~19 frames behind the newest;
  3. while trailing, the picked (oldest) slot is rewritten by 1.1 DURING tracking with probability ~T_track / P per
     iteration: then n2 != n1 -> DISCARD (row not written), last = Latest - 1, and the next pick is the newest frame: a jump.
     The lost run in a jump is >= 20 frames (the discarded frame q and everything up to Latest >= q + 20).
  Predicted numbers (150 s run): rows ~ 150 s / 0.1 s ~ 1500 minus the discards (~1460); frames written in that time ~2460-2540;
  lost frames ~1000-1100. Gap sizes: many 1-2 (trailing skips) and some >= 20 (one per discard, ~20-60 of them). Rows damaged:
  0. Order: strictly increasing, no repeated frame.
  - "Exact loss count" (my definition, stated before the run): lost = (last matched index - first matched index + 1) - rows,
    counted from the X/Y/Z alignment against S1, AND the same number counted from column 0 (FrameIdx + 20) independently;
    both must agree to the frame, every row must be in strictly increasing frame order, and every gap must be of a
    class the design explains (skip 1-2 while trailing, or >= 20 after a discard). A gap of 3..19 frames is NOT explained
    by the design and would be a FAIL of the prediction. The number of >= 20 gaps is the number of discards seen in the data.
  - If no gap >= 20 appears, the discard path never fired: "load" is NOT-VERIFIED for discards (not PASS).
  - An a-priori exact count from timing alone is not possible (both loops run on their own clocks; frame-to-frame jitter
    decides which iteration sees the overwrite). The numeric ranges above are the timing model's, reported against the data.

### Amendment ~16:20 (after build runs 1-3 and the diagnostic, BEFORE any leg; the text above is left as written)
- The Wait could not be put directly on loop 1.2's diagram: copying ANY node into the P6 copy (OpPrimCopyNested) re-sourced
  wires in the calibration flat sequence and left the VI broken (section 4). New T-load copies: loop 1.2's ONE call of
  `RingSeqCheck_v0.vi` is swapped (replace_object, the P6-2 route) for a byte copy of RingSeqCheck_v0 that contains ONE
  extra `Wait (ms)` fed by a panel control (default W), output unwired. The check's arithmetic is unchanged; its outputs
  leave after max(arithmetic, W). The delay is then IN SERIES after n2 is read, not in parallel with tracking:
  1.2 iteration ~ W + T_pick + T_track.
- Effect on the numbers: W = 40 still < P (61 ms) only if T_pick + T_track < ~20 ms. In P6-2 1.2 kept up with 61 ms frames
  with no backlog, but its own time per pick was not measured. So for W = 40 I keep "0 lost" as the prediction, with the
  note that a 1.2 time above ~21 ms would make even W = 40 an overload (then gaps appear and that is a wrong prediction,
  reported as such). W = 100: iteration ~110-120 ms -> ~1.8-2 frames written per iteration; rows ~1250-1400; lost ~1100-1300.
  The gap classes (1-2 while trailing, >= 20 after a discard, nothing in 3..19) are unchanged, because n1 -> track -> n2 is
  unchanged and the delay sits after n2.

## 2. Timeline (clock time; bgrun stamps are the reference)
| time | step |
|---|---|
| 15:45:20 | start; read CLAUDE.md, task_p63.md, lean_report.md, ring design PD238/PD246, ring-p4b, user rules, STATUS:131, debate rounds 3-5, p6_replay_facts |
| ~15:55 | offline tools: `p63_align.py` (self-test inside), checked on P6-2's data (2538/2538 aligned, col-0 fact); predictions written (section 1) |
| ~15:58 | md5 snapshot `md5_p63_start.json` (19 files) |
| 15:59:32 | `motor_gate.py --session start` OK (`p63_motor_start.log`) |
| 15:59:46 - 16:03 | build run 1 (`p63_build_run1.log`): STOP at L3 (warm edge diff, see section 4); nothing saved; LabVIEW gone (H9) |
| 16:04 - 16:07 | build run 2 (`p63_build_run2.log`): STOP at L6, ExecState 0 after Wait + constant; nothing saved |
| 16:08 - 16:10 | build run 3 (`p63_build_run3.log`): STOP at L6, ExecState 0 after Wait + panel control; nothing saved |
| 16:11 - 16:15 | diagnostic `p63_diag_wait.py` on a scratch copy (deleted): read stable without edit; Wait alone -> ExecState 0 and 16 calibration-area edges changed |
| 16:15 - 16:16 | build run 4 (`p63_build_run4.log`): RingSeqCheck route; crashed on the nested-only control verb (TopLevelDiagram owner); nothing saved |
| 16:16:39 - 16:30 | **build run 5** (`p63_build.log`, `p63_build.json`): **73 pass / 0 fail**, 7 files saved, cold-checked, refs 50/50, LabVIEW gone |
| (each run) | the unsaved Stage work copies of runs 1-4 (byte-identical to the input or to RingSeqCheck_v0) were removed by `p63_tidy.py --rm-unsaved` after an md5 check |
| 16:30:37 - 17:07:39 | legs `p63_legs.py` GAP (16:31-16:43), W40 (16:44-16:55), W100 (16:56-17:07); 26/26 chain gates (`p63_legs.log`, `out_p63/`) |
| ~17:08 | offline: alignment re-run with the final `p63_align.py` (`align2_*.json`); graph reads of the `Latest` and `FrameIdx` locals (`p63_wires.py`) |
| 17:09:27 - 17:13 | S1-gap build `p63_build_s1gap.py` 16/0 (`p63_build_s1gap.log`) |
| 17:13:45 - 17:25:20 | S1-gap leg (`p63_legs_s1gap.log`, `out_p63_s1gap/`), 10/10 chain gates |
| 17:25:34 | final `motor_gate.py --session end` OK (`p63_motor_end.log`) |
| 17:25:40 | `tasklist | grep -ic labview` = 0; md5 end snapshot `md5_p63_end.json`: EQUAL 19/19 with the start |
| 17:27 | report finished (~102 min after the start; about $17 spent) |

## 3. Test copies (all under `claudeDev\bench\lean\`, built by `tools/bench/lean_bench/p63_build.py` run 5)
| file | md5 | what changed | why no maths is touched |
|---|---|---|---|
| `gap_get_buff_image_paced60_20261013_161639.vi` | a885a8fbc06351ab789d539af460a8d7 | byte copy of `replay\replay_get_buff_image_paced60.vi` (59ec66b6); wire w99 (stand-in `Buffer Number Out` -> `current image number` + #76 `y`) deleted; ONE Increment #210 (copied from the paced stand-in's own Increment #222) inserted: BN Out -> Inc.x, Inc.x+1 -> both old sinks | it is the frame SOURCE (the camera stand-in's wrapper), not P6; images unchanged (paths[k]); only the reported buffer number is +1, i.e. every delivered frame skips one number |
| `D1_ring_p6_replay_gap_20261013_161639.vi` | a8ac64ccddd2e835574d669548d7fa76 | byte copy of the P6 replay copy 09a23608; call #31533 (P6-2's get-buff swap) -> the gap wrapper (new uid 31381) by `replace_object` | callee swap only; cold wire-edge set (uid remapped) == the input's (CE gap_p6) |
| `RingSeqCheck_w100_20261013_161639.vi` / `RingSeqCheck_w40_...` | 429cdc5dc55cbc861a609b9249c9347d / 581e2953c10b91439eedcaa18656b13f | byte copy of `RingSeqCheck_v0.vi` (0295a8d3) + ONE `Wait (ms)` #251 whose input is a panel control `milliseconds to wait` (default 100 / 40, read back cold), output unwired | the subVI's edge set after == before + exactly the control -> Wait edge (L5); the check's arithmetic is untouched; the Wait only delays the subVI's completion |
| `D1_ring_p6_replay_w100_20261013_161639.vi` / `..._w40_...` | 22c05b42347bb85ddbbe6146d4a8be0b / 29b84557b98cda853539f988fcc4f69f | byte copy of 09a23608; loop 1.2's ONE RingSeqCheck call #29724 (on d23166 of While #10170) -> the W copy (new uid 31381) | callee swap only; warm AND cold wire-edge diff 0 over 2426 edges after the uid remap (L13, CE) |
Every copy: ExecState 1 warm and cold; md5 unchanged by the cold load. The input 09a23608 and every pin (original, bed, S1 replay copy,
paced pair, RingSeqCheck_v0) unchanged (H2/H3).

## 4. What failed and how I fixed it
1. **Build run 1 - warm edge gate L3 failed.** After the Wait (ms) + constant went onto loop 1.2's diagram, the wire-edge set
   differed in 16 edges of the calibration area (`New Image`, `Cosine bandpass for Hilbert`, `2-sided cal image`, `Low/High
   bandpass`, `forget radius` pass-through tunnels), besides the intended edge. The script stopped before saving.
2. **Build run 2 - ExecState 0** after the same edit (the warm diff was then only recorded); stopped before saving. The constant
   verb (`stagekit.const_row` -> OpCreateConstOnTerm_v0) also returned uid 20140 with no new node in the census.
3. **Build run 3 - ExecState 0** again with a panel control instead of the constant (`create_control_nested`, by uid).
4. **Diagnostic `p63_diag_wait.py`** (scratch copy, never saved, deleted): two reads with no edit are identical; the Wait (ms)
   copy ALONE (OpPrimCopyNested, `create_primitive_nested`) makes ExecState 0 (now, +5 s, +20 s) and produces the same 16-edge
   change. So copying a node INTO this P6 copy re-sources wires in the calibration flat sequence: a tool/LabVIEW behaviour
   on this large VI, not a reader artefact. (The diagnostic's Error List read failed in my helper on a missing dict key; I did not
   pursue it.) Not fixed; avoided.
5. **Fix = route change:** the delay goes into a byte copy of the small `RingSeqCheck_v0.vi`, and the P6 copy only gets a callee
   swap (`replace_object`, the route already proven by P6-2 with a 0-edge diff). Run 4 crashed because `create_control_nested`
   refuses a top-level owner; run 5 uses the top-level verb `create_control` (as `diag_replay_standins.py` does) + `make_default`.
   Run 5: 73/0.
Consequence for the test: the delay is in series after n2 (inside the check), not in parallel with tracking (amendment in section 1).

## 5. Results per test (data = `p63_align.py` against P6-2's S1 leg `out_20261013d/run/replay_s1_20261013_142928`, 6321 rows, no repeated X/Y/Z key)
Legs (`p63_legs.py`, `p63_legs.log`, outputs `out_p63/`): picks 15, 150 s, each in its own motor session, 26/26 chain gates PASS
(H0, then per leg: pin before/after, motor start/end readback, VISA precheck, rc 0, 15 picks registered, LabVIEW gone; H at end).
Alignment files: `out_p63/align_GAP.json`, `out_p63/align2_W40.json`, `out_p63/align2_W100.json` (the `align2_*` files come from
the final p63_align version, re-run offline after the legs).

| leg | VI (md5) | tra rows | matched (X/Y/Z bits) | damaged | order | S1 frames spanned | lost in span | gaps | Total Lost Frames (v5) | frame-counter delta | v5 failing |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GAP | ..._gap_ (a8ac64cc) | 2537 | 2537 | **0** | strictly increasing | 0..2536 | **0** | none | **2526** | 4918 | L6, L8 |
| W40 | ..._w40_ (29b84557) | 2540 | 2540 | **0** | strictly increasing | 0..2539 | **0** | none | 0 | 2462 | L8 |
| W100 | ..._w100_ (22c05b42) | 1431 | 1431 | **0** | strictly increasing | 0..2520 | **1090** | 352: 311 x 1 frame, 41 x 19 frames | 0 | 2462 | L8 |
(v5 L8 = its "== 3 panels" contract, which never applies at 15 picks, as in P6-2; L6 on GAP = the `choose bandpass` window took
more than 30 s to appear, a GUI timing item; all 15 picks registered.)

### T-gap vs prediction
- G1 (rows, 0 lost, 0 damaged, consecutive from frame 0): **as predicted.**
- G2 (no discard/jump): as predicted (no gap in the data).
- G4 (Total Lost Frames +1 per frame): **as predicted**: 2526 against 2537 rows; the frame-counter delta 4918 is ~2 per frame
  (the counter follows the buffer number, which now advances by 2).
- **G3 WRONG:** column 0 is NOT (index - 20). It is `2*(index-20) + 1`, i.e. the CAMERA BUFFER NUMBER of the frame that sat in the
  same slot one ring lap earlier (the gap wrapper gives frame k the number 2k+1); rows 0-19 carry -1. So P6's per-slot `FrameIdx`
  holds the buffer number (`Num(i) = BufNum` in PD238(c) is mirrored by FrameIdx), not loop 1.1's counter.
- **What the original does on the same gapped numbers (S1-gap leg, run because G3 failed):** byte copy of the S1 replay copy
  (126f8497) whose ONE call of `replay\replay_get_buff_image.vi` (#23006) -> the same gap wrapper (`p63_build_s1gap.py`, 16/0:
  callee diff = that swap, 0 edge diff over 2216 edges, ES 1 warm and cold; saved `bench\lean\D1_s1_replay_gap_20261013_170927.vi`
  93f3cafe1614a3467af15336bc254fab). Leg (`p63_legs_s1gap.log`, `out_p63_s1gap/`, 10/10 chain gates): **2189 rows, all
  bit-identical to S1 frames 0..2188 in order, 0 lost, Total Lost Frames 2176**, column 0 = 1, 3, 5, ... = the buffer number of
  the row's OWN frame (2k+1). (My offline guess that S1's column 0 is the loop index was wrong too: the column holds the buffer
  number, which equals the loop index only when no number is skipped.)
- **So, gap handling P6 vs the original on the same gapped source:** both track every delivered frame, in order, X/Y/Z
  identical; both count the skipped numbers the same way (Total Lost Frames = rows - 11 in P6, rows - 13 in S1: +1 per frame,
  the same formula); both store the buffer number (stride 2) in column 0. **The one difference is P6's one-ring-lap lag of
  column 0** (frame k's row carries the buffer number of frame k-20; the first 20 rows carry -1). That lag is NOT caused by the
  gap: it is in P6-2's and W40's data too (column-0 finding below).

### T-load vs prediction
- **W40 (normal load): as predicted** - 2540 rows, every one matched, frames 0..2539 consecutive, 0 lost, 0 damaged; column 0 =
  index - 20 on all 2520 rows with index >= 20, -1 on the first 20.
- **W100 (overload):** 1431 rows, all 1431 bit-identical to S1's row of some frame (**0 damaged**), strictly increasing (no
  repeat, no reorder), frames 0..2520 spanned, **1090 lost**.
  - **Exact loss count, two independent ways:** from X/Y/Z alignment 2521 - 1431 = 1090; from column 0 alone (each row's own
    stored label) the steps sum to 1090 lost, 0 non-increasing steps. Equal to the frame. (In this leg column 0 == the matched
    index on 1430 rows, row 0 = -1; see the column-0 finding below.)
  - Numbers vs the predicted ranges: rows 1431 vs ~1460 (written first) / ~1250-1400 (amendment) -> inside the first, above the
    amended range; lost 1090 vs ~1000-1100 (first) / ~1100-1300 (amendment) -> inside the first, just below the amended range.
    The amendment over-estimated the in-series cost: 150 s / (1431 + 41) iterations ~ 102 ms, so pick + track + check cost only
    ~2 ms beyond W.
  - Gap classes: predicted "1-2 while trailing" and ">= 20 after a discard", with "3..19 = not explained = FAIL of the
    prediction". Observed: 311 gaps of exactly 1 and 41 gaps of exactly 19; nothing else. **The 19-gaps fall inside the band I
    said was unexplained, so that part of my prediction was wrong.** The cause was my assumption that `Latest` is read at check
    time. The graph shows `Latest` (local #30001 -> RingSeqCheck #29724 'Latest', wire 30101) and `n1` ('min Num' from the pick)
    are read with no ordering to tracking; `Latest` is read as an unordered local in the iteration, effectively at pick time.
    With 1.2 trailing at the oldest slot (q = Latest - 19), a discard sets last = Latest - 1 and the next pick is Latest = q + 19:
    frames q..q+18 are lost = **19**. A trailing skip (the wanted frame overwritten before its pick, F3's uncounted path) loses
    one frame at a time (2521 frames / 1472 iterations ~ 1.7 written per iteration, 1 consumed) -> **1**. Check: 311 x 1 +
    41 x 19 = 1090 = the loss count. Both classes come from the design as built; no other loss mechanism shows.
  - **Discard path: FIRED, 41 times** (each 19-gap can only come from the `next last = Latest - 1` branch, i.e. an invalid
    read: n2 != n1). The discard counter itself is not readable (F3), so this count is from the data, not from a counter.
  - Latest-wins (U8) as built: between discards 1.2 does NOT read the newest frame; it trails at the OLDEST slot (~19 frames
    = ~1.2 s behind) and skips single frames without counting them (311 here); it jumps to the newest only after a discard. Reported
    as a fact about the ring; not a P6-3 pass/fail item.

### Column-0 finding (P6 itself, beside the tests)
`FrameIdx` is read in loop 1.2 by local #30239 (-> IndexArray #30240, wire 30267) with no input wire, so it is NOT ordered after
the pick and NOT covered by the n1/n2 seqlock. When 1.2 is right behind 1.1 (P6-2, W40, GAP), the row gets the slot's PREVIOUS
occupant's value (index - 20, and -1 for the first 20 rows); when 1.2 trails ~19 frames (W100) it gets the right value. The same
read form very likely applies to `TransPos`/`RotPos` (P6-2's B4: trans row 0 = 0.0 vs S1 21.6852); not checked here. X/Y/Z are
not affected (they come from the image, which IS covered by the seqlock).
Why it matters: column 0 is the buffer number = the time axis (U7), and S1-gap shows the original stores the row's OWN buffer
number there. In P6 at normal load every row pairs frame k's X/Y/Z with frame k-20's buffer number: by U9's wording ("a
pixel/number mismatch is corruption") that is a mismatched pair in the SAVED FILE, on every row (P6-2: 2538/2538, W40: 2540/2540,
GAP: 2537/2537; W100: 1/1431). The rule-1a acceptance (X/Y/Z per frame) does not see it because column 0 is excluded from the
compare. Not fixed here (no P6 change is in this task); it is for the judgement.

## 6. Shared scripts edited
- `tools/bench/lean_bench/lean_md5.py` (made by the previous lean session): added the P6 replay copy 09a23608 to the md5 list
  (it is this task's read-only input).
- No other shared script was edited. New files of this session, all in `tools/bench/lean_bench/`: `p63_align.py`, `p63_build.py`,
  `p63_build_s1gap.py`, `p63_legs.py`, `p63_diag_wait.py`, `p63_tidy.py`, `p63_wires.py`, `p63_peek.py`.
- Not edited: `tools/hooks/**`, `tools/motor_gate.py`, `tools/bench/motor_limits.json`, `CLAUDE.md`, any recipe or driver
  (`p63_legs.py` calls `m8_legs.leg` / `motor_session` / `keep_leg_files` unchanged). No hook refused a command of mine; no
  `*_GUARD_OFF` was set. Nothing was committed.

## 7. Motor readback (every motion through `tools/motor_gate.py`, or v5's own call to it inside a leg)
- **Session start 15:59:32** (`p63_motor_start.log`): `LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0` ·
  `PI  : PI controller limits match the file (TMN 0.0000 / TMX 39.0000, tol 0.001) (sender code=0)` ·
  `PI  : reference {"FRF": 1.0, "POS": -0.0001, "POS_BEFORE": 0.0, "RON": 1.0} -> REFERENCED at 0; verify OK (attempt 1/3)` ·
  `LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402` ·
  `ASI : ASI controller limits match the file (SL {'X': -3.8475, 'Y': -4.7744} / SU {'X': 0.1525, 'Y': -0.7744} mm, tol 0.001) (sender code=0)` ·
  `SESSION START OK`
- **Each of the 4 legs** (GAP, W40, W100: `p63_legs.log:4-23 / 46-58, 207-226 / 249-261, 399-418 / 441-453`; S1GAP:
  `p63_legs_s1gap.log`) had its own start with the same lines as above (PI POS -5e-05 / 0.0 / 0.0 at reference) and its own end:
  `LIMITS TMN=0 TMX=52 SPA15=52 SPA30=0` · `PI  : ... (TMN 0.0000 / TMX 52.0000, tol 0.001)` · `LIMITS SL X=-500 Y=-500 SU X=500 Y=500` ·
  `ASI : ... (SL {'X': -500.0, 'Y': -500.0} / SU {'X': 500.0, 'Y': 500.0} mm, tol 0.001)` · `SESSION END OK - controller limits released`.
  Gates MS/ME PASS for all 4 legs (re-checked against motor_limits.json by `m8_legs.motor_session`).
- **Final session end 17:25:34** (`p63_motor_end.log`): `LIMITS TMN=0 TMX=52 SPA15=52 SPA30=0` ·
  `PI  : PI controller limits match the file (TMN 0.0000 / TMX 52.0000, tol 0.001) (sender code=0)` ·
  `LIMITS SL X=-500 Y=-500 SU X=500 Y=500` · `position after (must be unchanged): X=4559 Y=-37898` ·
  `ASI : ASI controller limits match the file (SL {'X': -500.0, 'Y': -500.0} / SU {'X': 500.0, 'Y': 500.0} mm, tol 0.001) (sender code=0)` ·
  `SESSION END OK - controller limits released ... motor_session.json deleted`

## 8. LabVIEW gone
- 17:25:40 `tasklist | grep -ic labview` -> `0` (after the final session end).
- Also verified after every build/diagnostic run (H9: build runs 1-5, the diagnostic, the S1-gap build = 7 runs), after every leg (T3, 4 legs) and at the end of both leg chains (H).

## 9. Input md5s, start (15:58) vs end (17:25): EQUAL 19/19 (`md5_p63_start.json` / `md5_p63_end.json`)
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
| bench\lean\D1_ring_p6_replay_20261013_135743.vi (P6 replay copy) | 09a23608c223a9a31ea6ca3638c1241c |
| original `Min_Track N beads V6_ParallelLoop.vi` | 2a78e17c449cacdaf5da389818526859 |
| G:\m8_replay_frames\frames_manifest.json | f9032ae5510e96126d9f53fc92f69cfe |
| p6_replay_frames_manifest.txt (worktree) | 73877ae04bd5386cac8b6aeed2d9716d |
| motor_limits.json / motor_gate.py | 65e9efae189ff0a911c9b109b19d0e69 / 0f06dd0dc937bf2959a336fb0ea23c7d |
| plans/plan_replay_swap_170.json | f3175f66039bf30a9c671caeac48582a |
No original was opened for writing; every LabVIEW save went to `claudeDev\bench\lean\` (7 files: the 6 of section 3 + the S1-gap
copy). `claudeDev\bench\lean\` now holds the P6 replay copy + those 7 files; the unsaved work copies of the failed runs were removed.

## 10. Verdict
- **T-gap: PASS.** On a source that skips one buffer number per frame, P6 tracked every delivered frame, in order, X/Y/Z
  bit-identical to S1 (2537/2537, 0 lost, 0 damaged); the original on the same gapped source does the same (2189/2189), counts
  the skipped numbers with the same formula, and stores the buffer number in column 0 as P6 does. Prediction G3 was wrong
  (column 0 is the buffer number, not a frame counter) and is reported above.
- **T-load: PASS.** Normal load (W40): 0 lost, 2540/2540 rows. Overload (W100): 1090 lost, counted identically from X/Y/Z
  alignment and from the rows' own column-0 labels; 0 damaged (1431/1431 bit-identical to S1 for some frame, strictly in
  order); the discard path fired (41 jumps of 19 frames, the only branch that makes them). My pre-run numbers held for the
  first prediction (rows ~1460 -> 1431, lost ~1000-1100 -> 1090), but my gap-class rule was wrong by one frame
  (19, not >= 20): the 19-frame jumps were in the band I had called unexplained. They are explained by a graph fact read
  after the run (`Latest` is an unordered local read in the iteration). I am reporting that as a wrong prediction, not hiding it.
  The discard count itself has no counter (F3); 41 is counted from the data.
- **Beside the tests (for the judgement): the column-0 finding.** P6 pairs frame k's X/Y/Z with frame k-20's buffer number in
  column 0 whenever 1.2 is not behind (every row of P6-2, W40 and GAP), because the `FrameIdx` local read (#30239) is outside
  the seqlock. The original stores the row's own buffer number. This is a saved-file difference from the original on the time
  axis (U7/U9) that the X/Y/Z acceptance does not cover; `TransPos`/`RotPos` very likely share it (P6-2's B4). And as built, under
  sustained overload the ring trails at the oldest slot and jumps to the newest only after a discard (U8 note).

RESULT {"p6_3": {"gap": "PASS", "load": "PASS"}, "minutes": 102, "details": {"gap": "P6 2537/2537 rows X/Y/Z = S1, 0 lost, 0 damaged; S1 on same gapped source 2189/2189, same counter formula (TLF P6 2526, S1 2176), both store buffer number in col 0", "load_normal_W40": "2540/2540, 0 lost", "load_overload_W100": "1431 rows, 0 damaged, strictly ordered, 1090 lost = X/Y/Z count = col-0 count; gaps 311x1 + 41x19; discard path fired 41 (from data, no counter)", "prediction_misses": ["G3 col0 is the buffer number, not a frame counter", "overload jump = 19 frames, predicted >= 20 (19 was in my 'unexplained' band)"], "finding_col0_one_lap_lag": "FAIL-finding: P6 col0 = buffer number of frame k-20 when 1.2 keeps up (P6-2 2538/2538, W40 2540/2540, GAP 2537/2537 rows; W100 1/1431); FrameIdx local #30239 outside seqlock; original stores own frame's number", "test_copy_route": "Wait inside a RingSeqCheck_v0 copy swapped into loop 1.2 (a node copied into the P6 copy broke it: ExecState 0, calibration wires re-sourced)", "build_gates": "73/0 (+ S1-gap 16/0)", "inputs_md5_equal": "19/19", "motor_sessions": "start/end OK with readback", "labview_gone": true}}
