# Context for the DIFF-ONLY prior-art review c150-s07-scratch (card 150-a3-2; docs/d1/ring-p4c.md PD364(c), PD365(d)(e), PD366(e)(g))

Under review: `tools/recipes/stage_d1_ring_p4_s07v18_scratch.py` (md5 80dbdb4175bd9ce18911ef4b38025fe3), the FULL
scratch run on a byte copy that precedes the real launch of ring P4 session 7 (`tools/recipes/stage_d1_ring_p4_s07v18.py`,
md5 e0f1152feffa81dde5f2d3b215366e0e). Its approved sibling is `tools/recipes/stage_d1_ring_p4_s06v18_scratch.py`
(md5 31009bfc), reviewed in `archive/peer/2026-10-08-priorart-c148-s06-scratch.md` (verdict novel) and run once with a
structural PASS 22/0 (`tools/bench/diag_c147_p4s06v18_scratch.log:1040`, adopted). Review ONLY the substantive changed
lines the dispatcher lists: per the guard_cycle refusal there are 3 substantive lines and no new classes. The only
non-name change is the sink-gate assertion (recipe:33-35): one declared sink gate per s07 census row (R.SG_CENSUS, read
by the build recipe from `tools/bench/prep_c150_a1_1_session.json`, 2 rows) instead of "exactly ONE".

Inputs the changed lines use (read them if a line refers to them):
- build recipe: `tools/recipes/stage_d1_ring_p4_s07v18.py` (SG_CENSUS / SGS / SINK_GATES / SINK_FNS at :50-74, :119-120)
- plan: `tools/bench/plan_ring_p4_s07v18.json` (md5 08c2ad4d2e6dd4bddd4dd5b18326562c)
- licence: `tools/bench/plan_ring_p4_s07v18_licence.json` (md5 aedbe1f168e4cd8c18d300848ce0b788)
- prediction: `tools/bench/plan_ring_p4_s07v18_pred.json` (md5 6f46fc3c67b3a7f3c045d07a2fa7163c)
- offline prep facts: `tools/bench/diag_c150_a3_1_facts.md`; step doc `docs/d1/ring-p4c.md`, index `docs/d1/INDEX.md`

The question is prior art only: does any changed line re-build a gate, helper or check the project already owns
(stagekit.py, stagexec.py check_sink_gates, stage_prerun.py, adopt_scratch, the s06 scratch recipe), or contradict a
measured or decided fact in those files? Cite file:line for every finding.
