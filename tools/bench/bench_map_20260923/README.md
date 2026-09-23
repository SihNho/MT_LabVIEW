---
type: benchmark
status: current
date: 2026-09-23
tags: [connectivity-map, jev, bench, step-5b]
---

# Connectivity-map bench, step 5b (layers A and B), 2026-09-23

This folder benchmarks steps 1–5 of `docs/connectivity-map-plan.md`: the whole-VI reader, the graph, path finding, diff, the Jev menus, and the executor. Every test has a known answer. Layer C (the first runner cycle compared with cycle 65) is not in this folder; the plan runs it after step 6.

## Environment

| item | value |
|---|---|
| LabVIEW | 2026 (26.3.1f1), Windows 10. Each LabVIEW script restarts the instance first (stagekit `fresh=True`). |
| test VI | `user.lib\claudeDev\D1_s1_copy.vi` (S1, the original's bytes), md5 `3e3d23cefd3a334001aa9d6156bf1aee`. Every script works on a **dated scratch copy**, deletes it at the end and saves nothing. The ORIGINAL (`2a78e17c…`) and all five stage pins were checked before and after each run and held every time. The real bed `D1_s3b_m3a3b_rowD_20260922_161040.vi` was never opened. |
| reader ops (md5) | `OpAllTerms_v1` `457a8d73…` · `OpReportAll_v0` `ffcec2c7…` · `OpWireSource_v5` `5dc45a04…` · `OpFsTunnelTerm_v0` `1b687f69…` · `OpFsInnerTunnelTerm_v0` `aedf93a0…` |
| writer ops (md5) | `OpConnectNested_v1` `b7a1bb56…` · `OpWireSR_LeftIn_v0` `ad79ba48…` · `OpWireSR_RightIn_v0` `969e333b…` · delete through `gscript.delete_object` (live Wire traverse index) |
| graph | `tools/vigraph.py` `build4` with the wiki's exact flat-sequence faces (step 4b) and ASSUMPTION A (plan OPEN A) |
| Jev | `tools/jev.py`, 5-sample consensus. Thresholds from `tools/bench/jev_menu_thresholds.json`, except PAIR in B, which follows A5 (see below). Cost estimated at $0.00008 per call (`docs/jev-integration-plan.md:13`). |
| model in the loop | none. B makes zero LLM turns. |

## Scripts, raw data, results

| test | script | log (`tools/bench/`, copied to `raw/`) | JSON | result |
|---|---|---|---|---|
| A1 mutation | `a1_mutation.py` | `bench_map_a1.log` | `raw/bench_map_a1.json` | **12 pass / 0 fail**, 266 s |
| A2 + A3 readers | `a23_readers.py` | `bench_map_a23.log` | `raw/bench_map_a23.json` | **12 pass / 0 fail**, 210 s |
| A4 functional units | `a4_units.py` (offline) | `bench_map_a4.log` | `a4_units.json` | 150/151, one miss explained |
| A5 held-out menus | `a5_heldout.py` (offline) | `bench_map_a5.log` | `a5_heldout.json` | **PAIR fails the criterion** |
| A5b follow-up from the review | `a5b_seeds.py` (offline) | `bench_map_a5b.log` | `a5b_seeds.json` | 503/1000 splits dangerous |
| B end to end, run 2 (current) | `b_endtoend.py` | `bench_map_b.log` (2nd block) | `raw/bench_map_b.json`, `raw/decision_bench_map_b.json` | **arm 1: 0 executed (PAIR not acting); oracle arm: 8/9 restored, ExecState 0**, 367 s |
| B run 1 (superseded) | same script before the review's fixes | `raw/bench_map_b_run1.log` | `raw/*_run1.json` | 6/9, because of a scorer fault (see B) |

Shared inputs are in `common.py`. The tool changes this bench needed are listed at the end.

## A1: mutation test (known answer: 9 rows)

On a scratch copy of S1, the script deleted 8 wires and added 1, all through `stagekit.from_decision`. The 8 wires were sampled with seed 20260923 from wires that have exactly one source and one sink, both on computation nodes: w13910, w13922, w16665, w17960, w18815, w21852, w23575, w28448. The added wire goes from `#1469 'error out'` to `#17780 'error in (no error)'`: two unwired Property terminals on diagram 639. `op_rule` chose `connect_nested`.

| gate | result |
|---|---|
| C0 control: fresh read of the unmutated scratch vs the S1 wiki graph | 0 edge rows, 0 node changes, 0 terminal changes |
| C1 diff(S1, mutated) | **precision 1.000, recall 1.000**: 9 expected, 9 observed, 0 missed, 0 spurious |
| C2 | 8 edges removed, 1 added, changed_sinks 9. After the purge of the one junk `Invoke` (a known side effect of `connect_nested_v1`), no node or terminal was added or removed. |

Reading the map took 24–86 s (GObject census, OpAllTerms_v1, and the join; 86 s includes the first cold load).

## A2: 200 random wires vs `OpWireSource_v5`

- Source owner: **200/200** agree.
- Full endpoint multiset (owner uid and direction of every terminal on the wire): **200/200** agree.
- Median cost is 0.085 s per wire; 44 s for all 200.

## A3: the 58 sequence tunnels

| class | n | fresh `read_tunnel` == wiki `fs_tunnel_pairs` | faces == the OpAllTerms_v1 rows that tunnel owns |
|---|---|---|---|
| FlatSequenceOuterTunnel | 58 | **58/58** | **58/58** |
| FlatSequenceInnerTunnel | 518 | 518/518 | 259/518 |

The fresh read uses the same op that built the wiki, so it checks repeatability. The comparison with the owned terminal rows uses a different reader. The FSIT figure of 259 matches the known 4b fact: each physical inner tunnel is two FSIT uids, and the traverse files all four rows under one of them.

## A4: functional units of `docs/frame-loop-wire-graph.md` reproduced by `path()`

| group | units | reproduced | path length min/med/max |
|---|---|---|---|
| K: kernel #5058 inputs (6 extended past the loop border) | 10 | 10 | 2/3/3 |
| KO: kernel outputs (named consumer, or out of the body) | 5 | 5 | 2/2/3 |
| SR: state carriers, write → right SR → left SR → read (must use an `sr` edge) | 14 | 14 | 4/4/4 |
| SRF: carrier final value → consumer on the parent | 4 | 4 | 4/4/4 |
| TI: loop-border input tunnels | 33 | 33 | 2/2/2 |
| TO: loop-border output tunnels | 10 | 10 | 2/2/2 |
| U: candidate-unit members (directed path to or from another member) | 73 | 72 | – |
| FS: sequence-crossing R1 / R2 (wire and fs edges only) | 2 | 2 | 10/12/12 |
| **all** | **151** | **150 (0.993)** | |

Notes:
- The miss is unit-0 member `#23175 Strip Path`. In S1 both of its outputs are unwired, and its only input shares wire 5090 with `#376`. Its unit-0 link in the document went through `#23020 Build Path`, which, like `#22700`, is **not in S1**: both were part of the 2026-09-01 TIFF fixture on the working copy that the document measured. Those two members are excluded from the count.
- 19 structures were resolved to their border tunnels by `jev_candidates.structure_terminals`, a heuristic.
- **Before this bench, `jev_candidates.load()` built the step-4 HEURISTIC fs edges**, because it never passed `fs_tunnel_pairs`. R1/R2 were reproduced 0/2 that way. It now passes them, and R1/R2 are 2/2.

## A5: Jev menus on a held-out half

Setup: step 5's stored answers, split 50/50 by seed 20260923 at item level. The threshold was set on half 1 and scored on half 2. No Jev calls were made.

| menu | n (h1/h2) | threshold (h1) | acc h2 | Brier h2 | dangerous h2 |
|---|---|---|---|---|---|
| PAIR | 24/25 | 0.65 | 0.92 | 0.040 | **1** (intent 1893, `'Focus Step (F1)' → '+Inc reference'`, p 0.698, correctly labelled FALSE) |
| CHAIN | 28/29 | 0.25 | 0.931 | 0.154 | 0 |
| RISK (proceed at p ≤ t) | 14/14 | 0.95 | 1.00 | 0.284 | 0 |
| OP | 10/10 | 0.95 | 0.50 argmax (1 acted, right) | 0.674 | 0 |

**PAIR fails the plan's criterion** (≥ 0.85 accuracy and 0 dangerous errors), so it does not keep acting.

A hypothesis review attacked this result (`archive/peer/2026-09-23-bench-map-a5-pair-heldout.md`). It argued that the result is one intent's sibling pins and that a Python name filter would fix it. Its own discriminating test was run as `a5b_seeds.py`:

- **Raw:** 503 of 1000 seeds give at least one dangerous error on half 2. The errors come from six intents: 1893 ×752, 2819 ×116, 7388 ×49, 4833 ×16, 11232 ×15, 23502 ×2. Leave-one-intent-out gives 2 dangerous errors.
- **With the exact-name filter:** 513 of 1000 seeds are still dangerous (7388, 11232, 23502). The filter removes 1893's negatives, which lowers the threshold. It also drops one true item.

By the reviewer's own falsifier, the claim holds. The filter was not adopted, because that is a design decision.

## B: end to end, zero LLM turns, on a scratch copy of S1

How the damage was made: **9 of the 11 wires exist in S1.** Wires 23502 and 23540 were created later by S3b, so on S1 there is nothing to cut and nothing to restore for them. Each of the 9 is one source to one sink on the frame-loop body, and each was **deleted whole**. The bed's 4 half-wires carry no edge either, and no op on disk can create a dangling half-wire.

The pipeline ran as code only: re-read, candidates, `decide(by_rule=True, risk_gates=False)` (Pre-decided 143 and 144), `from_decision`, re-read. PAIR did **not act**, per A5, so arm 1 executed nothing. **Arm 2** (labelled ORACLE) used the known S1 pair as the verdict, the same op rule, and the same executor. That measures the op and execution layers.

Run 2 changed three things, all taken from the hypothesis review of run 1 (`archive/peer/2026-09-23-bench-map-b-endtoend.md`):
- Every delete is verified against the Wire uid census.
- The severed graph's flags and tunnel rows are saved.
- The truth pair is mapped through `jev_candidates.map_key`, because terminals get renamed. Run 1 compared exact S1 keys, so it wrongly reported w1731 and w7337 as missing from the candidates and the oracle arm never tried them.

The table below is run 2. "Truth rank" uses TERMINAL CLASS as well as name: an outer terminal and its tunnel's inner terminals share both uid and name.

| wire | truth among candidates (n) | Jev: truth's rank, p (best other) | arm 1 action | op (decided by) | oracle-arm execution | restored | first failing layer |
|---|---|---|---|---|---|---|---|
| 1731 | yes, via rename map (5) | 1st, 0.558 (0.138) | llm | wire_sr LeftIn (rule) | ok, loop #637, reg echo #4334 | **yes, exact S1 key** | verdict (p < 0.70; PAIR not acting) |
| 1893 | yes (5) | 1st, 0.940 (0.730 `+Inc reference`) | llm | connect_nested (rule) | ok | **yes** | verdict (≥ 2 over 0.70) |
| 2819 | yes (5) | 1st, 0.936 (0.362) | llm | connect_nested (rule) | ok | **yes** | verdict (PAIR not acting) |
| 3947 | yes (5) | 1st, 0.946 (0.098) | llm | wire_sr LeftIn (rule) | ok, reg echo #4256 | **yes** | verdict (PAIR not acting) |
| 4833 | yes (5) | 1st, 0.942 (0.302) | llm | connect_nested (rule) | ok | **yes** | verdict (PAIR not acting) |
| 7337 | yes, via rename map (1) | 1st, 0.450 | llm | wire_sr RightIn (rule) | ok | **yes, exact S1 key** | verdict (p < 0.70) |
| 7388 | yes (6) | 1st, 0.934 (0.932, flipped inner terminal) | llm | connect_nested (rule; sink = structure #10407, found by geometry) | ok | **yes** | verdict (≥ 2 over 0.70) |
| 9635 | yes (3) | **3rd**, 0.940 (0.952 / 0.950, flipped inner terminals) | llm | none: the rule has no entry for a LoopTunnel inner source; Jev OP said connect_from_wire 0.668 and does not act | llm, not executed | no | **op** (and the verdict picked a wrong terminal) |
| 11232 | yes (6) | **2nd**, 0.932 (0.938, flipped inner terminal) | llm | connect_nested (for the wrong best pair, by Jev 0.878; the rule gives connect_nested for the truth) | ok | **yes** | verdict (wrong terminal ranked first) |
| 23502 | – | – | – | – | – | no | not in S1 |
| 23540 | – | – | – | – | – | no | not in S1 |

| gate | result |
|---|---|
| B0a: each delete removes exactly its uid | **9/9 PASS** |
| B0: damage explained | Every removed edge is explained, 0 unexplained: 20 removed = 9 cut + 5 tunnel-inner + 6 renamed. The gate printed FAIL only because of MY bookkeeping: one edge, `#11220 inner → #11263 'VISA out'`, was counted both as tunnel-inner and as renamed. |
| B1: 11/11 restored to S1 endpoints | **FAIL: 8/11** (8 of the 9 that exist in S1; w9635 is the one missing) |
| B2: ExecState 1 | **FAIL: 0** (w9635 is still cut) |
| B3: computation_diff ∅ | **FAIL: 1 row**. `#9243 'x'` is unsourced, downstream of w9635. No computation node was added or removed. |
| B4: diff ∅ | **FAIL: 2 rows**. `- #9641 → #9623 outer` (w9635) and `- #9623 inner [1] → #9243 'x'` (the inner wire exists but has no source while its tunnel is unfed). |

Timing and cost: 367 s wall. Of that, 151 s was intent → candidates → Jev → record, and about 25 s per map read. 260 Jev calls, about $0.021. **0 LLM turns.**

**Measured in run 2** (these replace run 1's inferences):
1. **Cutting an input tunnel's feed flips how its inner terminals are read.** They read as SINKS, so their wires have 0 sources and no edge (flags: w5773, w9612, w11209, w11303). The tunnels are selector tunnels #9623, #11348 and #11220. The candidate generator then offers those inner terminals as legal sinks. Jev scores them about as high as the real outer terminal (0.93–0.95), and on 9635 and 11232 it ranks one first. The asymmetry rule (≥ 2 candidates over 0.70 → llm) is what stops a wrong wire here.
2. **Cutting both wires of the VISA shift-register carrier renames its terminals** from `'VISA out'` to `'Outgoing Handle'` (6 edges). **Re-wiring w1731 and w7337 renames them back.** After repair every restored row matches its exact S1 key, so the name change does not reach a repaired VI.
3. The executor (`from_decision`, with `connect_nested_v1` and `wire_sr` LeftIn/RightIn, index triples read live with uid echo, and a structure-of-tunnel lookup by geometry) **executed 8 of 8 rows it was given, all correctly**.

## Tool changes this bench made (additive; existing behaviour kept unless named)

- `tools/jev_candidates.py`:
  - `load(key, fs=True)` now passes the wiki's `fs_tunnel_pairs` to `build4`. **This is a behaviour change**: before, it silently built the heuristic fs edges.
  - New: `from_parts()` and `node_labels_default()`.
- `tools/jev_pairs.py`:
  - New: `op_rule()`, which is Pre-decided 143 as code.
  - `decide(..., by_rule=, risk_gates=, top_diagram=)`. The defaults keep step 5's behaviour.
  - Every decision now carries `variant`, an `exec` block and `evidence.failed_layer`.
- `tools/stagekit.py`:
  - New: `Stage.address()`, `Stage.from_decision()` and `_wire_row()`, which execute the actions wire / delete / retire.
  - Structure-of-tunnel lookup is by geometry, a heuristic, made safe by requiring exactly one name match.
- `tools/wiki_build.py`: new `read_live()`, which is the graph inputs of a live VI without the subVI and conpane passes.
- `a4_units.py` is 204 lines, over the 120-line stage-script norm, because the document parsing is inline. It is offline and never touches LabVIEW.
