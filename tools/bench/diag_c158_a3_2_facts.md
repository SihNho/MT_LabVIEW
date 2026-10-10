---
type: facts
status: current
date: 2026-10-10
card: 158-a3-2
---
# Card 158-a3-2 facts: pre-checks == prediction; the scratch launch was REFUSED by guard_cycle (prior-art review older than the recipe); the card's flags forbid the priorart dispatch -> BLOCKED. No LabVIEW opened.
## Invariants before (`diag_c158_a3_2_inv_before.log`) 61/0
- Every card input md5 == pin (stagekit 07f9e35f, pred ed84b5fd, scratch 64b4f18b, stagexec 7a712ccb, plan 4284c22a, licence e8fd6a98, MAIN b52b9ff5, ring-p5 0f9ac5b0 ...);
  s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, failed copy 152721 cac5236b, memory_model c87d170a, adopted_scratch dd0aa787. Nothing changed after (no LabVIEW, no edit).
## Pre-checks on the current bytes
- dry MAIN `=== DRY PASS ... coverage 35/36 ... unverified 0` (diag_c158_a3_2_dry.log); dry scratch PASS 34/37, unverified 0 (_scr_dry.log).
- prerun MAIN 16/0, `X10 ... predicted peak 674.7 MB (fail above 680.0)` <= 675; Executor-only 669.6; X14 WARN rows 23 budget 15 (proven: no) (_prerun.log).
- prerun scratch 16/0, X10 669.6, recorded 664.6 (c156 log) (_scr_prerun.log); `--scratch-required` rc 3 CENSUS-UNPREDICTED rows 1-8,10-23 (_scrreq.log).
- check_launch on the full command (diag_c158_a3_2_checklaunch.log 2/0): `RETRY_CARD ('158-a3-2', None)`, ALLOW.
## The refusal
- Command: `py tools/bgrun.py --material --max-min 50 --retry-card tools/bench/cards/task_158-a3-2.json --log tools/bench/diag_c158_p5s02a_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py`
- guard_cycle: "this RECIPE HAS NO PRIOR-ART REVIEW NEWER THAN ITSELF. recipe stage_d1_ring_p5s02a_scratch.py (last changed 2026-10-10 01:56); newest priorart review
  archive\peer\2026-10-09-priorart-priorart-c156-a1-1-p5s02a.md (2026-10-09 14:34)". The 01:56 edit is card 158-a3-1's (71c3aed4 -> 64b4f18b, diag_c158_a3_1_facts.md:13).
- Not a gate false positive: the edit adds non-parameter lines (OPCENSUS install/print :42/:52, retry-card print :48), and the pattern is not PROVEN (X14 "proven: no");
  priorart_diff.scope() finds no approved sibling (diag_c158_a3_2_pascope.log: `null`), so a full review is owed. Not logged to gate_fp.
- Doing what the gate says was refused by the card: guard_bash "flags.peers ['hypothesis'] does not include 'priorart' - this card may not dispatch that review"
  for `prior_art_review.py --plan-file tools/bench/diag_c158_a3_2_priorart_plan.md --slug c158-a3-2-p5s02a-retry --trigger cycle-start --recipe <scratch>`.
- The same flag would also refuse brief item 7 (step-2 prior-art review).
## Not done: scratch, adopt, Error List, graph, load_by_vi, failed-copy delete, step-2 plan. No LabVIEW process (tasklist empty). Lock untouched.
## Files written: diag_c158_a3_2_inv.py / _checklaunch.py / _pascope.py / _priorart_plan.md (ready plan text for the review), their logs, this file.
OPEN: issue the prior-art review for the edited scratch recipe (plan text ready: tools/bench/diag_c158_a3_2_priorart_plan.md) - in a card whose flags.peers include priorart, or add priorart to this card's re-issue?
