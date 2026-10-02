# Card 136-P2 — P4 plan v3, OFFLINE (no LabVIEW, no VI opened)

Input plan `tools/bench/plan_ring_p4_v3_in.json` ded2d556 (stageplan/1 valid; PROVISIONAL; never launched) = v2 0d67d704 +
PD298(b)(c)(d)(e). stagesim output `tools/bench/plan_ring_p4_v3.json` d14c1bba (final=False). Per-action meta, load fit,
session table, route list: `tools/bench/plan_ring_p4_v3_meta.json` 8dd37a54. Latch stop form (CONDITIONAL):
`tools/bench/plan_ring_p4_v3_latch_in.json` d26c954f (valid, not replayed). Generator: scratchpad `gen_p4v3.py`.
163 actions / 164 ops (v2 159 / 154).

## 1. What v3 changes (PD298)

| PD | change |
|---|---|
| (b) | `p4_t_pool` tunnel on base While #10170 (body 23166, parent 686) BEFORE the pool wire. Source = the pool already on 686: FSOT #28809 face t28816 (w28794 → loop 1.1 tunnel #28771; chain #23099 → For exit #28975 → FSOT #28907 → #28809, P3b-1). `p4_x_pool` = same-diagram branch → TP1.outer; `p4_w_pool_in` TP1.inner → IAI1.array. v2's multi-border `p4_x_pool` + its RLE dropped |
| (c) | `decide` removed. `p4_ia_n2sink` = Index Array ($work #3163) in FS4.f0, index + element unwired; `p4_x_n2_order` #5058 t5111 `Bead is good? array out` → IAZ1.array (FS4 input tunnel) + RLE. Unit U09 moved LAST: the crossing re-creates t5111's net (`stagesim.py:1906-1912`), and `p4_rbC_dw` deletes w25348 by uid |
| (d) | Select output: t10871 (#10757 → indicator `index`, read by Local #23523 on diagram 23058 = another loop), t4168 (#2626 save row), t25573 (read by Local #25578 on 639). Raw: t3173, t9519 (display), t10975 (→ `min value` indicator, no Local in the graph), t2811 (→ registers E/F + `Extension vs Time` graph, stays in 1.2). Forward trace: scratchpad `p2_probe4.py` |
| (d) | **t25557 not settled**: fed by #9647 `x .and. y?` t9668 (w25415, also → Tunnel #10465), not by a register — no Select carries it. Written as `decide p4_dec_reseed` (3 options), counted 8 ops |
| (e) | Main plan: Local `stop (end)` in W1 and on 23166 (v2 form). Latch file: `StopAll` indicator born on t642 in #637's body 639 (one writer); the two Locals read `StopAll`. CONDITIONAL on 136-3 |

## 2. stagesim replay (`tools/bench/prep_c136_p2_sim.log`)

Real graph `graph_ring_p3b2b_20261002_133824.json` loaded (BASE-FLIPS 6 on #9503/#10177/#29777, `:3`). Steps 1–101 ok; cdiff 16
through step 97, 18 at 98 (`p4_mv_10068`), 20 at 99 (`p4_mv_29240`) (`:101-102`, the moved nodes' x/y are not wired yet).
**Step 102 `p4_x_fd` ERROR "#686 (686) owns no terminal in the current graph"** (`:105`); final=False, no end cdiff (`:106`).
The input graph has 5 rows owned by 686 incl. t8936 `# FD points` (scratchpad `p2_probe6.py`; same in the v2 base). Not
diagnosed, not retried. The scratch replay without the n2 exit pair (`prep_c136_p2_sim_noexit.log:105-106`) fails at the same
step. Predicted failure point (`p4_x_n2_out`, FS-frame exit unmodelled) was never reached. 103 step files in `tools/bench/sim/ring_p4_v3/`.

## 3. Load growth from MEASURED loads (ops counted since the P3a bed)

| ops | MB | file | meter line |
|---|---|---|---|
| 0 | 561.8 | P3a bed | `stage_d1_ring_p3b1.log:42` |
| 31 | 584.1 | P3b-1 file | `diag_c132_2_graph_p3b1.log:24` |
| 31 | 576.4 | P3b-1 file | `launch_p3b2_c135_a.log:48` |
| 52 | 605.0 | P3b-2a file | `launch_p3b2_c135_g.log:23` |
| 52 | 576.2 | P3b-2a file | `launch_p3b2_c135_b.log:56` |
| 70 | 600.2 | P3b-2b bed | `diag_c136_1_graph.log:24` |

Ops: 31 (`stage_d1_ring_p3b1.log:41`), 21 (`launch_p3b2_c135_a.log:47`), 18 (`launch_p3b2_c135_b.log:55`). Least squares:
**0.543 MB/op**, intercept 562.6, residual SD 10.6; the same file loaded twice differs by 7.7 and 28.8 MB. Excluded: the P3b-2a
SCRATCH 6cc69221 (588.5/588.1), an earlier plan's op count.

## 4. Sessions (start = 600.2 + 0.543 × applied ops + op-0 read 5.9; memory_model formula; limit 675; units kept whole)

| step | actions | sessions (start → X10) |
|---|---|---|
| 1 | 33 | 606.1→670.9 · 614.8→655.6 · 618.0→**681.0** |
| 2 | 35 | 624.0→**694.8** · 631.1→669.9 · 636.5→674.8 |
| 3 | 39 | 639.8→**681.5** · 647.3→**701.5** · 653.9→**699.3** |
| 4 | 36 | 660.9→**695.3** · 663.6→**702.4** · 669.1→**705.1** · 673.4→**706.7** · 676.7→**711.3** |
| 5 | 20 | 680.5→**713.7** · 683.7→**717.0** · 687.0→**725.5** · 691.3→**731.0** |

An EMPTY session (k0 read + final read) passes 675 after **85.6** more applied ops; P4 has 164. 4 of 18 sessions fit.
Whole v3 in one run: X10 1009.2.

## 5. UNMEASURED routes by class (113 actions; scratch item per class in the meta file `routes_unmeasured`)

Largest: connect on base While body 23166 (37), create on 23166 (16), branch on 23166 (9), connect in W1 body (8), wire_sr on
23166 (7), create in W1 body (6). New in v3: tunnel on base While #10170 + its branch from FSOT t28816 (S-TUN, no
census_samples.json record), create + connect_term_uid into FS4 on a While body (S-FSW), Select-output branches (S-SELB).

## 6. fp-30 / fp-32

`tools/bench/selftest_c134_1_dry.py` added to `protocol.OFFLINE_SELFTESTS` (`tools/protocol.py:402`). Measured with
`c125_1_offline_measure.py`: rc 0, 0 COM trips, 11/0; other 4 entries PASS (`selftest_c134_1_dry_c136_p2_measure.log:5-16`).
`gate_fp drain` fp-32 and fp-30: DRAINED.

## Not done

v2's 65 step files in `tools/bench/sim/ring_p4_v2/` NOT deleted: Remove-Item refused by the permission layer (twice).
