# Context for the DIFF-ONLY prior-art review c148-s06-scratch (card 148-a2-2; docs/d1/ring-p4c.md PD358(c), PD359(e))

Under review: `tools/recipes/stage_d1_ring_p4_s06v18_scratch.py` (md5 31009bfce0c0487b0600359c3dac2bd0), the FULL
scratch run on a byte copy that precedes the real launch of ring P4 session 6 (`tools/recipes/stage_d1_ring_p4_s06v18.py`,
md5 d947df5d9347b389dc4e4b221bf9d241). Its approved sibling is `tools/recipes/stage_d1_ring_p4_s03v18_scratch.py`, last
reviewed in `archive/peer/2026-10-03-priorart-c143-p2-p4s03v18.md` (verdict novel). Review ONLY the substantive changed
lines listed above (the gate code - sink gate SG, E1 real==sim, D/TD/PB structural gates, licence handling, MEMSTOP).

Inputs the changed lines use (read them if a line refers to them):
- plan: `tools/bench/plan_ring_p4_s06v18.json` (md5 cfbd9823d3b47be39de94f2125ad6b66)
- licence: `tools/bench/plan_ring_p4_s06v18_licence.json` (md5 7f70bbf9f64de105f25380f260632d56)
- prediction: `tools/bench/plan_ring_p4_s06v18_pred.json`
- step doc: `docs/d1/ring-p4c.md` (PD354-PD359), index `docs/d1/INDEX.md`

The question is prior art only: does any changed line re-build a gate, helper or check the project already owns
(stagekit.py, stagexec.py, stage_prerun.py, adopt_scratch, earlier s04/s05 scratch recipes), or contradict a measured
or decided fact in those files? Cite file:line for every finding.
