---
type: facts
status: current
date: 2026-10-02
tags: [card-139-6, ring-p4, v14, meta-step, offline]
---
# Card 139-6 facts (offline only; LabVIEW NOT opened; returned FAIL at the first unexpected gate, maker gate MS)
## 1. v14 maker — `tools/bench/prep_c139_6_mkv14.py` -> `tools/bench/prep_c139_6_mkv14.log` (rc=1 after 1 s, 2 pass / 1 fail)
- M0 PASS: v13 88e3f336, v13 meta 549f4e45, graph 50595c62, mkv11 a582a5ca, mkv13 6057e2b9 (`prep_c139_6_mkv14.log:3`).
- Inheritance `prep_c139_p2_mkv11.py:164-174` copied verbatim (KSF / NEW ids of `:55-69`): the 28 v13-meta gaps all get a step,
  no existing meta step overwritten, no id outside v13 (`prep_c139_6_mkv14.log:4-6`). Steps given: StopAll x4 (KSF, ISK, LWS2 write,
  its wire) -> 1 (from p4_lr_stop12); p4_f_min, p4_k_max_found -> 1; fnum/fgt/fsel tunnels x9 + p4_w_max_sel -> 2; fd/dt x4 -> 3;
  rbR x8 -> 5.
- **FAIL MS (`:8`)**: actions per step **{1: 39, 2: 43, 3: 40, 4: 36, 5: 27}** — step 2 = 43 > the gate's 42 (mkv13's MS bound;
  `docs/d1/ring-p4.md:184` "A step above ~42 is re-cut"). Every other MS clause holds: every id stepped, p4_w_last_gt with p4_t_last,
  0 late symbol refs (`:7-8`). Derived from `:5`: step 2 = 33 v14 ids already stepped in the v13 meta + 10 inherited (fnum 3,
  fgt 3 + p4_w_max_sel, fsel 3); PD316(a)'s "29" counted the v3 id set. Step 1 = 33 + 6, step 3 = 36 + 4, step 5 = 19 + 8.
- V14 PASS (`:9`): `plan_ring_p4_v14.json` 22f58271 = v13 actions / open_rows / finalized unchanged (the stageplan/1 action schema has no
  `step` field, `docs/protocol/stageplan.json` additionalProperties false), goal text only; `plan_ring_p4_v14_meta.json` 29f6535b = v13
  meta byte-equal + `inherited_c139_6` (28 {id, step, session, unit, cite}) + `recut_c139_6`; validates.
## 2. Not run (the card's return-at-first-unexpected rule)
- Step-1 pass A/B (row tying, FINAL), pred, recipe dry/prerun/X10, scratch run, Error List read. Step 1 itself = 39 actions (within 42),
  so the failing clause concerns step 2 only.
- Written, not run: `tools/recipes/stage_d1_ring_p4s1_scratch.py` (wrapper of the unchanged recipe, copy of
  `stage_d1_ring_p3b2b_scratch.py`; log `diag_c139_6_scratch.log`, X10 from `prep_c139_6_scr_prerun.log`, work copy
  `claudeDev\scratch_c139_6_ring_p4s1_<ts>.vi`). The maker's step-1 part (pass A row tying per stagesim's first_divergent rule; base rows
  accepted only if their pair is a declared open row of `plan_ring_p3b2b.json`; pass B FINAL) is in `prep_c139_6_mkv14.py` after the MS gate.
