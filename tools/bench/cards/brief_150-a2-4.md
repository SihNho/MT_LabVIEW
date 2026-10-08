---
card: 150-a2-4
status: current
date: 2026-10-08
---
# Brief 150-a2-4 - un-shadow `b` in the rebase CLI of stage_prerun.py; offline, ALONE

Card 150-a2-3 (s07 prep) returned FAIL at its first step: `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s07v18.json --graph tools/bench/graph_ring_p4s06_20261008_192149.json`
raised `AttributeError: 'bool' object has no attribute 'get'` (`tools/bench/prep_c150_a2_3_rebase.log:20-22`, `tools/bench/diag_c150_a2_3_facts.md:25-30`).
Cause (read from source): in the rebase function, `b` is the plan base dict (`stage_prerun.py:4261`) and is read again at `:4415` (`provisional={"path": b.get("path"), ...}`).
The two log loops `:4303` (RENAMED-OLD, card 150-a2-1) and `:4305` (FLIPPED-OLD, card 150-a2-2) use `b` as a loop target and overwrite it. The self-test R1-R4 never ran the CLI path, so it did not see this.

## Change (stage_prerun.py md5 now 6208b7b7; quote the new one)
Rename the loop targets at `:4303` and `:4305` so `b` is not rebound: e.g. `for u, o, old_v, new_v in ...` with the matching `.format` arguments. The log text must stay
byte-identical (`RENAMED-OLD <uid> #<owner> 'a'->'b'`, `FLIPPED-OLD <uid> #<owner> src <a>-><b>`). Before editing, grep the same function (`:4255` to its end) for ANY other loop target or assignment named `b`, `u`, `o`, `a`
that is read later, and rename those too if they clobber a variable used after the loop. Nothing else in the file changes. No `tools/hooks/**` edit.

## Test
Add to `tools/bench/selftest_rebind_c150.py` (keep <= 120 lines, keep R1-R4 + R3a/R3b) a check R5 that does NOT write files: parse stage_prerun.py with `ast`, find the function containing the
`FLIPPED-OLD` string, and assert no `for` target and no other assignment after `:4261`'s `b = plan.get("base")` rebinds `b` before `:4415`'s read. R5 must FAIL on the pre-edit text
(`git show HEAD:tools/stage_prerun.py` does not contain 150-a2-2, so use the in-tree 6208b7b7 saved first as `tools/bench/prep_c150_a2_4_stage_prerun_before.py` for the failing run) and PASS after.
Then run R1-R5, and the regressions with the 150-a2-2 AFTER counts as baseline: selftest_rebind_c142_5 4/0; selftest_rebind_c132_5 7/0; selftest_rebase_c132_6 8/0;
selftest_rebase_uidreuse_c143_4 same counts as before (2 pass/2 fail + KeyError rc 1, pre-existing); `py -m py_compile tools/stage_prerun.py`.
Do NOT run `--rebase` on the s07 plan here; that is card 150-a2-5's job.

## Invariants (md5 before = after)
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, graph a3ecb92b, plan s07 10a4f59a, pred e888ab67, recipes d6c8da7b / 273dc3de, s06 VI 569ffbf5, s05 3f9ac26b,
bed 39511877, memory_model 8eec443c, adopted_scratch 658fe5b9. No LabVIEW process; no hooks edit.

## Return conditions
Another shadowing or a different exception found that needs more than renaming; a regression count that differs; R5 passing on the pre-edit file.

## Report `tools/bench/diag_c150_a2_4_facts.md` (<= 25 lines)
Diff line ranges, old/new md5, R1-R5 results, regression counts, md5 table, `OPEN:` line. Facts only.
