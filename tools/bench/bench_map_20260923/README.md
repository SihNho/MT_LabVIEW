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
| **A5c** PAIR margin rule (continuation) | `a5c_margin.py` (offline) | `bench_map_a5c.log` | `a5c_margin.json` | **0 dangerous; PAIR acts** |
| **w9635 writer probe** (continuation) | `w9635_writers.py` | `bench_map_w9635.log` | `raw/bench_map_w9635.json` | 0/3 cells reuse #9641; 14/3, 176 s |
| **B run 4** (PD146 + corrected criterion, CURRENT) | `b_endtoend.py` | `bench_map_b4.log` | `raw/bench_map_b_run4.json`, `raw/decision_bench_map_b_run4.json` | **PASS 22/0: arm 1 7/9 (0 wrong), oracle +2, ExecState 1, cdiff ∅**, 349 s |
| B run 3 (superseded) | `b_endtoend.py` | `bench_map_b3.log` | `raw/bench_map_b_run3.json`, `raw/decision_bench_map_b_run3.json` | **arm 1: 6/9 restored; oracle +2; ExecState 0**, 336 s |

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

## Continuation, 2026-09-23 18:0x–18:2x: the judgement session's five decisions applied

The judgement session (chat, 16:xx) decided five changes after run 2. They were applied as given and then measured.

### A5c: PAIR with a margin rule

The new rule: PAIR acts only when the best candidate has p ≥ 0.75 **and** beats the runner-up for the same intent by at least 0.15. Otherwise the row goes to the LLM. Both numbers are stored in `jev_menu_thresholds.json` (`pair.act`, `pair.margin`). They are fixed values, so nothing is fitted on half 1. The data are the same stored answers as A5: 49 items, 11 intents.

| set | n | acc | Brier | acted (all correct) | dangerous |
|---|---|---|---|---|---|
| full set | 49 | 0.918 | 0.0745 | 7 of 11 positives | **0** |
| half 1, seed 20260923 | 24 | 0.875 | 0.111 | 2 | 0 |
| **half 2, seed 20260923** | 25 | **0.96** | **0.040** | 5 of 6 | **0** |
| half 2, runner-up from the same half only | 25 | 0.96 | 0.040 | 5 | 0 |
| **A5b: 1000 splits** | – | – | – | – | **0/1000** (0/1000 with the same-half runner-up too) |
| leave one intent out | 11 intents | – | – | 7 | 0 |

Acting intents: 1893 (0.916 over 0.698), 2819, 3947, 4833, 7388, 9635 and 11232. Going to the LLM: 1731 (0.446), 7337 (0.534), 23502 and 23540. **PAIR keeps acting** (`a5c_margin.json` `pair_keeps_acting: true`).

Caveat: 0.75 and 0.15 were chosen after run 2's numbers had been seen. The 1893 negative at 0.698 lies just under 0.75. So the held-out result is not an independent test of the thresholds. It only shows that no labelled item breaks the rule.

### The cut-input-tunnel rule in `jev_candidates`

`cut_input_tunnel()` excludes the inner terminals of a Selector, Loop or plain tunnel whose outer terminal reads as a sink (`is_source` False) and has `wire_uid` 0. In B run 3 it removed **10 candidate pairs**: 4 on w7388, 2 on w9635 and 4 on w11232. After that, the truth was the best candidate on 9 of 9 rows. In run 2, a flipped inner terminal was ranked above the truth on 9635 and 11232.

### w9635: can an existing writer make LoopTunnel #9641 inner → SelectorTunnel #9623 outer?

The probe ran three cells, each on a fresh scratch of S1 with w9635 deleted. After the cut, every cell read ExecState 0 and 132 LoopTunnels. The sink in every cell was `D[43].N[24].t1`, the #9623 outer terminal, addressed through its structure #10407 by `stagekit.address`.

