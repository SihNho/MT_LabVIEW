---
card: 156-b2-2
status: current
date: 2026-10-09
---
# Brief 156-b2-2 - OFFLINE: the per-card invariant helper becomes ONE shared module (PD380(e), docs/script-writing.md rules 1, 4, 7)

`tools/bench/diag_c156_a2_1_inv.py` (93 lines) is the 5th copy of the per-card "inv" script: it checks a list of md5 pins, takes (mode `before`)
or compares (mode `after`) a snapshot of the P4 recipes / plans / preds / `tools/hooks/**`, prints `GATE PASS|FAIL | label | detail`,
`FACT ...` lines and one `RESULT {...}` line. 23 `*_inv.py` files exist in `tools/bench/` (`ls tools/bench | grep _inv.py`), every one a
copy with pins and names changed. Read `docs/script-writing.md` first.

## What to build
1. ONE new module `tools/invcheck.py` (scope header `labview: none / hardware: none`; NOT under `tools/hooks/`, NOT in `tools/stagekit.py`).
   It holds the logic that is the same in every copy: the md5 helper, `gate()` counting, the pin loop (`startswith` match on a short md5),
   card-input pins taken from the card JSON, the `before` snapshot write / `after` snapshot compare, the leftover-scratch-file gate, the
   `RESULT` line and the exit code. Every parameter a copy changes is an ARGUMENT: card id / card path, pin dict, snapshot path, snapshot
   globs, scratch globs, claudeDev listing glob, main recipe path, the memory-model / adopted-scratch exemption and its `before` pins.
   A new public function carries a docstring (first line: what it does and returns; name its self-test), rule 9.
2. A thin caller `tools/bench/diag_c156_b2_2_inv_c156a21.py` (<= 40 lines, inputs and calls only) that reproduces the config of
   `diag_c156_a2_1_inv.py` (read its lines 5-52 and 57-59 for the config) by calling the module. Do NOT edit `diag_c156_a2_1_inv.py` or any
   other old inv file (they are the record of what ran).
3. Self-test `tools/bench/selftest_c156_b2_2_invcheck.py` run under `py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_c156_b2_2_invcheck.log -- py -u ...`:
   reproduce the recorded log `tools/bench/diag_c156_a2_1_inv_after.log` (and `_before.log`) by running the module on the SAME config with the
   snapshot path redirected to a temp file, and compare gate by gate (label, PASS/FAIL, in order). A gate whose pin legitimately drifted since the
   recording (list each by label and old/new md5; known: `ring-p5.md` was 742e54c4, now aa238a09; `memory_model.json` / `adopted_scratch.jsonl`
   may differ) is listed as DRIFT with both values, not hidden and not counted as a reproduction. At least one recorded PASS case and one FAIL
   case (a deliberately wrong pin in a temp config) must be reproduced exactly. Print a `RESULT` line.

## Rules
Write only `tools/invcheck.py`, `tools/bench/diag_c156_b2_2*`, `tools/bench/selftest_c156_b2_2*`. No edit to stagexec, stagesim, stagekit, addrcheck, gscript, vigraph,
stage_prerun, hooks, plans, recipes, preds, licences, `docs/`. No LabVIEW. Pins at start (must still equal at end): stagexec 25a1494c,
stagesim eb99c6ba, stagekit aec03c6c, addrcheck 207beb0d, gscript 1a80236e, vigraph a7eb58c7, stage_prerun 9decb20f. Failure budget 2.

## Report (facts, <= 25 lines)
The self-test counts; the DRIFT list; the module's public functions with their signatures; the number and names of old `*_inv.py` copies
(file list only, not rewritten). End with `OPEN:` lines for anything the data leaves undecided. Propose no other change.
