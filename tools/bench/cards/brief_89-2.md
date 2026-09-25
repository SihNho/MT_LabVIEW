# Brief 89-2 (cycle 89 judgement): the stamp helper `claudeDev\t0_stamp.vi` (tool, 2026-09-24 grant)

Decision on result 89-1 (FAIL at B0, `tools/bench/cards/result_89-1.json`), taken by judgement:
- **No FlatSequence-wrap verb.** Moving live nodes into frames is a multi-verb build of more than a cycle, and the
  question does not need exact brackets.
- **195(d) is measured by COMPLETION STAMPS.** A reentrant helper is fed a BRANCH of an existing output wire of each
  group's last node, plus a branch of each holding loop's `i` terminal (the iteration-start reference). The helper
  records the time at which that data became available.
- Per-group cost is then bounded offline: completion time minus iteration start, and the difference between groups
  along the dependency chain. The comparison between 8 and 15 picks shows where the per-bead growth accrues. That is
  the question. 89-1's facts: branch reads add 0 `computation_diff` rows (vigraph.py:847), and the error-wire splice
  is not used.

## Build the helper (this card only; the instrumented VI is the next card)
`claudeDev\t0_stamp.vi`, built by scripting:
- Reentrancy: **preallocated clone**. Each call site keeps its own state, and no call site can block another loop.
- Inputs: `data` as a Variant (any wire coerces to it) and `site` as I32. No outputs are required.
- Body: read High Resolution Relative Seconds and store it in a preallocated DBL buffer held in an uninitialised shift
  register, with a call counter. Every 1024th call, write the valid part of the buffer to
  `claudeDev\t0_out\site_<site>.bin` by OVERWRITING the file. Also write it on the first call so the file exists.
  Nothing else does file I/O.
- Buffer capacity must be at least 16,384 stamps. This covers 120 s at 90 Hz with margin.
- Implementation details (file format, buffer growth) are yours; write down what you chose.
- Self-test, called from a scripted test VI or by COM:
  - call it 3000 times with site=7;
  - the file must hold ≥ 2048 monotone non-decreasing stamps;
  - two sites called interleaved must give two files with the right counts (the negative case: stamps must not leak
    across sites);
  - handle count must be flat over 20 runs (±100).
- Report the helper's cost per call (median over the 3000 calls). Also report the cost of the Variant coercion for a
  2-D U16 1280×1024 input against an I32 input. That number decides which wires the next card may branch from.

Gates: ExecState 1, saved by script, md5, the self-test passes, handle count flat. Do not open or change
`D1_s1_copy.vi`, the kswap VI or the L2-A1 bed.
