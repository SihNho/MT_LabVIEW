---
type: facts
status: current
date: 2026-10-10
card: 158-a1-3
---
# Card 158-a1-3 facts: c156-a1-1 prior-art disposition filled, gate clean; dry + prerun PASS on stagexec df82d75e; planned MAIN 674.7 <= 675; LabVIEW 0
Valid for THESE bytes only: stagexec df82d75e, stagekit 0d8f6d25, stagesim eb99c6ba, addrcheck 207beb0d, stage_prerun 9decb20f, plan 4284c22a,
MAIN recipe b52b9ff5, scratch 71c3aed4 (all md5sum == card pins at start). A later stagexec change (PD384(a)) invalidates the records below.
## Part 1 - disposition (archive/peer/2026-10-09-priorart-priorart-c156-a1-1-p5s02a.md, cf1eab31 -> 536f8b24)
- `## What was done with it` filled: 10 lines, one per finding A1 A2 A3 A4 B1 B2 B3 B4(a) B4(b) C; no FIXED:/REFUTED: keyword (verdict novel).
  A4 + B4(a) stated as CARRIED to the scratch card (pred plan_ring_p5s02a_pred.json:166-199; E1 per run, closer op 12, PD384(b) ring-p5.md:269-274).
- Gate verdict (probe prep_c158_a1_3_gate.py e18343cb, `diag_c158_a1_3_gate.log:3-4`): guard_peer.undisposed('priorart') -> None
  (tools/hooks/guard_peer.py:838); newest prior-art = this file, non-novel [], open []. prior_art_review.py --dry-run NOT run: it writes a
  review card under tools/bench/cards/ (prior_art_review.py:333), outside this card's write globs; the gate function was called instead.
## Part 2 - dry / prerun
- dry MAIN PASS 1/0, PASS-UNVERIFIED PB, coverage 35/36 (`diag_c158_a1_3_dry.log` last lines, BGRUN END rc=0 28 s);
  dry scratch PASS 1/0, PASS-UNVERIFIED PB, 29/32 (`diag_c158_a1_3_scr_dry.log:93`); E1 PASS 17 ops both (`_dry.log:66`, `_scr_dry.log:78`).
- Checkpoints used, all four runs: (0, 1, 3, 6, 8, 9, 12, 15, 16, 17) (`_dry.log:21`, `_scr_dry.log:33`, `_prerun.log:21`, `_scr_prerun.log:33`);
  ops 10, 11 print "diff skipped (not a checkpoint)" (`_dry.log:45,47`); six `FATE step=10` lines, emitted at op 12 (`_scr_dry.log:61-66`).
- prerun MAIN PASS 16/0 (`diag_c158_a1_3_prerun.log:105`): X10 planned peak 674.7 MB, R 12, fail above 680.0 (:99, :101), recorded meter
  UNMEASURED (:101); Executor-only 669.6 MB, R 10 (:100); X17 PASS (:90); X14 WARN rows 23 budget 15, proven no (:102); X1 PASS-UNVERIFIED PB (:77).
- prerun scratch PASS 16/0 (`_scr_prerun.log:120`): X10 669.6 MB, R 10 (:114, :116), recorded meter 654.0 from diag_c156_p5s02a_scratch.log (:116);
  MEM_STOP_MB 680.0, "X10 from the md5-pinned pred 667.0" (:14).
- Planned MAIN 674.7 <= 675 (PD379(c), PD384(b)) -> plan stands, no re-cut. Was 679.7 on stagexec 69b1a301 (diag_c157_a1_2_facts.md:15).
- `--scratch-required tools/recipes/stage_d1_ring_p5s02a.py` rc 3: CENSUS-UNPREDICTED rows 1..8,10..23 (`diag_c158_a1_3_scrreq.log:3-4`).
## Launch gate on the FULL scratch command (not run): stage_prerun.check_launch (tools/stage_prerun.py:4815), refusal text :4888-4895,
## label match by startswith :4884, unverified_card_names :3343. Command: `py tools/bgrun.py --material --max-min 50 --log
## tools/bench/diag_c158_p5s02a_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py` (`diag_c158_a1_3_gate.log:5-10`).
- A as given: REFUSED "...scratch.py's newest dry is PASS-UNVERIFIED (2026-10-09 23:59:30); the gates ["PB frame-keyed cdiff(S1, real end) by
  POSITION ..."] ... a `rules`/`pass` string 'DRY-UNVERIFIED-OK: <label prefix>; ...' and pass `--unverified-card <card path>`" (:5).
- B + `--unverified-card tools/bench/cards/task_158-a1-3.json`: REFUSED, "card ... names no DRY-UNVERIFIED-OK gate" (:7).
- C + `--unverified-card` on a %TEMP% copy of this card with rules += "DRY-UNVERIFIED-OK: PB frame-keyed cdiff": ALLOW, named ['PB frame-keyed cdiff'] (:9-10).
  Label prefix: `PB frame-keyed cdiff`. stop_record.check_command ALLOW; guard_cycle.premature_build no block (:11-12). Probe RESULT 5/0.
## Records / files: prerun_records.jsonl += 6 rows (dry x4 incl. the preruns' own dry, prerun x2; ad4247f0 after); prep_c158_a1_3_gate.py e18343cb (new); logs diag_c158_a1_3_*.log.
- No LabVIEW process at any point (tasklist 0); no hook / recipe / plan / pred / licence / stage-tool / P5 edit; no gate refusal of my commands -> no gate-fp entry.
- Gate-ladder: no stage/recipe gate FAILED (every RESULT fail 0; scrreq rc 3 is the expected answer); no JEV-LADDER row; no review dispatched.
OPEN: the scratch launch card must carry rules "DRY-UNVERIFIED-OK: PB frame-keyed cdiff" and the command `--unverified-card <its path>`.
OPEN: planned MAIN 674.7 leaves 0.3 MB under the 675 step limit; scratch X10 uses the pinned-pred 667.0 for MEM_STOP (scr_prerun.log:14).
