---
type: facts
status: current
date: 2026-10-07
---
# Card 145-a1-P1 facts: P4 session 5 = v18 ops 98..124 (33 actions), PROVISIONAL on s04v18's simulated end; X10 678.5 at 598.5; EL 57; dry FAIL as provisional (same as 144-P1) + NEW X11 FAIL

OFFLINE only, no LabVIEW, nothing launched. No stage tool, s04 plan/pred/recipe edited (md5s unchanged: v18 2ea6cafa, s04v18 9ff46b0e,
recipes fe3f630c / f5e4bdf8).

## Step 1 - plan (prep_c145_p1_mk.log, 14/0, rc 0, 78 s)
- Provisional base `tools/bench/sim/ring_p4_s05v18_s04end/base_provisional.json` c159906d = END state of
  `sim/ring_p4_s04v18/step_23_wire.json` 3c4d8f8c; base ref `{provisional: true, sim_of: {plan_ring_p4_s04v18.json, 9ff46b0e}}`.
- One change vs prep_c144_p1_mk.py: s04 was rebased on the REAL s03 graph, so s01..s03 symbols are REAL uids in END4 (END4 sym = s04
  symbols only). They are resolved s03v18 END sym -> s03 creation map (`creation_map/plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl`
  a6146345) -> real uid, keyed by (uid, class) (PD350(d)) and checked against the s04 rebase where it bound the same symbol (gate R3):
  W1 -> #16483 WhileLoop (== s04 rebase), W1.body -> #29699 Diagram (== s04 rebase), SL1R -> #29403 RSR, SD1L -> #29655 LSR, SD1R -> #29648 RSR.
- 14 cross refs (5 to s03 symbols real, 9 to s04 symbols negative: PS1 -1, IAI1 -26, LRL1 -47, SQ1 -38); none to a later session.
- CUT ops **98..124**, first `p4_t_slot`, last `p4_w_fd_in`, 33 actions, compiled 27 ops (tunnel 3, connect 13, create 6, branch 3,
  move_in 2); wire_sr -> connect on ops 102/103/104 (earlier-session registers SL1R, SD1L, SD1R).
- X10 at PROVISIONAL start 598.5 (s03 file measured fresh load; s04's real load measured later by 145-a1-1): **peak 678.5, margin 1.5 MB**;
  **next op 125 peak 682.4**; no cut refused by an 'of' group. N 27, R 10.
- Pass A replays to end; TIE 19 end rows all tied; pass B FINAL, open_rows_match, 14 open pairs.
- Sessions left after s05 (prep_c145_p1_pred.log FACT SESSIONS-LEFT, same formula and start, estimate): **3** - ops 125..155 (678.9),
  156..186 (678.9), 187..190 (631.5). 66 of 190 ops left after s05.

## Step 3 - pred (prep_c145_p1_pred.log, 6/0) `plan_ring_p4_s05v18_pred.json` 6666a718
- EL by the PD349 rule (prep_c143_3_elrule.ELR.predict, owners from s04's real base a63f5929): base = s04 PREDICTED 60
  (plan_ring_p4_s04v18_pred.json 90eff870) -> **57** = new [] - closed [local -47, sr 29403, sr 29648]; uncertain [[29240, ['y']]]
  (base node newly unwired input, move_in op); open at start [local -47, local -32, sr 29403, sr 29648].
- Census {} - 33/33 actions UNPREDICTED. X17 PASS (3 primitives).

## Step 4 - recipes + dry/prerun (logs prep_c145_p1_{dry,prerun,scr_dry,scr_prerun,scrreq}.log)
- `tools/recipes/stage_d1_ring_p4_s05v18.py` 23c08932, `_scratch.py` cd14eb47: copies of fe3f630c / f5e4bdf8, names only, MEML 680 kept.
- Dry FAIL on both: `BASE: the scratch copy's graph differs from the plan's base graph: {'unbound': [-65, -64, -56, -55, -52, -51]}`
  (executed 0 of 27 ops) - the SAME class as card 144-P1's provisional s04 dry (`prep_c144_p1_dry.log`, unbound [-50..-40]).
- Prerun **12/4** on both: X1 (dry), X5 (consequence), X10 UNMEASURED (provisional base) - all three as in 144-P1 (13/3) - plus
  **NEW X11**: `p4_w_tp_row` (op 118) and `p4_w_rp_row` (op 119) wire Build Array #2626 inputs while sibling (2626, array) is an open row
  (v18 open_rows: "carried from R2: licensed rename (plan_l2b1_licence.json)"); the only pb-licence/1 file names plan_l2b1.json, none
  names a P4 plan. WARN X13 x4, X14 rows 33 > budget 15 (proven: no).
- `--prerun stage_d1_ring_p4_s05v18.py --scratch-required ...`: exit **3** SCRATCH-REQUIRED, CENSUS-UNPREDICTED rows 1..33.

## md5s
| file | md5 |
|---|---|
| tools/bench/plan_ring_p4_s05v18.json | b7d27e24e27a196a071c490053feafaa |
| tools/bench/plan_ring_p4_s05v18_in.json | 7fbdaa62298596fb5287a660a1cc9e81 |
| tools/bench/plan_ring_p4_s05v18_pred.json | 6666a7183fc4a2ca428e62fab5897803 |
| tools/bench/sim/ring_p4_s05v18_s04end/base_provisional.json | c159906d89a251f5495072fdf1872509 |
| tools/bench/prep_c145_p1_session.json | e5753f2e5d7b3260dfd8791f54cf4866 |
| tools/recipes/stage_d1_ring_p4_s05v18.py | 23c08932db7e3ace3ef5a1cd7d547266 |
| tools/recipes/stage_d1_ring_p4_s05v18_scratch.py | cd14eb476d2ccbe314cb8d5d36cbb67d |
| tools/bench/prep_c145_p1_mk.py | c7fdf26353add468b1660ed866c39cd2 |
| tools/bench/prep_c145_p1_pred.py | aeea73304c08fb145cb4792dd61fd992 |
