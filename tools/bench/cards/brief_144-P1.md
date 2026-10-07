---
type: brief
status: current
date: 2026-10-07
---
# Brief 144-P1 — OFFLINE prep of P4 session 4 (pipeline slot beside 144-2)

## Steps
1. Make `tools/bench/plan_ring_p4_s04v18.json` the way `tools/bench/prep_c143_p1_mk.py` made s03 (copy it to `prep_c144_p1_mk.py`): v18
   (`plan_ring_p4_v18.json` 2ea6cafa) from op **79**, the longest prefix whose X10 peak <= **680** (`memory_model.json`), splitting no `of` pair
   (PD320(c)). The session starts with the **PS1 subVI drop** (op 79, `RingPickSlot_v0.vi`); report whether SQ1 (op 88, `RingSeqCheck_v0.vi`)
   falls in this session. Base = stagesim's END graph of s03v18 as a provisional base:
   `{path, md5, "provisional": true, "sim_of": {"plan": "tools/bench/plan_ring_p4_s03v18.json", "md5": "da66a0300851133d93881be3c28f2fdc"}}`.
   Start load: 596.0 MB provisional (s03's real load is measured by 144-2 later; report the margin).
2. Report: first/last v18 op id, action count, X10 peak and the NEXT op's peak (margin), PS1/SQ1 placement.
3. Pred file for s04 (X10, census derivation, Error List prediction by the PD349 rule `tools/bench/prep_c143_3_elrule.py` with basis — never a
   hand-typed number), `--dry` and `--prerun` with counts, `--scratch-required` exit code (accepted `--prerun ... --scratch-required` form).
4. Recipe pair `tools/recipes/stage_d1_ring_p4_s04v18.py` + `_scratch.py` as copies of the s03v18 pair (main 61b0faf5 / scratch fa6423ab,
   MEML 680), each dry + prerun. Prior-art review of the s04 recipe only if the gate demands it; a subVI-drop op is a new op kind in this recipe
   family — report whether the dry resolves the drop.
5. If the s03v18 stagesim END graph is missing or make/replay stops: RETURN with the step and the line.

## Never
- edit stagexec / stagekit / stagesim / stage_prerun / gscript (a LabVIEW card is live beside this, PD281(a)); edit s03 plan/pred/recipes;
- launch anything (a provisional plan is never launched); touch LabVIEW.

Facts file: `tools/bench/prep_c144_p1_facts.md`.
