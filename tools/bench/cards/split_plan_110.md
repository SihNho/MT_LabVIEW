---
title: L2-B split page - group B into loop 1.2, B1/B2/B3 (PD223(b))
date: 2026-09-27
card: task_110-1.json
source: docs/d1-loop12-17-split-plan.md PD223(b) (:1902), PD163/164/166/175/182(c); tools/bench/cards/brief_110-1.md D/B
status: plan
---
# L2-B — cycle 110 (one page)

**Input (anchor):** `claudeDev\D1_l2_a3_20260927_151224.vi`, md5 `14337cfd…` (L2-A3, PD223(c)), never modified. Graph read
READ-ONLY from a byte copy (`claudeDev\scratch_c110_bed_*.vi`, deleted) by `tools/bench/diag_c110_bedgraph.py` →
`tools/bench/graph_l2a3_bed_20260927.json` md5 `f01e719d…` (`diag_c110_bedgraph.log`, 8/0: 172/172 diagrams owned; cdiff(S1,bed) ==
plan_l2a3's 6 open rows; LabVIEW gone, scratch deleted). Terminal table of every row below: `tools/bench/diag_c110_terms_bed.log`
(identical to the L2-A2 graph's for group B).

## 1. Property Value targets (brief M) — `diag_c110_bedgraph.log:275,285-286`, `diag_c110_terms_bedx.log`
| node | label (OpNodeLabels_v0, Traverse diagram 52) | target ControlTerminal (by label) | its writer | Value's consumers | class |
|---|---|---|---|---|---|
| `#30117` Property (implicit, `reference` unwired) | `Trans Pos (mm)` | `#30749` in FS frame `#18240` | FS tunnel `#18089 'Numeric'` | `#2626` element (saved record), `#9503`→`#1359`→`#28083 'Magnet position'`, `#20497` (1.1 case) | DATA |
| `#4580` Property (implicit) | `Rot pos (deg)` | `#6178` in FS frame `#113` | FS tunnel `#7511 'Current pos rot?'` | `#2626` element only | DATA |
Target identified by LABEL (an implicit node's header = its control's label, `docs/camera-acquisition-facts.md:310-314`);
`Property.Linked Control` is not built (`docs/NAMES.md:785`). Other D5 crossings: `#10068`/`#29240` = `i mod '# FD points'` /
`i mod '# DT points'` → ring-buffer column index (`#8634`/`#29625` 'index (col)'), `#5119` = image number − LastBufferNumber →
`#2626`, `#11608` Bundler → `#11261` element (`diag_c110_terms_cross.log`). **No crossing is a control/trigger signal (1c'').**

## 2. Cut set (stagesim, `tools/bench/plan_l2b1_sim.log`, 12 sequential moves)
40 cdiff rows after the moves (bed 6). Every B-internal wire is cut (R-SEQ). Sources outside B: 6 D5 data crossings
(QRT), 3 pre-loop feeds, 2 old SR pairs, `#5058`, 3 constants `#6404/#9050/#9906` (read only by B), 2 indicator terminals
`#8323/#28786` (fed only by B). `build_d1_v0.json`'s cut vs `d1_rewire_sources.json`: not re-counted row by row (see OPEN).

## 3. Rows
| stage | rows (wire actions) | file |
|---|---|---|
| **B1** (card 110-3, brief_110-3 item 1: re-cut; FINAL plan `tools/bench/plan_l2b1.json`, `tools/bench/plan_l2b1_sim5.log`; was card 110-2's 10-wire plan md5 `24904e75…`, `plan_l2b1_sim4.log`) | moves: 8 nodes + 4 control terminals + (J1, PD182(a)/(b)) indicators `#8323`/`#28786` + constants `#6404`/`#9050`/`#9906` = 17 (pos = base, PD183(e)); `add_shift_reg` ×2 on `#10170` (SRB1 = `#9018/#9025` ring, SRB2 = `#29505/#29512`); **8 wires**, every end a node or control terminal, none a case-tunnel face or LoopTunnel: `2451.Z out→9833.array`, `7091.X out→6104.array`, `9833.subarray→8885.x`, `11261.appended array→8323`, `6404→6104.index (col)`, `9050→8885.y`, `9906→9833.index (row)`, `5058.x,y,z array out→2626.array`; 29 open (node, term) pairs = 110-2's 27 + `5696`/`6085 'Correction Factor'` (the rows `9306→6132` closed) | `D1_l2_b1_<ts>.vi` |
| **B2** (≤13) | after a measured LoopTunnel owner route (§4b; J2: its own card): `8885.x*y→10004`, `8885.x*y→30135`, `11363→11261.array`, `28170→31051`, `29091→31137`, `29091→30896`, `29172→28786` (J1: #29172 = LoopTunnel of ForLoop #29874) (7); `5058 t5124→2765 t2811` (1); SRB1: init `8953 t8958→L.outer`, `9227 t9234→R.inner`, `L.inner→9087 t9092`; SRB2: `28124 t28172→L.outer`, `29616 t29624→R.inner`, `L.inner→29911 t29928` (6); (brief_110-3 item 1, after a bare-CT-source → case-tunnel-face route) `403 'Z/dZ'→2276 t2282` (w730; closes 0 cdiff rows, `#2276`'s inner faces are unwired on the bed), `9306 'Correction Factor'→6132 t6142` (w6096; closes `5696`/`6085 'Correction Factor'`) (2) = **16 > 13** → three rows to B3 when B2 is planned | `D1_l2_b2_<ts>.vi` |
| **B3** (≤13) | pre-loop T1 `27605 t27635→outer`, `inner→28370 t28378`; T2 `5183 t5186→outer`, `inner→2992 t2996`; T3 `5669 t5671→outer`, `inner→3176 t3193` (6) (+3 from B2 = 9) | `D1_l2_b3_<ts>.vi` |
| never (QRT, D5) | `#10068→10177`, `#30117→9503` + `→2626.element`, `#5119→2626.element`, `#4580→2626.element`, `#11608→11261.element`, `#29240→29777`, `#2626→#376` (w4517) | — |
Pass criteria (each stage, as L2-A3): L1 one op per action; E1 every checkpoint == sim; CT per moved/re-wired ControlTerminal;
D new/lost wires == sim; FU; PB cdiff(S1,end) == the plan's open_rows (FATAL pre-save); PS; IB node sinks after save; RBW.
B1 end rows (card 110-3) = the 29 open (node, term) pairs in `plan_l2b1_in.json` (9 QRT, 20 B2/B3); the 4 rows J1 closes in B1
(`8323`, `6104 index (col)`, `8885 y`, `9833 index (row)`) are no longer open. Checkpoints (J3) = the recipe's rule UNION every
compiled op whose kind is in `stagexec.BIND_KINDS` (here ops 18, 19 = the two `add_shift_reg`).

## 4. Why `5058→2765` left B1 (simulator limit, measured)
`#2765`'s two inner faces are SINKS on the bed (`diag_c110_terms_bed.log`, t2792/t2789 `src=False`: flipped when K moved `#5058`
out of 1.1). Wiring its outer from `#5058` closes 0 rows in the sim (first sim, step 26 cdiff 26→26), because
`stagesim._unflip_restored_tunnels` (`tools/stagesim.py:426-451`) reverts only flips registered in THIS simulation's `flip_reg`
(`:616-619`); the 81-5 F1 measurement says LabVIEW reverts every inner once the outer has a source. So the real run would close
`5696/6085 'x,y,z array'` and fail E1/PB. B1 keeps the row out; B2 carries it after `flip_reg` can be seeded from the base graph.

## 4b. Dry runs (`tools/stage_prerun.py --dry`, top-level, after prior-art `archive/peer/2026-09-27-priorart-c110a-l2b1.md` novel)
- dry 1 (`tools/bench/plan_l2b1_dry.log`): PRIME stop, 5 ForLoop LoopTunnel sinks not addressable (`stagexec.OWNER_ROUTED` =
  SelectorTunnel/Tunnel, `tools/stagexec.py:614`). B1 re-cut to 6 rows (the 5 + `11363→11261`, a LoopTunnel source, to B2).
- dry 2 (`tools/bench/plan_l2b1_dry2.log`): PRIME 6/6 + 2 CT proved; stop at CHECKPOINT: the recipe's derived set
  `[0,4,8,12,14,16,20]` lacks binding op 13 (the first `add_shift_reg`); stagexec needs `[13,14,20]`. Failure budget 2 spent.
  B2's size is then 6 + 1 + 6 + 2 = 15 > 13 → T1 moves to B3 (B2 13, B3 6 or 11).

## 4c. Card 110-3 (8-wire B1): dry 4 PASS, pre-run PASS, launch 1 stopped at PB — NO FILE
- Plan `plan_l2b1.json` md5 `9fb69b9b…` (`plan_l2b1_sim6.log:30`, final, open_rows_match, 32 end rows = 29 pairs); top-level dry
  `plan_l2b1_dry4.log:136` PASS (0 UNROUTABLE); pre-run `plan_l2b1_prerun4.log:148` 10/0 (X10 WARN unmeasured). Recipe bytes unchanged.
- Launch 1 (`stage_d1_l2b1.log`, 744 s): 27/27 ops, every checkpoint diff 0 (E1 `:496`), D 7 new / 14 lost == sim (`:511`), METER peak
  625.1 MB (`:498`); **PB FAIL extra `(2626, 'array')`** (`:550`): in the real end all four #2626 inputs are named `'array'`
  (`:516-519`; the `'element'` rows have `after: None`, `:520-522`) and #5058's wire sits on the 4th, uid 4168 (`:519`; E1 compares uid
  edges, `tools/stagesim.py:1056-1074`). S1 names: `'array'` (w505) + `'element'` ×3. #11261 (inputs unwired, output wired) kept its
  names (`:535-536`). Input md5 unchanged (`:559`), LabVIEW gone (`:574`), nothing saved.

## 5. OPEN (judgement) — 1 and 2 ANSWERED by brief_110-2 J1/J2 (card 110-2)
1. ANSWERED J1: the 5 objects move in B1 (PD182(a)/(b)); their 4 node/control-terminal rows are B1, `29172→28786` is B2.
   Dry-3 review `archive/peer/2026-09-27-c110b-l2b1-dry.md` §4 test: a constant move is measured in a real run (L2-A1 #10739/#10929,
   `tools/bench/stage_d1_l2a1_86-5.log:268,287`); all 10 B1 wires have both ends on #23166 before their step (no implicit tunnel).
2. ANSWERED J2: stagesim base-flip seeding and the stagexec LoopTunnel owner route are B2's tools, their own card.
3. X10: no meter record of this recipe → `X10 WARN unmeasured`. Analog: L2-A3 bed load 569.5 MB (`stage_d1_l2a3_c109b.log`
   METER), mean +1.1 MB/op, +4.7 MB/read; 26 ops + 9 checkpoint reads ≈ 640 MB < 690.
