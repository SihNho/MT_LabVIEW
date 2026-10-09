---
type: facts
status: current
date: 2026-10-09
card: 155-a3-1
---
# Card 155-a3-1 facts: P5-1b scratch PASS 20/0 (saved D1_ring_p5s01b_20261009_123319.vi 7f2582ae); RETURNED BEFORE ADOPT - adopt_scratch does not rename to D1_ring_p5s01_
## Pre-checks on the final bytes (all == diag_c155_a2_1_facts.md)
- Invariants before `diag_c155_a3_1_inv_before.log` 48/0: every card input md5 == pin (plan 75a77a00, pred 2f2cbcc3, licence e592cf7a, MAIN 6de2378d,
  scratch 9233749f, stagexec 53e17623, stagesim eb99c6ba, stage_prerun 9decb20f, vigraph a7eb58c7, P5-1a VI 2482fe7b, graph bd67a511, memory_model 386a4cf4).
- dry MAIN 1/0 (`diag_c155_a3_1_dry.log`), dry scratch 1/0 (`_scr_dry.log`); prerun MAIN 16/0, X10 peak 657.2, Executor 652.1, X17 PASS (`_prerun.log`);
  prerun scratch 16/0, X10 652.1 (`_scr_prerun.log`); `--scratch-required` rc 3, CENSUS-UNPREDICTED rows 1..12 (`_scrreq.log`); `--check-launch` ALLOW rc 0 (`_checklaunch.log`).
## Scratch (ONE run) `diag_c155_p5s01b_scratch.log` RESULT 20/0 (:189), BGRUN END rc=0 after 431 s
- NEW byte copy of 2482fe7b = `claudeDev\D1_ring_p5s01b_20261009_123319.vi`; saved md5 7f2582ae54dc5bc42c3df0bdf3c72d2e, 322490 B (:169, gui_save, ExecState 0 by design).
- SG 0 rows (:53); L1 12 actions -> 8 ops == pred kinds, checkpoints (0,2,4,6,7,8) (:54); every STEPX checkpoint diff 0 (:57-147); E1 PASS 8 ops (:148); NG PASS 0 ops (:149).
- FR 1 created object (Local 'records final (1.2 to 1.7)' #31213) on frame [686] == sim (:150). D new 8 == sim 8, lost 0 == 0 (:151). TD renames 0, unlicensed [] (:156).
- PB by position == pred 21 rows / 19 open pairs (:158). PRIM n/a (0 primitive creates; X17 PASS). X11 CLEAN (prep).
- Base-case route (first LabVIEW use): R1 t_qi -> ONE SelectorTunnel #31257 owned by Case #30726 (:129, :140); R2 t_qo -> ONE SelectorTunnel #31293 (:137, :141);
  case_frame_wire on frame 0 (#30914) both times, census diff 0 new nodes (:69, :147). sr_q add_sr bound -5 #31222 / -6 #31225 on loop #10170 (:112).
- CENSUS-ALL net: InnerTerminal 6, OuterTerminal 4, SelectorTunnel 2, LeftShiftRegister 1, RightShiftRegister 1, Local 1, Terminal 1, Wire 8; lost 0. CEN2 UNPREDICTED (pred census {}).
- Memory: METER start 564.3 MB (:55) vs pred start 608.5 (d -44.2) / P5-1a load 602.6 (d -38.3); peak 601.8 (:146, :191) vs Executor 652.1 (d -50.3) / MAIN 657.2 (d -55.4);
  MEM / MEML / IN / GONE PASS (:192-195).
- Handles: PH post-open 45639 -> before-save 46132, HB PASS (:159-160); H5 opened 9 == closed 9; at exit 40215. Input 2482fe7b unchanged (H2); H3 pins hold; H6 files left == [the saved file].
## Adopt - NOT RUN (RETURN, brief_155-a3-1.md item 3)
- The brief wants the adopted file named `D1_ring_p5s01_<stamp>.vi`; `stagexec.adopt_scratch` does no rename: "Nothing is copied or renamed: the recipe saved the
  work copy under the stage's normal name ... so the file IS the stage file" (tools/stagexec.py:4118-4119); its signature has no target-name argument (:4114-4115).
  The scratch recipe names the work copy `D1_ring_p5s01b_<ts>.vi` (tools/recipes/stage_d1_ring_p5s01b_scratch.py:29,52; brief_155-a2-1.md:42-43 "adopted later as D1_ring_p5s01_").
- adopted_scratch.jsonl unchanged (c6041e64); no adopt record for stage_d1_ring_p5s01b; no EL read, no graph read, no load_by_vi entry (memory_model 386a4cf4 unchanged).
## After `diag_c155_a3_1_inv_after.log` 48/0
- Every pin unchanged; 153 P4 recipe/plan + tools/hooks files unchanged vs snapshot; no _elc_* / scratch_c155_* in claudeDev; claudeDev P5 files = p5s01a 2482fe7b + p5s01b 7f2582ae.
- LabVIEW: "LabVIEW gone at exit: True" (scratch log), tasklist LabVIEW.exe = no task (checked after the run).
## Files written by this card (md5)
- diag_c155_a3_1_inv.py cfa8ef91 (copy of diag_c154_a3_3b_inv.py; changed lines 5-10, 18-46, 74-78: pins / names only); diag_c155_a3_1_inv_snap.json ffa6b57a;
  diag_c155_a3_1_peek.py 32821ec4 (read-only print of plan actions / pred EL); scratch outputs diag_c155_p5s01b_scratch.log 7b1a8cc5, .json 263296e4, _sum.json f4af3e63.
## Gate-ladder: no gate failed, no Jev ladder row, no hypothesis review dispatched.
## Script duplication (rule 4 of docs/script-writing.md; extraction is outside this card's write globs)
- OPEN: the inv / adopt / elexp / mkgraph / graph / memload / nodes helpers are re-copied per card (diag_c154_a3_3_*.py, diag_c152_b3_1_*.py); gate() alone in all of them.
OPEN: adopt the PASSed scratch file as-is (`D1_ring_p5s01b_20261009_123319.vi`, 7f2582ae) via adopt_scratch, or make `D1_ring_p5s01_<stamp>.vi` by a byte copy first (no tool renames)? The next card then runs EL / graph / load_by_vi.
