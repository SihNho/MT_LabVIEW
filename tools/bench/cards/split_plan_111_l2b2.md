---
title: L2-B2 split page - PD158 crossing of the 22 B2/B3 rows, and the B2a plan
date: 2026-09-27
card: task_111-5.json
source: docs/d1-loop12-17-split-plan.md PD225(f) (:1937), PD158 (:240-246); tools/bench/facts_c111b_l2b_rows.json; tools/bench/cards/split_plan_110.md
status: plan
---
# L2-B2 — cycle 111 (one page)

**Bed:** `claudeDev\D1_l2_b1_20260927_193100.vi` md5 `b705728a…` (PD225(c)); its graph `tools/bench/graph_l2b1_20260927.json` md5
`8327f974…` (re-checked, `tools/bench/diag_c111e_peek2.log:3`). Endpoint rows read from that graph: `diag_c111e_peek2.log`,
`diag_c111e_peek3.log`, `diag_c111e_peek4.log`. Census rows: `tools/bench/diag_c111e_census_dump2.log` (group B's 8 nodes: 38 cut
terminals in `d1_rewire_sources.json` = 38 in `build_d1_v0.json` `cut`, same (node, i, name, dir, wire) tuples).

## 1. PD158 crossing (RS = d1_rewire_sources row, BV = build_d1_v0 line)
| row | RS | BV | verdict |
|---|---|---|---|
| B2-01 `#8885→#10004` | #1359 i4 w28847 same-loop ← #8885 'x*y' | wired `:1015` | MATCH |
| B2-02 `#8885→#30135` | #29874 i4 w28847 same-loop | wired `:1059` | MATCH |
| B2-03 `#11363→#11261.array` | #11261 i1 w11352 ← #1359 i6 | wired `:1055` | MATCH |
| B2-04 `#28170→#31051` | #1359 i7 from-ctl **28148** 'Force smoothing half-width' | FAILED `:1141` (wire_control 5001) | MATCH by label: RS names the control uid, the row the bed's ControlTerminal #28170 (same label, peek3) |
| B2-05 `#29091→#31137` | #1359 i8 from-ctl **28996** | FAILED `:1145` | MATCH by label (#29091) |
| B2-06 `#29091→#30896` | #29874 i6 from-ctl 28996 | FAILED `:1153` | MATCH by label |
| B2-07 `#29172→#28786` | #29874 i1 source-side w32890, sinks [] | none (source-side) | PARTIAL: neither census names the indicator sink (J1 decision) |
| B2-08 `#5058→#2765` | #2222 i2 w505 to-sr (SR 1147/1142) | wired `:1023` to-sr | MATCH: the sink joins the wire #5058 → x,y,z register (bed w25283 → RSR #10850, peek4) |
| **B2-09** `#8953→SRB1 L.outer` | — (not a B-node terminal) | **no register**: BV `regs` on 1.2 = 1147/1142, 5796/5805, 119/2972, 7311/11001; `sr_changed` [] | **MISMATCH (listed, PD158): build_d1_v0 kept the #1359 ring #9018/#9025 on 1.1; D3 re-makes it on 1.2** |
| **B2-10** `#9227→SRB1 R.inner` | #1359 i2 source-side w9215, sinks [] | none | **MISMATCH (D3), terminal matches** |
| B2-11 `SRB1 L.inner→#9087` | #1359 i1 from-tunnel 9087, outer_source null | NOROUTE `:1167` (source LSR #9025) | MATCH terminal; source = SRB1 (D3) |
| **B2-12** `#28124→SRB2 L.outer` | — | no register (as B2-09) | **MISMATCH (D3, #29505/#29512)** |
| **B2-13** `#29616→SRB2 R.inner` | #29874 i5 source-side w29591 | none | **MISMATCH (D3), terminal matches** |
| B2-14 `SRB2 L.inner→#29911` | #29874 i3 from-tunnel 29911 | NOROUTE `:1183` | MATCH terminal; source = SRB2 (D3) |
| B2-15 `#403→#2276` | #2222 i0 from-ctl **47** 'Z/dZ' | NOROUTE `:1171` "wire_control is name-addressed on BOTH ends" | MATCH by label; no route then either |
| B2-16 `#9306→#6132` | #2222 i5 from-ctl 9289 | FAILED `:1149` | MATCH by label |
| B3-01/02 `#27605→T1→#28370` | #1359 i9 from-tunnel 28343, outer_source #27605 i0 | wired `:1019` | MATCH (T1 replaces 1.1's #28343) |
| B3-03/04 `#5183→T2→#2992` | #2222 i3 from-tunnel 5129 (outer w5174) | NOROUTE `:1175` (source FS inner tunnel 5183) | MATCH: #5183 is a FlatSequenceInnerTunnel, t5186 on w5174 (peek3) |
| B3-05/06 `#5669→T3→#3176` | #2222 i4 from-tunnel 5328 (outer w5336) | NOROUTE `:1179` (FS inner tunnel 5669) | MATCH |
All 38 census rows are covered: B1 11, B2 16, B3 3, never (QRT) 8. Disagreements = the 4 D3 register rows (B2-09/-10/-12/-13); B2-07 PARTIAL.

## 2. Split
| stage | rows | file |
|---|---|---|
| **B2a** (card 111-5) | B2-09..14 + B2-15 = **7** (PD225(f)); plan `tools/bench/plan_l2b2a.json` (`plan_l2b2a_sim2.log`, final, open_rows_match) | `D1_l2_b2a_<ts>.vi` |
| B2b | B2-01..08 + B2-16 = 9 (LoopTunnel owner route, J2; B2-08 after base-flip seeding) | `D1_l2_b2b_<ts>.vi` |
| B3 | 6 | `D1_l2_b3_<ts>.vi` |

## 3. B2a simulation (`tools/bench/plan_l2b2a_sim.log`, `plan_l2b2a_sim2.log`)
- The bed's own cdiff(S1) is **56 rows = 44 (node, term) pairs**, not B1's in-memory 32 rows / 29 pairs (`plan_l2b1_sim6.log`): the
  saved-and-reloaded B1 adds 15 pairs — `#2626` 'array' (4 inputs named 'array') and polymorphic cascades on #8634/#29625 (index
  (row), disabled index (row)), IndexArray #8741/#30331 (index, index (row), disabled index (col)), #8764 'x', FIR #28233 'X',
  #30306 'X', #29005 'element'. Sim 1 failed on that (open_rows 29 ≠ end); sim 2 carries the 15 as BASE rows: final, 56 → 56.
