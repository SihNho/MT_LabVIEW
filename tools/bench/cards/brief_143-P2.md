---
type: brief
status: current
date: 2026-10-03
---
# Brief 143-P2 — port 143-1's accepted recipe changes into the session-3 recipe pair (OFFLINE)

143-1 changed the s02v18 pair after its prior-art review r1/r2 (now `stage_d1_ring_p4_s02v18.py` 4af581f4 /
`_scratch.py` 7d80df4d; FIXED lines in `archive/peer/2026-10-03-priorart-c143-1-p4s02v18-r3.md`:473-478): MEM_STOP =
X10_FAIL_MB (PD328(a)), work_name `D1_ring_p4s03_<ts>.vi`, save_for_resume (PD329(a)(b)). 143-P1 wrote the s03v18 pair as
copies of the OLD pair (345b2c8b / 00378892).

## Steps
1. Diff old s02v18 pair (758b1673 / fdf58b0a, from git HEAD) → new pair; apply the same changes to
   `tools/recipes/stage_d1_ring_p4_s03v18.py` / `_scratch.py` (work_name for s03). Nothing else changes.
2. Dry + prerun both on the provisional plan (the E1 BASE-unbound dry stop is EXPECTED on a provisional base, as in 143-P1;
   report it, do not fight it). Prior-art review of the changed s03 recipe; release lines use the VERDICT slugs
   (143-1 fact: a review-slug FIXED line was refused by stop_record).
3. Report the diff (file:line), dry/prerun outcomes, review verdict + file.

Never edit stagexec/stagekit/stagesim/stage_prerun/gscript; never launch. Facts → `tools/bench/prep_c143_p2_facts.md`.
