# Lean task 4: overload = latest-wins (U8/U13), on top of the p6fix result
One session, <= 180 min, <= $60. Real project work (user 2026-10-13 "수정하고 다음 작업 시작").

Read `CLAUDE.md` (the lean rules), then `tools/bench/lean_bench/lean_report_p63.md` (T-load section) and
`lean_report_p6fix.md` (the task before this one).
**Start condition:** `lean_report_p6fix.md` exists and its RESULT says `"p6fix": "PASS"`. Otherwise do nothing in LabVIEW:
write `lean_report_latest.md` saying why and end with `RESULT {"latest": "NOT-STARTED", ...}`.
Start from the fixed VI that report names (`claudeDev\bench\lean\D1_ring_p6fix_<ts>.vi`, its md5) - read-only; make copies.

## The user's rules (docs/user-rules.md)
- U8: "큐를 버리고 새로 들어오는 프레임을 읽는 것이 가장 바람직함. 이는 시계열 데이터의 엄밀성을 위함." (overload: drop the
  backlog, take the newest frame).
- U13: on overwrite jump to the newest slot ("버퍼로 20 프레임이 있어도 문제가 생긴다면 최신 칸으로 움직이는게 맞음").
- U11 priority: (1) no corruption, (2) latest-wins, (3) sequential fallback. U9: a mismatched image/number pair is corruption.
- User 2026-10-13: every saved row's buffer number must be its own frame's, even under overload.

## As built (P6-3 W100): 1.2 trails at the OLDEST slot (~19 frames behind); a frame overwritten before its pick is skipped
one at a time (311 x 1); it jumps to the newest only after a seqlock discard (41 x 19).

## Do
1. Graph facts (offline): RingPickSlot's rule (smallest Num > last), RingSeqCheck's next-last rule, where `Latest` is read.
2. Design + predictions in the report BEFORE any LabVIEW edit: the smallest change that makes 1.2 take the NEWEST frame when
   it has fallen behind (e.g. pick = the slot holding `Latest` when Latest > last + 1, or next last = Latest - 1 whenever a
   frame was skipped) - choose and justify; keep the seqlock (n1 -> track -> n2) and the discard rule; no per-bead maths
   changes (rule 1a: only which frame is picked changes). Predict for W40 (unchanged: 0 lost) and W100 (lag ~0-1 frame,
   gap pattern, rows).
3. Build from a byte copy, save ONLY under `claudeDev\bench\lean\` as `D1_ring_p6latest_<ts>.vi` (and any changed ring subVI
   as a new file there), ExecState 1 warm and cold, edge diff = exactly the intended change.
4. Re-run with the P6-3 routes: P6-2 replay (normal), gap, W40, W100. Per condition: rows, own-buffer-number rows / total,
   X/Y/Z bit-identical rows, lost, damaged, strictly ordered, and for W100 the lag (how far behind the newest each pick was,
   from the data) vs the as-built 19.

Do NOT edit `tools/hooks/**`, `tools/motor_gate.py`, `tools/bench/motor_limits.json` or `CLAUDE.md`. Do not commit.

## Report `tools/bench/lean_bench/lean_report_latest.md`
Graph facts, design + predictions (first), timeline, the VI(s) (path, md5, exact change), per-condition numbers vs predictions,
what failed and how fixed, shared scripts edited, motor readback lines, LabVIEW-gone, input md5s start vs end, then
`RESULT {"latest": "PASS|FAIL|INCOMPLETE|NOT-STARTED", "own_number": {...}, "w100_lag": "...", "minutes": N}`.
