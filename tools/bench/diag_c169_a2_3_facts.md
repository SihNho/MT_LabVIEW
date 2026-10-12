# Card 169-a2-3 facts (drain fp-100 / fp-99 after the fp-98 revert) - status PASS

- Pins: all 9 card inputs matched their md5 at start (stage_prerun.py db81a1d3, protocol.py 055870f3); `protocol.py requires` PASS 2/0
  (tools/bench/cards/requires_169-a2-3.json). stage_prerun.py and protocol.py were NOT edited by this card (md5 unchanged at the end).
- No LabVIEW, no hardware. Every self-test ran alone through bgrun (two sequential batches, no parallel runs).

## Step 2 - selftest_c169_fp98_100.py (A1-A4 replaced, B1-B4 and C1-C2 kept)
- New A1/A2: x5_count(['rbw_method410']) PASS 'ops 0 vs plan wire rows 0'; + 'connect_wire' FAIL 'ops 1 vs plan wire rows 0' (selftest_c169_fp98_100.py:66-71).
- New A3: --prerun of diag_c167_a1_1_rbw.py as it is: X5 PASS ops 0, X10 PASS; A4: a temp copy with one plan-less connect_wire op -> X5 FAIL
  ops 1 vs 0; A5 temp copy deleted (selftest_c169_fp98_100.py:72-93).
- Result 13 pass / 0 fail (diag_c169_a2_3_selftest.log:16, BGRUN END rc=0 after 18s).

## Step 3 - existing self-tests, before (169-a2-2 `diag_c169_a2_2_before_*.log`) -> now (`diag_c169_a2_3_*.log`)
- c115c 9/1 -> 9/1 (T9, already failing; :14); c115a 8/0 -> 8/0 (:12); c148 8/0 -> 8/0 (:12); headcmp 2/0 -> 2/0 (:11); stageplan 12/0 -> 12/0 (:159)
- c106e 14/1 -> 14/1 (E1, already failing; :19); c114 15/1 -> 15/1 (R4; :20); c114d 11/1 -> 11/1 (R4; :16); c128b 5/1 -> 5/1 (T4; :12, 474 s)
- c103 0/4 -> 0/4 (already failing before; diag_c169_a2_2_before_c103.log:7 -> diag_c169_a2_3_c103.log:7, 552 s)
- protocol 46/2 -> 48/0 (better; diag_c169_a2_2_before_protocol.log:56 -> diag_c169_a2_3_protocol.log:56); protocol_wiring 66/0 -> 66/0 (:74)
- c106c: TIMEOUT before (diag_c169_a2_2_before_c106c.log, killed 602 s) -> now completes 3/3 in 579 s (diag_c169_a2_3_c106c.log:10).
  Not comparable as a count; C1-C5 are identical to the before log's lines (C2, C3 already FAIL with the same EXECUTOR-STOP
  UNROUTABLE in plan_disp.json, diag_c169_a2_2_before_c106c.log:4-5, written 22:10, before the first stage_prerun edit ~22:15).
  New C6 FAIL is that same EXECUTOR-STOP with graph par1359_95_graph.json (diag_c169_a2_3_c106c.log:8), not the 75773b0d md5 fp-100 skips.
  Older record: 6/0 at cycle 152 (diag_c152_a2_1_regress_after.log:15) - the breakage is between cycle 152 and 22:10 today.
- check_command guards (no 169-a2-2 before run): chat_p3 10/0 (diag_c169_a2_3_chat_p3.log:15);
  c125_1 16/4 (diag_c169_a2_3_c125_1.log:24) - the SAME 4 labels (A1, B3, C1, D1) failed on 2026-10-08 (diag_c148_a1_1_before_c125.log:7,13,14,17,27);
  no c125_1 command contains `drive_original_copy` (RUN_VI_CMD_RE, protocol.py:572), so the fp-99 hunk cannot change its outcome.
- Worse counts: none. Nothing reverted.

## Step 4 - drain calls
- `py tools/gate_fp.py drain --id fp-100 --fixed tools/stage_prerun.py:278 --selftest selftest_c169_fp98_100` -> `DRAINED fp-100 (tools/stage_prerun.py:278, selftest_c169_fp98_100)`
  (fix: POST_EDIT_NOTE_RE stage_prerun.py:202-208, used at :278; self-test B1-B4)
- `py tools/gate_fp.py drain --id fp-99 --fixed tools/protocol.py:1203 --selftest selftest_c169_fp98_100` -> `DRAINED fp-99 (tools/protocol.py:1203, selftest_c169_fp98_100)`
  (fix: protocol.py:1199-1205; self-test C1-C2)
- Queue after: fp-98, fp-101, fp-102 still `open`; fp-99, fp-100 `drained` (gate_fp_queue.jsonl).
- fp-98 stays open: X5 failing an UNPLANNED remove_bad_wires is a pinned rule (card 115-3, selftest_stage_prerun_c115c.py T8), and the 167 script
  already passes X5 through its label rbw_method410 (A3 above); changing the pinned rule is the judgement session's.

skipped: fp-98, fp-101, fp-102 and hook entries (card); a HEAD-protocol "before" run for c125_1/chat_p3 (code argument + 10-08 log instead);
diagnosing c106c C2/C3/C6 (pre-existing, outside this card); the labview:read self-tests (c110g, c128, graphload) and c128b_mktrace (writes a fixture).
