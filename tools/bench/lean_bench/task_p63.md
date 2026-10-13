# Lean task 2: P6-3 - the two ring tests (frame-number gap; overload with a test delay in loop 1.2)
One session, <= 180 min, <= $60. Real project work (user 2026-10-13 "진행해보자"), not a bench re-run.

Read `CLAUDE.md` (the lean rules) first. Your previous lean session finished P6-2 on this branch:
`tools/bench/lean_bench/lean_report.md` (replay chain, paced stand-ins, `--out-root`, compare, the Done-button reference
it cut) - reuse all of it. P6 bed: `claudeDev\D1_ring_p6_20261012_212645.vi` c2d9c13c (read-only). P6 replay copy:
`claudeDev\bench\lean\D1_ring_p6_replay_20261013_135743.vi` 09a23608 (read-only; make copies).

## What the two tests must show (PD384(d) in docs/d1/ring-p5.md:285-286, runner.md:57-59, ring-p6.md:53)
- **T-gap (frame-number gap):** when the frame source skips frame numbers, P6 handles it as the original would / as the
  ring design says (find the design: the P3a "new frame" counter #26879 / #27039, PD246(c); RingSeqCheck in
  docs/d1/ring-p4b.md:140-141; the user rules U1-U13 listed in docs/d1/INDEX.md; STATUS.md's 2026-09-28 overload note).
- **T-load (execution order with a test delay in loop 1.2):** no loss at normal load; under overload the loss count is
  exactly the predicted one and 0 rows are damaged (every tracked row equals S1's result for SOME input frame, in order).
  A discard path that never fires = "not verified", never "pass".
- Evidence is the DATA (the alignment idea of PD410(c): rows matched bit-for-bit against the S1 replay of the same
  frames), not an internal counter alone. Counters are reported beside it.

## How
1. FIRST write your predictions into the report (expected rows, expected loss count and how you derived it, what a gap
   should do) - before any LabVIEW run. A prediction that turns out wrong is a fact to report, not to hide.
2. Make test copies ONLY under `claudeDev\bench\lean\` (copies of the replay copy and/or replay stand-ins; e.g. a stand-in
   that skips frame numbers, a copy of P6 replay with one `Wait (ms)` node in loop 1.2 and no data wire). Never edit the
   bed, S1, or any file outside `claudeDev\bench\lean\`. A test delay changes timing only - no wire into the maths (rule 1a).
3. Motor sessions as before (start/end with readback, quoted). LabVIEW gone after each run.
4. Reuse the S1 replay leg of P6-2 as the reference where it covers the same frames; run a new S1 leg only if needed.

You decide how to handle surprises yourself. Do NOT edit `tools/hooks/**`, `tools/motor_gate.py`,
`tools/bench/motor_limits.json` or `CLAUDE.md`. Do not commit; the chat reviews and commits.

## Report `tools/bench/lean_bench/lean_report_p63.md`
Predictions (written first), timeline, test copies (path, md5, what was changed and why it touches no maths), per test the
numbers vs the prediction, what failed and how you fixed it, every shared script you edited (file + reason), motor
readback lines, LabVIEW-gone check, input md5s start vs end, then
`RESULT {"p6_3": {"gap": "PASS|FAIL|NOT-VERIFIED|INCOMPLETE", "load": "..."}, "minutes": N}`.
