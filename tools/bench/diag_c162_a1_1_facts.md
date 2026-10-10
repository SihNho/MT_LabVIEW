---
type: facts
status: current
date: 2026-10-10
card: 162-a1-1
---
# 162-a1-1 facts: pre-checks equal; the launch gate on the FULL command REFUSES (two causes, review-confirmed) -> BLOCKED before launch. No LabVIEW opened, nothing launched, nothing adopted.
## 1. Hashes (diag_c162_a1_1_hash.py, hashlib; protocol.input_md5_changes for the card inputs)
- before (diag_c162_a1_1_hash_before.log) 9/0: all 23 md5-pinned card inputs equal; s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, p5s02a 94ffff94;
  stagekit 9b8f82c1, stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f; memory_model 5b87de43, pred a1fd43fb, adopted_scratch 83e74ded.
- after (diag_c162_a1_1_hash_after.log) 9/0: identical; claudeDev holds only D1_ring_p5s02a_20261010_023239.vi among *p5s02*.
## 2. --scratch-required (diag_c162_a1_1_scrreq.log): `SCRATCH-REQUIRED | stage_d1_ring_p5s02b.py | CENSUS-UNPREDICTED ... rows [1..20]`, rc 3 (as expected).
## 3. check_launch on the FULL command (diag_c162_a1_1_checklaunch.py, log diag_c162_a1_1_checklaunch.log) - REFUSE (predicted ALLOW)
- CMD `py tools/bgrun.py --material --max-min 50 --unverified-card tools/bench/cards/task_162-a1-1.json --log tools/bench/diag_c161_p5s02b_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02b_scratch.py`
- `REFUSE LAUNCH GATE (card 134-1, PD287(a)): ...newest dry is PASS-UNVERIFIED (2026-10-10 10:16:18); the gates ['CEN2 new-object census (classes of the pred) == plan_ring_p5s02b_pred.json census'] were never evaluated on non-stub data. Name each ... 'DRY-UNVERIFIED-OK: <label prefix>'`
- Cause 1: entries are matched as label PREFIXES (stage_prerun.py:4980 `u.startswith(n)`); task_162-a1-1.json:85 (= task_161-b3-1.json:83) says `CEN2 census unpredicted`, not a prefix of `CEN2 new-object census ...`.
- Cause 2 (review, confirmed by test): the scratch recipe has NO prerun record. diag_c162_a1_1_discrim.log: scratch sha256 2235182c68b8 has one record, dry PASS-UNVERIFIED 10:16:18 rule 3;
  with the prefix patched to `CEN2 new-object census` (in-process only), check_launch REFUSES "has no prerun PASS record for sha256 2235182c68b8... Run first: --dry / --prerun tools/recipes/stage_d1_ring_p5s02b_scratch.py".
  diag_c161_b2_1_facts.md:19-21 lists a prerun of the MAIN recipe only (prep_c161_b2_1_prerun.log).
- Why c161 said ALLOW: prep_c161_b2_1_checklaunch.log ran the CLI on a BARE path; launched_stage_scripts finds no launched unit (stage_prerun.py:3186-3189) and check_launch returns (True, "") (:4919-4920), a vacuous ALLOW.
- The later gates (decision 4 :5006, RETRY_CAP :5010, check_scratch :5013, fn_record_gate :5016) were never reached for this recipe.
- Not a gate false positive (the gate is right on both causes): NOT logged to gate_fp.
## 4. Log-name conflict found before launch (for the re-issue)
- The scratch recipe reads METER lines from its own constant LOG = diag_c161_p5s02b_scratch.log (stage_d1_ring_p5s02b_scratch.py:29, read at stagekit.py:2836).
  A bgrun --log diag_c162_p5s02b_scratch.log (brief_162-a1-1.md:13) would leave that file absent -> peak None -> GATE MEM FAIL (stagekit.py:2843). It writes diag_c161_p5s02b_scratch{.json,_sum.json} too (:32).
## 5. Jev ladder / review
| log | ladder class p | NEXT-ACTION | what I did | result |
| diag_c162_a1_1_checklaunch.log | our-script-bug p=0.480, below 0.65 old path (jev_gate.log 10:41:17) | hypothesis review owed | dispatched claude -Role hypothesis (flags.peers) | ANSWERED 108 s, $1.03; claim 4 refuted; disposition filled |
- archive/peer/2026-10-10-c162-a1-1-checklaunch.md; its discriminating test = diag_c162_a1_1_discrim.log (FAIL = the review's predicted outcome, run after the review).
## 6. End state: no LabVIEW process (tasklist empty); lock untouched; no recipe / plan / pred / licence / EL / stage-tool / hook / card edit; memory_model and pred unchanged.
OPEN: the re-issued card needs `DRY-UNVERIFIED-OK: CEN2 new-object census` (a true prefix) AND a `--prerun` (and fresh `--dry`) of stage_d1_ring_p5s02b_scratch.py before launch - who runs the scratch prerun, given "do NOT redo prerun"?
OPEN: launch log name - the recipe's constant diag_c161_p5s02b_scratch.log (MEM gate works) or c162 as the brief says (MEM FAIL unless the recipe changes)?
OPEN: diag_c162_a1_1_discrim.log (FAIL by design, after the review) is the newest failing log; does guard_peer need a disposition line for it before the next build?
