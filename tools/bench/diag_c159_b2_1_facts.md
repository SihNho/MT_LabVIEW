---
card: 159-b2-1
date: 2026-10-10
status: current
---
# 159-b2-1 facts (PD388(d), DRY_RULE 2 -> 3), offline, no LabVIEW, no hook edit
- DIFF tools/stage_prerun.py:3434 `-DRY_RULE = 2` / `+DRY_RULE = 3`, nothing else: selftest_c159_b2_1_run2.log R0b (the line put back to 2 hashes to the pin 9ea1bdeb8afcd2eef4abfe6b3531f66f; one `DRY_RULE = ` line in the file).
- NEW md5 tools/stage_prerun.py 7605116f1dfe1c6fd4963dbfcf259de1 (selftest_c159_b2_1_run2.log:3).
- Self-test selftest_c159_b2_1.py (md5 18914fe4): run2 12 pass / 0 fail, BGRUN END rc=0 (selftest_c159_b2_1_run2.log:19-21).
- Run 1 (selftest_c159_b2_1.log, 10/2): C2 FAILED its prediction - the chat-S4 A ADOPTION gate (adopted_scratch.jsonl, D1_ring_p5s02a_20261010_023239.vi md5 94ffff94) refuses both p5s02a recipes BEFORE the dry filter. Run 2 isolates ADOPT_LOG for the gate, prints the as-is verdict as FACT C2a.
- check_launch call: `SP.check_launch('py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u "<SAND>/tools/recipes/stage_c159b21test.py"')`; sandbox env PRERUN_RECORDS / PRERUN_LOG_DIR / STAGE_RUNS / STAGE_RUNS_CYCLE=cycle 903 / SCRATCH_SKIP_LOG, fn_records.GATE_LOG -> %TEMP%.
- Source record: real dry PASS dry_rule 2 of tools/bench/diag_c158_a3_2b_graph.py 2026-10-10 03:25:33 (sha 128d78d55ed0) + its prerun PASS; only script/sha256/plan_md5s/t rebound to the fixture.
- T1 dry_rule 2 -> REFUSED "LAUNCH GATE (card 134-2, PD288(c)) ... recorded under dry rule 2, not dry_rule == 3"; T2 same records with dry_rule 3 -> ALLOWED; T3 records differ in dry_rule only; T4 write_record stamps 3.
- M1 mutant (stage_prerun.py:4976 filter replaced by `m = m`, exec in memory) ALLOWS the dry_rule-2 records -> T1 fails if the comparison is removed.
- Real prerun_records.jsonl (read only, md5 1452f9ee before == after): 1081 records, 1081 with dry_rule != 3 (all kinds; prerun records carry none); 729 of 729 dry records != 3 (values 2, None).
- p5s02a MAIN and scratch: no valid dry record. Adoption isolated -> refused PD288(c) (newest dry 02:31:32 / 02:32:05, rule 2). As-is -> refused first by the chat-S4 A adoption gate.
- selftest_c159_a4_1: before 13 pass / 0 fail (selftest_c159_a4_1_before_b2.log:33, rc=0 399 s); after 13 / 0 (diag_c159_b2_1_a4after.log:33, rc=0 425 s).
- Not run (brief): runcheck / wire0face / stagekit / c134_1_dry. selftest_c134_2_gates.py D2 hard-codes "dry_rule 2 -> allowed" (selftest_c134_2_gates.py:91-93) and will now fail - not run, not edited (outside write globs).
- Log-name note: the before-run log tools/bench/selftest_c159_a4_1_before_b2.log is outside the card's write globs (bgrun wrote it; nothing refused).
OPEN: p5s02a recipes are ADOPTED (adopted_scratch.jsonl); re-dry under rule 3 does not by itself make them launchable - does step 2 run them, or a new recipe?
OPEN: selftest_c134_2_gates.py D2 pins dry_rule 2 - re-pin in the later card that re-pins the other suites?
