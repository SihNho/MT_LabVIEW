---
card: 160-f3-1
status: current
date: 2026-10-10
---
# Brief 160-f3-1 (assignment 160-2) - OFFLINE tooling: selftest_c134_1_dry 11/0 and the stale pins (PD391(g))

`labview: none`, no tool edit (only the self-test files listed under `flags.write`), no `tools/hooks` edit, no pred or plan file re-pinned or edited. Read `docs/d1/ring-p5b.md`
PD391(g) (line 165-170) and `docs/script-writing.md`. Card 160-a2-1 moved `tools/stagesim.py` to 95a162ba and `tools/stagexec.py` to ddf23a31 (facts `diag_c160_a2_1_facts.md`, OPEN list).
A parallel card (160-b3-1) reads those tool files and writes plan json; you must not touch them or any `plan_ring_*` file.

## 1. `selftest_c134_1_dry.py` (10178208) - find, then fix per PD391(g)
It was 9/2 at the last run (`tools/bench/selftest_c134_1_dry_c159_f1_1.log`). Run it first on the current bytes and write the result to `selftest_c134_1_dry_c160_f3_1_before.log`.
Name the two failing gates and why each fails (T2a: the header-only pin of the stored pred rows; T2: the unverified-item count). Then, in the self-test file only:
(a) T2a: re-pin to the header-only md5 prefix 0d1f0c15 - first MEASURE the header-only md5 the way the gate computes it and confirm it prints 0d1f0c15; if it does not, FAIL with both values.
(b) PB rows: the stored pred rows carry four `2626|Terminal|array|0-3` PB rows that the current dry check drops; this is PD370(b)'s adopted position-PB change (commit 18c241ec, card 153-b2-1,
`ring-p4d.md:172-183`). PD370(b) keeps stored preds byte-unchanged and puts a CONVERTER in the self-test: apply that converter to the stored pred rows and the open pairs the self-test feeds
the check (find the existing PD370(b) converter in `stage_prerun.py` / `stagekit.py` and CALL it; if none exists, FAIL and say so - do not write a second one in a tool).
(c) T2: count unverified items by PD387(e)'s rule (`stage_prerun.py:1074-1075`) - read those two lines, quote them, and make the self-test count the same way by calling the same function.
Target `RESULT 11/0`; if a gate still fails, name it with the values (a named FAIL is an acceptable result, a silent loosening is not). Log: `selftest_c134_1_dry_c160_f3_1.log`.

## 2. `selftest_c156_b2_2_invcheck.py` (c6460301) - suite :83 reads the expected `docs/d1/ring-p5.md` md5 from disk at run time
Replace the pinned ring-p5.md md5 at suite :83 by a read from disk at run time (the same check, no stale pin). Re-pin only the tool md5s that card 160-a2-1 moved
(`:100`-`:101`: stagexec c4a6e0b6 -> ddf23a31, stagesim a3261b56 -> 95a162ba). Target `RESULT 20/0`; log `selftest_c156_b2_2_invcheck_c160_f3_1.log`. Update the docstring line that names the pins.

## 3. The two other stale pins from the a2-1 OPEN list
`selftest_c156_passwire.py:161-163` (stagesim a3261b56 -> 95a162ba) and `selftest_c155_basecase_frame.py:206`: re-pin ONLY the moved tool prefixes, run each, quote RESULT before (from its last
log) and after. A count that differs from its last pass is a FAIL of this card, not a re-pin. Other files pinning moved md5s (`diag_c160_*`, `prep_c160_b1_1_mk.py`) are listed `OPEN:` and not edited.

## Report `tools/bench/diag_c160_f3_1_facts.md` (<= 30 lines, facts only)
The two original T2a/T2 failures with values; the converter used (file:line); before/after RESULT lines for the four suites; md5 before/after of the four self-test files; md5 UNCHANGED:
stagesim 95a162ba, stagexec ddf23a31, stagekit 1441bb4c, stage_prerun 7605116f, ring-p5.md 99c812e6, plan_ring_p5s02b_in.json 56bfddd3, all `tools/bench/plan_ring_*`; tools/hooks untouched. `OPEN:` lines.
