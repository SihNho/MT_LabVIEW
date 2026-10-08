---
type: facts
status: current
date: 2026-10-08
card: 147-a1-8
---
# Card 147-a1-8 facts: s06 RETRY scratch ran ops 1..21, sink gate PASS, but D / TD / PB FAIL (RESULT 16/4) -> RETURN, NOT adopted

## Before
- `diag_c147_a1_8_check.log` 22/0: 13 card inputs + elrule a5ee7d5c, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun 61d6f590 == pins;
  s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877; no LabVIEW.
- Scratch recipe dry PASS 1/0 (`diag_c147_a1_8_scr_dry.log`), prerun 16/0 with X10 674.2 and X11 PASS licensed (`diag_c147_a1_8_scr_prerun.log:134-136,117`);
  `--scratch-required` rc 3, census unpredicted rows 1..25 (`diag_c147_a1_8_scrreq.log`).
- Launch: `py tools/bgrun.py --material --max-min 50 --retry-card tools/bench/cards/task_147-a1-8.json --log tools/bench/diag_c147_p4s06v18_scratch.log -- py -u tools/recipes/stage_d1_ring_p4_s06v18_scratch.py`; no gate refused it.

## Scratch (ONE run) `tools/bench/diag_c147_p4s06v18_scratch.log` lines 341-690 (bgrun APPENDS; 1-340 = card 147-a1-4's run), BGRUN END rc=1 after 772 s
- Work copy `claudeDev\D1_ring_p4s06_20261008_125230.vi` = NEW byte copy of 3f9ac26b (K3 PASS :398 area); deleted at close (H4 :668), NOT saved, NOT adopted.
- Ops 1..21 all ran. Op 21 wire_indicators raised "target BROKEN after wiring" (:640), DEFERRED to the declared gate (:644).
- PASS: SG-p4_rbA_re1 (:648, readback (a) t3173 on wire 23807, (b) t5171 #5058 on 23807, (c) sources on 23807 == [5171], (d) rows 6030 = read after op 21);
  E1 every checkpoint == sim incl. op 21 (:649); NG; FR (:651); PRIM on #30300 (:588); H5 refs 21 == 21 (:666); H2 input unchanged; H3; H6.
- FAIL D (:652): new 15 vs sim 16, lost 7 vs sim 8; real lost [10166,10187,28684,29006,29766,29787,9000] (w23807 NOT in it).
- FAIL TD (:657): unwired [(9505,9503,'Value')]; lost [(2832,2626,'array'),(4160,2626,'array'),(4165,2626,'array'),(9505,9503,'Value'),(9508,9503,'Value')]; recycled_uids same 5.
- FAIL PB (:659, FATAL before save): missing ['2626|Terminal|array|0..3']; STOP line :660. RESULT 16/4 (:683), first_fail D.
- CENSUS-ALL new by class {IndexArray 1, InnerTerminal 2, Local 1, LoopTunnel 2, OuterTerminal 2, Terminal 4, Wire 12}, lost uids 2 (:655) - NOT written to the pred (census C1 needs fail 0).
- MEMORY: METERED start 615.6 MB (:403; 147-a1-4 run 570.2) vs prerun assumption 612.6 (d +3.0); op-0 read 617.7 (:404); PEAK of this run 661.8 MB (:646)
  vs X10 674.2 (d -12.4); MEM_STOP 680 / MEMSTOP 695 not hit; MEM, MEML, IN, GONE PASS (:686-689). The scratch's own SCRATCH-P4S06V18 line (:685) also says 661.8
  (whole-file max; the old segment's peak 618.7 is lower, so not contaminating this time).
- Handles: after restart 34270 (:395), post-open 46016 (:403), after work 46502 (:667), exit 34004 (:678).
- Not reached: adopt, Error List read / EL-ADVISORY, final EL, fresh load, graph read, load_by_vi. Scripts written, unrun: diag_c147_a1_8_census.py,
  _adopt.py, _elexp.py, _mkgraph.py, _graph.py, _memload.py (copies of the 147-a1-4 ones restricted to the log's LAST segment).

## Review (owed by the Jev ladder)
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c147_p4s06v18_scratch.log | new-problem 0.868 (jev_gate.log 13:06:12) | hypothesis review owed (old path) | dispatched `-Role hypothesis` (task diag_c147_a1_8_hyp_task.md) | ANSWERED 258 s, $2.17, `archive/peer/2026-10-08-c147-a1-8-re1.md` |
- Review REJECTS my claim (ops 19-21 side effects). It reads `diag_c147_p4s06v18_scratch.json` real_end_rows: wiring == sim end (t5171 -> t10975 + t3173 on
  one wire, uid 23807 vs symbolic -25). #2626 2832/4160/4165 renamed 'array' -> 'element' (ops 4, 5, 18; 4168 untouched stays 'array'); #9503 9505/9508
  renamed 'Value' -> '' (op 3); uids/owners unchanged, 9505 still source of w28684. TD keys (uid, owner, name) (stagekit.py:1355-1357), PB key includes
  the name, D keys (wire uid, source identity) so a reused uid 23807 on the same source reads as "kept" (stagekit.py:1360-1371). E1 ignores names and
  wire ids (stagexec.py:845-858, 872-888). Its test: re-score D/TD/PB offline with (uid, owner) keys. Open in the review: whether op 19 really
  deleted w23807; why PB lists 4 missing rows for 3 renamed terminals. NOTHING APPLIED (card rules).

## After: `diag_c147_a1_8_check_after.log` 20/0: pred c4a6a35a and memory_model 88eeb037 UNCHANGED; s05 3f9ac26b, s04 95e408ff, s03 282301ca,
bed 39511877 unchanged; no LabVIEW process (tasklist count 0).
