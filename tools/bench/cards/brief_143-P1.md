---
type: brief
status: current
date: 2026-10-03
---
# Brief 143-P1 — OFFLINE prep of P4 session 3 (pipeline slot beside 143-1)

## Steps
1. Make `tools/bench/plan_ring_p4_s03v18.json` the way `tools/bench/prep_c142_5_mk.py` made s02: v18
   (`plan_ring_p4_v18.json` 2ea6cafa) from op **59**, the longest prefix whose X10 peak ≤ **680** (`memory_model.json`,
   PD331(c)), splitting no `of` pair (PD320(c)). Start load **596.5 MB provisional** (s02's real load is measured by 143-1
   later). Base = stagesim's END graph of s02v18: `{path, md5, "provisional": true, "sim_of": {"plan":
   "tools/bench/plan_ring_p4_s02v18.json", "md5": "e941ebbfaa3d98099bcd10d8c6237ef4"}}`.
2. Report: first/last v18 op id, action count, X10 peak and the NEXT op's peak (margin), whether the subVI drops (PS1 op 79 /
   SQ1 op 88) fall in this session.
3. Pred file (X10, census derivation, Error List prediction with its basis — one item per created node with an unwired
   input, PD322(e)), `--dry` and `--prerun` with counts, `--scratch-required` exit code (accepted `--prerun ...
   --scratch-required` form).
4. Recipe pair `tools/recipes/stage_d1_ring_p4_s03v18.py` + `_scratch.py` as copies of the s02v18 pair (MEML 680), each
   dry + prerun. Then the prior-art review of the s03 recipe (`tools/prior_art_review.py`), verdict recorded; release lines
   only with a citation.
5. If the s02v18 stagesim END graph is missing or the make/replay stops: RETURN with the step and the line.

## Never
- edit stagexec / stagekit / stagesim / stage_prerun / gscript (a LabVIEW card is live beside this, PD281(a));
- launch anything (a provisional plan is never launched).

Facts file: `tools/bench/prep_c143_p1_facts.md`.
