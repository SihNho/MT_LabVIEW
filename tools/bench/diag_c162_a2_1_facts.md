# diag_c162_a2_1_facts - card 162-a2-1 (offline, no LabVIEW) - status FAIL (step 4 returned)
## 1. Pin sweep (BEFORE any edit) - prep_c162_a2_1_pinsweep.py a90d0c7a -> prep_c162_a2_1_pinsweep.log (5/0, BGRUN END rc=0)
11 scope scripts, 37 pins read by ast. TARGET pins (stagekit/stagexec/stagesim/stage_prerun/plan_ring_p5s02b*/ring-p5b) 14: equal 12, STALE 2:
- selftest_c161_delckpt.py:138 plan_ring_p5s02b_pred.json a1fd43fb -> 4cef0a8c (re-written by card 162-a1-2 census, diag_c162_a1_2_facts.md:39)
- selftest_c159_a4_1.py:300 stagexec.py 7a712ccb -> a4df7e15
selftest_c157_innerface.py:72 stagesim already 95a162ba (EQUAL): the fp-85 pin edit was in the working tree before this card (git diff; file
md5 c6c5a2f9 == card input) - no edit made by this card. Other pins: 19 equal; regface.py:47 four claudeDev VI pins show MISSING only
because the extractor does not resolve CD+k+'.vi' (not a stale finding). No pins in l0stem, chat_p1, c156 licence, l0stem_regress.
Current md5: stagekit 9b8f82c1, stagexec a4df7e15, stagesim 95a162ba, stage_prerun 7605116f, ring-p5b.md 93dcb778.
## 2. Drained rows (gate_fp.py drain; queue read via gate_fp.py list)
| id | fixed | self-test (log) | gates | before -> after |
|---|---|---|---|---|
| fp-85 | tools/bench/selftest_c157_innerface.py:72 | selftest_c157_innerface (selftest_c157_innerface_c162_a2_1.log) | 13/0 | open -> drained |
| fp-82 | tools/stagekit.py:2532 (gate_l0 plan_in_matches_stem clause; fn :2994) | selftest_c160_l0stem (selftest_c160_l0stem_c162_a2_1.log) | 14/0 | open -> drained |
| fp-84 | NOT drained (would be tools/stagexec.py:2125 REREAD_KINDS) | selftest_c161_delckpt (selftest_c161_delckpt_c162_a2_1.log) | 10/1 | open -> open |
fp-84 run: D1, D2, V1-V5, S x3 PASS (:4-19); only FAIL `P pins unchanged` (:21) = the stale pred pin above. Not a named pin -> not edited
(card rule "ONE pin edit per stale pin named in the brief"; brief "stale pin outside the named ones = RETURN"). No JEV-LADDER row for that log.
Hook rows fp-75/80/81/83: untouched, still open. No other row changed.
## 3. Files
- tools/bench/prep_c162_a2_1_pinsweep.py (new, a90d0c7a): the sweep; md5/Gates CALLED from tools/invcheck.py.
- archive/peer/2026-10-10-c162-delckpt-stale-pin.md (-> 564d1f36): `## What was done with it` filled (conclusion held, correction adopted).
- tools/bench/gate_fp_queue.jsonl (-> b5a32198): fp-82, fp-85 drained by gate_fp.py.
- Originals, tools/hooks/**, stagekit/stagexec/stagesim/stage_prerun: not touched. STATUS not edited, no commit.
## OPEN
- OPEN: re-pin selftest_c161_delckpt.py:138 pred a1fd43fb -> 4cef0a8c (pin-only, content gates green) and then drain fp-84 at stagexec.py:2125?
- OPEN: selftest_c159_a4_1.py:300 stagexec pin 7a712ccb is stale (a4df7e15); for card 162-a2-2's scope.
- OPEN: the ast pin extractor is new logic in a prep script (outside shared-module write globs); move to a shared module if 162-a2-2 needs it.
