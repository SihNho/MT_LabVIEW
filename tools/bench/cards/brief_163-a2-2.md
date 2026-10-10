---
card: 163-a2-2
status: current
date: 2026-10-10
---
# Brief 163-a2-2 (assignment 163-1) - retry of 163-a2-1: prior-art review of the step-3 scratch recipe, then the ONE scratch, adopt

Card 163-a2-1 stopped before launch (`tools/bench/diag_c163_a2_1_facts.md` md5 64b4a6f0): `guard_cycle.py` demands a prior-art review newer than `stage_d1_ring_p5s02c_scratch.py`
(newest is c160-d4-1, 07:20) and the card's `flags.peers` did not allow `priorart`. All its other pre-checks passed (hashes 10/0, check_launch ALLOW, `--scratch-required` rc 3).
This card HAS `priorart` in `flags.peers`.

Everything in `brief_163-a2-1.md` (82c768b9) holds, with these deltas:
1. **Launch form:** bgrun has no `--unverified-card` option. The working form is the recipe form (as 162-a1-2 launched):
   `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c163_p5s02c_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02c_scratch.py --unverified-card tools/bench/cards/task_163-a2-2.json`
   (re-run `check_launch` on that exact string first, card id 163-a2-2; expect ALLOW).
2. **Prior art first (owed, the gate said so):** run `py tools/prior_art_review.py` for `tools/recipes/stage_d1_ring_p5s02c_scratch.py` (and the main recipe `stage_d1_ring_p5s02c.py` for the later launch if the tool takes both).
   Read how 162-a1-2 / c160-d4-1 invoked it (`archive/peer/2026-10-10-priorart-priorart-c160-d4-1-p5s02b.md`). The review ends with verdict `novel` or a release line (`REFUTED:` / `FIXED:`) with its
   citation under `## What was done with it`; quote the verdict and the disposition. Any verdict other than `novel` that you cannot release with a citation = RETURN with the text (no launch).
3. Then the single scratch, adopt, Error List, graph, memory-model entry, pred census, `adopted_scratch.jsonl` record, end-of-card hashes and LabVIEW gone, exactly as brief_163-a2-1 items 4-7.
   Facts file: `tools/bench/diag_c163_a2_2_facts.md` (<= 45 lines); helpers `diag_c163_a2_2_*`. Names `163-a2-1` in brief_163-a2-1 read `163-a2-2` here.
4. The pre-checks of 163-a2-1 are not repeated except: hash the card inputs once, check_launch on the exact launch string, `--scratch-required`.
