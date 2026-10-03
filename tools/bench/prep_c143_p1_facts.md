---
type: facts
status: current
date: 2026-10-03
---
# Card 143-P1 facts: P4 v18 session 3 plan, PROVISIONAL (offline, no LabVIEW, never launched)

## (1) Plan - `plan_ring_p4_s03v18.json` 9d5049d8 (in afb1e79a), maker `prep_c143_p1_mk.py` 12/0 (`prep_c143_p1_mk.log`)
- Provisional base = s02v18's stagesim END (finalized step 34, `sim/ring_p4_s02v18/step_34_create.json` 5f74a804, the re-sim on s01's real
  graph) -> `sim/ring_p4_s03v18_s02end/base_provisional.json` 11811176; sym RX4 -2 RX5 -8 KSF1 -14 ISK1 -16 LWS2 -18 LRS2 -20, neg -21;
  base {provisional: true, sim_of: {plan_ring_p4_s02v18.json, e941ebbf}}.
- v18 ops 1..58 == s01's 24 + s02v18's 34 ids. **Session 3 = v18 ops 59..78, 20 actions `p4_w_stop12`..`p4_lr_num_a`**, kinds stop 1,
  create 9, connect 4, connect_term_uid 2, wire_remove_loose_ends 2, add_sr 2 (N 20, R 14).
- **X10 peak 676.9 <= 680 at 596.5 (provisional start); margin 3.1 MB; next op 79 would be 680.8** (first op over the limit = 79; no
  'of' group refused a cut below the limit). Each 1 MB of extra start load moves the limit by one op or more (read_mb per bind op).
- **subVI drops: PS1 (op 79, p4_s1_pickslot) and SQ1 (op 88, p4_s2_seqcheck) are NOT in session 3**; op 79 is exactly the op the cut stops at.
- One cross ref: `p4_w_stop12` `new:LRS2.value` -> -20 (s02-made); none to s01 symbols, none to a later session's symbol (probe
  `prep_c143_p1_probe.log`).
- Pass A replays to its end; 16 end rows all tied (session-3 action or an s02v18 open row); 11 open pairs; SB FINAL provisional,
  open_rows_match; compiled X10 == table. Session table: `prep_c143_p1_session.json` 0c6a1eb2.

## (2) Pred - `plan_ring_p4_s03v18_pred.json` e2e69c04, `prep_c143_p1_pred.py` 6/0 (`prep_c143_p1_pred.log`)
- X10 676.9 at 596.5, X17 PASS. **Census derived {} - all 20 actions census-UNPREDICTED** (same as s02v18).
- **Error List predicted 54 = s02v18's PREDICTED 51 + 3** created nodes with an unwired input (PD322(e)): -48 (SL1R, ''), -57 (SD1R, ''),
  -67 (W1.body, ''); alternative 54 (no base node newly unwired). Basis caveat: -67 is the new While Loop's BODY diagram symbol
  (`new:W1.body`), not a node - whether LabVIEW lists it is unmeasured; -48/-57 are the two add_sr right terminals' owners.
  Base #23166 (s02's alternative item) is unwired at step 0 and wired/gone at the end.

## (3) Dry / prerun / scratch-required
- Recipe dry `prep_c143_p1_dry.log` **FAIL rc 1**: E1 `BASE: the scratch copy's graph differs from the plan's base graph: {'unbound':
  [-21, -19, -16, -15, -12, -11]}` (= s02-simulated objects of the provisional base). Scratch dry `prep_c143_p1_scr_dry.log` same.
- Prerun `prep_c143_p1_prerun.log` **13/3**: X1 (that dry stop), X5 (0 ops executed, cascade), X10 UNMEASURED (base PROVISIONAL)
  (`:24-25,42,46`); every other gate PASS; WARN X14 rows 20 budget 15 (proven: no). Scratch prerun 13/3 identical.
- Same outcome as the two earlier provisional session plans: 140-P1 (`prep_c140_p1_facts.md:22-25`) and 141-P1
  (`prep_c141_p1_facts.md:22-24`); c132_1 on P3b-2 likewise. A dry PASS on a provisional base with session-N-created objects has
  never been reached; it is reached after `--rebase`.
- `--prerun ... --scratch-required`: exit **3** SCRATCH-REQUIRED (CENSUS-UNPREDICTED rows 1..20) (`prep_c143_p1_scrreq.log:3`).

## (4) Recipes + prior art
- `tools/recipes/stage_d1_ring_p4_s03v18.py` 345b2c8b / `_scratch.py` 00378892: copies of the CARD-PINNED s02v18 pair (758b1673 /
  fdf58b0a), names only changed, MEML 680. Since then card 143-1 changed the s02v18 pair (now 4af581f4 / 7d80df4d: scratch
  MEM_STOP = SX.X10_FAIL_MB, adopt work name D1_ring_p4s02_<ts>.vi, `SX.save_for_resume` before report_stop;
  `archive/peer/2026-10-03-priorart-c143-1-p4s02v18-r3.md:473-478`).
- Prior-art review `archive/peer/2026-10-03-priorart-c143-p1-p4s03v18.md` (`prior_art_c143_p1_p4s03.log`): **settled-already** - exactly
  those three missing changes (scratch:18 stop 690; scratch:69 no work_name; recipe:46-47 no save_for_resume; PD328(a), PD329(a)(b)).
  STOP RECORDs armed on both files; NOT released (no citation-backed FIXED/REFUTED possible without changing the files).
