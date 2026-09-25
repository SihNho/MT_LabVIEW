Failed prediction: `tools/bench/selftest_errorlist_reuse_81.log` ended 13 PASS / 2 FAIL (C1, K6).

Hypothesis under attack (see the review card above): both failures are bugs in the self-test, not in
`tools/cycle_runner.py` `write_cycle_card` (bed field) or in `tools/hooks/guard_card.py` `pure_selftest` /
`decide` (the stagexec self-test exemption).

Files: the log, the self-test (`tools/bench/selftest_errorlist_reuse_81.py`, lines 127-164 are C1 and K*),
`tools/hooks/guard_card.py` lines 36-80, `tools/cycle_runner.py` (search `def write_cycle_card`, and the bed
fallback near line 560-600), `docs/protocol/cycle.json` (the effort enum).

Questions:
1. Does the old C1 call really pass effort 'e' (argument order vs `write_cycle_card`'s signature), and with a
   valid effort would `write_cycle_card` actually emit bed {path, md5} of D1_k_20260925_100155.vi when
   tools/bench/bed.json is absent? Or is there a second defect hidden behind the schema error?
2. K6: with a foreign path `C:/elsewhere/tools/stagexec.py`, is `decide()` returning allow a defect of guard_card
   (a real foreign stagexec.py that does exist would then be exempted?) or only an artefact of protocol having no
   source file to scan? Does replacing K6 with K8 (testing `pure_selftest` directly) leave any path uncovered?
3. The cheapest test that separates "self-test bug" from "code bug" for each gate.
