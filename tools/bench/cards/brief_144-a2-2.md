---
type: brief
status: current
date: 2026-10-07
---
# Brief 144-a2-2 - rebase session 4 on the REAL s03 graph (OFFLINE, ALONE of tooling; docs/d1/ring-p4b.md PD336)

Context: card 144-a2-1 adopted `claudeDev\D1_ring_p4s03_20261007_202957.vi` (282301ca) and read its graph
`tools/bench/graph_ring_p4s03_20261007_205535.json` (5638469b; fresh load 598.5 MB, 610.0 after reads). The s04 plan
`plan_ring_p4_s04v18.json` (3353cfc4, v18 ops 79..97, 23 actions) was made PROVISIONAL on stagesim's end of s03
(`tools/bench/prep_c144_p1_facts.md`). Note from 144-a2-1: W1 While `#16483` re-uses the uid of the wire the plan cut
(w16483) - key anything citing 16483 by (uid, class).

## Steps (measure and report; no result-dependent action)
1. `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s04v18.json --graph tools/bench/graph_ring_p4s03_20261007_205535.json`
   (copy the plan first to `tools/bench/plan_ring_p4_s04v18_provisional_3353cfc4.json` so the provisional bytes survive).
   Report the REBIND / REUSE-NOTED lines and the new md5.
2. X10 for the plan at the MEASURED start 598.5 MB (fresh load of the s03 file; 610.0 after reads is the reads' own cost,
   already in the model): peak, margin to 680, next op's peak. Report only; do not re-cut.
3. Regenerate the s04 pred EL block by the PD349 rule (basis = the adopted s03 expected EL file
   `tools/bench/errorlist_expected_D1_ring_p4s03_20261007_202957.json`, 55 items, MEASURED, not the s03 prediction).
4. `--dry` and `--prerun` on BOTH s04v18 recipes (`tools/recipes/stage_d1_ring_p4_s04v18.py`, `_scratch.py`), counts and any
   failing gate; whether the PS1 subVI drop (op 79) resolves in the dry; and `--prerun ... --scratch-required` exit code.
5. Report everything as facts; return at the first unexpected result.

## Never
edit stagexec / stagekit / stagesim / stage_prerun / gscript / any hook; touch LabVIEW; launch a recipe for real.
Facts -> `tools/bench/prep_c144_a2_2_facts.md`.
