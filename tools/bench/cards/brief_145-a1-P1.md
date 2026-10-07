---
type: brief
status: current
date: 2026-10-07
---
# Brief 145-a1-P1 — OFFLINE prep of P4 session 5 (pipeline slot beside 145-a1-1)

## Steps
1. Make `tools/bench/plan_ring_p4_s05v18.json` the way `tools/bench/prep_c144_p1_mk.py` (d3eb89fd) made s04 (copy it to `prep_c145_p1_mk.py`): v18
   (`plan_ring_p4_v18.json` 2ea6cafa) from op **98** (first op not in s04 = ops 79..97), the longest prefix whose X10 peak <= **680**
   (`memory_model.json` db163e03), splitting no `of` pair (PD320(c)). Base = stagesim's END graph of s04v18 as a PROVISIONAL base
   `{path, md5, "provisional": true, "sim_of": {"plan": "tools/bench/plan_ring_p4_s04v18.json", "md5": "9ff46b0ece1f238c831d7786616c4f05"}}`.
   Start load: use s04's provisional 598.5 MB-class figure only as a stated provisional (s04's real load is measured by 145-a1-1 later);
   report the margin. Key W1 While `#16483` by (uid, class) (PD350(d)).
2. Report: first/last v18 op id, action count, X10 peak and the NEXT op's peak (margin), total sessions left.
3. Pred file for s05 (X10, census derivation, Error List by the PD349 rule `tools/bench/prep_c143_3_elrule.py` with basis — never a hand-typed number),
   `--dry` and `--prerun` with counts, `--scratch-required` exit code (accepted `--prerun ... --scratch-required` form).
4. Recipe pair `tools/recipes/stage_d1_ring_p4_s05v18.py` + `_scratch.py` as copies of the s04v18 pair (fe3f630c / f5e4bdf8, MEML 680, names only
   changed), each dry + prerun. Prior-art review only if the gate demands it.
5. If the s04v18 stagesim END graph is missing or make/replay stops: RETURN with the step and the line.

## Never
- edit stagexec / stagekit / stagesim / stage_prerun / gscript (a LabVIEW card is live beside this, PD281(a)); edit any s04 plan/pred/recipe;
- launch anything (a provisional plan is never launched); touch LabVIEW, the camera or any motor.

Facts file: `tools/bench/prep_c145_p1_facts.md`.
