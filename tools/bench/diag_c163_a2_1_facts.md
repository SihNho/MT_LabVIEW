---
type: facts
status: current
date: 2026-10-10
card: 163-a2-1
---
# 163-a2-1 facts: BLOCKED before launch - guard_cycle demands a prior-art review of the scratch recipe; card flags.peers = [hypothesis] forbids dispatching it. Nothing launched, LabVIEW never opened.
## Pre-checks (offline)
- Hashes (diag_c163_a2_1_hash_before.log, 10/0): 19 card inputs equal in the main tree; VIs eb1d0f31 / 2482fe7b / 7f2582ae / 94ffff94 / f9ae7751 equal;
  stagekit dd57c1ca, stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f equal. claudeDev *p5s02*: only p5s02a 94ffff94, p5s02b f9ae7751.
- check_launch FULL command, brief form (--unverified-card before --log): ALLOW (diag_c163_a2_1_checklaunch.log); recipe form (--unverified-card after
  the recipe path, the form 162-a1-2 launched because bgrun has no --unverified-card option): ALLOW (diag_c163_a2_1_checklaunch2.log).
- --scratch-required (diag_c163_a2_1_scrreq.log): rc 3, `SCRATCH-REQUIRED | stage_d1_ring_p5s02c.py | CENSUS-UNPREDICTED ... rows [1..12]`.
- diag_c163_p5s02c_scratch.log absent before launch (ls); tasklist: no LabVIEW process.
## The refusal (launch command, recipe form, run_in_background)
- `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c163_p5s02c_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02c_scratch.py
  --unverified-card tools/bench/cards/task_163-a2-1.json` -> guard_cycle.py: "this RECIPE HAS NO PRIOR-ART REVIEW NEWER THAN ITSELF" (recipe 2026-10-10
  12:18; newest priorart review archive/peer/2026-10-10-priorart-priorart-c160-d4-1-p5s02b.md 07:20).
- Brief item 3 says run the review if the gate demands it, but a prior_art_review.py command was refused by guard_bash.py: "CARD 163-a2-1 ...
  flags.peers ['hypothesis'] does not include 'priorart' - this card may not dispatch that review". Card flags win -> BLOCKED, not routed around.
## Why no exemption applied (diag_c163_a2_1_pa.log, read-only calls of guard_cycle.py:572-589's readers)
- stage_prerun.proven_pattern(scratch recipe): ok=False, clean stages covering the signature = [stage_d1_ring_p5s02a_scratch.py] (needs >= 2);
  signature ops add_shift_reg / create / tunnel / wire, creates DigitalNumericConstant / Function. Main recipe: ok=False, stages [].
- priorart_diff.scope(both recipes) = None (no approved script of the same pattern found) -> no diff-only release.
- The p5s02b scratch (162-a1-2, PASS 20/0) is not among the covering stages (its signature carries no add_shift_reg / create:Function).
## Not done (all depend on the scratch run)
- No scratch, no adopt, no Error List, no graph, no memory_model.json entry, no pred census, no adopted_scratch.jsonl record. Nothing written
  except diag_c163_a2_1_{hash,checklaunch,pa}.py + logs and this file. No recipe / plan / licence / EL / stage-tool / hook edit; no original opened.
## OPEN
- Re-issue with flags.peers including `priorart` (review of tools/recipes/stage_d1_ring_p5s02c_scratch.py, and the main recipe for the later launch),
  or dispatch the prior-art review from a card that may, then re-run this card unchanged.
