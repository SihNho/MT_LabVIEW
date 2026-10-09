---
type: facts
status: current
date: 2026-10-09
card: 157-a1-2
---
# Card 157-a1-2 facts: pins re-set, self-tests 20/0 + 21/0; dry + prerun PASS on the new bytes; MAIN X10 peak 679.7 > 675 (card limit) -> RETURN, no re-cut; LabVIEW 0
## Part 1 - re-pin (only the stagekit md5 string changed)
- selftest_c156_passwire.py:161 and selftest_c155_basecase_frame.py:206: "stagekit.py": "aec03c6c" -> "0d8f6d25" (md5sum stagekit.py = 0d8f6d252eac3d0c28fc3a2141f54a14).
- md5 after: selftest_c156_passwire.py 8335875b -> 6be05037; selftest_c155_basecase_frame.py 9ecb15b8 -> e64cd4b5.
- selftest_c156_passwire 20/0 (`diag_c157_a1_2_st156.log:34`, BGRUN END rc=0 691 s); selftest_c155_basecase_frame 21/0 (`diag_c157_a1_2_st155.log:25`, rc=0 57 s).
## Part 2 - tool bytes in use: stagexec 69b1a301, stagekit 0d8f6d25, stagesim eb99c6ba, addrcheck 207beb0d, stage_prerun 9decb20f (all == card pins)
- dry MAIN PASS 1/0, PASS-UNVERIFIED PB, coverage 35/36 (`diag_c157_a1_2_dry.log:78-79`); dry scratch PASS 1/0, PASS-UNVERIFIED PB, 29/32 (`_scr_dry.log:93-94`).
- Checkpoints used, both: (0, 1, 3, 6, 8, 9, 10, 11, 12, 15, 16, 17) (`_dry.log:21`, `_scr_dry.log:33`); dry prints six `FATE step=10` lines (`_scr_dry.log:45-50`).
- prerun MAIN PASS 16/0 (`diag_c157_a1_2_prerun.log:105`): X10 planned peak 679.7 MB, R 14 reads, fail above 680.0 (:99, :101), recorded meter
  UNMEASURED for MAIN (:101); Executor-only 674.6 MB, R 12 (:100); X17 PASS (:90); X14 WARN rows 23 budget 15 (:102); X1 PASS-UNVERIFIED PB (:77).
- prerun scratch PASS 16/0 (`_scr_prerun.log:120`): X10 674.6 MB, R 12 (:114, :116), recorded meter 654.0 from diag_c156_p5s02a_scratch.log (:116).
- Before (old bytes, diag_c156_a2_1_facts.md:14): MAIN 672.1, Executor-only 667.0 -> now 679.7 / 674.6 (+7.6 each, the extra reads at 10,11,12).
- MAIN 679.7 > 675 (PD379(c), docs/d1/ring-p5.md:193) -> card rule "Return (do not re-cut)". Step 1 now ends at action 23 (group F2).
  Nearest group boundaries (group ends [7,8,9,14,17,20,23,26,...], diag_c156_a1_1_facts.md:21): action 20 (end of F1) and action 26
  (next group; old-bytes MAIN there 676.0, diag_c156_a1_1_facts.md:22). MAIN at either boundary with the new checkpoints is NOT computed here.
- `--scratch-required tools/recipes/stage_d1_ring_p5s02a.py` rc 3: CENSUS-UNPREDICTED rows 1..8,10..23 (`diag_c157_a1_2_scrreq.log:3-4`).
## Launch gate on the FULL scratch command (not run; probe tools/bench/prep_c157_a1_2_gate.py 54af5ad6, `diag_c157_a1_2_gate.log`, 3/0)
- Function: stage_prerun.check_launch (tools/stage_prerun.py:4815), called by guard_bash.prerun_gate (tools/hooks/guard_bash.py:376);
  refusal text at stage_prerun.py:4891-4895, card naming at unverified_card_names :3343-3360.
- A as given: REFUSED "LAUNCH GATE (card 134-1, PD287(a)): ...scratch.py's newest dry is PASS-UNVERIFIED (2026-10-09 19:34:57); the gates
  ["PB frame-keyed cdiff(S1, real end) by POSITION ..."] ... Name each ... 'DRY-UNVERIFIED-OK: <label prefix>; ...' and pass `--unverified-card`" (gate.log:3).
- B + `--unverified-card tools/bench/cards/task_157-a1-2.json`: REFUSED, "card ... names no DRY-UNVERIFIED-OK gate" (gate.log:5).
- C + `--unverified-card` on a temp copy of this card with rules += "DRY-UNVERIFIED-OK: PB frame-keyed cdiff": ALLOW (gate.log:7-8).
  Label prefix that releases it: `PB frame-keyed cdiff` (matched by startswith, stage_prerun.py:4884). X10 679.7 does not stop the gate (limit 680).
- stop_record.check_command ALLOW; guard_cycle.premature_build -> no block; prior-art verdict gate: newest review
  archive/peer/2026-10-09-priorart-priorart-c156-a1-1-p5s02a.md has no non-novel verdict, nothing open (gate.log:9-11) - still valid.
  That review's "What was done with it" is EMPTY (guard_peer undisposed check, tools/hooks/guard_peer.py:838-854): it blocks the next prior-art dispatch only.
## Gate FPs logged (no bypass, no hook edit)
- fp-78 guard_peer: a read-only grep naming the prior-art script as a file argument refused as a dispatch (guard_peer.py:832 regex on command text); routed via the Grep tool.
- fp-79 guard_bash card flags: `stage_prerun.py --check-launch "<full launch text>"` refused as a labview:build launch (quoted path); routed via the probe script.
- Gate-ladder: no stage/recipe gate FAILED (all RESULT lines fail 0; >675 is the card rule); no JEV-LADDER row; no review dispatched. LabVIEW never ran; no hooks/recipe/plan/pred/licence/stage-tool/P5 edit.
OPEN: MAIN planned 679.7 > 675 with checkpoints 10-12 added: re-cut step 1 at action 20 (end F1) or accept 679.7 (< 680 X10 limit) - PD379(c) judgement.
OPEN: the launch card for the scratch must carry rules "DRY-UNVERIFIED-OK: PB frame-keyed cdiff" and the command `--unverified-card <its path>`.
OPEN: prior-art review c156-a1-1 has an empty disposition section - write it before any next prior-art dispatch.
