---
card: 159-f1-1
status: current
date: 2026-10-10
---
# Brief 159-f1-1 (assignment 159-3) - OFFLINE: suite re-pins to the final tool bytes + the two labview-read suites (PD388(f), PD389(e))

No LabVIEW process is started; `labview: read` only because `selftest_stagekit` and `selftest_c134_1_dry` carry that header (PD388(f)). No hardware,
no `tools/hooks` edit, no stage-tool edit (stagekit is now `ac3a8f57`, stage_prerun `7605116f`, stagesim `eb99c6ba`, stagexec `7a712ccb`).
`docs/script-writing.md` binds you.

## 1. Re-pins (decided; do them in this order)
a. `selftest_c158_runcheck` and `selftest_c158_wire0face`: the "P pins unchanged" pin of `tools/stage_prerun.py` -> the current md5 (`7605116f...`); if either
   also pins `tools/stagekit.py`, -> `ac3a8f57...`. Find the pin lines with Grep; edit with Edit; quote the old and new line.
b. `selftest_c134_2_gates` D2 (`tools/bench/selftest_c134_2_gates.py:91-93`): the dry record it builds hard-codes `dry_rule` 2; re-pin to 3 (the value
   `tools/stage_prerun.py:3434` holds). Quote old/new.
c. Run each of the three suites after its edit; they must be green. Quote totals per suite.

## 2. The two labview-read suites (measure, do not edit)
Run `selftest_stagekit` and `selftest_c134_1_dry` under `py tools/bgrun.py --max-min 20 --log <log> -- py -u <suite>` (file names: Glob `tools/bench/selftest_*`).
For each, find its LAST PASSING log (Glob `tools/bench/selftest_stagekit*.log` / `selftest_c134_1_dry*.log`, newest with a pass total and 0 fails before today's
stagekit edit) and quote both totals. Report equal / not equal; for a difference list the case names that differ (do not fix a stage tool).
Any other self-test whose header pins `tools/stagekit.py` 9cd8822e and now fails on the pin alone: LIST it (name, line), do not re-pin it unasked.

## Report `tools/bench/diag_c159_f1_1_facts.md` (<= 30 lines)
Per re-pin: file:line old -> new. Per suite: command, log path, totals now vs last passing log. md5 after: stagekit, stage_prerun, stagesim, stagexec,
`tools/hooks/` untouched (git status line), VIs 94ffff94 / s09 eb1d0f31 / P5-1a 2482fe7b / P5-1 7f2582ae unchanged. `OPEN:` lines with file:line.
