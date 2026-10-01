ATTACK this claim about the failed gate in tools/bench/diag_c128_4_checks.log (script tools/bench/diag_c128_4_checks.py).

Failure: `S selftest_stage_prerun_c106e.py exit 0 and RESULT PASS` FAILED. The self-test's own log
tools/bench/selftest_c128_4_stage_prerun_c106e.log:14 says E1 ("Part-B prerun, no meter record: exit 0, WARN line, RESULT PASS
first_fail 'X10 WARN unmeasured'") got exit 1 with first_fail "X16 every declared terminal of a created primitive carries
term_class (PD251(b)): [{'action': 'r6_lr_ring', 'terminal': 'plot ring (display)', 'stage': 'disp'}, ...". 14 pass / 1 fail.
Its last green run is tools/bench/p3run_selftest_stage_prerun_c106e.log (2026-09-28, 15/0).

Card 128-4 changed tools/stage_prerun.py in three places only: x5_count (RLE ops counted 1:1 vs plan RLE rows, new
RLE_VERB_RE), patch_stagekit (Stage methods / K.mod / jev candidates wrapped from saved originals once per process), install()
(shutil._real_* saved only once), and main() resets D (D.__init__()) before dry/prerun. grep "RLE_VERB_RE|_dry_orig|D.__init__"
in tools/stage_prerun.py.

Claim: the E1 failure is PRE-EXISTING and not caused by 128-4: it is the X16 gate added by card 125-1 (PD251(b), 2026-10-01,
stage_prerun.py main's stageplan branch, `x16_gate`) refusing plan_disp rows whose created-primitive terminals carry no
term_class; X16 did not exist at the 2026-09-28 green run. The other 11 stage_prerun self-tests, selftest_census_predict,
selftest_case_frame_c124 and c125_1_offline_measure all PASS in the same run.

Attack: strongest reason this is wrong (could the D reset or the once-only wrapping change E1's path, e.g. an X10/meter
record read through D, or the selftest relying on accumulated D state?); an alternative explanation; the cheapest
discriminating test (e.g. run selftest_stage_prerun_c106e.py against `git show HEAD:tools/stage_prerun.py`, and/or find
whether any c106e run after 2026-10-01 PASSED). Answer in <= 25 lines with file:line evidence.
