# Lean report - latest RETRY 1 (latest-wins U8/U13: the per-pick lag under W100, measured from the data), 2026-10-14

One Opus session, started 02:35 (task `queue/running/latest.md`, retry 1 of 1). Start condition: `lean_report_p6fix.md:254`
ends `RESULT {"p6fix": "PASS", ...}` -> started. `user_notes.md` has ONE note (do not edit inside the big P6 VI; copy a small
subVI and swap only the call's callee); it does NOT say the user accepts the pick-rule test + end-lag estimate
(`questions_for_user.md:4` is still open), so steps 3-5 are done. The task text does not contradict the note.

## 1. Graph facts (offline, before any LabVIEW run)
- fail1 section 1 (`lean_report_latest_fail1.md:8-33`) stands: loop 1.2's pick loop calls the pick subVI once per poll with
  `Num` = a fresh read of the `Num` local (the 20 per-slot buffer numbers; a slot being written holds -1) and `last` = loop
  1.2's shift register. In the fail1 W100 copy (04e54006) that call is **#31367 -> `RingPickSlot_latest_20261014_010104.vi`**
  (fail1 build log `latest_build_run2.log:137-152`).
- Inside `RingPickSlot_latest` (8fc2ec26; fail1 build log line 59, top-level diagram #3): control terminals `Num` (#3 'Num')
  and `last` (#3 'last'); `GT` #156 Greater?(Num, last); For loop with Select #45 (masked = Num > last ? Num : last);
  Array Max & Min **#117**: `max value` -> indicator `min Num` + Less? #198 `y`; `max index (indices)` -> `min slot`;
  Less? **#198** `x < y?` (= last < max) -> `found`. Pane 11 Num, 10 last -> 3 min Num, 2 min slot, 1 found.
- Donor nodes for the observer (stored bed graph `tools/bench/graph_ring_p6_20261012_212645.json`, read by the new offline
  `latestobs_donors.py` / `latestobs_terms.py`): Tick Count **#10972** (`millisecond timer value`), Build Array **#23365**
  (inputs `array`, `element` x4 -> `appended array`). The bed has no Open/Write/Close-file primitive and the scripting tools
  have no verb that creates a constant inside a case frame, so the file write uses NI's `Write Delimited Spreadsheet (I64).vi`
  (vi.lib\Utility\file.llb; open-or-create, seek to end, write one row, close - one call) inside a small logger subVI whose
  path / append inputs are front-panel defaults (`make_default`).

## 2. Design and predictions (written BEFORE any LabVIEW run)
### Files (all new, under `claudeDev\bench\lean\`; nothing else is built or saved; the 6 fail1 files only byte-copied)
1. **`PickLog_latestobs_<ts>.vi`** (logger; byte copy of `claudeDev\EMPTY_v0.vi`): `Write Delimited Spreadsheet (I64).vi`
   (dropped by path) with controls created on its `file path`, `1D data` and `append to file?` inputs and an indicator on
   `error out` (so no automatic error dialog); defaults made current: path =
   `...\V6_lean\tools\bench\lean_bench\out_latest2\picklog_w100.txt`, append = True. Connector pane: `1D data` only
   (terminal 11). One call = one appended tab-separated line. No serial/VISA.
   *Deviation from the task text, stated:* the task named two files (observer + test copy); this third small file exists only
   because no tool can place the path / append constants inside the case frame. It holds no tracking maths.
2. **Observer `RingPickSlot_latestobs_<ts>.vi`** = byte copy of `RingPickSlot_latest_20261014_010104.vi` (8fc2ec26) plus,
   inside it only: Tick Count (copy of bed #10972) and Build Array (copy of bed #23365) on the top-level diagram, wired ONLY
   from existing sources: `array` <- control `Num`, the 4 `element`s <- control `last`, #117 `max value` (= the picked Num),
   #117 `max index` (= the picked slot), Tick Count; a Case structure (copy of `DonorCase_v0`) whose selector <- #198
   `x < y?` (= `found`, a new branch of the existing wire); in its **True** frame only the logger, `1D data` <- Build Array
   out (one new case tunnel). False frame empty, so idle polls write nothing. The new nodes are sinks of existing wires only;
   no existing edge is removed; pane, names, types and the 3 outputs unchanged.
   *Deviation from the task text, stated:* the log line holds the RAW ring snapshot instead of three counts:
   `Num[0..19], last, picked Num, picked slot, ms tick` (column order read back in the functional test). `ring max Num` =
   max(Num[0..19]), `unread` = count(Num > last), `in-write` = count(Num == -1) are computed OFFLINE from the same line by
   `latest_picklag.py`. Same information plus more (which slots, the exact numbers), four fewer new nodes (no second Array
   Max & Min, Equal?, 2 x Boolean To (0,1), 2 x Add Array Elements - none of them has a donor in the bed). The two
   unconditional new nodes (Tick Count, Build Array of 24 I32) run on every poll; cost ~microseconds.
3. **Test copy `D1_ring_p6latestobs_replay_w100_<ts>.vi`** = byte copy of the fail1 W100 copy 04e54006 + `replace_object` of
   its ONE call #31367 (RingPickSlot_latest) -> the observer. Nothing else.

### Gates (build script `latestobs_build.py`, one bgrun call; fatal gates stop before any save)
- Logger: copy md5 == EMPTY_v0's; after the edits ExecState 1; pane {11: '1D data'}; defaults read back (path, True) after
  save; md5 recorded.
- Observer: work copy md5 == 8fc2ec26; ExecState 1 before/after; pane before == after == fail1's; edge diff (new case tunnels
  with an in and an out collapsed, tunnel terminal names ignored as in fail1): **removed = {}**, added = exactly the 7 planned
  edges (Num->BA.array, last/max value/max index/tick -> BA.element, #198 -> case selector, BA.out -> logger `1D data`), every
  added edge's sink a NEW owner; case frame names {False, True}, the logger owned by the True frame.
  **Functional test, warm and again COLD from the saved file in a fresh LabVIEW: the 10 vectors of fail1 == fail1's Python
  reference (outputs unchanged) AND the log file grows by exactly 1 line on each found=True vector (7 of 10) and 0 lines on
  each found=False vector (3 of 10), the line = [Num, last, picked Num, picked slot] of that vector + a tick.** md5 unchanged
  by the runs / the cold load. The test lines are moved to `out_latest2\picklog_functest_<ts>.txt` before the leg.
- Test copy: copy md5 == 04e54006; exactly one call to RingPickSlot_latest, #31367; callee diff == exactly #31367 -> the
  observer; wire-edge diff 0 after uid remap; ExecState 1 warm and cold; cold edges == the source's cold edges; md5 unchanged
  by the cold load; source md5 unchanged. COLD load also lists every VI in memory (`ExportedVIs`) and the paths of those from
  `zz_LabView VI\background VIs\` (the loaded background subVIs; all 94 files of that folder are in the md5 lists).
- Hygiene: VI-Server refs opened == closed; pins unchanged; LabVIEW gone.

### Predictions (W100, 150 s, 15 picks, `p6fix_legs.py` unchanged, mode `same`, reference P6-2's S1 leg)
| quantity | prediction | basis |
|---|---|---|
| rows | 1440-1500 | fail1 1472; the log adds ~1 ms per ~102 ms iteration |
| log lines | = rows + discards; discards 0 -> lines == rows | one found=True call per iteration |
| **lag at the pick = ring max - picked Num** | **0 on every line** | in-write slot holds -1, so max(Num) is the newest COMPLETE frame and the pick IS it |
| unread per pick (count Num > last) | 1 (~27 %) or 2 (~73 %), never >= 3 | fail1's steps: 402 x 0-lost, 1069 x 1-lost |
| in-write per pick | 0 or 1 | 1.1 writes one slot at a time |
| lag at save = next line's ring max - this picked Num | 0..2 frames, mean ~1.7 (= frames written during one iteration) | 102 ms / 59 ms |
| log picked Num vs saved row col 0 | equal, in order, one-to-one on every row | the picked Num is n1; a row is written only when valid |
| own-number rows / total | all | p6fix seqlock unchanged |
| X/Y/Z bit-identical vs S1 | all rows | rule 1a, no maths node touched |
| damaged / order | 0 / strictly increasing | |
| lost | only 1-frame gaps, ~1050-1080, max step 2 | fail1 1069 x 1 |
- "The observer did not change the result" = the same checks pass and the gap pattern matches fail1's (only 1-frame gaps, max
  step 2); rows are timing-dependent, so +-3 % vs 1472 is not a change.
- P62 / GAP / W40: no new LabVIEW run; own-number + X/Y/Z re-computed offline with `p6fix_align.py` from fail1's run dirs,
  predicted equal to fail1's accepted numbers (2537/2537, 2538/2538, 2540/2540, X/Y/Z all, 0 lost).
- Risks named now: (a) Build Array of I32 + the U32 tick may coerce (I64/DBL out) - harmless (the I64 writer coerces); if it
  breaks the VI (ExecState 0) the build stops and run 2 drops the tick. (b) Connect Wire from the top level into the True
  frame must create the case tunnel itself (fail1 saw LabVIEW create a For-loop tunnel the same way); if not, the build stops.
  (c) the file open/append/close per pick could take > 5 ms on a busy disk; then rows drop a few % - visible in the tick column.
