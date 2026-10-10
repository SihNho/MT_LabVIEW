ATTACK this claim about the failed launch-gate check in tools/bench/diag_c162_a1_1_checklaunch.log (script tools/bench/diag_c162_a1_1_checklaunch.py; recipe tools/recipes/stage_d1_ring_p5s02b_scratch.py).

PREDICTION (from tools/bench/diag_c161_b2_1_facts.md:25-27 and tools/bench/cards/brief_162-a1-1.md:16-18): stage_prerun.check_launch on the FULL launch command
  py tools/bgrun.py --material --max-min 50 --unverified-card tools/bench/cards/task_162-a1-1.json --log tools/bench/diag_c161_p5s02b_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02b_scratch.py
returns ALLOW.
OBSERVED: REFUSE "LAUNCH GATE (card 134-1, PD287(a)): ...newest dry is PASS-UNVERIFIED (2026-10-10 10:16:18); the gates ['CEN2 new-object census (classes of the pred) == plan_ring_p5s02b_pred.json census'] were never evaluated on non-stub data. Name each as expected in the bound card (a rules/pass string 'DRY-UNVERIFIED-OK: <label prefix>; ...')".

CLAIM (mine):
1. check_launch matches each DRY-UNVERIFIED-OK entry as a label PREFIX of the unverified gate label (tools/stage_prerun.py:4980, `u.startswith(n)`; entries parsed at :3439-3456).
2. The card tools/bench/cards/task_162-a1-1.json rules (line ~85) carry "DRY-UNVERIFIED-OK: CEN2 census unpredicted". "CEN2 census unpredicted" is not a prefix of "CEN2 new-object census (classes of the pred) == ...", so the gate refuses. The gate behaves as designed; the defect is the card's wording (copied from task_161-b3-1.json:83, never launched).
3. The c161 "ALLOW" (tools/bench/prep_c161_b2_1_checklaunch.log) was the CLI form `--check-launch <bare recipe path>`: launched_stage_scripts finds no launched unit in a bare path, and check_launch returns (True, "") at tools/stage_prerun.py:4919-4920 - a vacuous ALLOW that never tested the unverified-card naming.
4. Fix is outside this material card: the card must say e.g. "DRY-UNVERIFIED-OK: CEN2 new-object census" (a true prefix). Nothing was launched; no LabVIEW opened.

Already ruled out: md5 drift (all 23 card inputs and the 4 VIs and 4 stage tools equal, tools/bench/diag_c162_a1_1_hash_before.log); a missing --unverified-card argument (it is in the command, regex :3435).

Give the strongest reason the claim is wrong, an alternative explanation, what would falsify it, and the cheapest discriminating test (offline only).