| cell | writer | source | op error / `Is Broken?` | new wire's source owner | LoopTunnel count | ExecState | gate |
|---|---|---|---|---|---|---|---|
| C1 | `OpConnectFromWire_v0` | w9649 term 1 (#9641 OUTER) | '' / False | **new LoopTunnel #23014** | 132 → 133 | 1 | FAIL |
| C2 | `OpConnectFromWire_v0` | w9649 term 0 (FSIT #9655, the feed's source) | '' / False | **new LoopTunnel #23014** | 132 → 133 | 1 | FAIL |
| C3 | `OpConnectNested_v1` | `D[19].N[4].t45` = WhileLoop #637's terminal on w9649 | '' | **new LoopTunnel #23058** | 132 → 133 | 1 | FAIL |

- Every writer produced a working VI: ExecState went from 0 to 1, and the new wire is not broken. In every case LabVIEW did this by making a **new** loop tunnel. #9641 stayed on the diagram, and its inner terminal stayed unwired.
- None of them reproduces S1's endpoints. The gate required uid and name to match.
- `OpFsInnerTunnelConnect_v1` was not tried. It casts the UID to `FlatSequenceInnerTunnel` (`tools/recipes/build_d1_m3a3b_d3.py:33`), and a LoopTunnel cannot pass that cast.
- **No existing writer can address a LoopTunnel's inner terminal as a source, so no op-rule entry was added** for "tunnel-inner-source → tunnel-outer-sink" or for "tunnel-inner-source → node-sink". Building a new op is a judgement call.
- The probe's docstring had predicted that C1 and C3 would give an op error or no wire. They made working wires through a new tunnel instead, so that sub-prediction failed.

### B run 3: fresh scratch, the same 9 cuts, zero LLM turns

The run used PAIR at act 0.75 with margin 0.15 (acting, per A5c), the cut-tunnel rule, and an unchanged op rule. The oracle arm then ran every row that arm 1 left undone.

| wire | cands (cut-rule removed) | truth best? | p (margin) | arm 1 | op (by) | arm 1 result | oracle arm | restored (exact S1 key) | first failing layer |
|---|---|---|---|---|---|---|---|---|---|
| 1731 | 5 (0) | yes | 0.578 (0.446) | llm | wire_sr LeftIn (rule) | – | ok, echo #4334 | yes | verdict (p < 0.75) |
| 1893 | 5 (0) | yes | 0.940 (0.220) | **wire** | connect_nested (rule) | ok | – | **yes** | – |
| 2819 | 5 (0) | yes | 0.938 (0.558) | **wire** | connect_nested | ok | – | **yes** | – |
| 3947 | 5 (0) | yes | 0.950 (0.854) | **wire** | wire_sr LeftIn | ok, echo #4256 | – | **yes** | – |
| 4833 | 5 (0) | yes | 0.946 (0.650) | **wire** | connect_nested | ok | – | **yes** | – |
| 7337 | 1 (0) | yes | 0.472 (0.472) | llm | wire_sr RightIn | – | ok | yes | verdict (p < 0.75) |
| 7388 | 2 (4) | yes | 0.924 (0.576) | **wire** | connect_nested (structure #10407) | ok | – | **yes** | – |
| 9635 | 1 (2) | yes | 0.940 (0.940) | llm | none (rule has no entry; Jev OP said connect_from_wire, does not act) | – | not executed | no | **op** |
| 11232 | 2 (4) | yes | 0.934 (0.588) | **wire** | connect_nested (structure #10407) | ok | – | **yes** | – |

| gate | result |
|---|---|
| B0a each delete removes exactly its uid | 9/9 PASS |
| B0 damage explained | printed FAIL. This is the same bookkeeping fault as in run 2: one edge is counted as both tunnel-inner and renamed. The run found 0 unexplained removed edges. |
| **B1a arm 1 alone restores 9/9** | **FAIL: 6/9**. All 6 rows that arm 1 executed came back with their exact S1 keys. |
| B1 11/11 | FAIL: 8/11. That is 6 from arm 1 and 2 from the oracle arm; 23502 and 23540 are not in S1. |
| B2 ExecState 1 | **FAIL: 0**, because w9635 is still cut |
| B3 computation_diff ∅ | **FAIL: 1 row**. `#9243 'x'` has lost its source `#27462 '# slices in stack'`, downstream of w9635. No node was added or removed. |
| B4 diff ∅ | FAIL: 2 rows, `- #9641 inner → #9623 outer` and `- #9623 inner [1] → #9243 'x'` |

Time and cost: 336 s wall, 205 Jev calls, about $0.016, **0 LLM turns**.

Compared with run 2, the verdict layer went from acting on 0 of 9 rows to acting on 7 of 9, with 0 wrong. The execution layer ran 6 of 6 correctly. The remaining failures are 1731 and 7337, where p is below 0.75 on the renamed VISA-carrier rows, and 9635, where the op layer has no writer.

## B run 4 (current, 18:3x): Pre-decided 146 and the corrected pass criterion

The judgement session made two decisions at 17:xx:
1. **Pre-decided 146.** A tunnel-inner source is re-made with `OpConnectFromWire_v0` off the tunnel's OUTER feed; LabVIEW mints a new tunnel, and the orphan tunnel is then deleted. Rows of this class are judged BEYOND the tunnel: the sink's `vigraph.effective_sources` in S1 against the repaired VI.
2. **Corrected B criterion.** Arm 1 must execute 0 WRONG rows. Arm 1 plus the oracle arm must restore 9/9. ExecState must be 1 and `computation_diff` empty. The number of rows handed to the LLM is a metric, not a failure.

Before this run, the owed hypothesis review of `w9635_writers.py` was dispatched (`archive/peer/2026-09-23-bench-map-w9635-writers.md`, claude/hypothesis, ANSWERED in 570 s, $1.40, verdict *unverified*). The review found a route that could reuse #9641: `Tunnel.Inside Terminals[]` as the `Wire Source`. That route needs a NEW op, a seed swap on a `LeftOutNode` copy, so it was not built. The review's test 1 was folded into this run.

| wire | p (margin) | arm 1 | op | oracle arm | restored |
|---|---|---|---|---|---|
| 1731 | 0.572 (0.434) | llm | wire_sr LeftIn | ok | yes (exact) |
| 1893 | 0.940 (0.232) | wire | connect_nested | – | yes (exact) |
| 2819 | 0.936 (0.550) | wire | connect_nested | – | yes (exact) |
| 3947 | 0.950 (0.854) | wire | wire_sr LeftIn | – | yes (exact) |
| 4833 | 0.948 (0.646) | wire | connect_nested | – | yes (exact) |
| 7337 | 0.486 (0.486) | llm | wire_sr RightIn | ok | yes (exact) |
| 7388 | 0.946 (0.606) | wire | connect_nested | – | yes (exact) |
| 9635 | 0.940 (0.940) | **wire** | **connect_from_wire / tunnel_outer (rule, PD146)** | – | **yes, beyond the tunnel** |
| 11232 | 0.940 (0.590) | wire | connect_nested | – | yes (exact) |

**Gates: 22 pass / 0 fail.** B0 passes now that the double-count is fixed. B1a: arm 1 made 0 wrong rows. B1: 9/9 restored. **B2: ExecState 1. B3: `computation_diff` ∅.** The LLM-row metric is **2/9** (1731 and 7337, p < 0.75). Wall 349 s, 200 Jev calls ≈ $0.016, 0 LLM turns. Pins and hygiene (H2–H6) all held, and no files were left on disk.

The diff still has 4 rows, which is expected under PD146: #9641 is replaced by the new LoopTunnel **#23006** on both of its edges. Review test 1, read in this run:
- The new tunnel's IndexMode is 0, the same as #9641's.
- Its outer net's source is `FlatSequenceInnerTunnel #9655`, the same source as before.
- **w9649 no longer exists.** The connect re-segmented the feed net, so both tunnels now sit on wire **23273**. This confirms the review's alternative explanation §2 about re-segmentation. It changes no computation.
- ExecState was 0 both before and after the orphan was deleted, because w11232 was still cut at that point. The final ExecState is 1, so deleting the tunnel left no broken loose end.

## Tool changes this bench made (additive; existing behaviour kept unless named)

- **Run 4 (18:3x):**
  - `jev_pairs.op_rule` has the PD146 entry. `decide()` now copies `outer_wire` into `exec.src`.
  - `jev_candidates.term_row` has `outer_wire` for tunnel terminals.
  - `stagekit._cfw_row` is the executor for `connect_from_wire` (generic, and `tunnel_outer` with the orphan delete and the new-tunnel read).
  - `b_endtoend.py`:
    - the beyond-tunnel restored check;
    - the corrected B1a/B1 gates;
    - B4 is now a FACT;
    - the B0 double-count is fixed.

- **Continuation (18:0x):**
  - `jev_candidates.cut_input_tunnel()` plus a new exclusion reason in `candidates()`. **This changes behaviour:** fewer sink candidates.
  - `jev_pairs.decide()` uses the margin rule whenever `th["pair"]` carries `margin`. When it does, the rule replaces the "≥ 2 over 0.70" check. The margin is recorded as `evidence.margin`.
  - `jev_menu_thresholds.json` `pair`: act 0.70 → **0.75**, plus **margin 0.15**.
  - `b_endtoend.py` reads `a5c_margin.json`. It gained the columns `cut_tunnel_excluded`, `margin` and `arm1_executed`, and the gate B1a.

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
