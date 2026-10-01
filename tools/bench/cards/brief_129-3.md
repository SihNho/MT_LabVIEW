# Brief for card 129-3 (cycle 129 judgement) — the CLOCK device, standalone half (`docs/violation-decisions.md` 2026-10-02 01:01)

OFFLINE ONLY. Runs beside the LabVIEW card 129-2, so it edits NO gate code: not `protocol.py`, not `tools/hooks/*`, not
`stage_prerun.py`. Wiring the check into `protocol.py validate` is a later card, after no LabVIEW card is live.

## 0. Time arithmetic (budget 20 min)
script ~60 lines: ~6 min · self-test with 4 cases on temp copies: ~6 min · runs: < 1 min · total ≈ 13 min.

## 1. `tools/card_clock.py <result_X.json>` (stdlib only)
- `id` from the result; the FIRST line of `tools/bench/cards/guard_card.log` matching `BOUND agent … (id <id>)` gives the bind
  time and its line number (format seen at `guard_card.log:575`: `2026-10-02 00:41:33 | ALLOW material … | BOUND agent … ->
  tools\bench\cards\task_128-5.json (id 128-5)`); the result file's mtime gives the write time; `tools/bench/cards/task_<id>.json`
  gives `budget.minutes`.
- measured = write − bind, in minutes (one decimal). Prints ONE line and a `RESULT {...}` line:
  `CLOCK id=<id> bound=<HH:MM:SS> (guard_card.log:<n>) written=<HH:MM:SS> measured=<m> claimed=<cost.minutes> budget=<b> verdict=<v> reason=<…>`
- verdict `CLOCK-MISMATCH` (exit 1) when (i) `first_fail` or `blocked_by` text cites the budget or minutes
  (`budget|minute|\bmin\b|time.?out|deadline`, case-insensitive) while measured < 0.8 × budget, or (ii) claimed >
  measured + max(5, 0.25 × measured). `CLOCK-UNMEASURED` (exit 2) when there is no bind line, no task card or no
  `cost.minutes`; never OK in that case. Otherwise `OK` (exit 0).
- Optional `--log <path>` and `--cards <dir>` arguments so the self-test can point it at fixtures.

## 2. Self-test `tools/bench/selftest_card_clock.py` (fixtures in a temp dir, mtimes set with `os.utime`)
(a) a copy of `result_128-5.json` + its real bind line (00:41:33) + mtime 00:49:02 → CLOCK-MISMATCH, both reasons;
(b) `result_129-1.json` copy + its real bind line + its real mtime → OK; (c) a result whose id has no bind line →
CLOCK-UNMEASURED; (d) honest claim but measured < 0.8 × budget and first_fail NOT about budget → OK. Then run the script on
the REAL files `tools/bench/cards/result_128-5.json` and `result_129-1.json` and report both lines.

## 3. Return
`result/1` (also `tools/bench/cards/result_129-3.json`), validated: script and self-test md5 + line counts, self-test
pass/fail counts, the two real CLOCK lines, minutes. Return at the first unexpected result.
