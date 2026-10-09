---
type: facts
status: current
date: 2026-10-09
card: 156-a2-1
---
# Card 156-a2-1 facts: pre-checks all == prediction; the ONE scratch launch REFUSED by the launch gate (PB dry PASS-UNVERIFIED, card names no DRY-UNVERIFIED-OK); BLOCKED, fp-76; LabVIEW never started
## Invariants before `diag_c156_a2_1_inv_before.log` RESULT 60/0
- Every card input md5 == pin (plan 4284c22a, pred 31d8e9be, licence e8fd6a98, MAIN b52b9ff5, scratch 71c3aed4, stagexec 25a1494c, stagesim eb99c6ba,
  stagekit aec03c6c, stage_prerun 9decb20f, vigraph a7eb58c7, addrcheck 207beb0d, gscript 1a80236e, graph 6716c499, ring-p5.md 742e54c4);
  P5-1 adopted VI 7f2582ae, P5-1a 2482fe7b, P5-1b 7f2582ae; memory_model c87d170a; adopted_scratch.jsonl dd0aa787; snapshot 153 P4+hooks files.
## Pre-checks (all == brief item 1 / diag_c156_a1_1_facts.md)
- dry MAIN PASS 1/0, PASS-UNVERIFIED PB, coverage 35/36 (`diag_c156_a2_1_dry.log:73-74`); dry scratch PASS 1/0, PASS-UNVERIFIED PB, 29/32 (`_scr_dry.log:88-89`).
- prerun MAIN PASS 16/0 (`_prerun.log:101`): X10 peak 672.1 (:96), Executor-only 667.0 (:95), X17 PASS (:85), X14 WARN rows 23 budget 15 (:97).
- prerun scratch PASS 16/0, X10 667.0 (`_scr_prerun.log:111,116`); `--scratch-required` rc 3, CENSUS-UNPREDICTED rows 1..8,10..23 (`_scrreq.log:4`, prerun :87).
- `--check-launch tools/recipes/stage_d1_ring_p5s02a_scratch.py` ALLOW rc 0 (`_checklaunch.log:3`) - VACUOUS: the CLI gets a bare path, no `py` command,
  so launched_stage_scripts finds no unit and returns True (tools/stage_prerun.py:4821-4824).
## Launch - REFUSED by guard_bash (no LabVIEW started, no byte copy made)
- Command: `py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c156_p5s02a_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py`.
- Refusal: "LAUNCH GATE (card 134-1, PD287(a)): ...scratch.py's newest dry is PASS-UNVERIFIED (2026-10-09 15:20:53); the gates ["PB frame-keyed cdiff(S1,
  real end) by POSITION ..."] were never evaluated on non-stub data. Name each as expected in the bound card (a `rules`/`pass` string
  'DRY-UNVERIFIED-OK: <label prefix>; ...') and pass `--unverified-card <card path>`" (tools/stage_prerun.py:4888-4895, unverified_card_names :3343-3360).
- task_156-a2-1.json `rules` / `pass` carry no `DRY-UNVERIFIED-OK:` string, so `--unverified-card` on this card cannot release it; the brief EXPECTED
  the PASS-UNVERIFIED PB (brief_156-a2-1.md:16) but the card does not name it. Not routed around (no other card, no env bypass, no card edit).
- Logged `fp-76` (gate guard_bash) in tools/bench/gate_fp_queue.jsonl. Precedent: 155-a3-1's dry was plain PASS (`diag_c155_a3_1_scr_dry.log:75`), so
  no recent card needed the string; the only card carrying it is 134-1 (result_134-1.json).
## Not done (depend on the scratch): E1 per move_in op, metered start/peak, adopt, final EL, graph read, load_by_vi entry.
## Invariants after `diag_c156_a2_1_inv_after.log` RESULT 59/0
- Every pin unchanged; 153 P4 recipes/plans + tools/hooks files unchanged; memory_model c87d170a, adopted_scratch.jsonl dd0aa787 unchanged;
  claudeDev P5 files = p5s01 7f2582ae, p5s01a 2482fe7b, p5s01b 7f2582ae; no _elc_* / scratch_c156_*; `tasklist` LabVIEW.exe: no task. Handles: not
  read (LabVIEW never started).
## Gate-ladder: no stage/recipe gate failed (the refusal is a launch gate, before any run); no JEV-LADDER row; no hypothesis review dispatched.
## Files written: diag_c156_a2_1_inv.py (copy of diag_c155_a3_2_inv.py f5573b02; lines 5-10, 23-52, 54, 59, 87-89 = pins/names), _inv_snap.json,
  the 8 pre-check / inv logs above, this file. Records: prerun_records.jsonl (dry/prerun), gate_fp_queue.jsonl (fp-76).
OPEN: re-issue the card with `rules` += "DRY-UNVERIFIED-OK: PB frame-keyed cdiff" and the launch command += `--unverified-card tools/bench/cards/task_<id>.json`?
OPEN: the CLI `--check-launch <path>` ALLOW is vacuous (no units); should pre-checks call it with the full launch command text?
OPEN: diag_c156_a2_1_inv.py is the 4th per-card copy of the inv helper (diag_c155_a3_1_inv.py, diag_c155_a3_2_inv.py, diag_c154_a3_3b_inv.py); extraction outside globs.
