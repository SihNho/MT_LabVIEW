---
type: facts
status: current
date: 2026-10-03
---
# Card 142-P2 facts: P4 plan v18 = v17 with the two subVIs (offline, no LabVIEW)

Maker `tools/bench/prep_c142_p2_mk.py`, log `tools/bench/prep_c142_p2_mk.log` (run 2, 10:14, 13/0, `BGRUN END rc=0`). Run 1 (10:08)
ended 12/1: the edge-diff check failed on the CHECKER (symbol keys carry the `new:` prefix, so no edge matched an alias); the same log's
`ED` lines already showed 126/127 differing edges naming a removed alias / PS1 / SQ1 and the 127th = FMN1's count Tunnel. Predicate fixed
(`prep_c142_p2_mk.py`, `touch`), rerun identical otherwise (same tables, same counts).

## Artefacts
| file | md5 |
|---|---|
| `tools/bench/plan_ring_p4_v18.json` (simulated plan, `finalized` block) | 2ea6cafa7d368dc7a054346d398daa3e |
| `tools/bench/plan_ring_p4_v18_in.json` | ae6861c6bb36d8c44eee3634240f6eb2 |
| `tools/bench/plan_ring_p4_v18_meta.json` (removed / re-pointed / provisional lists) | 8425195c5d894446dd06723af4143f55 |
| `tools/bench/prep_c142_p2_sessions.json` (X10 tables) | bed4b9f445f30495423caf96e7ab8a7a |
| replay steps | `tools/bench/sim/ring_p4_v18/ring_p4_v3/` |

## What changed v17 -> v18
- Actions **235 -> 202** (-35 +2); compiled ops **217 -> 190** (create 58->46, connect 88->79, tunnel 9->6, wire_sr 5->4, branch 6->4).
- `p4_s1_pickslot` (as `PS1`) replaces `p4_gt_last` in place, on `new:W1.body`, `subvi_path` claudeDev\RingPickSlot_v0.vi (md5 6fcf153f).
  12 declared terminals = pane slots 0..11: 1 `found`, 2 `min slot`, 3 `min Num` (sources), 10 `last`, 11 `Num` (sinks), the other 7 `''`
  sinks - MEASURED pane (`build_ringpickslot_v2.log` pane read back); unassigned slots as `''` wire-0 sinks = how the bed graph lists other
  subVIs (`graph_ring_p4s01_20261002_234419.json`, owners #30804, #4620).
- `p4_s2_seqcheck` (as `SQ1`) replaces `p4_eq_seq` in place, on diagram 23166, `subvi_path` claudeDev\RingSeqCheck_v0.vi. 8 declared
  terminals `n1 n2 last Latest discards` (sinks) / `next last`, `next discards`, `valid` (sources) - **PROVISIONAL** (from the brief; pane
  and unassigned `''` rows unread). Schema `stageplan/1` has no `provisional` field (additionalProperties false): marked in the action's
  `why` and in `plan_ring_p4_v18_meta.json` `provisional` (action, names, the 14 `new:SQ1.*` addresses). The file existed at run 2 (log
  line 6), it did not at run 1.
- Removed (35): S1 7 nodes + 11 inner For-tunnel/wire actions + `p4_t_fnum_in` (LRN4 -> For tunnel; `Num` now enters once via
  `p4_w_num_gt`); S2 7 nodes + 6 inner wires + `p4_w_n1_gt`, `p4_w_n1_sel`, `p4_w_disc_sel` (branches that fed n1 / discards a 2nd time).
- Re-pointed (19, `why` prefixed `c142-P2 re-pointed`): S1 `p4_t_last_out`->PS1.last, `p4_w_num_gt`->PS1.Num, `p4_w_lt_or` src PS1.found
  (-> OR1.x stays), `p4_t_n1_in` src PS1.min Num, `p4_t_slot_in` src PS1.min slot; S2 `p4_w_last_gt`->SQ1.last, `p4_t_n1_out`->SQ1.n1,
  `p4_w_lat_dec`->SQ1.Latest, `p4_w_disc_inc`->SQ1.discards, `p4_x_n2_out`->SQ1.n2, `p4_w_sel_last` src SQ1.next last, `p4_w_seld_r` src
  SQ1.next discards, `p4_rb{A,B,C,D,E,F,R}_s` src SQ1.valid (log `REPOINT` lines). No kept action names a removed alias (gate DEP).

## stagesim support for a SubVI created from a file
**YES, by the plan's declared terminal list, not from the file**: `tools/stagesim.py:2092,2156-2165` (generic create: one object of the
declared class + one row per declared terminal); `tools/stagexec.py:438-441` (route `subvi` needs `subvi_path` + `terminals`) and
`:3047-3054` (drop_subvi, one new SubVI). Gap (reported, not built): the subVI file is never opened offline, so a wrong terminal name or
pane in the plan is caught only by the real drop; precedent of the same shape: `plan_ring_p3b1_in.json:136-190` (IMAQ Copy).

## Replay / compile / diff
- Replay END: base + 202 steps, no error (gate RP). `final` false, `open_rows_match` false, undecided 0, route_check PASS, fs_border_gate
  PASS - **v17 is the same** (`final` false, `open_rows_match` false, route_check PASS; log line 5).
- End cdiff rows v18 == v17: 24 == 24, none only on either side (gate E).
- End graph edges (new objects named by alias): v17 7932 / v18 7927; 66 only in v17, 61 only in v18; all name a removed alias, PS1 or SQ1
  except one: `('thru', NEW:Tunnel '' -> NEW:Tunnel '')` only in v17 = FMN1's count terminal N, removed with FMN1 (gate ED, log `ED` lines).
- compile_plan v18: 190 ops, every action once. PS1 = op 79 `create`, SQ1 = op 88 `create`; `p4_x_n2_out` = op 189 `connect_term_uid`;
  the 7 rollback `s` wires = `connect` ops (first one now a plain connect, was a branch of AND1).

## X10 session table, non-repair part (ops 51..190; repair = ops 1..50 = v17 #1..#50 unchanged), start 596.5
Model `memory_model.json` (read/edit/other/final_read). Limit 680 = `fail_above_mb`:

| s | ops | first .. last | actions | N | R | peak MB |
|---|---|---|---|---|---|---|
| 1 | 51-72 | p4_dw_23310 .. p4_k_last | 22 | 22 | 14 | 679.7 |
| 2 | 73-89 | p4_w_klast .. p4_lr_latest | 17 | 17 | 16 | 677.8 |
| 3 | 90-114 | p4_ia_n2sink .. p4_ia_frameidx | 33 | 25 | 12 | 678.8 |
| 4 | 115-147 | p4_w_arr_frameidx .. p4_rbB_f | 37 | 33 | 8 | 679.7 |
| 5 | 148-180 | p4_rbB_s .. p4_rbR_t | 33 | 33 | 8 | 679.7 |
| 6 | 181-190 | p4_rbR_f .. p4_rle_x_n2_out | 10 | 10 | 5 | 640.3 |

At 675 (`docs/d1/ring-p4b.md:90`'s older cut limit) also 6 sessions: 51-70, 71-86, 87-108, 109-133, 134-165, 166-190 (peaks 674.4 /
673.9 / 674.6 / 673.7 / 673.2 / 668.6). The model has no term for loading a subVI file into memory when PS1/SQ1 are dropped (UNMODELLED).

## Not done (card scope)
No dry-run, no stage_prerun, no recipe, no LabVIEW. Prior-art not dispatched (no guard asked). Tools not edited.
