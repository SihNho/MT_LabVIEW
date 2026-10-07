---
type: facts
status: current
date: 2026-10-07
---
# Card 144-P1 facts: P4 v18 session 4 plan, PROVISIONAL (offline, no LabVIEW, never launched)

## (1) Plan - `plan_ring_p4_s04v18.json` 3353cfc4 (in 9c5f81e1), maker `prep_c144_p1_mk.py` 12/0 (`prep_c144_p1_mk.log`)
- Provisional base = s03v18's stagesim END (finalized step 20, `sim/ring_p4_s03v18/step_20_create.json` 5f31db45, the sim on s02's REAL
  graph after --rebase) -> `sim/ring_p4_s04v18_s03end/base_provisional.json` 9b330384; sym K6 -2 I6 -4 LRB1 -6 RAB1 -8 LWB1 -13 SL1R -27
  SL1L -28 KL1 -33 SD1R -36 SD1L -37 KD1 -42 W1 -45 W1.body -46 LRN4 -49, neg -50; base {provisional: true, sim_of: {plan_ring_p4_s03v18.json, da66a030}}.
- v18 ops 1..78 == s01's 24 + s02v18's 34 + s03v18's 20 ids. **Session 4 = v18 ops 79..97, 23 actions `p4_s1_pickslot`..`p4_t_n1_out`**,
  19 ops: create 12, connect 4, tunnel 2, stop 1 (N 19, R 15).
- **X10 peak 677.6 <= 680 at 596.0 (provisional start); margin 2.4 MB; next op 98 would be 681.5** (first op over the limit = 98; no
  'of' group refused a cut below the limit).
- **PS1 (op 79, `RingPickSlot_v0.vi`) is the session's first action; SQ1 (op 88, `RingSeqCheck_v0.vi`) is ALSO in session 4.**
- 13 cross refs, all to s03 symbols (W1.body -46 x7, W1 -45 x3 incl. W1.cond, SL1L.inner -28 x2, LRN4.value -49); none to s01/s02, none to a
  later session (probe `prep_c144_p1_probe.log`).
- Compile differs from v18 at ONE op: v18 op 91 `p4_w_last_gt` is `wire_sr` (reg new:SL1L, made in s03); bound to uid -28 it compiles to
  `connect`, which stagexec routes to wire_sr at run time when it touches a base register's inner face (`stagexec.py:1494-1505`, `:2576-2579`,
  card 112-1 T1). The copied X10s gate (kinds == v18) failed twice on this before the gate was widened to accept exactly that case.
- Pass A replays to its end; 16 end rows all tied (session-4 action or an s03v18 open row); 11 open pairs; SB FINAL provisional,
  open_rows_match; compiled X10 == table. Session table: `prep_c144_p1_session.json` d9bb85ea.

## (2) Pred - `plan_ring_p4_s04v18_pred.json` f325cdc9, `prep_c144_p1_pred.py` 6/0 (`prep_c144_p1_pred.log`)
- X10 677.6 at 596.0, X17 PASS (5 primitives). Census derived {} - all 23 actions census-UNPREDICTED.
- **Error List predicted 60** by the PD349 rule (`prep_c143_3_elrule.ELR.predict`, owners also from s03's real base fsmap c4a11939) = base
  55 (s03v18 PREDICTED total, `plan_ring_p4_s03v18_pred.json` e1ff772c, card 144-1; not yet measured) + new 7 [input -99, -88, -84, -76,
  -51; local -97, -82] - closed 2 [cond -46, local -49]; uncertain []. -51 = PS1 (7 unnamed unwired inputs, PROVISIONAL terminals);
  -88 = SQ1 (n2, Latest, discards).

## (3) Dry / prerun / scratch-required
- Recipe dry `prep_c144_p1_dry.log` **FAIL rc 1**: E1 `BASE: the scratch copy's graph differs from the plan's base graph: {'unbound':
  [-50, -48, -47, -43, -41, -40]}` (s03-simulated objects of the provisional base), 0 of 19 ops executed. Scratch dry same.
- Prerun `prep_c144_p1_prerun.log` **13/3**: X1 (that dry stop), X5 (0 ops executed), X10 UNMEASURED (base PROVISIONAL); WARN X13 x3,
  X14 rows 23 budget 15 (proven: no). Scratch prerun 13/3 identical.
- Same outcome as 143-P1 / 141-P1 / 140-P1 on a provisional base (`prep_c143_p1_facts.md:30-36`); reached after `--rebase`.
- **Whether the PS1 subVI drop resolves in the dry: NOT REACHED** (the dry stops before op 1).
- `--prerun ... --scratch-required`: exit **3** SCRATCH-REQUIRED (CENSUS-UNPREDICTED rows 1..23) (`prep_c144_p1_scrreq.log:3`).

## (4) Recipes
- `tools/recipes/stage_d1_ring_p4_s04v18.py` / `_scratch.py`: copies of the card-pinned s03v18 pair (61b0faf5 / fa6423ab), names only
  changed (plan, pred, card id, stage/work/scratch names, logs, out json), MEML 680, scratch stop SX.X10_FAIL_MB. No prior-art gate fired.
