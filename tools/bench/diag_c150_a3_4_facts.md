---
type: facts
status: current
date: 2026-10-08
card: 150-a3-4
---
# Card 150-a3-4 facts: dispo.py rule refined; self-test OLD 22/15, NEW 34/0; archive outputs exactly as expected
## Rule (tools/dispo.py heading_index)
- Heading = the LAST column-0 `## What was done with it` whose section (to the next column-0 `## ` or EOF) is non-empty after
  the `(Claude fills in)` placeholder is stripped; if none is, the LAST heading. Signature unchanged; the 4 sites are not edited.
- md5 tools/dispo.py 27f21667 -> 4b456b18; tools/bench/selftest_c150_a3_3.py fe349588 -> 5ce68563; new tools/bench/prep_c150_a3_4.py.
## Self-test `tools/bench/selftest_c150_a3_4.log` (BGRUN END rc=0, RESULT PASS 4/0)
- Added V6-V8 (cycle17 copy, synthetic SA/SB), R7-R12 + A4-7..12 (d1-s1-diagram-count, 23c-r2, cycle17 copies, SA, SB, all-placeholder SP).
- OLD (first-occurrence snapshots) 22 pass / 15 fail, SITE-FAILS V 4 R 4 A4 6 A9 1 (new old-fails A4-7, A4-10 = pattern A); NEW 34 / 0.
## Archive-output gate (1119 files carrying the heading string)
- Cut differs vs old: 38 inline-quote files + 8 pattern-A files exactly; pattern B (23c-r2, retrospective-cycle17) cut == old (1073 same).
- Output diffs == expected list: V cycle49/148/149; R cycle16/16b/26; A4 8 inline files + 7 pattern-A files (old blank -> new annotated;
  cycle7's output did not change). A4 blank 279 -> 280. A9 old == new (22 candidates). Pattern B: no output diff at any site.
## Regression `tools/bench/prep_c150_a3_4_after.log` (RESULT PASS 18/0)
- `py tools/violations.py`: 0 slugs awaiting; cycle148 under repeated-failure-class, cycle149 under device-failed + inference-over-measurement.
- retrospective-cycle17: 0 lines in violations output (old value, prep_c150_a3_3_before.log; 150-a3-3 code counted it under device-failed).
  device-failed 59 (old) / 61 (150-a3-3) / 60 now (= old + cycle149); repeated-failure-class 42, inference-over-measurement 32.
- Old self-tests unchanged: cycle_runner_retro 9/0 rc0; audit_a9_witness 10/0 rc0; c116a_landed 14/4 rc1 (pre-existing); stamp_window 15/0 rc0.
## Invariants
- 17 md5 pins equal (stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847,
  stagesim 748bbf30, s06 569ffbf5, s05 3f9ac26b, bed 39511877, s07 b3f86b32, card inputs violations/cycle_runner/audit_cycle/briefs/facts).
- tools/hooks: 24 files, every md5 == prep_c150_a3_3_after.log (material_marker.log excepted). No gate_fp entry logged. No LabVIEW process.
OPEN: site comments at violations.py:177, audit_cycle.py:326/:619 still say "LAST column-0 heading" (comment-only; brief said sites unchanged).
