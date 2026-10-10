---
card: 160-f2-1
status: current
date: 2026-10-10
---
# Brief 160-f2-1 (assignment 160-1) - OFFLINE: re-pin the stale tool pins of three suites and run them (PD390(g), second half)

`labview: none`. You may edit ONLY the three suites below (pin dict + the docstring line that lists the pins); no tool, recipe, plan or `tools/hooks` edit. `docs/script-writing.md` binds you.
The tools are at: `tools/stagekit.py` 1441bb4c (card 160-b1-1), `tools/stagesim.py` a3261b56 and `tools/stagexec.py` c4a6e0b6 (card 160-a1-1), `tools/stage_prerun.py` 7605116f
(since 159), `tools/addrcheck.py` 207beb0d, `tools/vigraph.py` a7eb58c7, `tools/gscript.py` unchanged (read its md5 now).

## Do
1. For each suite, read its pin dict and compare with the md5 on disk: `tools/bench/selftest_c156_passwire.py` (pins at :161 and docstring :32; also stagesim eb99c6ba),
   `tools/bench/selftest_c155_basecase_frame.py` (:206, docstring :28), `tools/bench/selftest_c156_b2_2_invcheck.py` (:101). Last passing runs: passwire 20/0
   (`selftest_c156_passwire.log:66`), basecase_frame 21/0 (`selftest_c155_basecase_frame.log:75`), invcheck 20/0 (`selftest_c156_b2_2_invcheck.log:163`).
2. Re-pin ONLY tool-md5 prefixes that differ (old -> new prefix; name each in the docstring line, e.g. "re-pinned 160-f2-1 from 9decb20f"). Run each suite under
   `py tools/bgrun.py --material --max-min 6 --log tools/bench/<suite>_c160.log -- py -u tools/bench/<suite>.py` and quote its RESULT line.
3. A count that differs from the last pass, or a failing gate that is NOT a tool pin (e.g. a doc md5 such as ring-p5.md, a data-file md5, a behaviour gate), is NOT re-pinned:
   report it as `OPEN:` with the gate name, the expected and found values and file:line, and leave that suite unedited beyond the tool pins. Rule 1a: no computation touched.

## Report `tools/bench/diag_c160_f2_1_facts.md` (<= 30 lines, facts only)
Per suite: old pins -> new pins, result line with count, OPEN lines. md5 before/after of the three suites; md5 UNCHANGED of stagekit 1441bb4c, stagesim a3261b56, stagexec c4a6e0b6,
stage_prerun 7605116f, addrcheck, vigraph, gscript; VIs 94ffff94 / eb1d0f31 / 2482fe7b / 7f2582ae unchanged; `tools/hooks` untouched.