- **None of the 7 rows closes a cdiff row in the sim.** B2-11/-14: #9087's / #29911's inners are flipped sinks on the bed, and
  `stagesim._unflip_restored_tunnels` reverts only flips of the same simulation (`tools/stagesim.py:426-451`, as split_plan_110 §4);
  LabVIEW reverts every inner once the outer has a source (81-5 F1) → real would close #8634 'array' / #29625 'array' and likely
  restore the cascade terminals → E1/PB would diverge. B2-15: the selector edge w730 has no cdiff row at all (B1's end had none
  either) — PB cannot see it; the Error List 'unwired selector' item is its only witness. SR rows: no cdiff-visible edge.

## 4. Recipe
`tools/recipes/stage_d1_l2b2a.py` (107 lines, stagekit; the cut of `stage_d1_l2b1.py`): L0/L1/E1/CT(#403)/D/FU/PB/PS as B1; no #2626
licence (base already names the 4 inputs 'array', carried in open_rows); **RBW-PRE** reads every re-wired sink's wire in the end read
(runs in dry on the sim end) and **RBW-PRE2** reads them in the scratch BEFORE Remove Bad Wires, then RBW checks none of those wires
is deleted (PD224(h) carry). Every sink is a face/register → no node IB (PD184(a)).

## 5. Prior art, dry, pre-run
- Prior art `archive/peer/2026-09-27-priorart-c111e-l2b2a.md` (ANSWERED, annotated): **settled-already / already-failed /
  contradicted / unread-evidence / already-measured.** B2-15 failed L2-B1's dry 3 (`plan_l2b1_dry3.log:84`, CONNECT-NO-VERB,
  `tools/stagexec.py:778-782`); `brief_110-3.md:12-14` put tooling (b) route check at finalize, (c) CT → structure-tunnel face route,
  (d) LoopTunnel owner route, (e) flip_reg seeding BEFORE B2; none is built (PD225(e)). Alternative offered: cut B2a to B2-09/-10/-12/-13.
- **Top-level `--dry` NOT RUN: refused by `guard_cycle.py` (prior-art findings neither refuted nor fixed).** Pre-run not run. The
  recipe's launch is stop-recorded (sha `6c3127bed0d1`). Card rule: a gate refusal is returned BLOCKED.
- Route status by code reading (not measured by a dry): B2-15 CONNECT-NO-VERB (`stagexec.py:778-782`); B2-11/-14 sinks are
  LoopTunnel outer faces (not `OWNER_ROUTED`, `stagexec.py:614`); B2-09..14 address registers made in ANOTHER session — `wire_sr`
  is compiled only for registers created by the same plan (`stagexec.py:406-409`) and SR outer faces need `loop_of`
  (`stagexec.py:1008-1011`), filled only by an `add_sr` op (`:1419`); `load_binding` refuses cross-session register tracking (`:1078-1080`).

## 6. OPEN (judgement)
1. B2a's row set: keep PD225(f)'s 7 rows behind tooling (b)–(e) (+ a route for registers made in an earlier session), or cut to
   the 4 register rows (which also route through the same register-address gap), or delete-and-re-make SRB1/SRB2 inside B2a so
   `wire_sr` applies.
2. The saved B1 differs from B1's in-memory end by 15 cdiff pairs (§3); whether E1/PB for later stages is keyed to the saved-file graph
   (as here) and how cascade terminals restored by LabVIEW are predicted.
