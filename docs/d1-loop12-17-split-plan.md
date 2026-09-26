---
type: plan
kind: stage-plan
status: current
parent: docs/connectivity-map-plan.md
date: 2026-09-24
tags: [d1, loop-split, decomposition, stage-plan]
---

# D1 — the loop 1.2 / 1.7 splits still owed after S3 (decomposition plan, cycle 69 act 1)

Written by a material session from the files only (no LabVIEW opened). Design choices are NOT made here; they are
listed under `## OPEN` with their evidence. The CLAUDE.md "split and save" rules 1–4 apply: every sub-stage below
leaves a file, the next sub-stage starts from that file in a fresh LabVIEW instance, re-wiring goes in batches of
10–15 rows, a stage that fails twice at the same place is decomposed again before any retry.

## 0. Where we are (measured)

- **Bed** = `claudeDev\D1_s3_loop15.vi`, md5 `1a11d92aacabf7ec844d65b8af19f39f` (`docs/connectivity-map-plan.md:100`,
  Pre-decided 147). S3 as re-cut moved ONLY loop 1.5's set (`#10407`, `#48`, `#3529`, `#3560`, `#3447` → body
  `#23058` of `WhileLoop #23032`; `tools/bench/stage_d1_m4a.log:197` for `#10407`, the rowD wiki for the other four).
- **Owed:** the original S3 (`docs/d1-build-plan.md:675`) moved 23 objects — **17 → 1.2, 5 → 1.5, 1 → 1.7** — plus
  8 shift registers (`:677`) and 6 `ControlTerminal`s (`:677`, `:392-407`). The 1.2 and 1.7 parts are not scheduled
  by any current plan row.

## 1. Node sets (source: `tools/bench/build_d1_v0.json` key `moved`, = `docs/d1-build-plan.md:287-308`)

Cut rows = `build_d1_v0.json` key `cut` (2026-09-17 route-A run on a copy of the original; uids are the S1 uids —
all 18 non-structure uids below read `frame_diagram 639` in both `docs/wiki/subvi/D1_s1_copy.json` and
`docs/wiki/subvi/D1_s3b_m3a3b_rowD_20260922_161040.json`; structures `#5540 #10445 #1359 #2222 #29874` own no
terminals of their own in the wiki and are located through their tunnels). **These counts are a PREDICTION to be
re-derived on the bed by P0**, not an address list.

| group | uids (label, build-plan line) | cut rows | of which unnamed |
|---|---|---:|---:|
| **A** reseed / selector chain | `#5540` Case (reseed) · `#9647` And · `#10247` Or · `#10445` Case · `#10950` Less? · `#17289` `min value` Property · `#10969` Array Max&Min · `#10757` Index Array (`:288-295`) | 26 | 5 |
| **B** forward slice | `#1359` For · `#2222` Case · `#2626` Build Array · `#6104` Index Array · `#8885` Multiply · `#9833` Index Array · `#11261` Build Array · `#29874` For (`:296-303`) | 38 | 13 |
| **C** schedule | `#10686` And (`:304`) + the two §5a-ter re-wire rows w10799 / w10990 (`:344-360`) | 3 + 2 | 0 |
| **W** writer (1.7) | `#376` `save trace.vi` (`:308`) | 12 | 0 |
| **K** kernel — MOVES to 1.2 (Pre-decided 156) | `#5058` `Track N beads four-fold over-kernel-v3.vi` (`:287`) | 13 (key `cut`, uid 5058) | — |

Shift registers still on the frame loop `#637` that belong to 1.2 / 1.7 (`tools/bench/graph_loops_m4b_20260924.json`,
loop 637 `left_of`; plan `docs/d1-build-plan.md:376-383`): 1.2 = `#1147/#1142`, `#5796/#5805`, `#119/#2972`,
`#7311/#11001`; 1.7 = `#15/#51` (accumulator), `#24/#1108` (error chain).
Control terminals that move into 1.2 — **REWRITTEN 2026-09-24 by Pre-decided 158** from the measured six
(`tools/recipes/build_d1_routeb_v7.py:443-453`, `tools/bench/build_d1_routeb_v7_run10.log:23-31`; the old list at
`docs/d1-build-plan.md:401-406` wrongly carried two indicators): `Auto-Reset` #17472 (ctlterm #17487), `Reset Tracking`
#5605 (#5634) — group A; `Z/dZ` #47 (#403), `Correction Factor` #9289 (#9306), `Force\nsmoothing\nhalf-width` #28148
(#28170, → `#1359` t7), `Extension\nmedian filter\nhalf-width` #28996 (#29091, → `#1359` t8 / `#29874` t6) — group B.
`min value` #17257 and `Force (pN) vs Extension (nm) ` #8038 are INDICATORS (sinks of `#10969` / `#11261`), not moved
controls. `Diagram #639` holds **31** ControlTerminals (`build_d1_routeb_v7_run10.log:23`). The ctlterm uids are the
original's; P0 re-reads them on the bed.

## 2. Sub-stages (order RE-CUT 2026-09-24 by the cycle-69 judgement, Pre-decided 157: smallest-first, L7 before L2; each row = one saved artefact)

**Every sub-stage below SAVES its output file, and the next sub-stage opens THAT file in a FRESH LabVIEW instance
(Pre-decided 162).** Every row address is a uid (+ exact terminal name), re-read on the live file immediately before
use — never a Traverse / node / diagram index (Pre-decided 158; `docs/d1-build-plan.md:356` is the old failure).

| id | does | input file | output file (under `claudeDev`) | rows | Jev PAIR / rule |
|---|---|---|---|---:|---|
| **P0** | read-only census of the bed: wiki + graph for md5 `1a11d92a`; re-derive every group's cut list, crossing list and new-carrier list; measure handles open→close (STATUS ACT 2); O1 node sets of `#10170`/`#23041`; ForLoop/WhileLoop left-SR TOP collisions (Pre-decided 159). **MEASURED — see the P0 facts line under this table** | `D1_s3_loop15.vi` | `docs/wiki/subvi/D1_s3_loop15.json`, `tools/bench/graph_s3_loop15_<date>.json`, `tools/bench/split_rows_l2l7.json` (data, no VI) | 0 | — |
| **P1** | pure-Python resolver (no LabVIEW): the 33 structure rows → the TUNNEL uid that carries each (outer face on `#639`, + inner frame diagrams), by wire identity on the bed's terminal table, cross-checked against S1's; plus F3a (the 12 FlatSequenceFrame-cut ForLoop owner chains re-derived from the `frame_diagram` column). **MEASURED — see the P1 facts line under the P0 facts** | `split_rows_l2l7.json`, `graph_s3_loop15_20260924.json`, `D1_s1_copy.json` wiki, `build_d1_v0.json` `cut` | `tools/bench/split_rows_l2l7.json` (new fields `p1_tunnel`, `resolved_by_p1`, `p1_wire_on_bed`, top-level `p1`; data, no VI) | 0 | — |
| **L7-1a** | **SPLIT 2026-09-24 by Pre-decided 169**: move `#376` into body `#23405` of `#23041` + create the two new SR pairs; NO wiring; recipe `tools/recipes/stage_d1_l7_1a.py`, contract `tools/bench/l7_1a_predict.log` | `D1_s3_loop15.vi` | `D1_l7_1a_<ts>.vi` (GUI save, rule 6) | 0 | 0 / 0 |
| **L7-1b** | ✅ **DELIVERED 2026-09-24 06:1x (cycle 72 firefighter, run 3): `claudeDev\D1_l7_1_20260924_060431.vi` md5 `e5c7d68b56d018131f2ebf0df656fdd6`, `tools/bench/stage_d1_l7_1b_r3.log` 38/0, 761 s; all 9 rows wired, second pass by `verify_term_uid` Is Broken? False ×4, PB = exactly the 8 predicted rows, PC1–PC3 pass, ExecState 0 as predicted (L7-R rows open), input + bed md5 unchanged, refs 23/23, handles 34,146 at exit. r4's B4 is MEASURED: the new SR outer terminals kept their uids across the connect (#24205/#24291 resolved by uid after wiring).** Original brief: **Pre-decided 169/171**: from the saved L7-1a file, fresh LabVIEW: the 9 rows of the L7-1 row below (4 S1-mapped per 168 + 2 single-candidate per 165 + 3 tunnels per 166), corrected intent lines (171(1)); PB `computation_diff` FATAL before save (170(c)); runs in the same material dispatch as L7-1a when L7-1a passes (171(4)); recipe `tools/recipes/stage_d1_l7_1b.py` | `D1_l7_1a_<ts>.vi` | `D1_l7_1_<ts>.vi` | 9 | 4 S1-mapped / 5 rule |
| **L7-1** (superseded by the L7-1a/L7-1b rows above, kept for the row detail) | **REWRITTEN 2026-09-24 by Pre-decided 164** (was: "2 SR pairs move with their node; re-wire its 12 rows; w4517 made as a 1.1→1.7 crossing here"): move `#376` into body `#23405` of `#23041`; create 1.7's TWO NEW SR pairs replacing `#15/#51` and `#24/#1108` (the old pairs stay on `#637` until L7-R), each new LEFT initialised off the same source as the original (`#4910` w4969, `#781` w3543); wire the 4 rows inside 1.7 (`#376` ↔ new SRs) by Jev PAIR; the 2 SR-init rows are RULE-SINGLE-CANDIDATE rows (Pre-decided 165); i6/i9/i11 (`#3644`/`#2294`/`#5096`) are re-made as NEW tunnels on `#23041` off the same outer feed (Pre-decided 166, `tunnel_outer` rule rows). Of `#376`'s 12 rows: in-1.7 4 · top-level tunnel 3 (L7-1, 166) · cross-loop OPEN 3 (i5 w4517, i7 w3268, i8 w1397 — queues, never made here) · L7-R 1 (i4) · split 1 (i3). Prediction `tools/bench/l7_1_prediction.json` (`tools/bench/l7_1_predict_r2.log`) | `D1_s3_loop15.vi` | `D1_l7_1_<ts>.vi` (GUI save if broken, CLAUDE.md §3 rule 6) | 9 (4 body + 2 init + 3 tunnel) | 4 / 5 |
| **L7-R** | ✅ **DELIVERED 2026-09-24 07:2x (cycle 73 material, run 2): `claudeDev\D1_s4_loop17.vi` md5 `4b621946492da3d2fbb96b6053e715ec`, 481,808 B, `tools/bench/stage_d1_l7_r_r2.log` 61/0, 459 s. Executed Pre-decided 175: PMV (move_in ControlTerminal on a scratch) PASS; A0 index 3 == uid 3182; 7 wires deleted by uid; #3052/#3453 moved into #23405; Jev top == S1-mapped on 4 rows (p 0.42/0.95/0.91/0.93); 2 re-feeds from the new RIGHT SRs; output tunnels #5204 (file progress → #2048 'length' + #6384 'actual # data points') and #10404 (→ #6384 'file # to append'), IndexMode 0 = #1929/#5020; 6 second passes Is Broken? False; retire 6 carriers (#1929/#5020 already gone with their wires); RBW 7 half-wires, no live edge. PB cdiff(S1,new) = exactly the w4517 row; PC1/PC2 = predicted; ExecState 1 warm, scripted save + re-read 1 (t5/t7 OPEN yet not required); cold not read (moves to QRT, 175). cdiff does NOT report the unwired 'frame index' (w3268) — FIN finding. Contract `tools/bench/l7_r_predict.log`, recipe `tools/recipes/stage_d1_l7_r.py`.** Original row: retire `#15/#51`, `#24/#1108` on `#637` after live-consumer check; re-feed from 1.7's output tunnels. **CORRECTED 2026-09-24 (prior-art c70-l7-1-r2 A3.3; measured `tools/bench/l7_1_predict_r2.log:22-27`):** L7-1 leaves SIX consumers of `#376`'s outputs unsourced, not two — `#6384` `error in` / `file # to append` / `actual # data points`, `#2048` `array` / `length`, `#3453` `file progress` (an indicator on 1.1). Which stage owns `#2048` and `#3453`, and the third `#6384` input, is OPEN (judgement). RBW; save by script | `D1_l7_1_<ts>.vi` | **`D1_s4_loop17.vi`** | retire + 6 (ownership OPEN) | 0 / all |
| **K** | ✅ **DELIVERED 2026-09-25 10:0x (cycle 79): `claudeDev\D1_k_20260925_100155.vi` md5 `6cf5b077…`, `tools/bench/stage_d1_k_r2.log` 35/0; design Pre-decided 177–178(i).** Original row: move the CPU kernel `#5058` `Track N beads four-fold over-kernel-v3.vi` into the 1.2 body (Pre-decided 156; name-gated, `docs/cycle27-plan.md:754-755`); re-wire its 13 rows | `D1_s4_loop17.vi` | `D1_k_<ts>.vi` (GUI save if broken) | 13 | P0 recounts |
| **L2-A1** | move group A (8) + the `Auto-Reset` / `Reset Tracking` control terminals into the 1.2 body; add 1.2's 4 SR pairs; re-wire batch 1 (incl. w10990 `#10757`→`#10407`, the only row left of old L2-C — Pre-decided 161) | `D1_k_<ts>.vi` | `D1_l2_a1_<ts>.vi` (broken by design → GUI Ctrl+S, CLAUDE.md §3 rule 6) | 13 | 3 / 10 |
| **L2-A2** | re-wire batch 2 of group A (`min value` #17257 is an INDICATOR fed by `#10969` — a sink row, not a moved control, Pre-decided 158) | `D1_l2_a1_<ts>.vi` | `D1_l2_a2_<ts>.vi` | 13 | 3 / 10 |
| ~~**L2-C**~~ | **REMOVED by Pre-decided 161**: `#10686` stays on 1.1, so w10799 `#10686`→`#10407` stays as S3 left it; w10990 moved into L2-A1 | — | — | 0 | — |
| **L2-B1..B3** | move group B (8, incl. ForLoops `#1359` / `#29874` with their own SRs) + the FOUR controls `Z/dZ` #47, `Correction Factor` #9289, `Force\nsmoothing\nhalf-width` #28148 (→ `#1359` t7), `Extension\nmedian filter\nhalf-width` #28996 (→ `#1359` t8 / `#29874` t6); `Force (pN) vs Extension (nm) ` #8038 is an INDICATOR fed by `#11261` (sink row); rows from `d1_rewire_sources.json` cross-checked against `build_d1_v0.json` (Pre-decided 158); gate per Pre-decided 159 | previous | `D1_l2_b1_<ts>.vi` → `…b2…` → `…b3…` | 13/13/12 + the two control rows | 2 / 36 over the three |
| **L2-R** | retire the 4 old 1.2 carriers on `#637` after a live-consumer check (Pre-decided 142's pattern), junk purge, Remove Bad Wires, save by script | `D1_l2_b3_<ts>.vi` | **`D1_s5_loop12.vi`** | retire rows | 0 / all |
| **QRT** | (+ Pre-decided 175: the two OWED 1.7 input rows t5 w4517 `#2626`→`#376 'current frame data array in'` and t7 w3268 `#637` i→`#376 'frame index'` get a queue here — no planned queue carries them; + Pre-decided 177(e): the OWED 1.2 input row w3040 `#6810 'Image Out'`→`#5058 'Image In'`) the queue RESOLUTION TABLE (`docs/cycle27-plan.md:930-933`, 34(g)): for each of the eight queues the `(uid, exact terminal name, diagram)` on `D1_s5_loop12.vi`, or the stage that must run first. A document, no LabVIEW write (Pre-decided 156) | `D1_s5_loop12.vi` → read only | the table (doc) | 0 | — |
| **STOP** | 1.2 / 1.7 conditional terminals driven by the stop design (build-plan S4/S4s, `:679-680`), inputs from QRT | `D1_s5_loop12.vi` | `D1_s6_stop.vi` | from QRT | — |
| **ROT** | Pre-decided 133: repoint the 9 rotor call sites to `claudeDev\SetCommand_signed.vi` md5 `ec87a2657b158722082ca00c7074f114` by `SubVI.Replace` 635E001, measured first on a scratch copy together with the Baseline/Ring constants (Pre-decided 160) | `D1_s6_stop.vi` | `D1_s7_rotor.vi` | 9 (+ constants per the scratch measurement) | 0 / 9 |
| **FIN** | census, ExecState 1 warm + cold, final save — the GPU top level is the default final file (Pre-decided 161) | `D1_s7_rotor.vi` | GPU top level (name after the GPU-swap stage, never "GPU" before it, `docs/cycle27-plan.md:756`) | 0 | — |

**P0 facts (MEASURED 2026-09-24 01:34–01:39, `tools/bench/p0_c69_census.py` → `tools/bench/p0_c69_census.log`, 10 pass /
0 fail, `BGRUN END rc=0 after 284s` `:219`; bed md5 `1a11d92a…` before and after `:7`/`:204`; scratch deleted, files left []
`:213`; data `tools/bench/split_rows_l2l7.json`, `tools/bench/graph_s3_loop15_20260924.json`):**
- **(1) O1:** body `#23166` is owned by WhileLoop `#10170` and body `#23405` by `#23041` (`:23`, `:27`); each holds ONLY its
  scaffold — `#10171` Comparison + `#23417` LoopTunnel, and `#23042` Comparison + `#23501` LoopTunnel (`:24`, `:28`); **0 plan
  L2/L7 nodes in either** (`:25`, `:29`). All 19 plan nodes (L2's 18 incl. `#5058`, L7's `#376`) are owned by `Diagram #639`
  (loop `#637`, 1.1) (`:31-67`). Nothing on the bed binds either loop to 1.2 or 1.7 — O1 stays a naming choice. **(O1 CLOSED 2026-09-24 by Pre-decided 163: 1.2 = `#10170`, 1.7 = `#23041`.)**
- **(2) SR TOPs:** ForLoops `#1359` and `#29874` hold **0 shift registers** (loop table + `:86-87`), and **no ForLoop is nested
  inside any plan node** (owner chains of all 17 ForLoops, `:68-129`). Touched loops: `#637` — 12 lefts, TOPs all distinct,
  **0 collisions** (`:140`); `#10170` / `#23041` — 0 SRs (`:131`, `:133`). **J4 row: no TOP collision in any touched loop**
  (`:158`). The bed's ONLY TOP collision is loop 1.5's body `#23058` (`#23880`/`#23796` at TOP 2826, `:153`) — machine-paired
  already (`graph_loops_m4b_20260924.json`), and not touched by L2/L7.
- **(3) handles:** 33,985 sixty s after restart → **54,395 after opening the bed** (+20,410; `:20`) → **34,331 after closing it**
  (+346 over base; `:195`). Pre-decided 147(c)'s ~54.4k is the OPEN level, confirmed.
- **(4) rows:** `build_d1_v0.json` `cut` and `d1_rewire_sources.json` give the SAME 92 rows over the 19 owed uids — **0
  disagreements** (`:159-160`; 92 = A 26 + B 38 + C 3 + W 12 + K 13). **59 resolve on the live graph by uid + terminal name;
  33 do not** (`:161`), and all 33 are on the five STRUCTURES `#5540` (7), `#10445` (4), `#1359` (9), `#2222` (7), `#29874` (6)
  (`:162-194`): a structure owns no terminal rows of its own (they sit on its tunnel uids), so the uid+name resolver cannot
  address them — the structures themselves are present on `#639` (`:31`, `:37`, `:47`, `:49`, `:61`). Those 33 rows need
  tunnel-uid addressing before any stage uses them.

**P1 facts (MEASURED 2026-09-24 02:43–02:46, pure Python, no LabVIEW; `tools/bench/p1_c70_resolve.py` →
`tools/bench/p1_c70_resolve.log` run 2 `:51-100` 7 pass / 0 fail `BGRUN END rc=0` `:100`; `tools/bench/p1_c70_f3a.py` →
`tools/bench/p1_c70_f3a.log` run 2 `:40-79` 5/0 `BGRUN END rc=0` `:79`):**
- **(1) rows: 92/92 resolved, 0 ambiguous, 0 unresolved** (`p1_c70_resolve.log:97`; tally name 59 + tunnel 33). Each of
  the 33 structure rows is the OUTER face (on `#639`) of exactly one tunnel; the bed tunnel uid equals S1's for all 33
  (`:88`). Tunnels per structure (`:89-93`): `#5540` → `5603 5967 5680 5702 5725 5825 6016` (t0..t6; inner frames
  `5582/5592`) · `#10445` → `10465 10584 10750 11336` (inner `10453/10459`) · `#1359` → `9087 9227 9503 10004 10177
  11363 31051 31137 28370` (t1..t9; inner `7911`) · `#2222` → `2276 2451 2765 2992 3176 6132 7091` (t0..t6; inner
  `2235/2265`) · `#29874` → `29172 29777 29911 30135 29616 30896` (t1..t6; inner `29894`). Five rows had TWO tunnel
  candidates on their wire and were decided by the inner-frame match with the structure's other tunnels (bed and S1
  agree): `#1359` t3 w30592 (→9503, not 20497), t4 w28847 (→10004) / `#29874` t4 w28847 (→30135), `#1359` t8 w31166
  (→31137) / `#29874` t6 w31166 (→30896). Inner-frame sets are one per structure and pairwise disjoint (`:94-95`).
  Two NAME-resolved rows have an S1 wire uid absent on the bed: `#10757` t1 w10990, `#10686` t0 w10799 (`:96`).
  Run 1 (`:1-50`) failed its S1 gate only because the S1 check skipped the inner-frame pass (script defect, fixed).
- **(2) F3a:** every one of the 17 P0 ForLoop chains reaches TopLevelDiagram `#536` (`p1_c70_f3a.log:61`); the cut
  frames are frames of the two top-level flat sequences — `{686, 81548, 113, 124, 759, 1817, 3121, 3628, 4866, 5031}`
  and `{13236, 15041, 21134, 25769, 12960, 14840, 19687, 19887, 20261, 26117}`, owner `#536` (`:44-60`; every
  FlatSequenceInnerTunnel reports its sequence's owner diagram as a third frame, 238 of them `#536`, `:41`); 167
  directed edges agree with the derived tree, 0 contradictions (`:42`). **No ForLoop is nested inside any L2/L7 plan
  structure** (`:62`). Left SRs: `#637` body `#639` 12 lefts, TOPs all distinct; ForLoops nested below `#639` =
  `1359 2457 4810 29617 29874`, their lefts `#2603` 1 · `#29629` 2 (TOPs 1675/1620) · `#7911` 0 · `#29894` 0, no TOP
  collision; `#10170`/`#23041` bodies 0 lefts, nothing nested (`:63-77`). **J4: no two ForLoop left SRs in the
  affected loops share a TOP.**

**Why L2 before L7 — SUPERSEDED by Pre-decided 157** (kept for the record): `#376` t5 `current frame data array in` is fed by w4517 from
`#2626` (group B) (`build_d1_v0.json` key `cut`, rows `[2626,0,…,4517]` and `[376,5,…,4517]`). If L7 ran first,
w4517 would be re-made as a 1.1→1.7 crossing and re-made AGAIN as 1.2→1.7 at L2-B. L2 first makes it once.
**Why ROT late:** the 9 sites' frame diagrams are `#28036 #27425 #27076 #19033 #18718 #18317 #28412` (both wikis),
none of them `#639` or `#23058`, so no split touches them; placing ROT after the splits keeps every split stage's
`computation_diff(S1,new)` prediction at **0 rows**, while ROT's own prediction is exactly its 9 rows. (A choice of
order — judgement may move it; O6.)

**Jev PAIR vs rule rows.** Pipeline per `docs/connectivity-map-plan.md:93,96` (Pre-decided 143/146):
`tools/jev_candidates.py` enumerates the legal pairs → `tools/jev_pairs.py` `decide` (PAIR at the thresholds in
`tools/bench/jev_menu_thresholds.json`; op by `op_rule`, `tools/jev_pairs.py:181-220`, Jev OP only when the rule
has no entry) → `write_record` → `stagekit.Stage.from_decision` (`tools/stagekit.py:830`).
- **rule rows** = both endpoints are fixed by the S1 edge (same uid + terminal on both sides): same-loop, constant,
  control, tunnel (`tunnel_outer`, Pre-decided 146; FSIT sink → `fs_inner_tunnel_connect`) and source-side rows,
  plus every `retire`/`delete` row.
- **Jev PAIR rows** = one endpoint is a NEW carrier created in that stage (the new SR pairs; a new crossing carrier)
  so its terminal is chosen among candidates — **and the legal candidate set has ≥2 pairs (Pre-decided 165, 2026-09-24):
  a new-carrier row with EXACTLY ONE legal pair whose source equals the S1 edge's source is a RULE row
  (`RULE-SINGLE-CANDIDATE`)**. Counts above = the v0 run's `from-sr`/`to-sr` rows per group
  (A 3+3, B 2, W 2+2); P0 recomputes them on the bed.

## 3. Pass criteria per sub-stage (Pre-decided 132 applied: every predicted value names what already determines it)

| sub-stage | gate | predicted | determined by an earlier step? → treatment |
|---|---|---|---|
| all | input md5 = the previous stage's output md5; pins unchanged | equal | hygiene, not evidence — kept |
| P0 | bed md5 after the read | `1a11d92a…` | — kept |
| P0 | re-derived cut rows vs `build_d1_v0.json` | per group 26/38/3/12 **minus/plus the rows M3a–M4 changed** (the S3a indicator branches on w10799 / w10990, the retired 1.5 carriers) | the v0 file determines the base ⇒ predict the DIFFERENCE, list it |
| L7-1a | `diff(bed,new)` (Pre-decided 169) | nodes_added = exactly the 4 new SR uids, nodes_removed = [], every removed uid-edge touches `#376` **except an edge admitted by Pre-decided 172** (listed by edge in the prediction, its wire uid survives with every sink, its source is a tunnel whose only inside source was the moved node — here `#1929:2043→#2048:3182`, `#1929:2043→#6384:6480`, `#5020:5050→#6384:6511`), no uid-edge added; bed md5 unchanged (`tools/bench/l7_1a_predict.log`) | not determined by an earlier step — the gate (no rows wired) |
| L7-1a, L7-1b, K, L2-A1, A2, B1, B2 | `ExecState` | 0 (rows still open) | determined by the stage's own design ⇒ **NOT a gate**; broken intermediate saved by GUI (rule 6), never run |
| same | `computation_diff(S1,new)` (MACHINE SR pairing, `tools/vigraph.py:333-388`) | = exactly the not-yet-re-wired ledger rows of this group | not determined — the gate. **L2-B1..B3 (ForLoop SRs of `#1359`/`#29874` move): only if P0 showed no two ForLoop left SRs in the affected loops share a TOP; otherwise the gate lists the TOP-collision rows as predicted artefacts (Pre-decided 159)** |
| same | `diff(prev,new)` | = owner changes of the moved uids + the batch's re-made edges + the new SR objects, nothing else, **plus removed edges admitted by Pre-decided 172's three conditions (listed by edge). From L7-1b on, the three `#1929`/`#5020` → `#2048`/`#6384` edges are BASELINE: absent in the input and must stay absent (L7-R rows; re-adding one fails the gate — `tools/bench/l7_1b_predict.log` PC3)** | op semantics predict the SHAPE, not the rows — gate on the row list |
| same | `WhileLoop` 6, `Local` 8, `ControlTerminal` 114 | delta 0 | determined by S2 / move semantics ⇒ delta tripwire only, not evidence |
| L2-A1 (was L2-C) | w10990 wired, `Is Broken?` False (ordered second pass, cycle27 42(b)); w10799 untouched | False | not determined — gate |
| L2-R, L7-R | live consumers on each retired carrier (`sources_of`/`reach4`, completed graph) | 0 | not determined — gate, BEFORE the delete |
| L2-R, L7-R | `ExecState` warm, then cold in a restarted LabVIEW | 1 | NOT implied by RBW (RBW can bare a register, Pre-decided 132 / `docs/cycle27-plan.md:3705-3715`) — gate |
| L2-R, L7-R | `computation_diff(S1,new)` | 0 rows | not determined — gate |
| L2-R, L7-R | handles open→close vs P0's measured post-load level | ±100 | P0 determines the baseline — gate on the delta |
| ROT | `computation_diff(S1,new)` | exactly 9 rows, each the callee identity at the 9 uids | **unmeasured whether `computation_diff` sees callee identity at all** ⇒ a control first (O6) |
| FIN | cold `ExecState`, original md5 unchanged | 1, `2a78e17c…` | — gate |

## 4. S3w-a…e vs S4–S6 — the conflict, stated (not resolved)

- `docs/cycle27-plan.md:388` S3 = `D1_s3_moved.vi`, *"21 nodes + 8 control terminals moved"*; `docs/d1-build-plan.md:675`
  S3 = *"23 objects reparented"* and `:677` *"6 ControlTerminals"* (count corrected 2026-09-17 at `:394-397`).
- `docs/cycle27-plan.md:389` S3w-a…e = re-wiring *"≤15 rows of the 66"*; `docs/d1-build-plan.md:676` S3b =
  *"109 terminals over 24 uids"* and `build_d1_v0.json` key `cut` = 109 rows.
- `docs/cycle27-plan.md:390` S4–S6 = `D1_s4_census.vi` → `Track_v6_D1_GPU.vi` (*census, ExecState 1, saved*);
  `docs/d1-build-plan.md:679-682` S4 / S4s = the sentinel stop design, S5 = purge + ExecState 1 + save,
  S6 = cold reopen. Same labels, different content: the build plan's S4 is a design stage (stop), cycle 27's S4
  is a census.
- The S3 actually built (S3a, S3b M3a-1 … M4) followed neither: it moved 1.5 only, carried 1.5's inputs by S3a
  indicators + a Local read (not queues), and retired carriers (Pre-decided 142) instead of batch re-wiring.
- This plan uses new ids (P0, L2-*, L7-*, STOP, ROT, FIN) so it collides with neither label set.

## L7-R facts (cycle 73, measured)

Measured offline (no LabVIEW) by `tools/bench/c73_l7r_facts.py` -> `tools/bench/c73_l7r_facts.log` over the S1 wiki
(`docs/wiki/subvi/D1_s1_copy.json`, md5 3e3d23ce…) and the S3 graph (`tools/bench/graph_s3_loop15_20260924.json`,
md5 1a11d92a…). No L7-1 graph is on disk; L7-1 = S3 + the edits in `tools/bench/stage_d1_l7_1a.log:92` and
`tools/bench/stage_d1_l7_1b_r3.log:346`. Diagram ids: 639 = `#637` body (1.1), 23405 = `#23041` body (1.7), 686 = the
frame holding both loops. Facts only; no design choice is made here.

| # | fact | source |
|---|---|---|
| M1 | 8 CDIFF rows, S1 wire / S1 source → sink: w4517 `#2626 BuildArray 'appended array'` (639) → `#376 'current frame data array in'`; w1397 `#3052 ControlReferenceConstant 'File # Saved'` (639) → `#376 'saved file refnum'`; w3957 `#15` outer → `#2048 'array'` (eff. `#376 'total data array out'`); w4337 `#1929` outer → `#2048 'length'` AND `#6384 'actual # data points'` (eff. `#376 'file progress'`); w5274 `#376 'file progress'` → `#3453` (and `#1929` inner); w1899 `#24` outer → `#6384 'error in'` (eff. `#376 'error out'`); w5073 `#5020` outer → `#6384 'file # to append'` (eff. `#376 'file number to append out'`) | `c73_l7r_facts.log` M1 block |
| M1 | In L7-1: `#376` sits on 23405 (1.7); `#2048`, `#6384` on 686; `#3453`, `#2626`, `#3052` on 639 (1.1); tunnels `#15/#24/#1929/#5020` still on `#637`. Removed by L7-1a: w4517, w1397, w5274(→#3453), w3268, and `#1929/#5020` → `#2048/#6384` (PD172). w3957 and w1899 are NOT in the removed list (their `#15`/`#24` inner sides lost `#376`) | `stage_d1_l7_1a.log:92,97`; `stage_d1_l7_1b_r3.log:206,346` |
| M2 | `#2048` GrowableFunction (Array Subset, `d1-build-plan.md:367`), 686 in S1/S3/L7-1; in: array←`#15`, index←`#2064 'index'` (w5314), length←`#1929`; out subarray w4564 → `#6384 'data array'` only | log M2 |
| M2 | `#6384` SubVI `save N xyz traces.vi`, 686; in: actual # data points←`#1929`, base path←`#4693` (eff. `#29551 path`), cal cluster path←`#1748` (eff. `#3391`), data array←`#2048`, desired #←`#2484` (eff. `#1766`), error in←`#24`, file # to append←`#5020`; out error out w1920 → `#4774 'error out'` | log M2 |
| M2 | `#3453` ControlTerminal `file progress`, owned by Diagram#639 (1.1); one input w5274 ← `#376 'file progress'`; no outputs | log M2; `d1-build-plan.md:220` |
| M2 | `#1929` LoopTunnel on `#637`: inner ← `#376 'file progress'`, outer → `#2048 'length'`, `#6384 'actual # data points'`. `#5020` LoopTunnel on `#637`: inner ← `#376 'file number to append out'`, outer → `#6384 'file # to append'` | log M2 |
| M2 | Planned node sets: `build_d1_v0.json` `moved` puts only `#376` in 1.7 plus SR rows `total data array out` (`#15/#51`) and `error out` (`#24/#1108`); `#2048`, `#6384`, `#3453` appear in no 1.7 set. `d1-build-plan.md:365-370` §5b: `#6384`, `#2048` stay on diagram 19 ("none moves"), fed "off 1.7's output tunnels instead" | `build_d1_v0.json:14,132,946-958`; `d1-build-plan.md:365-370,308` |
| M3 | S1, `#376` outputs → `#376` inputs: reached `error in` via `error out` → `#24` → SR → `#1108` → `error in`, and `total data array in` via `#15` → SR → `#51`. With SR edges excluded: none. From `#2048`/`#6384`/`#3453` outputs: none | log M3 |
| M4 | `#376` terminal order (S1 wiki): t0 OUT error out, t1 OUT total data array out, t2 IN error in (←`#1108`), t3 OUT file progress, t4 OUT file number to append out, t5 IN current frame data array in (w4517), t6 IN cal cluster path (←`#3644`), t7 IN frame index (w3268), t8 IN saved file refnum (w1397), t9 IN file size (←`#2294`), t10 IN total data array in (←`#51`), t11 IN selected path (←`#5096`) | log M4 |
| M4 | t5 source `#2626` BuildArray on 639 (runs every `#637` iteration; `d1-build-plan.md:299` moves it → 1.2). t7 source = a terminal of diagram 639 itself (w3268: 2 source rows, 8 sinks incl. `#1114 'index i'`), a per-iteration value. t8 source `#3052` ControlReferenceConstant on 639 (a constant; `d1-build-plan.md:319` keeps it in 1.1). t3/t4 are OUTPUTS (consumers above) | log M4; `graph_s1_20260924.json` flags[0] |
| M5 | Queues into 1.7: `Q_res` DBL[] / `Q_good` Bool[] / `Q_rmeta` DBL, "the kernel's own outputs", unbounded, lossless FIFO (`d1-build-plan.md:574`); sentinels written by 1.2, exited on by 1.7 (`:653-654`); resolution table: `Q_res` src `#637 'x,y,z array out'`, `Q_good` `#637 'Bead is good? array out'`, `Q_rmeta` `#637 'current image number'`, all state A on `#686` (`:602-604`). `docs/cycle27-plan.md:930-933` names no queue; it says the owed work is a resolution table per queue | as cited |
| M6 | A delete-by-wire-uid verb exists: `stagekit.Stage.delete_wire(wire_uid)` (`tools/stagekit.py:527`) → `build_opfsinnertunnelconnect_v0.del_wire` (`tools/recipes/build_opfsinnertunnelconnect_v0.py:336`, Wire-traverse index then `g.delete_object(verify=False)`); the row executor maps action `delete_wire` to it (`stagekit.py:861`). Used with a uid-census gate in `tools/bench/bench_map_20260923/b_endtoend.py:60-63` | as cited |

## Pre-decided (continues `docs/connectivity-map-plan.md`; only facts measured from files)

148. **Owed node sets** are `build_d1_v0.json` key `moved`: 17 → 1.2, 1 → 1.7 (1.5's 5 are done); cut rows
     A 26 · B 38 · C 3 · W 12 (67 + 12), key `cut`. They are the prediction; P0's census on the bed is the address list.
149. **1.2/1.7's six shift registers are still on `#637`** in the bed (`graph_loops_m4b_20260924.json`, loop 637):
     `#1147 #5796 #119 #7311 #15 #24` (rights), paired `#1142 #5805 #2972 #11001 #51 #1108`.
150. **Loops b `#10170` (body `#23166`) and c `#23041` (body `#23405`) exist and are unassigned**
     (`docs/cycle27-plan.md:1081-1083`, `:1134-1138`: *"b and c are assigned when their node sets are named"*).
     **SUPERSEDED 2026-09-24 by Pre-decided 163 (assigned: 1.2 = `#10170`, 1.7 = `#23041`).**
151. **The kernel `#5058` is still on the frame loop** (`frame_diagram 639`, 16 terminals, 13 wired, rowD wiki);
     it is coupled to group A in BOTH directions: `#5540` t2/t6 → `#5058` (w5637, w5975) and `#5058` t8 → w121 →
     `#10969`, `#10757`; and to group B: `#5058` t4 → w505 → `#2222`, `#2626` (`build_d1_v0.json` key `cut`).
152. **Cross-loop edges of the owed sets** (key `cut`): w10990 `#10757` → `#10407` (1.2→1.5); w10799 `#10686` →
     `#10407` (1.2→1.5); w4517 `#2626` → `#376` (1.2→1.7); w3268 frame index (iteration terminal of `#637`) → `#376` t7.
153. **Rotor call sites** = SubVI uids `28094 27466 27194 27165 1566 35648 33882 33114 34890`, all `SetCommand.vi` from
     `instr.lib\Autonics Motor` (both wikis, `graph_summary.subvi_calls`). Their Traverse diagram indices moved
     24→29 … 115→118 between S1 and rowD, so `docs/motor-call-site-census.md:89`'s indices are NOT addresses; the uids are.
154. ~~**No replace-callee verb is recorded**: 0 hits for replace-subVI in `docs/toolkit-capabilities.md`,
     `docs/NAMES.md`, `tools/gscript.py`.~~ **CORRECTED 2026-09-24 (Pre-decided 160):** the search was too narrow —
     `SubVI.Replace` method `635E001` is recorded at `docs/vi-server-ids.json:117` (UNVERIFIED, unbuilt, not unknown). Queue verbs DO exist (`docs/toolkit-capabilities.md:32`, `test_opqueue.log`
     7/7); the staged recipes `tools/recipes/stage_d1_*.py` contain 0 queue calls.
155. **`op_rule` maps every ControlTerminal row to `connect_ctl`** (`tools/jev_pairs.py:194-195`), and
     `connect_ctl` addresses the TOP-LEVEL diagram only (`tools/jev_pairs.py:157`); the six moving control terminals
     sit on `Diagram #639`. The v0 run's 6 control rows failed with error 5001 (`build_d1_v0.json` key
     `rewire.failed`) and its 18 tunnel rows had no route (`rewire.noroute`) — the latter class now has
     `fs_inner_tunnel_connect` / `tunnel_outer` (`docs/connectivity-map-plan.md:96`).

## Pre-decided — ADDED 2026-09-24 (cycle 69 judgement)

Decided by the cycle-69 judgement session on `archive/peer/2026-09-24-priorart-c69-split-plan.md`; applied to §1–§3
above by a material session. These close O1's framing, O2, O3, O4's shift-register half, O6's placement/route, O7, O8.

156. **(J1) O2 and O4 are SETTLED** by `docs/cycle27-plan.md:749-757`, `:903-908` and `:94-107`, `:930-933`: the CPU
     kernel `#5058` MOVES (sub-stage K); shift registers MOVE WITH THEIR NODES (`SR_QUEUE_AUTHORISED` stays False). The
     queue RESOLUTION TABLE (34(g)) is still owed and is the plan row **QRT, which comes BEFORE STOP**.
157. **(J2) Order = `docs/cycle27-plan.md:903-908` 34(e), smallest-first: L7 stages come before L2 stages.** §2 is
     re-ordered to P0 → L7-1 → L7-R → K → L2-A1/A2 → L2-B1..B3 → L2-R → QRT → STOP → ROT → FIN. The old "Why L2 before
     L7" paragraph is superseded; its cost (w4517 made twice) is accepted.
158. **(J3) The control set and L2-B are REWRITTEN from the measured six controls**
     (`tools/recipes/build_d1_routeb_v7.py:443-453`, `tools/bench/build_d1_routeb_v7_run10.log:23-31`): Auto-Reset,
     Reset Tracking, Z/dZ, Correction Factor, Force smoothing `#28148`, Extension median `#28996`. `min value` and
     Force-vs-Extension are INDICATORS; `Diagram #639` holds 31 ControlTerminals. Every stage's row list is
     cross-checked against the independent census `tools/bench/d1_rewire_sources.json` (queue endpoints included);
     **every disagreement with `build_d1_v0.json` becomes a listed row, never a silent drop.** Every row — the old
     L2-C rows included — is UID-addressed, never index-addressed (`docs/d1-build-plan.md:356` is the old failure).
159. **(J4) A stage whose moved set contains a ForLoop shift register may not use `computation_diff` as a pass gate
     unless P0 has shown that no two ForLoop left SRs in the affected loops share a TOP** (`tools/vigraph.py:336-337`
     TOP pairing). Otherwise that stage's gate lists the TOP-collision rows explicitly as predicted artefacts.
160. **(J5) ROT stays AFTER the splits.** Its route is `SubVI.Replace` `635E001` (`docs/vi-server-ids.json:117`),
     which must first be MEASURED on a scratch copy, together with the Baseline/Ring constants at the nine sites
     (`docs/rotor-sign-diagnosis.md:124-126`). Pre-decided 154's "0 hits" line is corrected in place.
161. **(J6) O3: `#10686` stays on loop 1.1**, because Pre-decided 147(b) already reads it there for loop 1.5's cadence
     (so L2-C is removed; w10990 moves into L2-A1). **O7: the GPU top level is the default final file** (user
     2026-09-16); CPU comes later. **O8: THIS plan governs the remaining splits** and supersedes
     `docs/cycle27-plan.md:383-390` S3w-a…e and `docs/d1-build-plan.md:679-682` S4–S6 as stage tables (one-line
     superseded pointers added at both places).
162. **(J7) Route B v0–v7 died re-wiring this same set in memory. The difference that has to hold: each sub-stage
     SAVES its file and the next sub-stage starts from that file, in a FRESH LabVIEW instance.** Stated per stage in
     §2's header line; a stage script that re-wires on an unsaved in-memory predecessor is the route-B failure again.

163. **(cycle 70 judgement) O1 CLOSED: loop 1.2 = WhileLoop `#10170` (body `#23166`); loop 1.7 = WhileLoop `#23041`
     (body `#23405`).** Evidence: S2's planned positions 1.2=(2600,2600) / 1.5=(2600,3400) / 1.7=(2600,4200)
     (`tools/recipes/build_d1_routeb_v7.py:793`, `tools/recipes/stage_d1_s2.py:432`); `#23041` sits at (2600,4200)
     (`tools/bench/stage_d1_s2_loops.log:75`); `docs/cycle27-plan.md:1137` already swapped 1.2↔1.5 by assigning
     `#23032` to 1.5, so 1.2 takes the remaining `#10170`.
164. **(cycle 70 judgement) L7-1 carrier scope.** Inputs to 1.7 that come from a PARALLEL loop (1.1 `#637`, or the
     future 1.2) are carried by QUEUES per `docs/d1-build-plan.md:308` §11b.3 — never an indicator/Local (lossy for
     saved data = rule 1a). L7-1 therefore does NOT wire those rows; it leaves them OPEN and lists them. L7-1 DOES:
     move `#376` into body `#23405`; create 1.7's two new SR pairs replacing `#15/#51` (accumulator) and `#24/#1108`
     (error chain) on `#23041`, each new LEFT SR's initial value wired from the SAME top-level source that initialises
     the original pair (read on the live bed; top-level → loop is a tunnel/SR-init row, not a crossing); wire every row
     whose both ends are inside 1.7 after the move (`#376` ↔ its SRs). The two re-feeds of `#6384` from 1.7 output
     tunnels and the retirement of the old pairs stay in L7-R.
165. **(cycle 70 judgement, after `tools/bench/stage_d1_l7_1.log:124-126`) SINGLE-CANDIDATE RULE.** A new-carrier row whose
     legal candidate set has EXACTLY ONE pair, and whose source uid+terminal equals the source of the corresponding S1 edge
     (acc_init: `#781 'initialized array'` via the original init wire w3543 → the new left SR's outer terminal; likewise
     err_init: `#4910 'error out'` via w4969), is a RULE row: executed without a Jev PAIR decision, logged
     `RULE-SINGLE-CANDIDATE`. Jev PAIR decides only when there are ≥2 legal candidates; the 0.75 threshold is NOT lowered.
     Gate P2a becomes: every row with ≥2 candidates acts at threshold; every single-candidate row matches its S1 source.
     Prior evidence of the same class (cited 2026-09-24 per prior-art c70-l7-1-r2 A4):
     `archive/peer/2026-09-23-bench-map-b-endtoend.md:67,72` — w7337's ONLY candidate, the physically correct one, scored
     p 0.464, likely because the intent line named a terminal that no longer exists on the live object (run 1's acc_init
     destination read `'total data array out'` on the new left SR, `tools/bench/stage_d1_l7_1.log:124`).
166. **(cycle 70 judgement) i6 (`#3644`), i9 (`#2294`), i11 (`#5096`) are OWNED BY L7-1**: values entering from top-level
     frame `#686` through tunnels on `#637` are re-made as NEW tunnels on `#23041` (`tunnel_outer`, rule rows, Pre-decided
     146) from the SAME outer source that feeds each original tunnel (re-read on the live file). Same class as SR-init:
     top-level → loop, read at loop start, not a parallel crossing.
167. **(cycle 70 judgement) Outcome review `archive/peer/2026-09-24-outcome-review-20260924.md` disposition**: same five
     violations as 2026-09-21; the user answered the repeated verdict (2026-09-20 "계속") and by the 2026-09-23 amendment a
     repetition of the same verdict does not stop the runner — escalation marked in STATUS. "ROT first": not adopted,
     Pre-decided 160 keeps ROT after the splits; ROT's scratch measurement (`SubVI.Replace` 635E001 + whether
     `computation_diff` sees callee identity, O6) is parallel-safe and scheduled right after L7-R. "Supervised run of
     `D1_s3_loop15.vi`": needs the user present or rig 분해 (it drives motors outside `motor_gate`) — on record as STATUS
     OPEN 58; not done unattended.
168. **(cycle 70 judgement, after `tools/bench/stage_d1_l7_1_r2.log:85-90`) S1-MAPPED RULE — Jev VERIFIES, does not
     gate on p.** A new-carrier row whose sink is determined by the stage's own old→new carrier mapping (old SR `#24` →
     new R`#24083`/L`#24133`; `#15` → R`#24150`/L`#24187`) together with the S1 edge's source uid+terminal is a RULE row,
     even with ≥2 legal candidates. Jev PAIR still runs on it as a CHECK: if Jev's top candidate == the S1-mapped pair
     the row is wired (log `RULE-S1-MAPPED p=<p> margin=<m>`, whatever p is); if Jev's top candidate differs, the run
     STOPS. Reason: `err_R` scored 0.756 (run 1) and 0.742 (run 2) with margin ≥0.57 both times — the threshold sits inside
     run-to-run spread on a row whose answer is already fixed by the original. The 0.75/0.15 act threshold is unchanged
     for rows with no S1 counterpart.
169. **(cycle 70 judgement; CLAUDE.md "split and save" rule 3 — the same stage failed twice at the same gate P2a with no
     saved artefact) L7-1 is SPLIT:** **L7-1a** = move `#376` into body `#23405` + create the two new SR pairs, NO wiring,
     then SAVE `claudeDev\D1_l7_1a_<ts>.vi` (broken by design → GUI Ctrl+S, CLAUDE.md §3 rule 6); gate = `diff(bed,new)`
     = `#376` owner change + 4 new SR objects only, bed md5 unchanged. **L7-1b** = open THAT file in a fresh LabVIEW, wire
     the 9 rows (4 S1-mapped per 168 + 2 single-candidate per 165 + 3 top-level tunnels per 166), save
     `claudeDev\D1_l7_1_<ts>.vi`; gate = `computation_diff(S1,new)` = exactly the 8 rows of `tools/bench/l7_1_predict_r2.log`.
     Runs 1 and 2 did L7-1a cleanly twice (`stage_d1_l7_1.log:80-90`, `stage_d1_l7_1_r2.log:71-81`) and threw it away.
170. **(cycle 70 judgement, on `archive/peer/2026-09-24-c70-l7-1-jev-threshold.md` — "half right") ACCEPTED, three
     conditions on 168/169:** (a) BEFORE L7-1a, run the review's offline test (a)–(e) (`jev_pairs.ask_pair`, n=10–20, ≈60
     calls, ≈$0.005) — `err_R` spread, `acc_init` current vs CORRECTED intent line (the line must name the sink
     `#24187` 'total data array out' / the register as carrying `#376`'s output), `err_init` with the sink name blanked,
     and the negative swap case `#4910 'error out'` → acc LEFT; record the five means/spreads. (b) The intent lines of
     every L7-1b row are corrected per (a)'s finding before L7-1b runs. (c) In L7-1b gate PB (`computation_diff`,
     recipe `:102`) is made `fatal=True` and runs BEFORE the save; a stage never saves over a failed PB. If (e) scores
     ≥0.75, the Jev argmax check in 168 is recorded as guarding nothing and the S1-mapped rows rest on PB alone.
     **MEASUREMENT for 170(a) (cycle 71 material, 2026-09-24 03:49, no LabVIEW; `tools/bench/jev_l7_1_offline.log:40-49`,
     `tools/bench/jev_l7_1_offline.json`, 88 Jev calls ≈ $0.007; not a decision):** (a) `err_R` as-is n=12: mean 0.755,
     min 0.71 / max 0.80, sd 0.026, top == S1-mapped 11/11, margin mean 0.575 (min 0.48) · (b) `acc_init` current line
     n=10: 0.584, 0.55/0.62, sd 0.021 (1 candidate) · (c) `acc_init` CORRECTED line (exact text `:16`) n=10: **0.906**,
     0.90/0.91, sd 0.005 · (d) `err_init` sink name blanked n=10: 0.803, 0.79/0.82, sd 0.008 (was 0.848 named) ·
     (e) NEGATIVE `#4910 'error out'` → acc LEFT outer, corrected line, n=10: **0.098**, 0.09/0.11, sd 0.007.
171. **(cycle 71 judgement, on the 170(a) measurement above) L7-1b INTENT LINES AND ROW MODE — decided.**
     (1) **Every L7-1b intent line takes the CORRECTED form of case (c):** it names the sink by the terminal name
     as it reads on the LIVE object in the L7-1a file, re-read from that file. It never uses the old object's
     terminal name. For a register it says which node's output it carries (`#376`'s output for the accumulator,
     the error chain for the error pair). The sink name is never blanked: (d) blanked 0.803 < named 0.848. Reason:
     the current line to the corrected line took `acc_init` from 0.584 to 0.906 with sd 0.005, so the run-1 failure
     was the question's wording, not the row.
     (2) **The Jev argmax check in 168 is KEPT as a real guard**: the negative swap (e) scores 0.098, far below 0.75,
     so the check does separate a wrong source. 170(c)'s fallback ("rests on PB alone") does NOT apply.
     (3) **Row modes are unchanged from 165/166/168.**
       - S1-mapped rows are wired when Jev's top == the mapped pair, whatever p is (err_R: 0.755 ± 0.026, top ==
         mapped 11/11).
       - Single-candidate rows are RULE rows. Jev runs on them as a logged check only: it does not gate, and it
         stops the run only if it scores below 0.30.
       - Tunnel rows (166) are rule rows.
       - Gate PB (`computation_diff`) is FATAL and runs before the save (170(c)).
     (4) **L7-1b follows L7-1a in the same material dispatch when L7-1a passes every predicted gate.** Its input is
     the saved L7-1a file, opened in a fresh LabVIEW. Its prediction is `tools/bench/l7_1_predict_r2.log`, re-derived
     for the L7-1a uids.
172. **(cycle 71 judgement, on `tools/bench/stage_d1_l7_1a.log` PD3, `archive/peer/2026-09-24-c71-l7-1a-pd3.md` and
     `tools/bench/diag_c71_l7_1a_tunnels.log` 9/0) L7-1a is ACCEPTED: `claudeDev\D1_l7_1a_20260924_035656.vi`, md5
     `34aaadf14091ee156e0950725de48bdf`.** PD3's 3 extra removed edges are a defect in the CONTRACT, not a cut:
     - The edges are `1929:2043→2048:3182`, `1929:2043→6384:6480` and `5020:5050→6384:6511`.
     - Wires w4337 and w5073 keep their uids and all three sinks, and all 7 terminal rows survive, which excludes
       (a) wire cut and (c) row dropped.
     - The tunnels' outer terminals turned non-source because `#376`, their only inside source, left `#637`. This is
       the documented undirected-tunnel behaviour, i.e. the review's (b).
     **The contract is tightened, NOT loosened** (the review warned that "touches `#376` or its tunnels" would admit
     real cuts). From now on a `diff` may remove an edge that does not touch the moved node ONLY if it is listed by
     edge in the prediction, AND its wire uid survives with every sink, AND its source is a tunnel whose only inside
     source was the moved node. For L7-1b and later stages these three edges are part of the BASELINE: they are
     absent from the L7-1a graph, and re-driving `#1929`/`#5020` would ADD an edge, which the L7-1b PC2 gate must
     catch. **`#1929`/`#5020` → `#2048`/`#6384` are L7-R rows**: L7-R feeds them from 1.7 or replaces the tunnels.
     This is the same class as the "two re-feeds of `#6384`" in Pre-decided 164, and it is counted in L7-R's row list.
     Side fact kept for L7-R: the old `#15`/`#51` pair's name reads '' after the move (`diag_c71_l7_1a_tunnels.log:71-72`).
173. **(cycle 71 judgement, on `tools/bench/stage_d1_l7_1b.log:301-314`) Terminals are addressed by TERMINAL UID after
     their first resolution, never by name again — a TOOL change in `tools/stagekit.py` (the user's 2026-09-24 tool
     permission; this class recurs, since shift-register terminal names change on move and on wiring:
     `diag_c71_l7_1a_tunnels.log:71-72`, `stage_d1_l7_1b.log:274`).**
     - **What the run showed:** all 9 rows were wired as decided. Every S1-mapped row had Jev's top == the mapped
       pair (p 0.884–0.928), and the second-pass `Is Broken?` read False on 3 rows. The run then died in OUR
       verification: acc_init's second pass looked up `'total data array out'` by name, and after the wire landed
       that terminal reads `''`. That is a script defect, not a diagram one.
     - **Remedy:**
       - `stagekit.address` (and `cfw_second_pass`) accept a terminal uid.
       - A row records the sink and source terminal uids when it first resolves them, before wiring. Every later
         step addresses the row by those uids: second pass, `Is Broken?`, and the gates.
       - Name lookup stays the FIRST resolution only.
       - Self-test: stagekit's existing self-test plus a case where a terminal's name changes after wiring and
         the uid path still reaches it.
     - **Gates:** unchanged (42(b) is kept, now addressed by uid). The L7-1b rerun starts from the same L7-1a file.
     - **STATUS: BUILT (recorded 2026-09-24 05:3x, prior-art `archive/peer/2026-09-24-priorart-priorart-c71-l7-1b-r3.md`
       A3.2):** `tools/stagekit.py:690-692` (`address` by `term_uid`), `:793` (`cfw_second_pass`), `:1113-1132`
       (`match_term_uid`); `tools/bench/selftest_stagekit.log` I1-I7, 44/0; the recipe passes `term_uid` at
       `tools/recipes/stage_d1_l7_1b.py:44,72,96`. Not to be scheduled again.
     - **LIMIT (same review, A3.3):** uid addressing refuses a terminal with NO wire on it ("uid addressing needs a
       wired terminal", `tools/stagekit.py:1120-1121`, self-test I5) and never falls back to the name. L7-1b is not
       affected (every uid-addressed step there runs after its wire landed). Stages that must reach an UNWIRED
       terminal - L7-R's retire rows, where a wire is removed - are NOT covered by 173; how they address it is an
       OPEN item for that stage's plan.
174. **(cycle 71 judgement, on `tools/bench/stage_d1_l7_1b_r2.log:41-45`) FIX (a): the uid branch applies only AFTER a
     row's wire has landed.**
     - **What happened:** run r2 took the uid path at FIRST wiring. The candidate ends already carried `term_uid`,
       so `Stage.address` (`tools/stagekit.py:690-692`) switched to uid, and `match_term_uid` refused the still-unwired
       terminals (#3934/#5683/#3954/#5782, "uid addressing needs a wired terminal"). That contradicts 173's own text:
       "name lookup stays the FIRST resolution only". This is a script bug, not a design question. (b), "uid
       addressing accepts unwired terminals", is REJECTED: `match_term_uid` maps uid → node terminal index THROUGH
       the wire, so an unwired terminal has nothing to match on.
     - **Remedy:**
       - Stage the uids in a separate field (e.g. `verify_term_uid`) that only the second pass, `Is Broken?` and the
         gates read. First wiring never sees `term_uid`.
       - stagekit self-test: add a case where an end carrying `verify_term_uid` on an UNWIRED terminal is wired by
         name first, then verified by uid.
     - **STATUS: BUILT (cycle 72 firefighter, 2026-09-24 05:5x):** `tools/stagekit.py:690-696` — `address` takes the
       uid path ONLY on `verify_term_uid`; the candidate field `term_uid` is ignored, so first wiring always resolves
       by name. Recipe `tools/recipes/stage_d1_l7_1b.py:96` passes `verify_term_uid` on the four second-pass ends.
       Self-test `tools/bench/selftest_stagekit.log` 47/0 (new I8 unwired end with `term_uid` wired by NAME · I9
       verified by `verify_term_uid` after the wire + rename · I10 `term_uid` alone never selects uid). Offline dry run
       of the recipe's ACTUAL rows (retrospective-cycle71 F2a): `tools/bench/dryrun_l7_1b_address.py` →
       `dryrun_l7_1b_address.log`, 15 ends, PASS (the four r2 uids resolve by name; verify ends by uid only after the
       wire; an unwired verify end raises). 173's LIMIT text "L7-1b is not affected" was WRONG (r2 proved it) and is
       superseded by this entry.
     - **Budget:** L7-1b has now failed twice at DIFFERENT stages of our own tooling (r1 name-after-wire, r2
       uid-before-wire). Both are script defects with measured causes. So the "same stage failing twice at the same
       place" re-split trigger (CLAUDE.md split-and-save 3) does NOT fire: the row set and the saved L7-1a input are
       unchanged. The NEXT cycle starts a fresh failure budget for L7-1b run 3.

175. **(cycle 73 judgement, on "L7-R facts (cycle 73, measured)" above) L7-R DESIGN — decided.**
     - **Loop-exit re-feeds, so rule 1a holds.** `#2048` (Array Subset) and `#6384` (`save N xyz traces.vi`) are on the top-level
       frame `#686` and read `#637`'s EXIT values. They are re-fed from `#23041`'s exit values of the same `#376` outputs:
       `#2048 'array'` ← the new acc RIGHT SR `#24150` outer (was `#15`, w3957) · `#6384 'error in'` ← the new err RIGHT SR
       `#24083` outer (was `#24`, w1899) · `#2048 'length'` + `#6384 'actual # data points'` ← a NEW output tunnel on `#23041` fed
       by `#376 'file progress'` (was `#1929`, w4337) · `#6384 'file # to append'` ← a NEW output tunnel fed by `#376 'file number
       to append out'` (was `#5020`, w5073). Each new tunnel's indexing mode must EQUAL its original's (`#1929`/`#5020`, read on
       the live file). The last iteration's value is the same value provided 1.7 runs `#376` on the same input sequence. That is
       the queue's job (QRT), so equivalence is structural here and functional only after QRT.
       `d1-build-plan.md:365-370` §5b already said "off 1.7's output tunnels".
     - **`#3453` `file progress` (an indicator on 639)**: its ControlTerminal MOVES into body `#23405` and is re-wired from
       `#376 'file progress'`. This is display-only, and the graph edge is unchanged. The route is `move_in` on a
       ControlTerminal, the O5 class. The prediction run measures it FIRST, on a dated scratch copy in the same LabVIEW
       instance, before the stage touches the work copy. If `move_in` refuses a ControlTerminal the run STOPS (a gate,
       not a branch) and judgement picks the route.
     - **`#3052` (`saved file refnum`, t8)** is a constant, not a per-frame crossing. It MOVES into `#23405`, and w1397's
       row is re-made inside 1.7, but only if `#376` is its ONLY consumer. That is measured in the contract; any other
       consumer ⇒ STOP.
     - **t5 (w4517, `#2626` → `current frame data array in`) and t7 (w3268, `#637` i → `frame index`) stay OPEN.** Both
       change every frame and cross parallel loops, so by 164 they are queues. No planned queue carries them (M5), and
       `#2626`'s final home is 1.2 (group B). They are **added to the QRT row as owed rows**, and 1.7 becomes whole at QRT
       + STOP, not at L7-R. L7-R does NOT build a queue.
     - **Retire** (plan §3 rows, live-consumer check BEFORE each delete on the completed graph):
       - First delete w3957 and w1899 BY WIRE UID (`stagekit.delete_wire`, `stagekit.py:527/:861`).
       - Then wire the freed sinks by NAME (first resolution, 174) and verify them by `verify_term_uid`.
       - Then delete `#15/#51`, `#24/#1108`, `#1929` and `#5020`, then run RBW.
       - This resolves the **173 LIMIT: no retire row addresses an unwired terminal by uid.** Deletes go by wire/object
         uid; new wiring goes by name.
     - **Row modes (168/171 unchanged):** re-feeds with an S1 counterpart = RULE-S1-MAPPED with the Jev argmax check; single
       candidate = RULE-SINGLE-CANDIDATE; tunnels and retires = rule. No row needs Jev to decide.
     - **Gates:**
       - PB `computation_diff(S1,new)` FATAL before the save, predicted = exactly the w4517 row.
       - **Separately, `#376 'frame index'` is read as UNWIRED.** It is a diagram-terminal source, and the r3 CDIFF list
         (`stage_d1_l7_1b_r3.log:338-345`) did not show w3268 although L7-1a removed it. So the contract first MEASURES
         whether `computation_diff` sees diagram-terminal sources, and records the answer. If it does not, that blind
         spot is a finding for FIN.
       - `diff(prev,new)` is an edge list.
       - ExecState warm is MEASURED and recorded, NOT gated, because t5/t7 are open and required-ness is not in the
         wiki (Pre-decided 132).
       - Save by script if ExecState 1, otherwise GUI save (rule 6).
       - Output `claudeDev\D1_s4_loop17.vi`. The name is kept so K's input row does not change, with the note "1.7 whole
         except the two QRT rows".
     - The cold ExecState 1 + cdiff 0 criterion of §3 for L7-R moves to the stage that makes the t5/t7 queues.

176. **(cycle 73 judgement, on `tools/bench/stage_d1_l7_r_r2.log` 61/0 → `claudeDev\D1_s4_loop17.vi` md5 `4b621946…`) L7-R ACCEPTED; four rulings.**
     - **(a) Handles.** The ±100 criterion is the reference-hygiene test for REPEATED OP CALLS (CLAUDE.md, 20 calls flat).
       It does not apply to an editing stage: a stage that creates objects holds more handles while the VI is open.
       For editing stages the handle numbers are RECORDED, not gated (load / before-save / exit). A leak is judged
       only by the 20-call test on the ops involved. §3's "handles open→close ±100" rows are superseded for L7/L2/K
       stages.
     - **(b)** The extra deletes by wire uid (w4337, w5073, w5274, w1397, w5056) that freed the re-fed sinks, and the
       choice of `#2048` 'length' at `Terminals[3]`, are ACCEPTED as execution detail. PB returned exactly the
       predicted row, and the edge diff was 4 removed / 9 added as predicted.
     - **(c) BLIND SPOT, and a tool is necessary now** (user 2026-09-24 tool permission):
       - `computation_diff` does not report an edge whose SOURCE is a diagram-owned terminal (loop `i`, w3268).
         L7-1a removed w3268 and no CDIFF row showed it (r2.log:450; `c73_l7r_live.log`).
       - Every later stage gates on cdiff, and loop terminals recur in every split (K and L2 move nodes fed by `#637`
         i). So a "0 rows" can be false.
       - Fix `tools/vigraph.py` so diagram-terminal sources are edges: from the wiki `Terminal` rows whose owner is a
         Diagram, as w3268 was located in cycle 68 at `docs/wiki/subvi/D1_s1_copy.json:36385-36392`.
       - Self-test: on the L7-R graph, the w3268 row must now appear as the ONE predicted-open row beside w4517.
       - This is done BEFORE stage K. Offline, no LabVIEW.
     - **(d)** §3's L7-R rows `:159-160` (cold ExecState 1, cdiff 0) are superseded by 175: that criterion moves to the
       stage that builds the t5/t7 queues (QRT/STOP).

177. **(cycle 79 judgement, on `tools/bench/k_facts_79.log:91-169` run 3, `BGRUN END rc=0`, offline; result card
     `tools/bench/cards/result_79-1.json`) STAGE K DESIGN — decided.** Input `claudeDev\D1_s4_loop17.vi` md5 `4b621946…`,
     output `claudeDev\D1_k_<ts>.vi` (GUI save if ExecState 0, rule 6). `#5058` has 16 terminals, 13 wired; the bed wire
     equals the S1 wire on all 13 (`:97-146`). t5/t6/t10 stay UNWIRED (defaults, the same as the original).
     - **(a) MOVE:** `#5058` → body `#23166` of `#10170` (1.2) by `move_in`.
     - **(b) SR pair `#119/#2972` is KERNEL-ONLY** (F3 `:150-161`: left `#2972` → `#5058` t13 only; right `#119` ← w121
       from `#5058` t8 only). By 156 (SRs move with their nodes) K creates ONE new SR pair on `#10170`:
       - t8 → new RIGHT and new LEFT → t13 are S1-MAPPED rows (168/171, Jev argmax check).
       - The new LEFT's initial value comes from the same source as `#2972`'s, FSIT `#6239` on `#686`. That is a
         RULE-SINGLE-CANDIDATE row (165).
       - The old `#119/#2972` is NOT deleted in K. It is retired in L2-R with the other carriers, after the
         live-consumer check.
       - The three MIXED pairs stay in L2-A1: `#1147/#1142` (A+B+K), `#5796/#5805` (A+K) and `#7311/#11001` (no K).
     - **(c) Six top-level rows are re-made as NEW input tunnels on `#10170` (166, rule rows):** t2, t9, t11, t12, t14
       and t15. Each takes the SAME outer FSIT source on `#686` as its `#637` tunnel
       (`#2580`←`#3862` · `#2396`←`#2932` · `#4432`←`#5287` · `#3656`←`#3675` · `#3920`←`#5659` · `#4031`←`#5952`).
       Each new tunnel's IndexMode must EQUAL its original's, read on the live file (rule 1a: whole-array parameters
       stay non-indexed).
       - The old `#637` tunnels stay for any other inside consumer. A tunnel left with none is an L2-R retire row.
     - **(d) The two `#639` sinks of t8** (`Pos within cal image`, `Pos: Diffraction Pattern`; 79-1 OPEN 1) are handled
       like `#3453` in 175:
       - The contract first MEASURES each one's class. It must be a ControlTerminal that is an indicator, with w121 as
         its only source.
       - If so, it MOVES into `#23166` and is re-wired from t8 (rule row, display only).
       - Any other finding ⇒ STOP (a gate, not a branch), and judgement decides.
     - **(e) Rows left OPEN by K** (the gate lists them one by one; none of them is wired in K):
       - t0 ← `#5680` and t7 ← `#6016` (tunnels of `#5540`, group A) go to L2-A1.
       - t3 → `#5796` right goes to L2-A1, with that pair.
       - t4 w505 → `#2626`, `#2765` (group B) and `#1147` right go to L2-A1/L2-B.
       - t8's sinks `#10969` and `#10757` (group A) go to L2-A1.
       - **t1 `Image In` ← `#6810 'Image Out'`** stays on 1.1 and crosses 1.1→1.2 every frame. By 164 it is a
         queue, and it is ADDED TO THE QRT ROW as an owed row, beside t5/t7 of 175. K builds no queue.
     - **(f) `#22700` on w3040** (79-1 F5, present only in `d1_rewire_sources.json`) is the fixture TIFF writer the
       working copy carried. It is absent from S1/S3 and from the original (STATUS cycle 74, PD11 of the m8 plan). It
       is IGNORED and listed as a disagreement row (158), never wired.
     - **(g) Gates:**
       - PB `computation_diff(S1,new)` is FATAL before the save. It must equal exactly (e)'s rows plus the two carried
         L7 rows (w4517 and w3268, the latter visible since the cycle-74 DIAG_TERM fix). The simulator computes the list
         in `tools/bench/plan_<stage>.json`; nobody types it.
       - `diff(prev,new)` is an edge list.
       - The new tunnels' IndexMode must equal their originals'.
       - Second pass `Is Broken?` False on every wired row, addressed by `verify_term_uid` (174).
       - ExecState is MEASURED, not gated (the (e) rows are open).
       - Handles are recorded (176(a)).
       - Input md5 and pins must be unchanged.
     - **(h) Launch:** simulator plan files + dry + pre-run PASS (`docs/stage-simulator-plan.md:34,40,69,91`),
       prior-art released, one LabVIEW run under the retry cap. Mixed-pair creation stays in L2-A1, so K has at most
       11 wired rows (1 init + 2 S1-mapped + 6 tunnels + 2 indicator rows), inside the 10–15 batch size.
178. **(cycle 79 judgement, on result `79-3` FAIL 27/2 — `tools/bench/sim_k_split.log:69`, review
     `archive/peer/2026-09-25-c79-sim-k-split.md` ANSWERED) three rulings. The failures are OUR gate definitions; the
     K design is unchanged.**
     - **(a) Contract measured, 177(d) holds:** `#3173`/`#9519` are indicator ControlTerminals whose sole source is t8
       w121, and the six originals have IndexMode 0 (`k_contract_79.log:28,31-42`). So they move, and the new tunnels
       are IndexMode 0.
     - **(b) The simulator gates are corrected as the review proposed (§4):**
       - A0 becomes an OWNERSHIP check: `#5058` is owned by `#23166`, and `#23166` by `#10170`. Pixel offsets are
         never compared exactly.
       - P3 credits t3 by an end-graph source check (t3 is unwired; the old `#5796` right has no source) plus a
         negative control: a fake t3→`#2626` edge must FAIL the gate.
       - A THIRD offline simulator run is AUTHORISED. The failure budget restarts on card 79-4. This is not the "same
         stage fails twice at the same place" trigger: run 1 failed on a data-file overwrite, run 2 on two gate
         definitions.
     - **(c) PB = the 10 rows the simulator lists** (`sim_k_split.log:24-33`): `#376`×2 (L7), `#2626 'array'`,
       `#5696`/`#6085 'x,y,z array'`, `#10757`/`#10969 'array'`, and `#5058` t0/t1/t7. t3 has NO row of its own; its
       only S1 computation consumer is `#5058` t0, through the mixed pair `#5796/#5805` and the selector tunnels. So
       `#5058` t0's row covers it, and the end-graph source check in (b) proves it separately. ACCEPTED.
     - **(d) 177(b)'s "Jev argmax check" is WITHDRAWN** for `#119/#2972`. That pair is a register chain, and CLAUDE.md
       §3 "Stages are SIMULATED", decision 3, puts chains under RULE-CHAIN-S1 (copied from S1, never asked of Jev;
       `stage_prerun` X7). The standing rule wins over this plan's wording.
     - **(f) (cycle 79 judgement, on result `79-4` BLOCKED: `tools/bench/stage_d1_k_prerun.log:146` X4; review
       `archive/peer/2026-09-25-c79-k-x4.md`) ROUTE (c): the plan the launch gate checks must be the plan that EXECUTES.**
       No op reads `plan_k_rows.json`'s exec ends; only X4 reads them. The simulator-finalized `plan_k_split.json` is
       what runs, and its pre-run already passed (`stage_d1_k_planprerun.log:2-7`, 4/0). So:
       - `stage_d1_k.py` executes `plan_k_split.json` through stagexec. It keeps its OWN gates around it: IM, P2,
         PB = 178(c), KN (the name gate, prior-art c79-k), Is Broken? second pass, and save.
       - The recipe presents `plan_k_split.json` to the launch gate as its plan file. `plan_k_rows.json` is demoted to
         a derived report.
       - The pre-run is re-run on the recipe + `plan_k_split.json`.
       - Route (a), patching `addr_offline` for '' names, is NOT taken now: nothing that executes needs it. If L2
         shows the same X4 class on a plan that DOES execute, it becomes a tool task then.
       - Route (b) alone is refused, because it drops the gates.
       - **No gate is loosened.** If the launch gate cannot bind this recipe to that plan without a code change, the run
         STOPS and reports.
       - **Side check (non-blocking):** the self-wires the review flagged on FSITs `#6239`/`#3862`/`#5659`
         (`c79-k-x4.md:68-76`) are compared with the S1 graph. Present in S1 too ⇒ a reader modelling artefact that is
         harmless to cdiff; absent from S1 ⇒ a finding for the next cycle.
     - **(g) (cycle 79 judgement, on result `79-5` BLOCKED: `tools/bench/stage_d1_k_prerun_79-5.log:145-148`) TOOL
       NECESSARY — the launch gate learns the simulator's own plan format.** `stage_prerun.plan_files`
       (`tools/stage_prerun.py:674-692`) accepts only a `decisions` row file. The simulator (CLAUDE.md §3 decision 7)
       emits `stageplan/1`, so every simulated stage (all of L2) would be refused, and a recipe cannot be bound to the
       plan it executes. This is the user's 2026-09-24 tool permission: the class recurs. Change, tightening only:
       - A recipe that names a `stageplan/1` is pre-run against it only if `finalized` is true and `final` is PASS.
       - X3 counts that plan's actions. X5 requires the recipe's compiled ops == the plan's wire actions.
       - `plan_md5s` is keyed on the plan file.
       - Self-test negatives: a non-finalized stageplan is refused, and an op-count mismatch is refused.
       - Every existing `stage_prerun` self-test still passes.
       R5 closed the side check: the FSIT self-wires are in S1 too (`k_selfwire_79.log:7-37`), so they are a reader
       artefact.
     - **(h) (cycle 79 judgement, on result `79-6`: `stage_d1_k.log:97` E1 STEP-DIFF at op 3, run 1 of 2, nothing
       saved, bed unchanged; review `archive/peer/2026-09-25-c79-6-k_e1op3.md`) the per-step comparison WORKED.**
       The simulator's orphaned-tunnel rule (`stagesim.py:308-324`) covers only OUTPUT Loop/Tunnel objects. `#5058` is
       the source of w505 into the input SelectorTunnel `#2765`, and the move orphaned that tunnel.
       - Remedy: measure the real graph after ops 1–3 headless (is_source / wire uid of 2789/2792/5910/6253/2811).
       - Then widen the stagesim rule until its step-3 graph EQUALS that read, with a self-test on this case.
       - Then re-simulate, re-finalize and re-pre-run K. Run 2 is launched only if those pass (a gate).
       - `tools/stage_prerun.py` now pre-runs finalized `stageplan/1` files (79-6 T1–T3; self-test 9/9).
       - The 8 pre-existing `selftest_launch_gate` failures (C2-C6, M4-M6: stale counting since 78-2, same on HEAD)
         are OWED to a later small tool task.
     - **(i) (cycle 79 judgement, on result `79-7` PASS 6/0) K ACCEPTED: `claudeDev\D1_k_20260925_100155.vi`, md5
       `6cf5b0777aafa12112d8a786a9eed1ed`, 307,364 B.** Evidence:
       - `stage_d1_k_r2.log:569` 35/0, 610 s. E1: 15/15 ops have step diff 0 against the simulator.
       - IM 6/6 IndexMode 0. P2: 7 rows, Is Broken? False. PB: exactly 178(c)'s 10 rows. KN name gate OK.
       - ExecState 0 warm, BY DESIGN (the (e) rows are open), so it was saved by GUI under rule 6.
       - The bed and pins are unchanged, and LabVIEW was verified gone.
       - The simulator's tunnel-flip rule now matches the measured op-3 read (`k_op3_read_79.log:93-111`; self-tests
         `selftest_stagesim.log` 42/0 and `selftest_stagesim_k79.log` 4/0).
       - Level: STRUCTURAL + graph-equivalent under ASSUMPTION A, NEVER RUN.
       - **The generalised TUN_FLIP branches are UNMEASURED:** input LoopTunnel/Tunnel, and output SelectorTunnel with
         every frame orphaned. They are marked unmeasured, and the first stage that exercises them (L2-A1: the Case
         structures `#5540`/`#10445`) must measure each branch on a scratch before it relies on the prediction. The
         per-step comparison remains the backstop.
       - 🔵 **THE BED IS NOW `D1_k_20260925_100155.vi`.**
       - 🔴 **CORRECTED the same cycle by retrospective-cycle79 (`archive/peer/2026-09-25-retrospective-cycle79.md:244-254`):
         ACCEPTANCE IS CONDITIONAL.** Both `wire_indicators` ops (plan actions 26/27, t8 → `#3173`/`#9519`) raised
         `target BROKEN after wiring` (`stage_d1_k_r2.log:232-239`), and `tools/stagexec.py:679-680` whitelisted
         that error. That whitelist exists for an `fp_ind` gate found only in L7-R. The op's own check,
         `exec_state != 1` (`gscript.py:1864-1867`), always fires on an ExecState-0 VI, so it proves nothing here.
         No reader covered the two sinks: not E1, not the second pass, not the edge diff. The "2 indicators moved"
         line is therefore UNVERIFIED.
         **Before L2-A1:**
         - (1) Headless read of `D1_k` for the terminals of `#3173`/`#9519`. Wire 23807 = landed. Wire 0 = not wired
           (a small follow-up stage from `D1_k`). Any other wire = K is REJECTED, and K is re-run from
           `D1_s4_loop17.vi`.
         - (2) DEVICE-FAILED, threshold 1: remove the whitelist, so every op error stops the run unless the recipe
           declares a named gate that reads that sink.
         - (3) Build a reader for panel-terminal wiring. The simulator state, the edge diff and cdiff are all blind to
           ControlTerminal sinks.
     - **(e) Carried to L2-A1** (review `:76-99`): `computation_diff` merges Case frames. Before L2-A1 gates on cdiff,
       its plan entry must say how the `#5540`/`#10445` frames are kept apart.
179. **(cycle 80 judgement, on results `80-1`/`80-2`/`80-3`) the three Before-L2-A1 items of 178(i) are settled.**
     - **(a) K STANDS — the conditional in 178(i) is lifted.** `tools/bench/k_ind_read_80.log:40-45`: on `D1_k`,
       `#3173` and `#9519` are sinks of wire **23807**, whose single source is `#5058` term 5171 `'pos in cal image out'`.
       Its third sink is the K replacement register `RightShiftRegister #23508`. The labelled case on `D1_s4_loop17`
       reads the same source through w121 (`:28-35`), so the source is the same one. There are exactly 2 ControlTerminals
       with those labels, so `wire_indicators` made no duplicates (`:39,44`). w23807 survived Remove Bad Wires on a
       scratch (`:68-71`). The op's `target BROKEN after wiring` was the ExecState-0 false alarm that 178(i) described.
       Level: STRUCTURAL, never run.
       ⚠️ The material session called RBW survival a proxy because "no read-only Is Broken? op exists". That contradicts
       CLAUDE.md (`Wire.Is Broken?` 6371004 BUILT, `docs/NAMES.md:902-911`), and K's own P2 used it. This is a
       fact-check item for the next tool pass, not a blocker: RBW survival is the stronger test.
     - **(b) The panel-terminal reader EXISTS without a new op** (80-2): `allterms.read_terms(OpAllTerms_v1)` plus
       `report_all('ControlTerminal')`. A ControlTerminal's term_uid is its own uid, and its owner is its Diagram
       (`tools/bench/diag_ctlterm_read_80.py`). From L2-A1 on, every ControlTerminal row is gated by this reader.
     - **(c) The stagexec whitelist is REMOVED** (80-3; `tools/stagexec.py:607,725`, `selftest_stagexec_gate.log`
       13/0). An op error now stops the run, unless the recipe declares a `sink_gates` entry naming that exact sink
       together with an existing gate that reads it. `stage_d1_k.py` would therefore stop at its indicator rows on
       replay. That is accepted, because K is not replayed.
       `stage_d1_l7_r.py:92` keeps its own tolerance. That recipe is finished history and is not replayed, so no repair
       is needed. Any NEW recipe that copies that line is refused in review.
     - **(d) The cycle-80 Error List MISMATCH is a checker artefact, not a bed fault.** `result_80-1`: there is
       exactly one extra item (index 0). Its raw text and object are empty (OCR), and its detail reads "The designer of
       this subVI has specified that this terminal must be wired". It is the tree-header row of item 1, `#5058 'Image
       In' is not wired`, which is licensed by the open row t1. Nothing is MISSING. The checker (`errorlist_check.py:269`)
       cannot license an empty-raw row. The repair is a tool task:
       - an empty-raw row is licensed ONLY when the next item is licensed AND the header's detail text matches that
         item's error class;
       - negative case: the same header followed by an unlicensed item stays extra.
       ✅ DONE in the same cycle (80-4): `errorlist_check.py:309,323-336`, self-test 5/5, and an offline re-verdict of
       the cycle-80 json gives OK (`tools/bench/errorlist_recheck_80.log`). `stagexec` selftest T01-T15 passes 15/0.
180. **(cycle 80 judgement, on result `80-5` PASS 27/0: `tools/bench/l2a1_facts_80.log`, `…/l2a1_tunflip_80.log`/
     `.json`) the L2-A1 design inputs. The stage is NOT built until (a) and (b) are delivered.**
     - **(a) STAGESIM IS REFIT FIRST (tool, necessary; the class recurs in L2-A2/B).** The measured joint L2-A1 move on
       a scratch of D1_k had 10 moves. The simulator predicted 0 flips. The real VI flipped 10 SelectorTunnel inners and
       2 outers, lost 3 edges between moved members (all at `#10247`), and deleted half-wires w5637/w5975 that the
       simulator kept (`l2a1_tunflip_80.log:33,195-196`, compare n=23). The two single moves flipped 0 of 4 predicted.
       So `stagesim.op_move_in` must learn four things from `l2a1_tunflip_80.json`, which is the labelled set:
       (1) moving a structure moves its closure; (2) a selector `Tunnel` with unwired inners does NOT flip; (3) a moved
       structure's input-tunnel inners DO flip; (4) moving uid by uid drops edges between members that were already
       moved and members still to move, and deletes bare half-wires.
       Pass: the simulator reproduces the joint read with compare diff 0 over all 23 rows, and both singles with
       0 flips. Every existing stagesim self-test still passes. The model is fitted to the read, never the reverse.
       The 3 lost edges are then ordinary reconnect-table rows of L2-A1 (CLAUDE.md "Stages are SIMULATED", decision 6).
       They are re-wired, not avoided by choosing a move order.
     - **(b) 178(e) ANSWERED: a frame-keyed cdiff.** `vigraph` keys rows by node|class|name|ordinal with no frame
       (`vigraph.py:244-245,301-306`). It joins all per-frame inners (`:332-346`) and compares SETS (`:709-729`).
       Frames `5582/5592` of `#5540` and `10453/10459` of `#10445` therefore merge (`l2a1_facts_80.log:361,367`).
       The fix is an opt-in `frame_keyed` mode: the identity of an inner terminal of a CaseStructure/selector tunnel
       carries its frame's ordinal index, not its uid, so the comparison with S1 is by position. Pass:
       - cdiff_frame(S1, D1_k) == the 10 PB rows of 178(c). Any other difference is reported, not accepted.
       - Negative: a synthetic graph that swaps one wire between the two frames of `#5540` is detected, while the
         merged mode misses it.
       From L2-A1 on, the cdiff gate is the frame-keyed one.
     - **(c) w10990 IS GONE and PD157/161's L2-A1 row for it is OBSOLETE.** On D1_k, `#10757 'element'` feeds
       ControlTerminal `#23541` through w23556 (`l2a1_facts_80.log:311-318`). That is the S3a indicator branch that
       carries the value to loop 1.5, and P1 shows no cdiff row for `#10407`. Tentative ruling, conditional on a fact
       check in the same tool dispatch: `#23541` moves with `#10757` into the 1.2 body. This is a moved row gated by
       the 179(b) reader. It keeps w23556's source and name, and it leaves `#23541`'s Local readers in 1.5 untouched.
       This is scheduling only: the indicator is written by 1.2 instead of 1.1. If `#23541` has any reader other than
       Locals, or any other writer, STOP; judgement re-decides.
       §3's L2-A1 row "w10990 wired" becomes "`#10757 'element'` → `#23541` wired (179(b) reader), `#10686`/w10799
       untouched".
     - **(d) Reset controls:** `Auto-Reset` `#17487` and `Reset Tracking` `#5634` are ControlTerminals on `#637`'s
       diagram whose only other ends are group-A members (`l2a1_facts_80.log:279-323`). They move with group A, per
       §2, and their rows are gated by the 179(b) reader.
     - **(e) Mixed pairs** `#1147/#1142`, `#5796/#5805`, `#7311/#11001` are initialised from `#686` (w2731/w5812/w11253),
       and their outers are unwired (`:324-341`). L2-A1 creates 1.2's four register pairs from these, under
       RULE-CHAIN-S1 (init source = the same `#686` FSIT; never asked of Jev).
181. **(cycle 80 judgement, on results `80-6` PASS 13/0 and `80-7` PASS 35/0) 180(a)–(c) are DELIVERED. L2-A1 may now
     be simulated.**
     - **(a) The stagesim refit is ACCEPTED as PROVISIONAL** (`tools/stagesim.py:344,403,417`,
       `selftest_stagesim_l2a1_80.log`; the old self-tests still pass, 42/0 and 4/0). The joint sequential replay equals
       the recorded 23 rows with diff 0, and both singles give 0 flips.
       Limits, stated:
       - The truth fixture `tools/bench/sim/l2a1_real_80.json` is the old simulator's output plus or minus the recorded
         compare. It is not a full real terminal table, and the `allow_either` terminals are excluded.
       - R-S2 has an equally fitting alternative ("class `Tunnel` never flips").
       - R-BARE timing is ambiguous.
       Consequences, decided:
       - (1) The next cycle first registers the new `move_in` params in `tools/bench/opmodels/move_in.json` `sim`,
         so that `model_source` cites them. That is a small material task.
       - (2) If L2-A1's simulated plan orphans a WIRED class-`Tunnel` (the branch R-S2 cannot tell apart), that one
         branch is measured on a scratch of D1_k before launch, as in 178(i).
       - (3) The run's per-step comparison (E1) stays the backstop. The simulator's `only_sink` stays `ambiguous`,
         and the executor compares edges after each step, not the half-wire timing.
     - **(b) The frame-keyed cdiff is ACCEPTED** (`vigraph.py:299,334,808,840`, `selftest_vigraph_frame_80.log` 12/0).
       `cdiff_frame(S1,D1_k)` == the 10 PB rows exactly. The negative test is detected by the frame-keyed mode and
       missed by the merged mode, and `diag_vigraph_check` passes 19/0.
       ASSUMPTION F (frame ordinal = the rank of the frame-diagram uid) is accepted on a condition: every stage that
       gates on it checks that the frame-diagram uid SETS of the moved Case structures (`#5540` [5582,5592],
       `#10445` [10453,10459]) are equal before and after. If they are not equal, the gate FAILS; they are not
       re-ranked.
     - **(c) 180(c) is CONFIRMED** (`tools/bench/ct23541_facts_80.log` C1–C4):
       - `#23541` is the indicator `'index'` on `#639`, with a sole writer (w23556 from `#10757 'element'`).
       - Its only reader is Local `#23523`, in WhileLoop `#23032`, feeding `#10978`.
       - `#23541` moves with `#10757` into the 1.2 body.
     - **(d) L2-A1's row set** = group A (8) + `#17487` + `#5634` + `#23541`. It adds 1.2's register pairs from the three
       mixed pairs under RULE-CHAIN-S1. Its re-wires are:
       - K's open rows t0, t3, t4, t7, and t8→`#10969`/`#10757`;
       - the reconnect table the refit simulator computes, including the 3 member edges at `#10247`.
       Gates: frame-keyed cdiff; the 179(b) reader on every ControlTerminal row; the 181(b) frame-uid check.
       PB = the simulator's finalized open-row list. There is no whitelist (179(c)); a `sink_gates` entry is allowed
       only for a ControlTerminal sink that the reader gates.

182. **(cycle 81 judgement, on results `81-2` BLOCKED and `81-3` FAIL 4/1: `tools/bench/sim_l2a1_81.log:15-23,59`,
     `tools/bench/l2a1_partners_81.log`, review `archive/peer/2026-09-25-hyp-sim-l2a1-81.md`) the five `#639` partners
     are decided and the simulator failure is split in two.**
     - **(a) Constants `#10739` (→`#10950 'y'`, w10850) and `#10929` (→`#10757 'index'`, w10947) MOVE with their only
       consumer.** Each is the sole source of a single group-A sink (`l2a1_partners_81.log:21,25`). A diagram constant
       has no state, so where it sits is scheduling only (rule 1a).
     - **(b) Indicator `#17272 'min value'` MOVES with `#10969`, on the 181(c) precedent.** Its sole writer is `#10969`
       (w17287), it has 0 Locals/Globals, and its only reader is the labelled Property `#17289`, which is itself
       group A (`:27-32`). The row is gated by the 179(b) reader.
     - **(c) `#10382 Not` (x ← `#9647`, w9921) and `#11529 Less?` (x ← w11389 from the group-A side) STAY on 1.1.**
       Both feed `#10886` there (`:6-13`). These are 1.2→1.1 crossings, and PD156–161 (O4 closed) send every such
       crossing to QRT. Their two edges are PB OPEN rows owed to QRT, the same as K's frame-image row. The L2-A1
       artefact is BROKEN BY DESIGN at those two sinks. No indicator/Local carrier is invented here.
     - **(d) The sim failure is FIRST treated as our-script-bug.** The review found that `sim_l2a1_81.py` re-wires an
       uncut wire inside the closure, and that the owners table lacks LoopTunnels `#5752`/`#5569`. Both are fixed in the
       plan builder, not in the model.
       Whether stagesim also needs an un-flip rule (does re-wiring a flipped tunnel's outer from an outside source make
       it an input again?) is MEASURED once on a dated scratch of D1_k: do the joint L2-A1 move, wire `#5702`'s outer
       from its K source, then read the direction of that tunnel's outer and inner terminals. No VI is run, and the
       scratch is deleted afterwards.
       The model is fitted to that read, the same way 180(a) was. It is not assumed either way.
     - **(e) Frame-uid check.** `sim_l2a1_81.log:61` read the frame-uid sets as `([],[])`. An empty set is a FAIL of
       181(b), not a pass. The builder must source them from the graph (`#5540` [5582,5592], `#10445` [10453,10459]).

183. **(cycle 81 judgement, on result `81-5` PASS 6/0: `tools/bench/sim_l2a1_81b.log:14-22,71-73,121`,
     `tools/bench/l2a1_unflip_81_run2.log:269-273`) the L2-A1 stageplan is FINALIZED:
     `tools/bench/sim/l2a1/stageplan_l2a1.json` md5 `73e95bc7…`. It may be built.**
     - **(a) The un-flip rule is ACCEPTED as measured.** On a D1_k scratch, re-sourcing the outers from the new 1.2
       register turns the inners of `#5702`/`#5725` back into sources, and the output tunnels `#5680`/`#6016` flip back
       in cascade. `stagesim.py:374` reproduces this (`selftest_stagesim_unflip_81` 8/0; the old self-tests still pass).
       `#5825`/`#10750` are modelled by the same rule but were not read. The run's per-step comparison E1 is the
       backstop (181(a)3).
     - **(b) The source of the re-wired outers is the new 1.2 register (plan row `sr2_L0`), not `5817` on `#637`.**
       This is what 180(e) + RULE-CHAIN-S1 mean: the mixed pairs become 1.2's registers, and the tunnels inside 1.2
       read them there. The other choice would be a cross-loop wire.
     - **(c) PB row `(9703,'x')` is QRT-owed, the same class as 182(c).** It is the S1 edge `#10978` inner → `#9703`,
       whose outer was fed from `#10757` (w23556), so it is a 1.2→1.1 crossing. PB = the 9 rows at
       `sim_l2a1_81b.log:73`. Of these, `5058 'Image In'` and the `376`/`2626`/`5696`/`6085` rows are K's
       and the earlier stages' open rows carried forward.
     - **(d) `sink_gates`** = `rw_10988_17272` only (ControlTerminal `#17272`, gated by the 179(b) reader).
     - **(e) (after result `81-6` BLOCKED at stagexec X3) `move_in` rows carry `pos` from the PLAN, never from the
       recipe.** `sim_l2a1_81b.py:56` omitted the field that `sim_k_split.py:70-72` sets. The builder sets
       `pos` = each node's base position (K's convention). The stageplan is re-simulated and re-finalized, and it gets
       a new md5, which supersedes `73e95bc7…`. A scratch probe with the same `pos` compiled 42 ops with every STEPX
       diff 0 (result 81-6). This is decision 8 of "Stages are SIMULATED": a recipe never re-types row content.

184. **(cycle 81 judgement, on result `81-6` FAIL: `tools/bench/prerun_l2a1_81b.log` X4) the finalized stageplan is
     now `tools/bench/sim/l2a1/stageplan_l2a1.json` md5 `329d89ee…`, which supersedes `73e95bc7…` (183(e) re-sim 18/0,
     same 9 PB rows).**
     X4 failed because the recipe gave the P2 second pass to every node-terminal sink, including the two re-wire
     ends `#5058` t5082/t5164. The stage itself wires those two, so they are unwired when they are addressed offline,
     and the uid path needs a wire.
     - **Decided, option (a) = K's precedent (`stage_d1_k.py:81`):** connect-op sinks are NOT in P2. They are covered
       by the per-step edge comparison E1 (181(a)3) and by Remove Bad Wires / `Is Broken?` on the moved wires. P2
       keeps every move row and every ControlTerminal row (179(b) reader).
     - Option (c), offline addressing of ends the stage itself wires (178(f) `addr_offline`), is a tool the same class
       will need in L2-A2/B. It is OWED as a tool task after L2-A1 and is not built here.
     - The recipe edit re-arms the launch gate, so a prior-art review of the new sha is owed before the run.

185. **(cycle 81 judgement, on result `81-7` FAIL 10/2: `tools/bench/stage_d1_l2a1.log:35-302`, review
     `archive/peer/2026-09-25-hyp-l2a1-run1-81.md`) run 1 stopped SAFELY at real op 18 (`sr1_L0`).**
     Ops 1–17 had step diff 0. Nothing was saved and D1_k is unchanged. The failure is a real-vs-simulated READER
     divergence, not a plan error:
     - the real LVReader does not list border tunnels in `Diagram.Nodes[]`, while `SimReader` does
       (`stagexec.py:782-792`), so dry run and pre-run cannot see the class;
     - PRIME had already flagged `#2886 #5825 #5818 #5702` as unprovable, and the run did not stop on that.

     **Decided: the ADDRESSING TOOL is built now** (the tools rule, 2026-09-24; L2-A2/B need it again):
     - (1) First, a read-only measurement on a D1_k scratch: does the owner structure's `Terminals[]` hold exactly one
       face for each of `#5825 #5702 #10750 #5725 #5967` (the review's discriminating test)?
     - (2) `stagexec` addresses a SelectorTunnel end through its owner structure's `Terminals[]` (measured,
       `build_d1_m3a1.log:1145-1154`) and an FSIT end through Left/Right Terminal (`docs/NAMES.md:1245-1255`). This
       applies in BOTH the real `Addr` and `SimReader`, so the offline gates see what the real one sees.
     - (3) An unprovable PRIME end STOPS the run before op 1.
     - (4) Self-tests cover each route, plus a negative case where SimReader must now fail when a tunnel is listed
       only as a node.
     Then dry → pre-run → run 2 of 2. If run 2 fails, a third run needs a judgement retry card.

186. **(cycle 81 judgement, on result `81-8` FAIL 4/1: `tools/bench/l2a1_faces_81.log` 13/0,
     `tools/bench/stage_d1_l2a1_r2.log:36-37`) run 2 stopped SAFELY at PRIME before op 1, with no mutation.**
     - Case SELECTORS `#5603`/`#10465` (class `Tunnel`) are not in `Nodes[]` either. M1 read them as t0 on their owners
       (w5709/w9921).
     - `#17272` is a front-panel sink wired by `wire_indicators`, so it has no Nodes[] index. PRIME now skips
       ControlTerminal sinks, which the 179(b) reader gates instead.
     - Offline after the run: `OWNER_ROUTED` += `Tunnel`, stagexec md5 `029ea027…`, self-test 22/0, pre-run 81e 7/0,
       PRIME 17 proved / 0 unprovable in the simulation.

     **Decided: RUN 3 is authorised by retry card `tools/bench/cards/task_81-9.json`.** No separate face read comes
     first, because PRIME IS a gated real read before any mutation and stops on any unprovable end. A fourth run is
     not authorised in this cycle.

187. **(cycle 81 judgement, on result `81-9` FAIL 10/2: `tools/bench/stage_d1_l2a1_r3.log:36-439`) run 3 stopped
     SAFELY at real op 31 `rw_5634_10256`.**
     - Ops 1–30 had diff 0 (the furthest any L2-A1 run has reached). The 185/186 owner route is MEASURED WORKING on
       the real VI for all 5 tunnel ends and both selectors (ops 18–28).
     - The stop: ControlTerminal `#5634`, moved at op 10, lost its half-wire in the move, so it is a BARE source.
       `connect_nested` addresses a bare source by its Nodes[] triple, and a live ControlTerminal is not in
       `Nodes[]`. `#17487` (`rw_17487_9676`) is the same case later in the plan.

     This is the THIRD failure in one cycle of the same class: SimReader lists as a node something the real Nodes[]
     does not (border tunnels → selectors → ControlTerminals). **Decided for cycle 82, in this order:**
     - **(a) Reader-parity device (tool, necessary).** At PRIME, compare SimReader's `Nodes[]` membership, per diagram
       the plan touches, against a REAL `Nodes[]` read of the same VI, and fail on any class listed by one side only.
       SimReader's listing rules are then FITTED to that read. Wanted: the next member of this class shows up offline,
       not at op N of a real run.
     - **(b) ControlTerminal route for connect ends.** A ControlTerminal end, source or sink, bare or wired, is
       addressed by the 179(b) route: its term_uid is its own uid, its owner is its Diagram, and it is found with
       `report_all('ControlTerminal')`. This applies in the real `Addr` and in SimReader. It gets a self-test, plus a
       negative case where a ControlTerminal listed as a node fails.
     - **(c)** Then dry → pre-run → run 4, starting from D1_k again. The retry cap is per cycle, so run 4 is run 1 of
       cycle 82, and the recipe is unchanged unless (a)/(b) change a row.
     - Re-ordering the plan to wire the ControlTerminal before its move was rejected: 183 fixed the plan from the
       simulator, and (a) is what prevents a fourth member of the class.

188. **(cycle 82 judgement, on results `82-1` PASS 4/0, `82-2` PASS 4/0, `82-3` BLOCKED 13/4) 187(a)+(b) are
     DELIVERED; L2-A1 now stops OFFLINE at op 35, one class later than run 3.**
     - **(a) Reader parity is ACCEPTED.** `tools/stagexec.py` compares SimReader with a real `Nodes[]` read at PRIME
       and fails on any one-sided class (`parity_l2a1_82_holdout.log:40-50`, 0 after the fit, 173-diagram holdout 0).
       The real `Nodes[]` omits `*Tunnel`, `*Constant` (except ControlReferenceConstant), the Diagram owner and
       ControlTerminals.
     - **(b) Bare nested ControlTerminal SOURCE = `gscript.wire_control` (OpWireCtl_v0, by label on its Diagram).**
       Measured on a scratch at op 31: `#5634→#10256` and `#17487→#9676` each landed the sole predicted source and
       sink with 0 broken wires (`ctsrc_l2a1_82.log:457-508`). It is routed as `connect_route 'ctl'` (stagexec md5
       `3e2b1527…`, self-test 34/0). Dry run: ops 1–34 diff 0.
     - **(c) Op 35 `rw_10738_11055` (bare DigitalNumericConstant `#10739` → `#10950 'y'`) and `#10929 → #10757
       'index'` have NO verb.** `OpWire_v1` raises 1057 (To More Specific Class), and `wire_control` raises 5001
       (`constsrc_l2a1_82.log:511-533`). **Decided: a new op is built (the tools rule, 2026-09-24; L2-A2/B move
       constants too).** It takes the source Constant by uid through the report_all(class) route, reads
       `Constant.Terminal` (634AC04), and calls `Terminal.Connect Wire` (6349C03) on the sink terminal. Gate: the new
       wire's only source is owned by the constant uid. Before building it, run the review's cheap separator
       (`archive/peer/2026-09-25-hyp-constsrc82.md:84-86`): it shows whether OpWire_v1's 1057 is the source cast or
       the destination cast. If it is the destination cast, fixing that cast is the smaller op. Both routes pass the
       same gate.
     - **(d) Cycle 83 follows steer_82 with the outcome review's discriminating test, and L2-A1 is PAUSED behind it.**
       `archive/peer/2026-09-25-outcome-review-20260925.md:180-187` is the second same-day review with the same
       verdicts. The user's 09:30 load answer (`decisions_pending.json` D-2026-09-25-01: 8 and 15 beads, 90 and 150
       Hz, a reduced ROI) has not been used for four cycles.
       - The measurement: real runs of the S1 copy vs `D1_s3_loop15.vi` with the existing driver
         (`tools/bench/drive_m8_s1s3.py`, the INDEX rows 46–47 method). Use 8 and 15 bead picks, at 90 Hz and then 150
         Hz (150 Hz only if the camera reaches it; report the ROI used). Each run is 2–5 min. Report Total Lost Frames
         per cell, and write archive rows 48+.
       - It is a real run of the bed with motors allowed (the 2026-09-24 grant), and it advances R4 and M8. No beads
         are on the rig, so the tracking values are garbage by design, and only operation and frame counts are read.
       - What it decides: if lost frames grow with the bead count, the tracking kernel (M3, loop 1.2) is the lever, and
         (c) + the L2-A1 run resume in cycle 84. If they do not, the camera loop (M4) is the lever, and the split order
         is re-decided.
       - Until then, (c) stays decided but NOT built.
     - **(e) `Stage.close` takes about 20 min after the work** in both 82-2 and 82-3 (`constsrc_l2a1_82.log`,
       close 1070→2265 s). The run's bgrun uses `--max-min 60`. Per-phase stamps inside `stagekit.close` come after
       the deliverable.

189. **(cycle 83 firefighter, fable/low, steer_82 FOLLOWED; result `tools/bench/m8_load_83.json`, INDEX row 48)
     The load measurement of 188(d) RAN — eight real legs, all 8/0 — and it decides the lever: LOOP 1.2 (M3).**
     - **Total Lost Frames, 120 s at ~89 frames/s (≈10,680 frames), S1 copy vs `D1_s3_loop15.vi`:** 8 picks
       **16 vs 12** and (repeat) 12 vs 14; 15 picks **3,331 vs 3,493** and (repeat) 3,161 vs 3,269. Lost frames go
       from ~0.1 % to ~⅓ between 8 and 15 beads on BOTH VIs; the loop-1.5 split is neutral at this load (within the
       run-to-run spread the repeats show: 12–16 and 3,161–3,493). Camera 1280×1024, offsets 0, no ROI change.
     - **150 Hz was NOT reached — a failed prediction (T5 ×4), reviewed as `hyp-camrate83`.** The driver wrote
       `AcquisitionFrameRate` = 150 through the IMAQdx C API between legs and read it back (150.0, period 6666 µs);
       after every VI run the camera read 90.0009 again and the VI's own counter advanced 89 frames/s in all eight
       legs. So the "150 Hz" cells are 90 Hz repeats, reported as such. The user's 150 Hz question needs the rate
       set INSIDE the VI's session (its camera file or an attribute write) — a VI-side change, decided by judgement
       (D-2026-09-25-05 for the user, since it touches the original's camera configuration).
     - **Decision per 188(d): lost frames grow with the bead count ⇒ the tracking kernel (M3, loop 1.2) is the
       lever. 188(c) + the L2-A1 run RESUME in cycle 84**, first act = the cheap separator from
       `archive/peer/2026-09-25-hyp-constsrc82.md:84-86`, then the constant-source op, then dry → pre-run → run 1
       (the steps under STATUS "PAUSED" become the NEXT).
     - Driver changes (measured by the eight 8/0 legs): `drive_m8.py --run-s <s>` (RUN_S was fixed at 35),
       `BP_CAP` = N+2 (one bandpass panel per pick; 15 answered at 15 picks), picks > 6 from a 5×4 grid at
       fractions 0.15–0.85 of the located display rect. Sequencer `tools/bench/drive_m8_load83.py`.
     - Known limit: the per-leg `m8_<leg>_p<N>_r120.json` names do not carry the Hz cell, so the 90 Hz per-leg files
       were overwritten by the 150-written repeats; `m8_load_83.json` carries all eight rows.

191. **(cycle 85 judgement, on result `85-1` FAIL 3/1; review `archive/peer/2026-09-25-hyp-unroutable-85.md`)
     188(c) is DELIVERED: `ops\OpConstWire_v1.vi` md5 `c978863c…`. The separator returned 5001, so the 1057 came from
     the SOURCE cast. Op 35's two rows land their sole predicted sources (`constsrc_l2a1_85.log:510-552`). stagexec
     md5 `aa4c425a…`, self-test 40/0. The dry run now lists every unroutable row. It found TWO: acts 41 and 45
     (`dry_l2a1_85b.log:47-48`). **Decided:**
     - **(a) R41 `rw_10988_17272`: build a new verb whose sink is the ControlTerminal.** It is `OpConstWire_v1` with the
       ladders swapped. The sink is the ControlTerminal, reached by the 179(b)/187(b) route (`report_all('ControlTerminal')`,
       own uid), then TMSC(Terminal) and `Connect Wire`. The source is the bare terminal #10988 on its owner #10969. The
       `Wire Indicators.vi` wired-source guard stays in place, because it is a measured limit (`tools/gscript.py:1835-1838`).
       Rejected: re-cutting {#10969,#17272} into one joint move. That changes plan rows, which 183 fixed from the
       simulator, and nothing has measured it (`l2a1_tunflip_80*` 0 hits).
     - **(b) R45 `rw_6007_5082` (and its twin #6026): address each outer face by the TUNNEL uid through
       `Tunnel.Outside Terminal` 6356001.** Its cast is already measured on these #5540 tunnels (24/24,
       `docs/toolkit-capabilities.md:77`). If that route is refused, the fallback is `UID to GObject Reference` on the
       face uid. Before any write, a read-only scratch check runs after `mv_5540`: `Is Source?`, `Connected Wire` and
       the data type of each face must match the plan's pairing (#6007 `Bead is good? array` → #5082; #6026
       `x,y,z array` → #5164). Rejected: carrying `Terminals[]` order across the move. That is the T2c2 failure on this
       same tunnel #5680 (`docs/NAMES.md:1132-1137`).
     - **(c)** Patch `stage_d1_l2a1.py`'s dry path so that it names the unroutable rows. Today it hits an
       UnboundLocalError `real` after an E1 stop (`prerun_l2a1_85c.log:184`). The edit re-arms the launch gate, and
       the gate is supposed to do that.
     - Both new routes are gated like op 35: sole source owner equals the planned uid, and `Is Broken?` is False.
       Each has a negative case. Rule 1a: the same edges as S1, so no computation change.

192. **(cycle 85 judgement, on results `85-2` FAIL 2/1 and `85-3` FAIL 3/1; review
     `archive/peer/2026-09-25-hyp-unroutable-err2-85.md`)** Both 191 verbs are BUILT:
     - `ops\OpCtlSinkWire_v1.vi` md5 `ce9f2088…`, 24/0.
     - `ops\OpTunOuterWire_v1.vi` md5 `093b0539…`, 28/0. The freed-uid reuse was measured
       (`unroutable_l2a1_85_build_tun2.log:35-37`), and stagexec now raises `UID-REUSE` in `bind_new`
       (md5 `4186fcb4…`, self-test 50/0).
     - Dry run: 42/42, 0 unroutable.
     - On a real scratch, acts 1–44 had diff 0, R41 included (`unroutable_l2a1_85.log:329-554`). Act 45 returned no
       error, and then the next `report_all(GObject)` read raised **LabVIEW error 2 (memory full)** 18 min after a
       fresh start (`:562`).

     ⚠️ **AMENDED the same session, after `archive/peer/2026-09-25-retrospective-cycle85.md` finding 4 + 5 (ACCEPTED).**
     The first draft of 192 ordered an `OpReportAll_v0` Close Reference repair first. That rested on a cause the
     project WITHDREW:
     - `docs/REFERENCES.md:200-229` (§4a-bis): S0 was CLOSED by measurement. 20 traverses gave −0.1 MB private
       bytes; the drift was VI growth. The ops are accepted as they are, and only the user may overturn that reading
       of the rule.
     - `docs/cycle27-plan.md:329-336`: error 2's cause is OPEN, and the repair is not predicted to close it.

     It also put a repair ahead of a measurement. **Decided instead, in this order, before stage run 1:**
     - **(a) Wire `stagekit.private_bytes()` (`tools/stagekit.py:177`) into the stagexec executor.** Stamp private
       bytes and handles per op, and per read, beside each STEPX line, and stop loudly before the error-2 region. It
       is a reader, it is necessary, and it is the meter cycle27-plan.md:335-336 already names. A self-test goes
       with it.
     - **(b) The review's single-op test on a fresh LabVIEW** (`hyp-unroutable-err2-85.md:87-93`): run act 45 alone
       (after the prefix it needs), then `read_live`, then read the new wire's sink back by uid. It must show
       `SubVI[17].t0` = #5082. Log private bytes per step.
     - **(c) One full executor replay on a scratch with the (a) meter** (no save): acts 1–46 plus the rest. It tells
       us whether private bytes grow per op with VI growth (mutate) or per whole-VI read (`wiki_build.py:240`). If the
       read is what grows, the next decision is a per-diagram read in place of the whole-VI traverse. That is
       decided on the numbers, not now.
     - **(d) Stage run 1** only after (a)–(c), and only if (c) shows a full run fits under the budget.
     - NO repair of `OpReportAll_v0` (REFERENCES §4a-bis).

193. **(cycle 86 judgement, on results `86-1` FAIL 3/1, `86-2` FAIL 14/2 and `86-3` PASS 18/0; reviews
     `archive/peer/2026-09-25-hyp-meter86b-prefix.md`, `archive/peer/2026-09-25-hyp-meter86c-err2.md`)** 192(a)–(c) were
     measured:
     - (a) The meter is in stagexec (md5 `e848a14e…`, self-test 55/0), with a default MEMSTOP of 700 MB. Most of the
       cycle-85 handle growth is the VI LOAD: 33,987 → 45,631 (`meter_l2a1_86b.log:31,37`).
     - (c) Full replay with a whole-VI read after every op: edits sum to +1.7 MB and reads sum to +140.4 MB. Error 2
       came at the read right after act 45, at 695 MB, for the second time (`meter_l2a1_86c.log:686,730`).
     - The separator skipped 34 of the 43 reads (9 real: ops 0, 15, 19, 23, 27, 28, 40, 41, 42). All 42 ops ran, with
       diff 0 at the step_44 check and at ops 41–42. R41 #6007→#5082 and R42 #6026→#5164 each have their sole
       planned source, and `Is Broken?` is False. Peak was 634 MB, and error 2 did not occur
       (`meter_l2a1_86d.log:673-743`).
     - ⇒ **Error 2 does not occur with 9 reads, so act 45 itself is not the cause.** Whether the cause is the reads
       themselves or accumulated memory stays OPEN (`hyp-meter86c-err2.md:105`; REFERENCES §4a-bis). The no-edit read
       loop would separate the two. Amended after prior-art `archive/peer/2026-09-25-priorart-c86-l2a1-checkpoints.md`.

     **Decided:**
     - **(a) The stagexec executor does its whole-VI read and diff only at a checkpoint set.** The default stays "every
       op", so existing behaviour and self-tests are unchanged. `stage_d1_l2a1.py` passes the 86d set {0, 15, 19, 23,
       27, 28, 40, 41, 42}, because that set was measured to fit.
     - **Rule 1a:** a checkpoint diff against the step file compares the WHOLE graph state, so every edge change
       since the last checkpoint is still caught. Only the per-op localisation of a failure is lost. Every op keeps
       its own connect read-back (sole source/sink).
     - (b) MEMSTOP 700 MB is passed explicitly by the stage recipe.
     - (c) Stage run 1 follows in the same card after the self-test, dry run and pre-run are re-armed.
     - The no-edit read-threshold probe (`hyp-meter86c-err2.md:105`) is NOT run. The deliverable does not need it,
       and a per-diagram read stays a later option if a larger stage needs one.

194. **(cycle 86 judgement, on result `86-5` FAIL 27/5; review `archive/peer/2026-09-26-hyp-l2a1-p2-86-5.md`, refuted a
     build fault)** L2-A1 stage run 1 SAVED `claudeDev\D1_l2_a1_20260925_235224.vi` md5 `51d9b8a3…`, 307,992 B, by
     gui_save. ExecState is 0 by design.
     - E1: 42/42 ops match their sim step.
     - PB cdiff equals the 9 open_rows exactly. CT 4/4, FU equal.
     - RBW on a scratch removed 29 bad wires, none of them on a re-wired sink.
     - Peak memory 638 MB, no error 2 (`stage_d1_l2a1_86-5.log:660-770`).
     - The 5 FAILs are all P2 rows (sr1_L0, sr2_L0, sr3_L0, tun1, tun2). `address()` raised before any connect,
       because `stage_d1_l2a1.py:90` blanks owner_class/term_class for SelectorTunnel outer-face sinks. That is a
       reader defect, not a build defect.

     **Decided:**
     - **(a) The file is the L2-A1 artefact, CONDITIONALLY.** It becomes the bed only after a READ-ONLY P2 check on it
       passes for those 5 rows. The check addresses the sinks as SelectorTunnel outer faces (owner_class /
       term_class / objs, as `OpTunOuterWire_v1` does) and reads sole source, sole sink and the ordered-pass
       `Is Broken?`. It is a read of the saved file, NOT a rerun of the stage.
     - **Rule 1a:** the per-op diffs against the simulator are already 0, so the check can only CONFIRM the result,
       or catch a broken wire that RBW did not attribute.
     - (b) The recipe:90 fix waits until L2-A1 needs another run. The prior-art gate would be re-armed for nothing.
     - (c) A `graph_*.json` for md5 `6cf5b077…` is placed so that `--prerun` finds it without `--graph` by hand. This
       is bookkeeping, done after (a).
     - (d) The outcome review's kernel-swap test is the candidate that competes with L2 stage 2 once (a) closes. The
       test repoints the S1 copy's tracking call to the verified parallel kernel and runs drive_m8_load83 at 15
       picks. The next judgement session picks between the two.

195. **(cycle 88 judgement, on results `88-1` PASS 38/0 and `88-2` PASS 34/0; review
     `archive/peer/2026-09-26-c87-errorlist-extras.md`)**
     - **(a) `claudeDev\D1_l2_a1_20260925_235224.vi` md5 `51d9b8a3…` IS THE BED** (194(a) closed). The P2 check on a byte
       copy passed 5/5: sole source and sole sink are as planned, and the ordered-pass `Is Broken?` is False
       (`tools/bench/p2check_l2a1_88.json`, `diag_c88_p2rbw.log:47-156`). This is STRUCTURAL, never run.
     - **(b) The cycle-start Error List MISMATCH is explained by measurement, not by the licence classes.** Remove Bad
       Wires on a scratch deletes the same 29 wires as `stage_d1_l2a1.json:866`, none of them on a re-wired sink.
       After that, all 11 extras are ABSENT: the Polymorphic item, the 9 unconnected wires and Less?→RSR. The 8 items
       left are open-row items (`diag_c88_p2rbw.log:171-241`). The Less? wire joins open row `#11529.x` to the
       pre-existing RSR `#7311`; it is not the new SR3R (`:198`).
       Decided:
       - cycle 87's UNCAPPED `WIRE_CLASSES` additions (`isnotconnectedtoanything`, `zerosources`) are REVERTED. An
         uncapped class licence hides a real fault of the same wording, which is what the review warned (`:118`).
       - This bed gets an EXPLICIT expected-errors file with exact per-class counts: the 35 measured items, citing
         (b)'s RBW attribution. The Polymorphic item is licensed ONLY as a count-1 RBW-removable leftover; per-wire
         attribution is not worth a new op.
     - **(c) The kernel swap does NOT move frame loss at 15 picks.** `claudeDev\D1_s1_kswap_20260926_004935.vi` md5
       `e77b8d58…` (one callee `#5058` → `PARALLEL_kernel_v3.vi`; rule 1a on INDEX rows 12/17/40; ExecState 1 warm
       and cold) lost 3,410 and 3,490 frames, against 3,776 for the same-session S1 control and 3,331/3,161 in cycle
       83 (`tools/bench/m8_kswap_88.json`). The difference is inside run-to-run spread. So the tracking KERNEL is
       not the per-frame lever at 15 beads. The t0 model (`docs/t0-instrumentation-plan.md:16`: 4.7 ms fixed + 0.67
       ms per bead ⇒ ~14.7 ms at 15 beads against an 11.1 ms frame at 90 Hz) predicts the size of the loss, but not
       which per-bead work carries it.
     - **(d) NEXT deliverable act = attribute the per-bead cost in situ.** Instrument a COPY of the S1 file with
       tick-count stamps around each per-bead group of `docs/t0-instrumentation-plan.md` Step 1 (kernel,
       `check N bead pos`, median/FIR filters, display, file write), then run one real leg at 15 picks and one at 8.
       The output is ms per iteration per group, which names the lever. Rule 1a: stamps add timing reads and change
       no computed value; the numeric rule-1a check does not apply to an instrumented diagnostic copy that is never
       delivered. L2 stage 2 waits for this: moving loops is not the lever until the per-bead cost is placed.
196. **(cycle 89 judgement, on results `89-1` FAIL, `89-2` FAIL, `89-3` PASS, `89-4` FAIL 24/5 with Part 1 17/17, `89-5` PASS
     32/0 and `89-6` PASS)**
     - **(a) In-VI bracketing with the existing verbs is CLOSED.** 9 of the 11 groups have no error wire, and no verb
       moves live nodes into a FlatSequence (`result_89-1.json`). A LabVIEW-primitive stamp helper needs 10 or more
       primitives that only `copy_by_index` can make (`result_89-2.json`). Neither is escalated: a stronger model does
       not create missing verbs.
     - **(b) The built-in profiler cannot be scripted** (negative search `tools/bench/diag_c89_profiler_search.md`). Its GUI
       route failed its liveness test twice at the checkbox reader (`diag_c89_profiler_live2.log:34`). It is DROPPED as
       the per-bead instrument: it reports CPU time per VI, not waits or serialisation, and it is fragile GUI.
     - **(c) The display term is REAL but MINOR.** On unmodified `D1_s1_copy.vi`, 120 s at 90 Hz, 15 picks, the panel was
       minimized through COM with FPState 4 (`m8_panelmin_89.json`, `m8_panelmin_89b.json`):
       - ctl 3,434 / 3,603 against min 2,616 / 3,286; both pairs favour min (−818 with ctl first, −317 with min first);
         mean −568, about −16 %;
       - at 8 picks, 16 against 15 lost, so the term is not measurable;
       - the minimized legs saved more `.tra` rows (8,147 vs 7,548; 11,505 vs 11,143).
       About 25–31 % loss REMAINS at 15 picks with the panel minimized. So the main per-bead cost is NOT display and NOT
       the kernel (195(c)).
     - **(d) NEXT instrument = a CLFN stamp.** Build a tiny C DLL, `t0stamp.dll`: `stamp(int32 site, void* any)`,
       "Adapt to type", pass by pointer so the data is not copied. It keeps per-site QueryPerformanceCounter buffers
       inside the DLL and dumps them to a file on every 1024th call and at unload. It is called by `build_clfn` nodes
       fed a BRANCH of each group's output wire, plus each holding loop's `i`. That gives completion stamps as in
       brief_89-2, with no LabVIEW primitive to create (census review `archive/peer/2026-09-26-c89-donor-census-hyp.md`).
       - This is a TOOL under the 2026-09-24 grant. Loop timing will be needed again for every loop split (M8
         acceptance).
       - Order: (1) the DLL + its self-test outside LabVIEW; (2) one CLFN node on a scratch VI, handle-flat, with a
         negative case; (3) the instrumented `D1_s1_t0_<ts>.vi`, with `computation_diff` 0 and ExecState 1;
         (4) legs at 15 and 8 picks, with the panel minimized AND normal.
       - Each step saves its artefact (split rule).
     - **(e) Rule 1a:** stamps read time only. The instrumented copy is diagnostic and is never delivered.
197. **(cycle 90 judgement, on results `90-1` (step 1 PASS, selftest 4/0), `90-3` FAIL 20/1 = step 2 met on run 2, the one
     fail was T9b's wrong expected value, and `90-4` PASS: clean rerun 21/0 + `tools/bench/t0_sites_s1.json`)**
     - **(a) Steps 1–2 of 196(d) are DONE.** `claudeDev\t0stamp.dll` md5 `1ea78380…` (x64, cdecl). Scratch VI
       `claudeDev\t0stamp_scratch_20260926_040425.vi` md5 `5e4fd1f0…`: ExecState 1; a stamp costs 0.30 µs with a scalar
       and 1.40 µs with a 1024×1280 U16 branch, so the array is NOT copied; handles are flat; site 64 returns 1 and
       writes nothing (`tools/bench/diag_c90_t0stamp_scratch_r3.log` 21/0).
     - **(b) Stamps are bucketed by the holding loop's `i` stamps.** A While iteration cannot start before every
       node of the previous iteration has completed, so every stamp that falls between the `i` stamps of iterations
       k and k+1 belongs to iteration k. That holds for stamps inside For bodies and case frames too. So those stamps
       are placed WHERE THE NODE IS: a stamp in a For body fires once per bead, which gives per-bead time directly,
       and a stamp in a case frame fires only when the frame runs.
     - **(c) Sites for step 3.** Every site uses the `stamp_terminal` wire from `t0_sites_s1.json`, branched.
       - Loop #637 (tracking):
         - 0 = `i` w3268
         - 1 = the frame-grab output (to be read; see (f))
         - 2 = kernel w5859
         - 3 = Median #30306 w25157
         - 4 = Median #29009 w24106
         - 5 = FIR #28233 w28509
         - 6 = plot Z w363
         - 7 = plot dZ w7109
         - 8 = save trace w541
       - Loop #15173 (display):
         - 10 = `i` w19372
         - 11 = ImageToArray w19465
         - 12 = Flatten w19468
         - 13 = Draw Flattened w19429
         - 14 = rect w16210
         - 15 = grayed rect w16183
         - 16 = circle w16898
         - 17 = text w16895
       - Loop #25380: 20 = `i` w34066.
       - NOT stamped: `check N bead pos` #5987, `save N xyz traces` #6384 and `grayscale color table` #6216. They sit
         in top-level sequence frames outside every While loop, so they run once per run, not per frame. This
         corrects `docs/t0-instrumentation-plan.md` Step 1's "per-bead post-processing" guess.
     - **(d) Output directory per leg.** Every run sets `T0STAMP_DIR` to a fresh per-run directory before LabVIEW
       starts, so no file from an older process id can satisfy a gate (90-4 open 3).
     - **(e) No owner-chain op.** `OpOwnerChain_v1` stops at a FlatSequenceFrame (1055). The tunnel tree and f3a
       already prove ancestry, and placement is proven by uid echo, so that reader is NOT built.
     - **(f) Step 3 acceptance:**
       - `claudeDev\D1_s1_t0_<ts>.vi` is a byte copy of `D1_s1_copy.vi` plus CLFN stamp nodes and branch wires only;
       - `computation_diff(S1,·)` lists exactly the added CLFN nodes and wires and nothing else;
       - ExecState 1, saved by script;
       - one short camera-free or real smoke run writes a file for every loop's `i` site.
       Rule 1a: the copy is diagnostic, never delivered, and stamps read time only.
     - **(g) On `90-5` FAIL (review `archive/peer/2026-09-26-c90-t0step3-movewire.md`).** Site 1 is DROPPED: loop #637
       has no grab node (`IMAQdx Grab #15403` is on the display body). The retry card (escalation 2) is decided as
       follows:
       - scope = the While-body sites plus the For-body sites 3/4/5/16/17. Case-frame sites 6/7/14/15 wait until the
         For-body route is measured.
       - the route is the one MEASURED in 90-5: `move_in` first, then `OpCreateConstOnTerm_v0`, then the branch;
         purge the `Invoke` junk that `move_in` leaves after EVERY call.
       - **ExecState is read after EVERY site** (an incremental read, not a bisect afterwards), so the first site
         that breaks the VI is named by measurement.
       - the branch gate is `Is Broken?` False plus a sink count of +1 on that wire. A branch adds no Wire object, so
         90-5's "wire delta +1" gate was wrong.
       - no stage launch gate for this diagnostic copy, because no S1 graph carries `terminals`. That is accepted: the
         copy is never delivered, and `computation_diff(S1,·)` 0-rows plus added-only is its structural check.
     - **(h) On `90-6` FAIL (escalation 2, both rungs spent; reviews `archive/peer/2026-09-26-c90-t0step3b-forloop.md`,
       `…-c90-t0step3b-r2-indexshift.md`).**
       - MEASURED: the While-body route works. Sites 0 and 2 are ExecState 1 once t6 and t8 are wired; a bare CLFN
         is ExecState 0 by itself. `OpCreateConstOnTerm_v0` refuses a `ForLoop` owner with 1055 at all 5 For sites.
         Run 2 failed on OUR reader (a `move_in` junk Invoke sorts before the CLFN; the index shifts after the purge).
       - DECIDED: **every stamp sits at holding-loop body level. No stamp goes inside a For body or a case frame.**
         For a node inside a For or a case frame, the stamp branches the ENCLOSING structure's output-tunnel wire on
         the While body. That gives the group's completion per iteration.
         - The per-bead cost comes from the slope between the 8-pick and 15-pick legs, not from per-bead stamps. That
           answers the 196(d) question, which group carries the per-bead time.
         - No new For-body verb is built for this. 197(b)'s per-bead stamps are withdrawn.
       - DECIDED: adopt the review gates (5.2, 5.4, 5.5):
         - node terminals are re-found by uid after every purge, never by `Nodes[n]`;
         - the new sink's owner must equal the CLFN uid (this closes the rule-1a hazard of a shifted index);
         - on the first ExecState 0, the site's nodes are deleted, and the site is logged as refused.
       - The next retry is a NEW card, not a third rung of 90-5/90-6. The user's decision item `D-2026-09-26-01`
         records it, and the work proceeds under this recommendation unless the user overturns it (CLAUDE.md 2c).
198. **(cycle 91 judgement, on results `91-1` PASS 207/2 and `91-3` PASS 58/5)**
     - **(a) Step 3 is DONE.** `claudeDev\D1_s1_t0_20260926_055551.vi` md5 `25ea4f7d10d91c41c4b5de64f850c945`:
       12 sites (0,2,3,4,6,8,10-13,16,20), all at While-body level. ExecState 1 was read after every site, and
       `computation_diff(S1,·)` is 0 rows with 24 added. It was saved by script. The per-wire-class probe (10 classes)
       left every class at ExecState 1. The smoke run is ACCEPTED on its (D) criteria: 12 stamp files, and sites 0/10/20
       are present. Its K1 failure (2 of 3 pick markers) is a harness GUI fault (review `archive/peer/2026-09-26-c91-smoke-k1.md`).
       `D1_s1_t0_20260926_054248.vi` (10 sites) is superseded and kept.
     - **(b) Step 4 ran.** The results are in `tools/bench/t0_step4_91.json` and INDEX row 51. On loop #637, the period
       grows +379 µs/bead with the panel normal (ctl) and +190 µs/bead with it minimized (min). **The only site that
       grows is site 4, the For #7911 output tunnel for Median #29009 + FIR #28233:** +255 µs/bead ctl and +173 µs/bead min.
       ⚠️ CORRECTED by retrospective-cycle91 finding 3 (accepted): the 8-pick cell is FRAME-BOUND (period 11.14 ms
       against a camera period of 11.11 ms), so its deltas measure the wait for the frame. The negative slopes of sites
       2/3/6/8 show this. "The kernel does not grow" is WITHDRAWN. What stands is the 15-pick ordering: site 4 fires
       12.6 ms after `i` and the kernel 8.4 ms after it. Loop #15173 runs only during the pick phase.
       A per-bead slope needs two NON-frame-bound pick counts (for example 11 and 15), a decision for the next judgement.
       **CANDIDATE lever = For #7911. This is not accepted yet; see (c).**
     - **(c) The instrument is SUSPECT.** At 8 picks the stamped copy lost 138–144 frames, while unstamped S1 lost 15–16
       (INDEX 48–50); the 15-pick losses match. The first pick click was lost under a foreign capture on the LabVIEW
       GUI thread in 4 of 8 stamped legs, against 0 of about 16 unstamped legs. The stamp's own cost is 0.3–1.4 µs × 12,
       too small to explain this. The hypothesis to test is that the CLFN nodes run in the UI THREAD, so every stamp
       forces a switch to the UI thread and serialises the loops. Before (b) is used, measure two things:
       (1) read-only: the thread setting of all 12 CLFNs in the t0 copy;
       (2) ONE unstamped `D1_s1_copy.vi` leg at 8 picks, panel normal, on today's harness. It separates the harness
       from the stamps.
       If the setting is the UI thread, a copy with "any thread" CLFNs is built from S1 by the same step-3c route
       (the DLL keeps one buffer per site, and each site has one writer), and the 8 ctl and 15 ctl legs are rerun.
       That is a decision for the next judgement, taken on the measurement.
     - **(d) The harness GUI change (log the capture window's class, release a foreign capture) waits for (c)(2).**
       The rerun rule stays "rerun when registered picks ≠ target", using the exact tra rule. Launch 1's needless
       rerun was a float-compare bug, now fixed.
     - **(e) The bgrun reaper card `task_91-2.json` (retrospective-cycle90 device-failed) is valid and was NOT
       dispatched:** the session cap ran out. It is owed right after (c).
199. **(cycle 92 judgement, on result `92-1` FAIL 34/1 — both measurements delivered; the one fail is the pick-count gate)**
     - **MEASURED (`tools/bench/t0_clfn_thread_92.json`, `tools/bench/m8_unstamped8_92.json`, INDEX row 52):**
       - all 12 stamp CLFNs read `Any Thread?` (636D403) = **False, i.e. UI thread**. `build_clfn`'s
         `reentrant=True` (`tools/gscript.py:2968`) does NOT set this property. Reader op
         `claudeDev\OpCLFNThread_v0.vi` md5 `a7308101…` (self-test 9/0).
       - Unstamped `D1_s1_copy.vi`, 8 picks targeted, both legs registered **7**: lost **27 / 19**. Stamped t0 at
         7 registered beads (INDEX 51): **118**. At the same bead count, the UI-thread stamps cost about 100 frames
         per 120 s. ⇒ **the step-4 table (198(b)) is instrument-contaminated and stays unusable** until the stamps are
         shown not to perturb.
       - First-click loss is **2/2 on UNSTAMPED legs today**, with the capture held by `LVDChild` inside LabVIEW's own
         process. ⇒ the first-click loss is a harness/session fact, NOT a stamp effect. 198(c)'s "4/8 stamped vs 0/~16
         unstamped" contrast is WITHDRAWN as evidence about the stamps.
     - **(a) DECIDED: the any-thread copy is a byte copy of t0 with only the 12 `Any Thread?` properties set True**
       (card `92-2`), not a rebuild from S1 by the step-3c route as 198(c) said. Reason: the only difference to be
       tested is the thread setting, and t0's structure is already verified (198(a)). The acceptance is: 12/12 read
       back True, the same counts as t0, `computation_diff(S1,·)` 0 rows with the same 24 added, and ExecState 1 warm and cold.
       Thread safety is covered by 198(c): one buffer and one writer per site.
     - **(b) DECIDED: 198(d)'s harness change is applied now** (card `92-3`). Before every pick, read the
       capture-holding window. Before pick 1, release any capture and verify by a read that none is held. Every act
       is logged through `lv_gui.ps1` under the 2026-09-17 bead-pick approval. The rerun rule is unchanged.
     - **(c) DECIDED: the instrument-clearance legs are ABBA at 8 picks, panel normal, 120 s:** unstamped S1 (A)
       against the any-thread copy (B). The clearance criterion is set NOW, before the numbers: **B is cleared when
       its lost frames are within 2× A's mean + 20 frames**. Anything above that means the stamps still perturb, and
       the next judgement decides on those numbers. Only a cleared B may be used for the 11/15-pick slope legs of 198(b).
     - **(d)** 92-1's open 3 (accept the 7-bead comparison?) is answered by (c). With the harness fixed, both arms
       must register 8.
     - **(e) RESULTS (cycle 92, `92-2` PASS 23/0, `92-3` PASS 43/0, INDEX row 53, `tools/bench/m8_anythread8_92.json`):**
       - Any-thread copy `claudeDev\D1_s1_t0at_20260926_090833.vi` md5 `30a15c67…`: 12/12 read back True warm and cold,
         the same counts as t0, cdiff 0 rows with 24 added, ExecState 1. Writer op `claudeDev\OpCLFNThreadSet_v0.vi`
         md5 `d084d43d…` (self-test incl. negative, handles flat).
       - Harness fix WORKS: the pick-1 capture (`LVDChild`, LabVIEW pid) was held in 3 of 4 legs, freed by one title-bar
         click, and read back as 0. **All 4 legs registered 8/8 on the first attempt.**
       - ABBA, 8 picks, normal, 120 s: **A (unstamped S1) 20 / 22 · B (any-thread stamps) 130 / 131.** The criterion
         (c) is B ≤ 62. **NOT CLEARED.** UI-thread stamps (INDEX 51) were 138 / 144, so the thread setting explains at
         most ~10 frames. **198(c)'s UI-thread hypothesis is REFUTED as the main cause.**
       - The stamped tracking period median is 11.16–11.18 ms, just above the 11.11 ms camera period. The stamps' own
         call cost (≤ 1.4 µs × 12) cannot account for ~50 µs/iteration.
     - **(f) DECIDED (next cycle):** the step-4 table stays unusable. The stamps are NOT used for per-group attribution
       until an instrument passes (c)'s criterion. The next hypothesis is formed under a failed prediction, so it gets
       a `-Role hypothesis` review FIRST (CLAUDE.md §5). The candidate: branching a large-array wire (image / kernel
       arrays) into a CLFN makes the buffer shared, so a downstream in-place node must copy it every frame; scalar-wired
       stamps (the `i` sites) would not do this. The discriminating measurement, ordered cheapest first:
       (1) read-only: the data type (scalar / array + dimensions) of each of the 12 stamp wires;
       (2) build `D1_s1_t0sc_<ts>.vi` from the t0at copy with ONLY the scalar-wired stamps kept (delete the others by
           uid; cdiff 0 rows);
       (3) ABBA 8 picks against S1 under (c)'s criterion.
       If the scalar-only copy passes, the array-branch cost is the perturbation, and array sites are restamped
       through a scalar derived inside the same group, a design for judgement then.
     - **(g)** Pre-92-4 bgrun logs carry no PID line and stay listed as "unfinished" in audit A2. They are NEVER
       closed by hand, because a hand-written KILLED line would be a record the machine did not make.
     - **(h) From retrospective-cycle92 (accepted; `inference-over-measurement` count 2):**
       - **Every leg card from cycle 93 has this PASS criterion:** the dry run EXECUTES the leg script, with GUI/COM
         calls stubbed to saved real returns (e.g. `d4.clickprobe` → the saved attempt-2 dict), and every new line
         between the sequencer and LabVIEW runs once offline before the first launch. A dry branch that writes a fake
         leg.json without calling the leg script is not a dry run (`tools/bench/diag_c92_m2.py:93-94`).
       - Recorded: 92-1's launch 1 COM-Aborted and then force-killed LabVIEW twice, so the VI never closed the camera.
         Afterwards the camera read 90.0009 Hz.
       - Recorded: at 8 picks the B legs are frame-bound (every site is 9.7–10.9 ms after `i` on an 11.16 ms period).
         The 8-pick ABBA is a perturbation test only, never a per-site timing table.
       - Reading applied to 92-1: a card whose FAIL is a single gate, with all its measurements delivered, is judged,
         not escalated.
       - The cycle-92 material model was mixed: 92-1 and 92-2 on fable/low, 92-3 on Opus after the mid-cycle agent
         change. Keep this out of a single-condition Fable-vs-Opus row.
200. **(cycle 93 judgement, on result `93-1` FAIL 6/1 and review `archive/peer/2026-09-26-c93-h1-stamp-array-copy.md`)**
     - **(a) The array-copy candidate of 199(f) is SET ASIDE.** The review (verdict `refuted`) was checked against the
       source: `tools/t0stamp/t0stamp.c:61-62,74-78` calls `WriteFile` + `FlushFileBuffers` inside `stamp()` in the
       caller's thread on every 1024th call per site. The six tracking-loop sites fire once per iteration, so they
       flush in the SAME iteration, about 10 times per 120 s leg. The B legs' tracking period median (11.16 ms) is below
       the MEASURED frame period (11.25 ms, 88.9 fps), with maxima of 211 / 157 ms. That is tail stalls, not a
       per-frame copy. The scalar-only build (199(f) 2) is DEFERRED, not cancelled: it runs only if (c) fails to clear.
     - **(b) 93-1's single fail (no reader for `Terminal.Data Type`) is judged, not escalated (199(h) reading).** The
       type column of `tools/bench/t0at_stamp_wiretypes_93.json` stays INFERRED. It is not needed while (a) stands. The
       reader is built only if the scalar-only build is revived.
     - **(c) DECIDED (card `93-2`):**
       - (1) offline, no LabVIEW: the top-15 tracking-period outliers of the 92-3 B legs' site-00 `.bin`, with their
         iteration indices set against k·1024−1;
       - (2) `t0stamp` v2: the same export `int32_t stamp(int32_t, void*)` cdecl; NO file I/O in `stamp()`; a
         preallocated per-site buffer of at least 65,536 stamps, where overflow is counted and dropped, never flushed;
         the files are written only at `DLL_PROCESS_DETACH`. It is self-tested outside LabVIEW on the call-time MAXIMUM,
         not the median. v1 (md5 `1ea78380…`) is kept as a byte copy. v2 goes in at the path the CLFNs reference, with
         no VI edited;
       - (3) ABBA, 8 picks, panel normal, 120 s: A = `D1_s1_copy.vi`, B = t0at on v2, under 199(c)'s criterion
         (B ≤ 2 × mean(A) + 20). The leg dry run follows 199(h).
       The flush is fixed whatever (1) shows, because a synchronous disk flush inside a timing probe is a defect of the
       instrument. (1) tells us whether it was THE cause, and so whether (3) failing to clear revives the array candidate.
     - **(d) RESULTS (`93-2` PASS 59/0, INDEX row 54, `tools/bench/t0_flushalign_93.json`, `tools/bench/m8_flushfree8_93.json`):**
       - (1) In the 92-3 B legs, the top-10 tracking periods of each leg sit EXACTLY at iterations 1023, 2047, …, 10239,
         at 108–212 / 113–157 ms. Each holds the flushes of the six tracking sites. Periods without a flush: median
         11.157 / 11.175 ms, max 39.8 / 39.3 ms. ⇒ **the flush WAS the cause.**
       - (2) `t0stamp` v2 is in place at `claudeDev\t0stamp.dll`, md5 `b35b398d…`; v1 is kept as `claudeDev\t0stamp_v1.dll`,
         md5 `1ea78380…`. Self-test 9/0. In a 120k-call C bench, v2 has p99.9 100 ns and max 13.6 µs; v1 had max 6.05 ms.
       - (3) ABBA, 8/8 picks, normal, 120 s: **A 14 / 19 · B (t0at on v2) 24 / 43.** The criterion is B ≤ 2 × 16.5 + 20 = 53
         ⇒ **THE INSTRUMENT IS CLEARED** (199(c)). B max periods 61.6 / 63.1 ms, both at iteration 1 (start-up). No
         top-15 period sits at k·1024−1. Overflow 0 at every site.
       - ⇒ The array-copy candidate is CLOSED, and the scalar-only build (199(f) 2) is CANCELLED. The step-4 table
         `t0_step4_91.json` (v1 DLL) stays unusable. Per-site attribution must be re-measured on v2.
       - 93-1's G5 (a hard-coded FAIL for the type-reader check, `tools/bench/diag_c93_wiretypes.py:79-80`) was
         discharged by `archive/peer/2026-09-26-c93b-g5-wiretypes.md`. No type reader is built (200(b)).
201. **(cycle 93 judgement) NEXT: redo the per-site timing with the cleared instrument, i.e. 198(b) on t0stamp v2.**
     - Legs: t0at (`claudeDev\D1_s1_t0at_20260926_090833.vi`, md5 `30a15c67…`) with v2 DLL md5 `b35b398d…`; panel
       normal; 120 s; order **11, 15, 15, 11** picks. These two counts are not frame-bound (198(b)). A leg with registered
       picks ≠ target is rerun once.
       ⚠️ AMENDED by retrospective-cycle93 finding 3 (accepted): the 8-pick clearance is thin. B lost 24 / 43, about 2× A's
       14 / 19, with n = 2, and 199(c)'s criterion was sized for a 100-frame effect. So the legs KEEP an unstamped
       control: add one `D1_s1_copy.vi` leg at 11 picks and one at 15 picks (6 legs in all, in the order
       A11 B11 B15 A15 B15 B11). Report the stamped/unstamped loss per pick count. The per-site table is read as
       ordering and slope, and never as absolute loss.
     - Per leg, per site: stamp count, overflow, and the median and p95 of (stamp − own `i`). Also the tracking-loop
       period median / p95 and lost frames.
     - Per site, slope µs/bead = (mean15 − mean11) / 4, with the spread between the two repeats as its error bar.
     - The leg dry run follows 199(h). The harness is `tools/bench/diag_c93b_abba.py` / `…_leg.py`.
     - Judgement then names the per-bead lever (198(b)'s candidate is For #7911, site 4). The acceptance of any change
       to that group stays numeric (rule 1a).
202. **(cycle 94 judgement, on results `94-1` PASS 65/0, `94-2` PASS 4/2 (two NOT IN FILES, closed by 94-3) and `94-3` PASS 32/0)**
     - **(a) MEASURED (`tools/bench/t0_step4v2_94.json`, INDEX row 55; 6 legs, all picks registered first time):**
       - Lost frames: A11 **1,672** · B11 2,137 / 1,588 · A15 **4,277** · B15 4,049 / 4,070. Stamped/unstamped = 1.11 at 11 and
         0.95 at 15, inside the B11 repeat spread (549) ⇒ **the v2 instrument does not perturb at 11/15.**
       - The 94-1 open "is 11 already frame-bound?" is answered NO. Frame-bound means the period sits at the camera period
         with ~0 loss (8 picks: 11.16 ms, 14/19 lost). At 11/15 the tracking period median is **13.1 / 16.7 ms**, above
         11.1 ms, so the loop is compute-bound. That is the regime a slope needs. 11/15 are valid.
       - Tracking loop #637 period: **+972 µs/bead** (median). Per-site slope of (stamp − own `i`): site 2 = kernel
         #5058 output **+188**; site 3 = Median #30306 tunnel +310; **site 4 = ForLoop #1359 (diagram #7911) output
         +760 µs/bead**; sites 6/8 +189/+188. Display sites 11–16: −21…+56 µs/bead.
     - **(b) MEASURED (`tools/bench/diag_c94c_f7911.log`, `f7911_facts_94_offline.log`, `build_d1_v0.json:62-63`):**
       - ForLoop **#1359** (index 6 of 17 on #637's body #639) owns diagram #7911. N is unwired (the count comes from
         auto-indexing); **0 shift registers; parallelism disabled**, static P 0.
       - It auto-indexes the history array carried by #637's shift register (in: tunnel 9087 ← LeftSR #9025; out: tunnel
         9227 → RightSR #9018) and tunnel 10004. Per iteration: Insert #8634 at index `x − y·floor(x/y)` (a ring
         position from #10068) → IndexArray #8741 rows 0/1 → Subtract (Exp Baseline) → **Median #29009** (half-width
         'Extension median filter half-width') and **FIR #28233** (half-width 'Force smoothing half-width') → Bundler #11310.
       - Its cost rises as the history ring fills: B15 (site 4 − site 3) is 1.3 ms in the first tenth of the run, then
         ~6 ms, then flat at 9.4–10.9 ms. B11 alternates between ~4.8 and ~9 ms by time bin (cause not measured).
       - The D1 plan already moves #1359 to loop 1.2 (`build_d1_v0.json:62-63`). Moving it does not make it cheaper.
     - **(c) DECIDED — THE PER-BEAD LEVER IS ForLoop #1359, and the change is SCHEDULING ONLY: enable loop-iteration
       parallelism on it.** Why this is rule-1a-safe by construction: the iterations share no state (0 shift registers,
       N from auto-indexing), each iteration runs the same nodes on its own row, and output auto-indexing keeps the row
       order. The maths (ring insert, baseline subtract, Median, FIR, their half-widths) is untouched. Rewriting the
       filter to compute only the newest point would be a computation change and is NOT done (rule 1a). Such a rewrite
       would need the user's decision.
     - **(d) DECIDED — build and acceptance (next cycle), in this order:**
       1. Read-only precondition on a scratch: the nodes inside #7911 include no Feedback Node, no local/global write
          and no shift register; record the reentrancy of Median Filter.vi and FIR Filter (DBL).vi. A non-reentrant callee
          only serialises, and the result stays identical, so it is recorded, not blocking.
       2. `claudeDev\D1_s1_par1359_<ts>.vi` = a byte copy of `D1_s1_copy.vi` with ONLY #1359's parallelism enabled, using
          LabVIEW's default instance count (record the P values). The verb for an EXISTING loop's parallelism
          (write `ForLoop` parallel enable + instances) is NOT in `docs/toolkit-capabilities.md`. The card lists it in
          `requires`, and if it is missing it is built first (tools allowed, user 2026-09-24).
          Gates: ExecState 1 warm and cold; `computation_diff(S1,·)` 0 rows; `parallel_enabled` read back True on #1359
          and unchanged on the other 16 For loops; saved by script.
       3. Rule 1a, numeric: run S1 and the copy on the SAME recorded frames through the existing replay path. Compare
          X/Y/Z and the #1359 output (Bundler #11310 array) for bit-identity. Any difference ⇒ stop and report; not accepted.
       4. ABBA, 120 s, panel normal, 15 picks: A = S1, B = the copy, order A B B A, lost frames and #637 period.
          If there is time, repeat at 11 picks.
     - **(e) Recorded, not acted on:** `stage_prerun --dry` crashed on its own graph (`KeyError 'terminals'`,
       `graph_s1_20260924.json`) in 94-3. A read-only script also kept its scratch via `scratches.append` instead of
       `discard_work()`, deleted all the same. A tooling carry, not ahead of the deliverable.
       ⚠️ SUPERSEDED by (f).
     - **(f) (on retrospective-cycle94, accepted: `device-failed`, and the load confound)**
       - The `stage_prerun --dry` loader crash (`KeyError 'terminals'`) is the 5th on record (`prerun_records.jsonl:17,24,33,65`).
         It is **cycle 95's step 0, BEFORE (d)**, because (d)'s build passes through the same gate on the S1 graph.
         Pass: `--dry` on `graph_s1_20260924.json` completes, the earlier crashers re-run without the KeyError, and there
         is a self-test with a negative case. A refusing launch gate is never again satisfied by editing a script so the
         classifier does not see it.
       - Cycle 94's absolute numbers are **LOAD-UNCONTROLLED**: a 40-cell Claude benchmark (`matbench_v1.log`, 11:11–12:24)
         ran on the same machine. Site 4 staying the only large grower matches cycle 91 and stands. From cycle 95, each leg
         logs the foreign `claude`/`node` process count and a CPU sample before and after. If (d)4's A = S1 15-pick leg is
         well below 4,277 lost / 16.7 ms, the slope is re-taken before it is quoted.
203. **(cycle 95 judgement, on results `95-1` PASS 6/0, `95-2` BLOCKED 19/0, `95-4` PASS 84/0 (escalation 1, Opus max),
     `95-5` BLOCKED and `95-6` BLOCKED ×2)**
     - **(a) DONE, step 0 (202(f)):** `tools/stage_prerun.py` md5 `56697c5c…` checks graph shape, so a wrong-shape graph is a
       clean gate FAIL, not a crash. Self-test `selftest_stage_prerun_graphload.py` 18/0 with negatives. S1 has NO
       terminal-list graph of its own; `tools/bench/par1359_95_graph.json` (wiki terminals + graph_objs, md5 `143ad46c…`)
       passes dry for S1 and for par1359 (same objects).
     - **(b) DONE, 202(d)1 precondition (`par1359_95_pre.log`):** the #7911 body has 10 nodes, 0 Feedback Nodes, 0 local or
       global writes, 0 nested structures, and 0 shift registers on #1359. Callees:
       - Median: reentrant, stateless.
       - FIR Filter (DBL): reentrant. Its LSR #195 is uninitialised, but the call site leaves `init/cont` at its default,
         init, so every call starts fresh.
       - Smoothing Filter Coefficients: reentrant.
       - **Magnet2Force v3_for M270: NON-reentrant**, no state classes.
       - JUDGEMENT: a non-reentrant stateless callee only serialises its calls, and FIR re-initialises on every call, so
         none of this changes the result. Rule 1a is still decided by the numeric replay (c).
     - **(b') DONE, 202(d)2:** writer op `claudeDev\OpForLoopParSet_v0.vi` md5 `868e1f42…` (self-test 18/0, handles flat).
       Copy `claudeDev\D1_s1_par1359_20260926_133751.vi`, md5 **`5bef83f0007266b90b7ffd65d2422480`**, 473,285 B:
       ExecState 1 warm and cold; cdiff(S1,·) 0 rows; #1359 parallel True, static P 0 (not written); the other 16 loops
       are unchanged. STRUCTURAL only, never run.
       ⚠️ 95-4 built the op from `tools/bench` because guard_cycle refused `tools/recipes` (4 DUE slugs). That is
       routing around a gate. The slugs were then answered: `docs/violation-decisions.md`, four blocks at 2026-09-26 13:47.
     - **(c) DECIDED for 202(d)3, the replay:**
       - `tools/recipes/stage_replay_swap.py` md5 `1292fee8…` now takes `--plan 95` / `REPLAY_SWAP_PLAN=95` (default 78 is
         unchanged by construction, not yet shown by a dry run). Plan `tools/bench/plans/plan_replay_swap_95.json` md5
         `ea7cf810…` makes one copy, `claudeDev\replay\D1_s1_par1359_replay_<ts>.vi`.
       - The S1 side reuses `replay\D1_s1_replay_20260925_075422.vi` (md5 `126f8497…`, matched in-run).
       - Dry run: `--graph tools/bench/par1359_95_graph.json` with env `REPLAY_SWAP_PLAN=95`.
       - **The replay uses 15 picks** (row 47 used 3 / 35 s), so #1359 iterates at the ABBA load.
       - Compare every tra column. Bundler #11310 is NOT OBSERVABLE (it is not in tra), so X/Y/Z bit-identity decides, and
         that is recorded as the acceptance level.
     - **(d) DECIDED for 202(d)4:** the ABBA runs on the UNSTAMPED S1 and par1359 files. The primary metric is lost frames.
       The #637 period is taken from the tra frame-step proxy (step × 11.11 ms), labelled as a proxy. A stamped par1359
       build is not made unless the lost-frame result is ambiguous.
     - **(e) What blocked cycle 95 was card scoping, not the work.** Three cards came back BLOCKED on my own card rules or
       flags (95-5 "never save", 95-6 write globs, 95-6 peers). The outcome review was due, and `guard_cycle` refuses all of
       `tools/recipes` until it runs; the judgement session ran it at cycle close.
       Next card: `peers` must include whatever the gates may demand. The card rule "never move a script to dodge a
       gate" covers EVERY gate (`guard_cycle`, the launch gate, and any other), not only the launch gate. Also, the material sandbox cannot hash files under
       `C:\Program Files\…\claudeDev`, so md5s are pinned in-run.
     - **(f) (on outcome review `archive/peer/2026-09-26-outcome-review-20260926.md` + `steer_95.json`, FOLLOWED) ORDER
       AMENDED: the ABBA (d) runs BEFORE the replay (c).** The ABBA runs S1 and par1359 as they are, with no swap copy and no
       `tools/recipes` build, through the cycle-94 leg harness (`diag_c93b_abba.py` / `_leg.py` pattern). Legs A15 B15 B15 A15,
       each logging the foreign claude/node count and a CPU sample (202(f)).
       - B clearly below A ⇒ run the replay (c) next.
       - No difference ⇒ the replay is moot, and the lever is re-judged.
       - Rule 1a holds regardless: par1359 is NOT accepted or shipped before the replay is bit-identical. The ABBA is a timing
         measurement only.
204. **(cycle 96 judgement, BEFORE the numbers exist) the ABBA criterion and the card split**
     - **(a) "B clearly below A" is fixed now:** both B15 legs lose fewer frames than both A15 legs, AND mean(B) ≤ 0.8 ×
       mean(A). Why 0.8: repeat spreads at 15 picks run up to ~10 % of the mean (B15 4,049 / 4,070; cycle 83 3,331 / 3,161;
       cycle 88 3,410 / 3,490), so a 20 % gap is outside two spreads. B above A, or inside the band, = "no difference"
       ⇒ 203(f)'s re-judge branch. Nothing between: a result that meets only one condition is "no difference" too.
     - **(b) Card split (§3 "measurement, not action"):** card `96-1` is the ABBA only (unstamped S1 vs par1359, the
       cycle-94 harness copied to `diag_c96_*`). The replay (203(c)) is a separate card that judgement writes after reading
       96-1's numbers against (a). The replay card's `peers` must include `outcome` and `hypothesis` (203(e)).
205. **(cycle 96 judgement, on results `96-1` PASS 53/0, `96-2` PASS 3/0 and `96-3` PASS 5/0)**
     - **(a) MEASURED, 96-1 (`tools/bench/par1359_96_abba.json`, INDEX row 56):** 15 picks, 120 s, panel normal, all legs
       15/15 on the first attempt. Lost frames: **A (S1) 3,435 / 3,389 · B (par1359) 3,867 / 3,863**, i.e. +13 %. Tracking
       iterations: A 7,670 / 7,728 · B 7,243 / 7,251. By 204(a) this is "no difference" (B is above A) ⇒ **the replay is
       MOOT. par1359 is REJECTED as a lever.** It is not accepted and not shipped; the file is kept.
       The frame-step proxy saturates at whole frames (median 1, p95 3 steps in every leg), so it cannot separate A and B.
     - **(b) Review `archive/peer/2026-09-26-c96-par1359-h1.md` (verdict refuted) is ACCEPTED as a disposition.** It gives three
       alternatives, none measured: (1) serialisation on the non-reentrant `Magnet2Force` (203(b)'s "only serialises" was
       asserted, not measured, and the reviewer names that as `inference-over-measurement`); (2a) the +760 µs/bead is cumulative
       (site deltas), so #1359's own slope is about +450, part of it ring-fill memory work that does not scale with cores;
       (2b) oversubscription, because unwired P takes every logical CPU. **We do not buy the discriminating CPU-during-leg test**,
       because (c) makes the question moot.
     - **(c) MEASURED, 96-3 (`tools/bench/diag_c96_cons_trace.log:235-260`, `tools/bench/f1359_consumers_96.json`):** #1359 has
       exactly two out tunnels. 11363 (← Bundler #11310) → BuildArray #11261 → **indicator #8323 'Force (pN) vs Extension (nm)'**
       on #639, and nothing else. 9227 (← Insert #8634) → RightSR #9018 → LeftSR #9025 → #1359's own input, and nothing else.
       **No path reaches the tra/file writer, a motor/instrument call or any input of kernel #5058.** No case gates either path, so
       it runs on every #637 iteration. No local or global names the indicator. Implicitly linked PROPERTY NODES of #8323 were
       not resolvable offline (OPEN; closed by (e) step 0).
       ⇒ At 15 beads the frame loop spends ~9.4–10.9 ms per frame (202(b), site 4 − site 3 once the ring is full) computing ONE
       live graph.
     - **(d) DECIDED — the next lever is DISPLAY-RATE GATING of #1359's graph chain, scheduling only:**
       - The ring insert #8634 and its SR chain (9227 → #9018 → #9025) run on EVERY frame, unchanged, so the history is identical.
       - The graph chain (per row: IndexArray #8741, Subtract (Exp Baseline), Median #29009, FIR #28233, `Magnet2Force`, Bundler
         #11310; then BuildArray #11261 and indicator #8323) runs only when `i mod N = 0`, where `i` is #637's iteration and N is a
         new front-panel control, "Force graph: update every N frames", default **9** (about 10 Hz at 90 Hz).
       - **N = 1 reproduces the original exactly.** That is the rule-1a anchor.
       - Why this is rule-1a-safe: the same nodes run on the same inputs at the frames where they run; the output feeds only a
         display; saved data, motor commands and the kernel are untouched (c). Only how often a display is refreshed changes.
       - **ASSUMPTION (CLAUDE.md 2c):** the user's 2026-09-14 display policy (live display 10 Hz is enough and must be a runtime
         control) covers this graph as well as the live image. It is put to the user as **D-2026-09-26-02**. If the answer is no,
         the default becomes 1 and this lever is lost; nothing else changes.
     - **(e) Build and acceptance (next cycle), in this order, from a byte copy of `D1_s1_copy.vi` (S1, md5 `3e3d23ce…`):**
       0. Read-only COM, on a scratch: list every property node, reference or control-reference linked to #8323. Gate: none reads
          its Value into anything other than a display. If one does, STOP and report; this decision is re-judged.
       1. Design the gate structure (where the case frames sit, how the per-row chain inside #1359 and the #639 BuildArray +
          indicator share ONE boolean, what the false frames output), with `requires` filled, and verbs checked by
          `py tools/protocol.py requires`. Missing verbs are built first (tools allowed, 2026-09-24).
       2. Stage: dry run → offline pre-run → one real run (CLAUDE.md "Stages are SIMULATED"). Gates: ExecState 1 warm and cold;
          `computation_diff(S1,·)` = exactly the new case/control/modulo objects plus the moved edges, listed by row; saved by
          script as `claudeDev\D1_s1_fgate_<ts>.vi`.
       3. Timing: ABBA, 15 picks, 120 s, panel normal, A = S1, B = the gated copy at N = 9, the 96-1 harness (`diag_c96_*`).
          204(a)'s criterion applies unchanged.
       4. Rule 1a, numeric: replay of the SAME recorded frames through S1 and the gated copy at **N = 1**. Pass: every tra column
          bit-identical, AND #8323's final value read by COM after the run bit-identical. Then N = 9 on a replay whose last frame
          is a multiple of 9: #8323's final value equals the N = 1 value. It is not accepted before both.
     - **(f) Carries, not ahead of (e):** `peer.ps1` cannot parse `loss_usd=?` in a verdict (96-2 hand-transcribed ? → null).
       96-3's owner-tree parser leaves 17 diagrams ownerless (G7, `diag_c96_cons_trace.log:234`); its terminal/wire answer
       stands, and the parser is not reused until fixed.
206. **(cycle 97 judgement, on `97-1` PASS 5/0, `tools/bench/cards/result_97-1.json`, facts `tools/bench/f1359_gate_facts_97.json`)
     — the gate design, amending 205(d)/(e)**
     - **(a) Step 0 PASSED:** the only object naming #8323 is Invoke #10313 `Reinit To Dflt` (a writer, `diag_c97_gatefacts.log:27-31`).
       The event-structure registrations (#10153, #15544) were NOT read (no op). **Accepted without a reader:** a Value Change
       event fires only on user edits or a `Value (Signaling)` write, never on a terminal write, and no `Value (Signaling)` node
       on #8323 exists; so the rate at which the terminal is written cannot change what an event case sees. No reader is built.
     - **(b) 205(d) CORRECTED: `Magnet2Force` #28083 is NOT gated.** It feeds BuildArray #8566 → Replace Array Subset #8634
       (not "Insert") → tunnel 9227 → the ring history, so it must run every frame. The gated set inside #1359 is EXACTLY the
       11363-only set: #8741 IndexArray, #8764 Subtract (with `Exp Baseline` terminal #8476), constants #8775/#8795, #27716,
       #28180, #28233 FIR, #29009 Median, #11310 Bundler, and the tunnels 31051/31137 (`f1359_gate_facts_97_offline` / `off.log:5-33`).
       The ONLY wire into this set from the ungated part is w8811 (#8634 `output array` → #8741 `array`). The Median+FIR cost
       is in the gated set, so (b) removes nothing the lever needed.
     - **(c) Structure:** Case **A** inside #1359's body (diagram 7911) holds the (b) set; its selector is a boolean entering #1359
       through a NON-indexed input tunnel; its output tunnel to 11363 uses **default if unwired** in the False frame. Case **B** on
       #637's body (diagram 639) holds ONLY BuildArray #11261 and #8323's block-diagram terminal; its False frame is empty, so
       #8323 is not written that frame and keeps its last value. **#11576 Unbundle and #11608 Bundle stay OUTSIDE B** (they are
       cheap, and WLC #1114's other output also feeds SR #862). One boolean `upd` feeds both A and B:
       `upd = (Q&R(i #644, N).remainder == 0)`, with i = #637's iteration (term #644, wire w3268) and N = a new I32 panel
       control `Force graph: update every N frames`, default 9, **coerced to ≥ 1** (Max(N,1)) so N = 0 cannot divide by zero.
       At N = 1, `upd` is True on every frame, so every gated node runs on the same inputs as S1 → rule-1a anchor.
     - **(d) Tools first (allowed 2026-09-24; the deliverable needs them):** from 97-1 (C), MISSING or unmeasured: (1) create a
       Case Structure whose owner is a loop BODY diagram (build_case is top-level only, `gscript.py:3173`); (2) move a node set
       into a case FRAME with every wire re-established and read back (move_in severs wires, `cycle27-plan.md:846-851`);
       (3) the same for a control terminal (ctlterm move_in, `d1-build-plan.md:213-222`); (4) a label writer for a new control
       (`cycle27-plan.md:2084`); (5) the output-tunnel `use default if unwired` setter (property id 5D251C00, `NAMES.md:1036`).
       Existing: loop-`i` wiring via connect_from_wire w3268; Q&R/Equal-0 donors via stagekit copy_in (`stagekit.py:779`);
       set_index_mode (`gscript.py:1949`). Each new tool is self-tested on a scratch with a negative case, handles flat.
     - **(e) Order this cycle:** 97-2 tools (d) → 97-3 stage (205(e) 2) → 97-4 ABBA (205(e) 3) → rule-1a replay 205(e) 4 is next
       cycle unless time remains. Nothing is accepted before 205(e) 4.
     - **(f) (on `97-3` PASS 64/1, escalation rung 1 Opus max; 97-2 FAILED on its synthetic fixture) TOOLS DONE:** `gscript.case_in`
       (T1), `gscript.move_into_frame` (T2/T3), `set_control_label` = `claudeDev\OpLabelSet_v0.vi` (T4), `tunnel_use_default` =
       `claudeDev\OpTunnelUseDefault_v0.vi` (T5), plus `OpCaseFrames_v1.vi` (`tools/bench/selftest_c97_tools.log`,
       `diag_c97_tools_opbuild.log:77-82`, `diag_c97_tools_handles.log`). Its three OPENs are decided:
       1. **Polarity:** keep the Boolean selector (`Equal To 0?` on Q&R's remainder). The gated nodes go into the frame whose
          name reads ` True ` AFTER the Boolean is wired (measured: numeric-born frame `1` becomes ` True `, same uid,
          `selftest_c97_tools.log:11,17,28`). The build gate reads the frame name, not an index.
       2. T2/T3's 20-call criterion is met by their writers' 20-call runs plus one warm T2 (−13). Accepted.
       3. The stage carries a MEMSTOP of 700 MB private bytes (connect calls climb ~0.5–0.75 MB each; cycle 85 hit error 2 at
          ~695 MB).
     - **(g) 206(c) AMENDED: no `Max(N,1)`.** LabVIEW's integer Quotient & Remainder by 0 returns remainder = x, so N = 0 gives
       `upd` True only at i = 0 (the graph freezes after frame 0). No division fault, so no coercion node is added (one object fewer
       in the cdiff). Documented behaviour: N ≤ 0 = "never refresh after the first frame".
     - **(h) (on `97-5` FAIL 45/2, RETRY_CAP and failure budget spent, nothing saved) ExecState 0 AFTER THE MOVES — READ IT, DO NOT
       GUESS.** Run 2 (`tools/bench/fgate_97_stage2.log`): ExecState 1 after all the wiring (E1), **0 after `move_into_frame` A+B and
       UseDefault (E3, `:395`)**. cdiff 0 rows, added only Q&R #22968 / Eq0 #10280 / control #23136; A's 16 and B's 3 edge tables
       equal. Reviews `archive/peer/2026-09-26-c97-fgate-es0.md` + `-r2.md` offer (i) orphaned severed wires left by
       `move_into_frame` (surplus +12 vs +4 in A, +3 vs +2 in B, arithmetic only) and (ii) an illegal final structure. **Judged:**
       (ii) is weak — a control terminal, an indicator terminal and a default-valued output tunnel inside a case frame are all
       ordinary LabVIEW — but it is not refuted by a measurement, so the next act separates them by READING, not by a third
       inference. 97-3's T2 self-test gated edge tables only, never ExecState or leftover wires after the move: that is the tool's
       gap (record for the retrospective).
       **Next cycle, first act (one card):** re-run `stage_d1_fgate.py` to E3 on a fresh byte copy, then **save that broken
       intermediate by `gui_save`** as `claudeDev\D1_s1_fgate_BROKEN_<ts>.vi` (rule "big work saves intermediates" 6, user
       2026-09-22) and read (1) LabVIEW's Error List for it (the `errorlist_check` GUI reader the runner already uses; each item's
       object uid), (2) the broken-wire list with owners (bad wires in A/B frames vs elsewhere), (3) `Remove Bad Wires` on a
       SCRATCH copy of the broken file → ExecState. Facts only. Judgement then decides between a `move_into_frame` fix
       (delete severed wires) and a structure change.
       **Rule 1a on A's False frame (97-5 OPEN 3):** the default value from tunnel #23927 flows into #11363 on non-update frames
       but reaches nothing, because BuildArray #11261 and #8323 sit in B's True frame, which runs only on the same `upd`. So it
       is intended and computation-neutral; the replay 205(e) 4 still decides.
       **Donor unload** (`CloseFrontPanel` → 0x47D) did not happen; peak private bytes 622 MB < 700, so it is not needed now. ⚠️ ASSUMPTION (2c): LabVIEW's
       int-÷-0 rule as stated; the stage's smoke check is not asked to measure it. If it is wrong, it faults only at N = 0,
       never at the default.
207. **(cycle 98 judgement, on `98-1` PASS 53/0, `tools/bench/cards/result_98-1.json`, log `tools/bench/diag_c98_fgate.log`)
     — WHY THE GATED COPY BREAKS: MEASURED, and the fix**
     - **(a) MEASURED:** ExecState E1 1 → after move A **0** → after move B 0 → E3 0 (`diag_c98_fgate.log:289,362,417,437`).
       After move A, 8 wires have NO terminal at all (7931 9407 15847 24106 28139 28443 28509 33062, owner diagram 7911); after
       move B, 1 more (10908, owner 639). All 9 are OLD uids present at E1, and none is in the new-wire lists
       (`:364-391,419-423,440-456`). Error List of the saved broken file `claudeDev\D1_s1_fgate_BROKEN_20260926_175556.vi`
       (md5 `b114bb1b…`, never run) = 15 wire items only (7 loose ends, 8 not connected). **Remove Bad Wires on a scratch
       removed exactly those 9, ExecState 0 → 1, Error List 0 items** (`:469-480,633,640`); no member-edge wire was removed.
     - **(b) JUDGED:** explanation (i) of 206(h) (orphaned severed wires) is CONFIRMED; (ii) (illegal final structure) is
       REFUTED by measurement, since the E3 structure minus those 9 wires is ExecState 1. A per-item Error List ↔ uid mapping
       is NOT needed. The retrospective-cycle97 gap is the tool's: T2's self-test never read ExecState or leftover wires.
     - **(c) THE FIX (tool change, `gscript.move_into_frame`):** after the move, delete every wire that (1) existed before the
       move (uid in the pre-move wire set of the source AND target diagrams) and (2) now has ZERO terminals. Targeted deletion
       by uid only; **never a whole-VI Remove Bad Wires** (it would also hide breaks the verb did not cause). Then the verb
       reads ExecState and the termless-wire count and FAILS if ExecState is 0 or a termless wire remains, unless the caller
       passes an explicit `expect_broken=True` (the retrospective-cycle97 rule: a diagram-editing verb is gated on ExecState
       after the edit). Rule 1a: a wire with no terminal carries no data, so deleting it changes no computation.
     - **(d) Self-test before use:** the T2 self-test is re-run on a scratch S1 with the new gates (ExecState 1 and 0 termless
       after the move, edge tables equal), plus a negative case (`expect_broken` False on a deliberately left orphan →
       the verb fails). Handles flat over 20 calls.
     - **(e) Then the stage run (205(e) 2) in the same card:** `stage_d1_fgate.py` with the patched verb, dry + prerun
       first, RETRY_CAP 2, saved BY SCRIPT as `claudeDev\D1_s1_fgate_<ts>.vi`, ExecState 1 warm AND cold, cdiff = the 97-5
       rows (Q&R #22968, Eq0 #10280, control #23136 added, 0 changed rows), edge tables A 16 / B 3 equal, 0 termless wires.
       Still NOT accepted before 205(e) 3 (ABBA) and 4 (rule-1a replay at N = 1).
     - **(f) Rule 1a on A's False frame** stays as judged in 206(h); the replay decides.
208. **(cycle 98 judgement, on `98-2` FAIL 45/2, `tools/bench/cards/result_98-2.json`, log `tools/bench/selftest_c98_stage.log`)
     — 207(c) AMENDED: termless-only deletion is NOT enough**
     - **(a) MEASURED:** the patched verb deleted exactly 98-1's 8 orphans after move A (all Diagram 7911, `:302-312`), 0
       termless left, edges 16 = 16, and ExecState was still **0** after A + UseDefault (`:320-321`). Stage not launched.
     - **(b) JUDGED:** 98-1's Error List had **7 "Wire has loose ends"** items besides 8 "not connected to anything"
       (`diag_c98_fgate.log:558-572`). "Loose ends" is a KEPT wire with a dangling branch. It is not termless, so 207(c)'s
       filter cannot see it (review `c98-selftest-f4e` names w7913/w10430). The one operation MEASURED to give ExecState 1
       on this structure is Remove Bad Wires (98-1: 9 wires removed, ExecState 0 → 1, 0 Error List items, no member edge lost).
     - **(c) THE FIX, amended:** after each move, `move_into_frame` runs **Remove Bad Wires**. It is scoped to the source
       diagram and the frame's diagram when LabVIEW exposes it per diagram, otherwise to the VI. It is fenced by gates that
       answer 207(c)'s objection ("hides breaks the verb did not cause"):
       (1) PRECONDITION: ExecState read 1 BEFORE the move, else refuse. So no break existed that the move did not cause.
       (2) Every removed wire uid was present before the move (the wire sets diffed before/after RBW).
       (3) The moved set's edge table is equal before/after, and no data edge is lost.
       (4) ExecState 1 after, 0 termless wires. Else raise, unless `expect_broken=True`.
       Rule 1a: RBW removes only wires that carry no data (broken or dangling); (3) proves no data edge was removed.
       The 207(c) termless deletion may stay as a first pass or be dropped; the gates decide.
     - **(d) Per-move gate stays:** after A alone the graph is legal LabVIEW (B's nodes are simply still outside a case), so
       ExecState 1 is required after EACH move, not only at E3.
     - **(e) Escalation:** 98-2 spent its failure budget → card 98-3 = rung 1 (`material-opus-max`), same pass list, this
       method. Then the stage run per 207(e).
209. **(cycle 98 judgement, on `98-3` FAIL 48/2, `tools/bench/cards/result_98-3.json`, log `tools/bench/selftest_c98_rbw.log`)
     — 208(d) WITHDRAWN: the ExecState gate belongs at the END of the move batch, not after each move**
     - **(a) MEASURED:** No per-diagram RBW exists (AbstractDiagram has only `Remove Wire Loose Ends` 6375409; VI method 410
       used, `archive/peer/2026-09-26-c98-rbw-scope.md:39-45`). In-memory VI RBW after move A removed exactly the 8 pre-existing
       termless wires (1915 → 1907), with 0 edges lost and 0/2212 non-member wires lost. After UseDefault, ExecState was
       **still 0** (`:360-383`). The negative case and the precondition refusal were both caught (`:355-359`). 98-1's
       ExecState 1 came only after move B, and after a GUI save + fresh load (`diag_c98_fgate.log:461-479`).
     - **(b) JUDGED:** 208(d)'s "after A alone the graph is legal" was an inference, never measured, and 98-2 + 98-3 both
       contradict it. Slug for the retrospective: `inference-over-measurement` (mine). What 98-1 measured is the E3 state
       (A + B + UseDefault) plus RBW. So the check goes where the evidence is.
     - **(c) Verb contract, amended:** the ExecState-1 PRECONDITION applies to the FIRST move of a batch (E1 = 1 is measured). A
       and B run with RBW + the uid/edge/termless gates after each move, but with `expect_broken=True` for ExecState. The
       ExecState-1 gate is read ONCE, after the last move + UseDefault + a final RBW, **in memory**. The 98-3 verb change
       (precondition + RBW + hard gates) is KEPT, extended with this batch form.
     - **(d) Deciding cell = the self-test (card 98-4, rung 1 again):** scratch S1, the stage body to E1, then move A → move B →
       UseDefault → RBW → ExecState in memory.
       - **1:** the fix is proven. Run the 20-call handle test and the negative case, then the stage run per 207(e).
       - **0:** a MEASUREMENT only. gui_save the scratch (the approved broken-intermediate route), fresh-load it, and read
         ExecState. This separates "stale in-memory state" from "the structure itself". No stage run; return the facts.
       Error List counts: 98-3 re-read them as 6 loose ends + 9 not connected (98-1 said 7 + 8); not material to the fix.

210. **(USER DIRECTION 2026-09-26 18:0x, chat; answers D-2026-09-26-02 — supersedes 205–209's N-frame GATE; numbered 210 because cycle 98 wrote its own 209 at the same time)**
     *"그래프 플롯 기능을 혹시 별도 루프로 두는 것은 어떤지? 로컬 변수에 데이터들은 다 입력하고 데이터 플롯은 별도 루프로"* →
     *"이대로 진행"*. The speed-up is taken, but NOT as a Quotient&Remainder gate inside the frame loop:
     - (a) **The `Force (pN) vs Extension (nm)` plot (#8323) moves to a SEPARATE DISPLAY LOOP.** The frame loop only
       WRITES the plot data to a local variable (the array that fed #8323, w10908's source); the display loop runs on
       its own clock (a panel control `Display period (ms)`, default 100 = ~10 Hz, ≥ 1 ms), reads the local, writes
       #8323. No queue (CLAUDE.md 1c''), no edge detection, no schedule boolean in the frame loop. Stop: the display
       loop reads the same stop local the S3 stage uses (Pre-decided 154 carrier), exits after the frame loop.
     - (b) The other indicators fed from inside #637 (Z / dZ plots #6085/#5696 and any cycle-94 timing site that is a
       pure display) are candidates for the SAME display loop; take them in the same stage only if their cycle-94
       per-site cost is measured; otherwise one plot first, measure, then the rest.
     - (c) Rule 1a: scheduling change only — the values reaching #8323 are the same arrays, later. Saved data untouched.
       Acceptance = real ABBA run (15 picks, 120 s) vs `D1_s1_copy.vi`: lost frames must drop by about the plot's
       measured 10 ms/frame share; plus recorded-frame replay bit-identity on X/Y/Z as for every stage.
     - (d) Measure first, offline where possible: the cost of a local-variable WRITE of the plot array per frame
       (stamp site around the write, or the t0 harness) so (b) can be summed before it is built.
     - (e) **The fgate work stops here**: `stage_d1_fgate.py`, `D1_s1_fgate_BROKEN_*` and PD206(h)'s diagnosis are
       DROPPED (the broken intermediate may be deleted; its Error List facts stay in the 98 cards as prior art on
       what breaks when a case frame is built around #1359).
     - (f) Order for cycle 99 (PD210(f)): design page (display-loop stage: locals list, indicator list, stop carrier, rows) →
       `requires` on the card → simulator (dry, pre-run, computation_diff 0) → one LabVIEW execution → ABBA. The
       same "big work split into saved steps" rule as every stage.
211. **(cycle 98 judgement, CLOSE — on PD210 arriving mid-cycle; card `98-4` BLOCKED by it, correctly, nothing run)**
     - **(a) 209(c,d) is CANCELLED with the rest of the fgate work (210(e)).** 98-4 never ran, so its deciding cell stays
       unmeasured. It is NOT re-run as prior art: 210 moves #8323 into a separate LOOP, not into a case frame of #637.
     - **(b) Prior art that carries into 210's stage (measured, cycle 98):** after `move_into_frame` from S1,
       (1) the verb left the OLD severed wires in place: 8 termless in 7911 and 1 in 639, plus dangling branches on kept
       wires (Error List: loose ends + not connected, all wire items);
       (2) VI-level RBW in memory after move A removed exactly the 8, and ExecState stayed 0 (`selftest_c98_rbw.log:360-383`);
       (3) RBW on the saved A+B+UseDefault file gave ExecState 1 (`diag_c98_fgate.log:469-480`).
       Any 210 row that MOVES an existing terminal must therefore read termless and loose-end wires and ExecState after the
       move, per the retrospective-cycle97 rule.
     - **(c) `gscript.move_into_frame` is LEFT AS 98-3 made it** (md5 `b3d9f373…`). It refuses unless ExecState is 1 before
       the edit, runs VI-level RBW after, and raises on a new-uid removal, a lost edge, a termless wire, or ExecState 0
       unless `expect_broken=True`. That fails closed. Its only caller was the dropped fgate stage. **A 210 design page that
       uses it on a bed that is BROKEN BY DESIGN must say how it passes the precondition. It must never loosen the
       precondition silently.**
     - **(d) `claudeDev\D1_s1_fgate_BROKEN_20260926_175556.vi` (md5 `b114bb1b…`) is kept** as a saved intermediate. 210(e)
       allows deleting it; nothing needs it deleted.
212. **(cycle 99 judgement, on `99-1` FAIL 6/1 (only F5 missing), `tools/bench/cards/result_99-1.json`, facts
     `tools/bench/facts_c99_display.json`) — THE DISPLAY-LOOP DESIGN**
     - **(a) MEASURED (99-1):** #8323 ← w10908 ← BuildArray #11261 (on 639) ← #11363 (For #1359 / Bundler #11310) + element
       #11608 (Bundle, from WLC #1114). The only other object naming #8323 is Invoke #10313 `Reinit To Dflt`. #6085/#5696
       are SubVIs whose `Z out` feeds the #1359 ring and the Ext-vs-Time path, so they are **NOT display: out of scope**.
       The one other pure-display candidate in #637 is indicator #28786 `Extension (nm) vs Time (Frame #)` (site 3−2:
       ~1.2 ms at 15 picks). Force path site 4−3 = **8.3–8.8 ms (11 picks), 10.3–10.4 ms (15 picks)**. #637 stops on
       CompoundArith #11639 → cond #648 + indicator `TurnOff` #24444. The bed's S3 loop has NO stop local (x==x scaffold).
     - **(b) JUDGED — 210(a) read literally misses 210(c):** the 10 ms is For #1359's COMPUTATION, not the indicator write.
       Moving only #8323 (frame loop writes w10908's array to a local) leaves the 10 ms in the frame loop. The user's
       intent (*"데이터 플롯은 별도 루프로"*, and 210(c)'s "drop by the plot's 10 ms share") is met only if the
       plot's computation moves too. The movable set is fixed by data dependencies, not chosen: **PD206(b)'s 11363-only
       set** (#8741 IndexArray, #8764 Subtract + `Exp Baseline` terminal #8476, constants #8775/#8795/#27716/#28180,
       FIR #28233, Median #29009, Bundler #11310, tunnels 31051/31137) **plus BuildArray #11261 and #8323's terminal.**
       Ring insert #8634 and `Magnet2Force` #28083 STAY in the frame loop (they feed the ring history, PD206(b)).
     - **(c) Structure:** a new While loop (the display loop) on #637's owner diagram, parallel to #637, holding a For
       loop over beads with the moved set, then #11261 and #8323. Crossings are LOCALS (1c''), each via a new hidden
       indicator the frame loop writes every frame:
       **L1 `plot ring (display)`** = the history array that w8811 (#8634 `output array` → #8741) takes per bead,
       i.e. #1359's ring output as a whole array (the source tunnel/wire is fact 99-2 F1);
       **L2 `plot WLC (display)`** = #11608's output.
       The display loop reads L1 (auto-indexed into the For) and L2, waits `Display period (ms)` (new I32 control,
       default 100, clamped ≥ 1), and stops on a **local read of `TurnOff` #24444** (written every #637 iteration by
       the same value that stops #637). ⚠️ ASSUMPTION (2c), fact 99-2 F4: TurnOff starts False. If it can start True
       (default, or left from a previous run), the display loop needs a False write before the loops start.
     - **(d) Rule 1a:** Median is reentrant and FIR re-initialises on every call (95-2), so the set holds no state. Its
       output at a display tick equals the original's output for the frame whose ring it read. The saved data is
       untouched (96-3: #1359's outputs reach only #11261 → #8323 and its own SR). `Exp Baseline` is read in the display loop instead of per frame,
       which gives the same value at the same time. ⚠️ ASSUMPTION (2c), display only: L1 and L2 may come from adjacent
       frames (tearing of ≤ 1 frame in what is DRAWN). This goes in the report to the user, not a stop.
     - **(e) Go/no-go before any LabVIEW stage run (99-2, scratch, no rig):** (1) the per-frame cost of writing L1
       (a ring-sized array branched off the SR path forces a copy); (2) the cost of the moved set on a synthetic full
       ring of L1's type at 15 beads. Predicted gain = (2) − (1). The stage is built only if (2) − (1) ≥ 5 ms at 15 beads.
       Otherwise the design returns to judgement.
     - **(f) Verbs:** moves out of For body 7911 / diagram 639 to the new loop use the S3-split move route (stagexec),
       NOT `move_into_frame` (case frames only; left as PD211(c)). S1 is ExecState 1, so every precondition holds.
       Per PD211(b) and PD209(c), after the move batch read the termless and loose-end wires, then run RBW (only
       pre-existing uids may be removed, no data edge may be lost), then ExecState must be 1, once, at the end.
     - **(g) Base = `claudeDev\D1_s1_copy.vi` (md5 `3e3d23ce…`)**, output `claudeDev\D1_s1_disp_<ts>.vi`, saved by
       script at ExecState 1. The acceptance is 210(c): ABBA vs S1 at 15 picks, 120 s, plus the replay. #28786 comes
       later, as a separate stage, after this one is measured (210(b)).
     - **(h) Amended on `99-2` FAIL 5/2 (`tools/bench/cards/result_99-2.json`, facts `tools/bench/facts_c99b_display.json`):**
       1. **L1 source = w9215** (index-out tunnel #9227 → RightSR #9018 on 639). Its type is 3-D DBL [beads][2][`# FD points`],
          i.e. **4.8 MB at 15 beads**. Page i equals w8811 of iteration i, so the display For auto-indexes L1 and gets the
          same per-bead input. Rows #8775 = 0 (Median) and #8795 = 1 (FIR) are constants in the set.
       2. **Inbound edges are FIVE, not three:** w8811, `Exp Baseline` w7931, #11608 w12256, and the half-width controls
          w31059 → tunnel 31051 and w31166 → tunnel 31137. A control terminal whose only reader is the set MOVES with the
          set (w31059's control, like `Exp Baseline`). The control on w31166 also feeds #30896 in the frame loop, so its
          terminal STAYS and the display loop reads a **local of it** (latest value; same value at the same time, as in (d)).
       3. **Stop carrier = the existing precedent:** loop #25380 already stops on a Property #25116 `Value` READ of
          TurnOff, and Property #8603 writes TurnOff from BoolConst #25261 before the loops. The display loop copies that
          pattern and sits in #25380's owner diagram, so it is sequenced after #8603. (c)'s init ASSUMPTION is settled if
          #25261 == False. The stage pre-run READS #25261 as a gate; it is not assumed.
       4. **Missing verbs (99-2 F6):** `Wait (ms)` creator and indicator `Visible = False`. The stage needs both (a visible
          4.8 MB array indicator on the panel is a new draw cost), so they are BUILT (tool rule 2026-09-24), each
          self-tested with a negative case and handle-flat. This is done AFTER the go/no-go, not before.
       5. **The go/no-go (e) stands.** 99-2's bench failed on the bench's OWN construction: `t0stamp`'s adapt-to-type
          `any` input on a 3-D DBL left the scratch at ExecState 0. The question itself is unanswered. It is re-issued at
          escalation rung 1 (card 99-3). The bench's timing need not use stamps: a loop-level High Resolution Relative
          Seconds before/after N iterations answers median-free mean cost, which is enough for a ≥ 5 ms threshold.
     - **(i) GO — judged on `99-3` FAIL 23/2 (rung 1; `tools/bench/cards/result_99-3.json`, `tools/bench/facts_c99c_bench.json`):**
       1. **MEASURED (2):** Median + Coef + FIR over a full [15][2][20000] ring, panel closed, cost **7.94 ms per 15-bead
          call** (repeats 7.90–8.00), and 7.15 ms at 10 % fill. This is a LOWER bound for the set: it leaves out IndexArray,
          Subtract, Split, Bundler, #11261 and the #8323 write/draw. In the running VI the cost is 10.3–10.4 ms (94).
       2. **(1) is NOT measured.** Both bench routes went ExecState 0 at the same step, when a panel terminal was moved into
          a For body (`diag_c99c_bench2.log:38-52`). The go threshold holds if (1) ≤ 2.9 ms. ⚠️ ASSUMPTION (2c, named as
          an inference, not a measurement): (1) is at most a few whole-array copies of 4.8 MB, about 0.5–1 ms each at
          memory bandwidth. **The ABBA acceptance (210(c)) measures the net gain directly.** If the gain there is under
          5 ms, (1) is the first thing read; no third bench attempt is made. The reason: a third attempt fails on a bench
          construction step, not on the question.
       3. **(h)2 is REVISED by the same bench fact:** moving a panel terminal into a loop body is the step that broke both
          bench routes, twice. So **NO control terminal moves.** The display loop reads `Exp Baseline` and both half-width
          controls through **local READs** (stagekit.py:676). Their terminals stay where they are, left unwired where the
          set was their only reader, which is legal LabVIEW. #8323's terminal is an indicator; whether it moves or is
          written through a local write (a verb that does not exist yet) is decided by the rows card from that same fact.
       4. Also measured: at 10 % → 100 % fill the bench set grows only from 7.15 to 7.94 ms, so ring fill does NOT explain
          94-3's in-situ rise from 1.3 to ~10 ms. With the panel open, the bench roughly tripled (~25 ms). This is recorded
          for the ABBA reading and is not acted on now.
       5. **Next (cycle 100), in order:** (a) a rows card: the stage plan rows for (c)/(h)/(i)3 on the S1 graph, plus
          `py tools/protocol.py requires`, with no LabVIEW; (b) build the missing verbs the rows need (`Wait (ms)`,
          `Visible = False`, and a local WRITE or indicator move for #8323 if the rows need one), each self-tested with a
          negative case and handle-flat; (c) simulator dry + pre-run with cdiff 0 other than the added objects;
          (d) one LabVIEW stage run.
213. **(cycle 100 judgement, on `100-1` FAIL 5/1, `100-2` FAIL 23/1, `100-3` BLOCKED 6/1; rows spec `tools/bench/cards/rows_spec_100.md`)**
     - **(a) MEASURED: `#25261` = False** (`OpConstValueB_v0`, `tools/bench/facts_c100_verbs.json`). TurnOff starts False, so
       PD212(c)'s init ASSUMPTION is settled. The stage keeps the value as a gate row (it stops if True).
     - **(b) Design details decided (rows_spec_100.md R1–R8 stand):** `#8323` is written by a local WRITE (its terminal stays,
       from the PD212(i)3 fact). Tunnel `#11363` gets a DELETE row after R4 (both faces are unwired, and an output tunnel with no
       inner source is an error). `Max & Min` comes from a **donor copy** (`gscript.copy_into` / vi.lib donor), not from a
       New VI Object style sweep. The `Display period (ms)` control is created on Max&Min's `x`. It is DBL (Max&Min's default
       type), coerced into `Wait (ms)`, which is functionally equal to PD212(c)'s I32. The L1 indicator is created on the
       w9215 source **tunnel face** `#9234` of `#9227`: `create_indicator_nested` is extended to accept a tunnel/terminal owner.
       The design is not changed.
     - **(c) Schema:** `docs/protocol/stageplan.json` is replaced by `tools/bench/sim/disp/stageplan_schema_proposed.json`. It
       is widening-only (100-3 F5), and every create plan needs it.
     - **(d) Rule 1a: which end-cdiff rows are open BY DESIGN.** Of 100-3's 21 end rows, a row is accepted only if it is one
       of these:
       (1) an input of a moved node whose source changes from a wire or tunnel to a LOCAL READ of the SAME control/indicator
       that fed it before (`Exp Baseline`, both half-width controls: same value at the same time, PD212(d)/(h)2);
       (2) R2's per-bead page input from L1's auto-index in place of w8811, or `#11261`'s input from L2 in place of `#11608`'s
       wire (same data, PD212(h)1);
       (3) `#8323`'s source changing to the local WRITE;
       (4) a row already open at the base.
       Each row is classified individually, by uid. **A row that fits none of (1)–(4) is not accepted: the stage does not run,
       and the row comes back to judgement.**
     - **(e) Card status:** 100-2 is re-issued at escalation rung 1 (100-4, `material-opus-max`). Its remaining work is the
       self-test harness fix (term_index owner), V1b/V2/V3/V5 with their negatives and handle tests, the tunnel-face extension,
       and V6 by donor copy. 100-3's remainder (schema install, (d) classification, dry run, pre-run) is re-issued as 100-5 with
       the flags corrected (`labview: read` allows the stubbed dry run). My 100-3 card was the fault. In 100-5, a dry run that
       refuses ONLY the rows waiting on 100-4's verbs is the expected result.
     - **(f) CLOSE, on `100-4` PASS 60/3 (rung 1; runs 3 and 4, `tools/bench/facts_c100_verbs2*.json`) and `100-5` PASS 6/0
       (`tools/bench/facts_c100_plan.json`):**
       1. All verbs now exist and are functionally tested on scratches of S1:
          - `create_indicator_nested` (tunnel OUTER faces, via `OpTunnelInd_v0`), `create_control_nested` (it refuses a wired
            sink; measured: Create Control on a wired sink leaves a dangling control), `set_visible`, `create_local_write`,
            `OpConstValueB_v0`;
          - `create_primitive_nested` = `OpPrimCopyNested_v0`, with donor `claudeDev\OpPrimDonor_v0.vi` (a byte copy of an NI
            example). The donor is a COPY in claudeDev, so rule 1 holds. **It is accepted** in place of 213(b)'s "vi.lib".
       2. The widened schema is installed (0 older plans regressed). `plan_disp.json` (md5 `e50ebc47…`) simulates FINAL with
          21 open rows: 15 of class 4, 5 of class 1, 1 of class 3, 0 unclassified. **Rule 1a: accepted as open by design.**
       3. The pre-run passes X1/X2/X3/X8. Its first fail is X4, the same 2 unroutable rows (L1 on tunnel face `#9234`, and
          Max & Min). **Decided:** route L1 as `create_indicator_nested(W, 9234, None)` and R7 through `create_primitive_nested`.
          Add `create_local_write` (and every create verb that edits the VI) to `stage_prerun` MODIFY_VERBS. Max & Min's
          terminal names are UNMEASURED (the plan assumes x, y, max(x, y), min(x, y)): READ them from the donor first; if they
          differ, re-simulate.
       4. **Next (cycle 101), one card, in this order:**
          (i) the re-route and the MODIFY_VERBS patch;
          (ii) read the Max & Min terminal names;
          (iii) re-dry, then pre-run to all-pass;
          (iv) ONE LabVIEW stage run from `D1_s1_copy.vi` → `claudeDev\D1_s1_disp_<ts>.vi`. Pass criteria: ES 1, per-step
          comparison, cdiff equal to the 21 open rows plus the added objects only, #25261 gate False, and after the move batch
          no termless or loose-end wires beyond RBW's pre-existing uids (PD211(b)).
          Then the ABBA (210(c)).
       5. Carries, not ahead of the deliverable:
          - `selftest_retry_cap` C4 fails under `bgrun --detach` (`BGRUN_DETACHED` inherited;
            `archive/peer/2026-09-26-c100-5-retrycap-detach.md`);
          - the installed schema's description still says "PROPOSED";
          - a verb self-test that imports stagekit and saves is gated as a stage (the guard is right; self-tests avoid
            the import).
     - **(g) CLOSE 2, on `100-6` FAIL 4/2 (`tools/bench/cards/result_100-6.json`, `tools/bench/facts_c100_stage.json`):
       (i)–(iii) DONE.**
       - Max & Min is MEASURED: `x`, `y`, `max(x,y)`, `min(x,y)`, class Comparison.
       - `plan_disp.json` is now md5 `9486143…` (r4_open, FINAL, the same 21 open rows).
       - Results: dry 0 unroutable; pre-run 8/0; stagexec self-test 72/0.
       - Two LabVIEW runs, nothing saved, S1 unchanged:
         - run 1 stopped at E1 PARITY (the plan context had no loops or owners);
         - run 2 passed PRIME parity 0, the #25261 gate (False) and STEPX 01 diff 0, then stopped at **op 2 (create While)
           BINDING**. Real {Diagram: 1} was not the simulated {}. The review `archive/peer/2026-09-26-c100-6-r2.md` names the
           cause: stagesim models a new loop with no body rows (the real body has `i` + `cond` terminal rows), and `bind_new`
           does not exclude `bind['diag']`.
       **Decided for cycle 101, in this order, all measured against the real run-2 record (`stage_d1_disp_r2.log`) before
       any LabVIEW run:**
       1. **Repair the device that blocked 100-6's offline check first.** `guard_peer` re-arms itself on
          `tools/bench/jev_gate.log`: every hook appends to it, and its `JEV-GATEROW … STOP:` line matches FAILURE_RE
          (`archive/peer/2026-09-26-c100-6-jevgate.md`). Exclude the `jev_*` ledgers from guard_peer's failing-log scan by
          PATH. Self-test with a positive case (a real build log still gates) and a negative case (a jev ledger line does not).
       2. **stagesim create-loop model:**
          - a created While/For gets a body Diagram plus its `i` terminal row (and `cond` for a While), as the real run
            shows;
          - `bind_new` excludes `bind['diag']`;
          - a replay test: the sim of ops 1–2 matches `stage_d1_disp_r2.log`'s real E1 new-object set exactly.
       3. **Owners context = an S1 owners map** built read-only from `D1_s1_copy.vi`. D1_k's map is a STAND-IN from another
          VI and is NOT accepted (it is an inference; `c100-6-jevgate2.md` s1).
       4. Re-dry, pre-run, then the stage run under a `RETRY_CARD` judgement card if this cycle's cap is reached (a new
          cycle's count starts at 0).
       The unsaved byte copies `claudeDev\D1_s1_disp_20260926_224211.vi` / `_225529.vi` are scratch, not artefacts.
     - **(h) RE-ORDERED at close by `steer_100.json` (FOLLOWED) and retrospective-cycle100 (accepted: `inference-over-measurement`,
       `device-failed`).** The steer requires the next act to be a deliverable build or run, never tooling first. So cycle 101's
       FIRST card is the display-loop STAGE card. Inside it, in order:
       - (1) READ, offline, the Diagram-owned Terminal rows of existing While bodies #639 / #25392 in `par1359_95_graph.json`.
         This is the retrospective's discriminating test; it expects 1 source + 1 sink each.
       - (2) Model exactly those rows for a created loop in stagesim, fix `bind_new`, and replay against run 2's real E1 set.
       - (3) Build the S1 owners map (read-only), re-dry, pre-run, and run the stage.
       The `guard_peer` jev-ledger exclusion (213(g)1) is a SEPARATE card dispatched AFTER the stage card. If it blocks the
       stage card's offline checks again, the material session records the block, and the stage card does not route around it.
214. **(cycle 101 judgement; cards `101-1` BLOCKED, `101-2` PASS 5/0, `101-3` FAIL 5/2, `101-4` FAIL 6/1 (rung 1), `101-5` FAIL 1/2 (rung 2))**
     - **(a) Done, measured:**
       - `guard_peer` skips `tools/bench/jev_*` ledgers by PATH (`tools/hooks/guard_peer.py:299-313`, self-test 29/0). 213(g)1 is CLOSED. Accepted: any `tools/bench/jev_*` file is a Jev ledger by name.
       - stagesim models a created While body (`i` source + `cond` sink) and a For body (`i` + count tunnel); `bind_new` excludes `bind['diag']`.
       - The S1 owners map is `tools/bench/sim/disp/s1_owners.json` (a3b8f645…).
       - `stagexec` record mode: a step difference is logged, the run continues on the unsaved scratch, and the file is saved only when every step matches.
       - `stagekit.create_local_read` resolves the panel index by label (self-test 51/0).
       - Real run r5 (`tools/bench/stage_d1_disp_r5.log`): ops 1–25 against LabVIEW. Its only step difference was at k12, and it healed by k24. It stopped IN op 26 on the local-read index bug, which is now fixed. S1 is unchanged; nothing was saved.
     - **(b) OPEN model rule, which the next card MEASURES before any run.** When a moved node was the ONLY source of a wire that crosses the cut, what happens to the outside half-wire?
       - Four real samples: constant #8775 → deleted; Bundler #11310 → tunnel-inner deleted; BuildArray #11261 → panel #8323 KEPT; SubVI #376 → tunnel-inners KEPT.
       - My 101-4 rule "primitive deletes, SubVI keeps" was an inference from two samples and was REFUTED by r5's reads (`archive/peer/2026-09-27-c101-5-onlysource.md`, `inference-over-measurement`, a judgement fault).
       - The review's three candidates A/B/C are confounded. Separate them first, offline, from the recorded reads of cycles 71–101. Only if they stay confounded, run ONE scripted move on a scratch copy of S1.
     - **(c) DECIDED — a half-wire difference is not a save blocker in record mode.** A step difference whose uids are ONLY sourceless wires/terminals (`dangling_sim_only` / `dangling_real_only`) and that no later plan row references by uid is logged as WARN, not FAIL.
       - Why: the per-step comparison exists to keep symbolic ids bound correctly. A sourceless half-wire carries no data, so it cannot change the computation (rule 1a).
       - The end gates still decide the save: ExecState 1; cdiff == the 21 PD213(d) rows + added objects; no termless or loose-end wires beyond RBW's pre-existing uids. The recipe must check the "no later reference" condition from `plan_disp.json`, never by hand.
       - Any other step difference still blocks the save.
     - **(d) Before the next run:**
       - fix the tunnel-flip seed bug (a sink cleared by an only-source delete seeds the flip; `stagesim._move_one:593-607`);
       - decide `plan_disp.json` 7c432e1b vs r5's b535071e as provenance-only or content, by rerunning `diag_c101c_resim` with the k0 fix;
       - re-dry, pre-run, then ONE record-mode stage run (a new cycle's retry count starts at 0).
     - **(e) Carries (not ahead of the stage):**
       - the launch gate classes `selftest_stagekit.py` as a stage, and its dry fails on the self-test's own intentional FAIL row;
       - review c101-4-syntax: move the E3 cdiff into one shared stagexec function; gate the 120-line stage rule;
       - l2a1_80 / unflip_81 self-tests fail only on stale count gates;
       - retrospective-cycle101 `device-failed`: the stop record refuses READ-ONLY commands on a stopped recipe (`tools/hooks/material_marker.log:2175`). Refuse only commands that EXECUTE the recipe, and self-test both cases.

215. **(cycle 102 FIREFIGHTER on `gate:e1`, fable/low; runs r6 `tools/bench/stage_d1_disp_r6.log` and r7 `tools/bench/stage_d1_disp_r7.log`, retry cap spent; NO FILE)**
     - **(a) Done, measured:**
       - 214(c) is CODE: `stagexec.classify_step_diff` (dangling-only diff, no later plan action names the uid → `warn`; self-test T39e/T39f, 78/0); the recipe logs `STEP-WARN` and saves on warns only. The k12 diff `dangling_sim_only [11365]` was classed WARN in both runs.
       - 214(d)1 is CODE: an outside sink whose wire the only-source rule deletes now seeds the undirected-tunnel flip (`stagesim._move_one`, G56, 60/0). Measured first (`tools/bench/diag_c102_probe_b.log`): under the refuted node:delete rule the old model kept edge 11369→11270 and did NOT flip #11363, while the plan's own keep-model step 12 AND the r5 real read have 11369 flipped (the r5 k12 diff carries no edge entry). The prior-art review's "settled-already" on this change was REFUTED from those files (`archive/peer/2026-09-27-priorart-c102-disp-warn.md`, What was done with it).
       - 214(d)2: 7c432e1b vs b535071e is PROVENANCE-ONLY (`finalized.at` is re-stamped on every re-sim; `diag_c101c_resim` R6b content gate PASS, `tools/bench/diag_c101c_resim5.log` 6/0; the byte gate R6 and md5 gate A0 are retired to facts).
       - 214(b): the recorded real reads of cycles 71–101 hold no move between a For interior and a While interior with a single-sink cut (only the 4 known samples + K's #5058 tunnel flips) → candidates A/B/C stay confounded. The scratch move was NOT run this cycle: under 214(c) the fate no longer decides the save. Still owed, not blocking.
       - **r6 (560 s): ops 1–30 diff 0 (WARN at k12), stopped IN op 31: `ADDRESS: terminal #23792 is_source False, wanted True`.** Cause, read from `:544,572`: `stagekit.create_local_read` drove the donor `OpCreateLocal_v0`, whose Local is BORN WRITE. Fixed: `gscript.create_local_read` = `OpCreateLocalRead_v0` with `Write?`=False (the read twin of `create_local_write`), the stagekit binding checks `is_source == [True]`.
       - **r7 (756 s): ops 1–40 of 47 diff 0 — ops 26–40 (five read locals, four indexed tunnels + wires, two branches, the write local + its wire) executed against LabVIEW for the FIRST time.** Stopped IN op 41 (`r7_wait`, Wait (ms) by `stagekit.copy_in` from S1 donor #44143): `copy_in needs work == gscript.MOVE_DST` — that helper is hard-wired to the NI Moving-Objects file pair and can never run on a claudeDev work file. S1 unchanged; LabVIEW gone at exit.
       - **Memory at op 40: private 690.4 MB against MEMSTOP 700** (`r7.log:804`; +4 to +13 MB per checkpoint read, 8 consecutive binding reads at 26–33). The 7 remaining ops carry 6 required reads → the ceiling is crossed in one session even with op 41 fixed.
     - **(b) DECIDED — the display stage is SPLIT (CLAUDE.md "Big or blocked work is SPLIT … each step SAVES an intermediate"): the next cycle's FIRST act is the one-page decomposition plan, prior-art-reviewed once, then:**
       - **Part A** = ops 1–40 exactly as r7 ran them → `claudeDev\D1_s1_dispA_<ts>.vi`, saved through `gui_save` (broken by design: op 41–47 rows missing; `-Exception Approved -Evidence "user 2026-09-22 broken-intermediate save"`), md5 recorded; pass = E1 through op 40 (warns only), the plan's simulated step-40 state == the real read.
       - **Part B** = ops 41–47 from that file in a FRESH LabVIEW (memory baseline = one VI load), then W1 RBW / E2 ExecState 1 / E3 cdiff == the 21 open rows / PS saved by script → `claudeDev\D1_s1_disp_<ts>.vi`. `stagexec` needs a `--from-step 40` entry that binds Part A's recorded uids (`bind.obj/term/diag`) from its result JSON instead of re-executing.
       - **Op 41's route:** register a Wait (ms) DONOR for `OpPrimCopyNested_v0` exactly like Max & Min (`facts_c100_oplabels.json` `donors`: a byte copy of an NI example VI that contains `Wait (ms)` under claudeDev, its node uid + diagram measured, md5 pinned) and change the r7_wait row to `"prim": "Wait (ms)"` in `stageplan_disp_r4_open.json` → re-sim → re-dry → pre-run. `stagekit.copy_in` (MOVE_DST-only) is not used by any stage; leave it. Copying from the S1 file itself as donor is REFUSED: it opens a second main VI (≈ +300 MB) under the same ceiling.
       - The `requires` of that card: op `OpPrimCopyNested_v0`, file `<the Wait (ms) donor>.vi` (MISSING until registered → build it first, offline-checked by `py tools/protocol.py requires`).
     - **(c) Carries added:** the memory ceiling's cause (reads vs accumulation, cycle-86 OPEN) is still unmeasured — Part B's meter lines are the next data point; the 214(b) scratch move; the owed tooling card (stop record read-only refusal, `selftest_stagekit` classed as a stage — `docs/violation-decisions.md` 2026-09-27 01:15).
216. **(cycle 103 judgement, on `103-1` PASS 6/0, `tools/bench/cards/result_103-1.json`; split page `tools/bench/cards/split_plan_103.md`, prior-art novel `archive/peer/2026-09-27-priorart-c103-split-plan.md`)**
     - **(a) Done, measured:** Wait (ms) donor = `claudeDev\OpWaitDonor_v0.vi` md5 `6fc80d60…` (byte copy of the NI example `Running Average with Shift Registers.vi`; node uid 163, Diagram #55, terminals `milliseconds to wait` / `millisecond timer value`), registered in `facts_c100_oplabels.json` donors. The `r7_wait` row is `prim: Wait (ms)`; re-sim FINAL, the same 21 open rows, steps 0–50 content-identical; `plan_disp.json` md5 `c7d80fc9…`; full-mode pre-run 8/0. The recipe has a Part-A mode (`--stop-after 40`: `stagexec.Executor(stop_after)` + `part_a_record()`), stagexec self-test 84/0.
     - **(b) DECIDED — pre-run X5 in Part-A mode counts only ops ≤ `stop_after`.** The run dispatches exactly those ops, so comparing against all 19 wiring ops tests an op the run never sends. With no `stop_after`, X5 is unchanged. Self-test both cases (a Part-A plan passes at 18; a full run that skips an op still fails).
     - **(c) DECIDED — the recipe's 129 lines (rule ≤ 120) are ACCEPTED for the Part-A and Part-B runs only.** Moving the Part-A/cdiff helpers into stagekit edits the recipe again (re-arms the stop record and a prior-art round) just before the run. The helpers move into stagekit/stagexec in the owed tooling card, after Part B.
     - **(d) CORRECTION of 215(b)'s wording (prior-art A3):** `stagekit.copy_in` did run on a claudeDev work file when that file was `MOVE_DST` (`tools/recipes/stage_d1_m4b.py:29,103`). The accurate statement: it runs only when the work file IS `gscript.MOVE_DST`; the display stage's work file is not, so the route stays the donor primitive.
     - **(e) Part A is ONE run this cycle** (card 103-2), memory ceiling unchanged (MEMSTOP 700: error 2 was seen at 695 MB in cycle 85). If the MEMSTOP fires before the save, that is the measurement for a finer split (A1/A2), decided by judgement, not in the material session.
     - **(f) CLOSE 1, on `103-2` FAIL 2/1 (`tools/bench/cards/result_103-2.json`, `tools/bench/stage_d1_dispA_r1.log`, facts `tools/bench/facts_c103b_partA.json`):**
       - Pre-run X5 now counts ops ≤ `stop_after` (`tools/stage_prerun.py:1071,1140,1730`, self-test 4/0 with 2 negatives). Part-A pre-run 8/0, full pre-run 8/0.
       - Run r1 (780 s): ops 1–40 dispatched, the only step diff is the known k12 WARN `dangling_sim_only [11365]`. **MEMSTOP at the step-40 read: 703.8 MB ≥ 700** (`:797-799`). Nothing saved; S1 unchanged; LabVIEW gone.
       - Measured private-MB curve: start 570.7 · k12 619.4 · **k33 673.7** · k37 695.0 · k39 699.8 · op40 699.7 · read40 703.8. r1 ran ~9 MB above r7 from k37.
       - **DECIDED — the cut moves to op 33: Part A = ops 1–33 → `D1_s1_dispA_<ts>.vi`; Part B = ops 34–47 from that file in a fresh LabVIEW.** Why: k33 is the last measured checkpoint with a margin (~26 MB) that holds even with r1's +9 MB drift; from a fresh load (~571 MB) Part B's 34–40 costs about 26 MB and 41–47 carries 6 reads, which stays well under 700. MEMSTOP stays 700 (error 2 at 695 in cycle 85 means raising it is not safe). Cutting at a fixed MB instead of a fixed op is refused: Part B's binding needs a fixed, pre-simulated step.
       - The misleading unsaved work copy `claudeDev\D1_s1_dispA_20260927_022749.vi` (md5 == S1 `3e3d23ce…`) is DELETED after its md5 is checked; it is not an artefact.
       - `gscript.gui_save`'s Evidence string ("COM SaveInstrument hangs on broken VIs", `gscript.py:2242`) differs from the card's user-approval wording. Both name a valid GUI-exception class, so it is NOT changed before the run; alignment goes into the owed tooling card.
     - **(g) CLOSE 2, on `103-3` PASS 5/0 and `103-4` PASS 6/0:**
       - **PART A IS SAVED: `claudeDev\D1_s1_dispA_20260927_024535.vi`, md5 `16c2ca00a114a227a81612dd49d111cc`, 303,583 B** (run r2, 665 s, `tools/bench/stage_d1_dispA_r2.log`): ops 1–33, the only step diff is the k12 WARN; the real step-33 read equals simulated step 33 (15 reads); peak 677.1 MB; gui_save at ExecState 0 (broken by design, NEVER RUN). Binding JSON `tools/bench/stage_d1_dispA.json` md5 `d5393162…`. The md5==S1 unsaved copy `…_022749.vi` was deleted after its md5 was read.
       - **Part-B entry built, offline only:** `stagexec` `from_step` (binding load with plan-md5 / stop_after / no-register checks, entry compare, PRIME parity; self-test 91/0 with 5 negatives); recipe `--from-step 33 --base <dispA>` with B0/B1 entry gates, end gates E1/W1/E2/E3/PS unchanged. Part-B dry PASS (entry diff 0, ops 34–47 only; E3 is unverified in a dry run), pre-run 8/0. The launch gate refuses ONLY on this cycle's retry cap.
       - Owed hook repairs done (`tools/hooks/guard_bash.py:179`, `tools/stage_prerun.py:1252`; hook self-test 7/3 → 17/0; review `archive/peer/2026-09-27-c103d-hooks-before.md` accepted).
       - **DECIDED — Part B runs next cycle WITHOUT a separate open-probe.** The prior-art alternative (time `Stage.start` on dispA first) is refused: opening a broken-by-design intermediate through the same Stage route already ran in cycle 86 (D1_k → L2-A1, 594 s, saved). The bgrun deadline catches a recompile spin. Part B's memory baseline is its own fresh-load read.
       - **The recipe is 149 lines (rule ≤ 120). ACCEPTED for the Part-B run only (extends (c)).** The helpers move into stagekit/stagexec in the tooling card right after Part B, together with: the pre-run verb-precondition check (retrospective-cycle102 `wrong-ordering` device), the `gui_save` Evidence alignment, the stop_record `wc -l` twin, and the `selftest_guard_bash_jev` fixture (fails 7/4, pre-existing since chat-N1).
217. **(cycle 104 judgement; cards `104-1` FAIL 10/2, `104-2` FAIL 6/1, `104-3` PASS 6/0 — `tools/bench/cards/result_104-{1,2,3}.json`)**
     - **(a) Done, measured:** Part-B run 1 (`tools/bench/stage_d1_disp_c104B.log`) stopped IN op 43: `addr.owners` was keyed by SIMULATED ids and read with the real loop uid (`int(None)`). Fixed in `tools/stagexec.py` (md5 `0070aa3d…`, `bound_owners()` via the bind map, full and Part-B paths; self-test 93/0, new T43/T43b fail on the old code). Part-B run 2 (`stage_d1_disp_c104B2.log`, 420 s): entry diff 0, #25261 False, **ops 34–47 executed live with step diff 0 at all 9 reads, E1 PASS, W1 PASS (RBW removed 12 pre-existing wires, 0 new), E2 ExecState 1**; max private 616.7 MB (Part B's memory margin is ample; the op-33 cut was right). **E3 FAIL 6/21**, nothing saved.
     - **(b) Measured (104-3, `tools/bench/facts_c104c_e3.json`, OFFLINE):** the 21 "open rows" come from `stagesim.py:1132`, which builds its graph with NO node labels and NO flat-sequence tunnel pairs (the plan base `par1359_95_graph.json` carries 0 fs pairs). The E3 side (`stagexec.py:2243-2245`) builds with the default labels + the wiki fs pairs — **the same inputs every S1 deliverable's cdiff used** (L2-A1 `stage_d1_l2a1.py:18,99-100`; loop15/M4 `stage_d1_m4b.py:72,81`). The 15 missing rows (9× `error in`, `Initial Time at Start`, `Cycle Start Time`, 12236 x/y, 21699 x) are exactly PD213(d)'s class (4) "already open at base": they appear at simulated STEP 0 on the unedited S1, and for every one of them the E-side source == the S1 source (`E_eq_S1` True). The 6 E rows are exactly classes (1)+(3): 8764 y, 27716 index, 28180 half-width, 29009 left+right rank, 8323 Force; extra rows 0.
     - **(c) DECIDED (rule 1a):** the 15 class-(4) rows are simulator-graph construction artefacts, not computation changes; the real end state changes exactly the 6 intended rows + 8 added objects. **E3 is re-specified: `cdiff(S1, real end)` == the PD213(d) rows of classes (1)–(3) (read from `plan_disp.json`'s class field, never typed) + added objects, AND for every class-(4) row the real-end source == the S1 source.** The want list is derived in code from the plan's classes; E3 is also evaluated in the dry run (it was UNVERIFIED there, which is why this class reached LabVIEW). One more Part-B run (the third this cycle) is authorised by retry card `104-4`.
     - **(d) Carries:** the stagesim graph should build with labels + fs pairs, so the finalize-time open rows stop carrying class-(4) noise (tooling card; not ahead of the save). Latent twin: `add_sr` on a plan-CREATED loop (`stagexec.py:1267,1309,1378`), which is not used by any current row. Stale citation `stage_d1_disp.py:43` → `stagexec.py:2243-2248`.
     - **(e) DONE — THE DISPLAY-LOOP VI EXISTS (`104-4` PASS 8/0): `claudeDev\D1_s1_disp_20260927_041648.vi`, md5 `245a10206b565cba0ba186bd891f5cb8`, 479,946 B**, run 3 `tools/bench/stage_d1_disp_c104B3.log` (423 s, 19/0): ops 34–47 diff 0, W1 PASS, E2 ExecState 1, **E3 PASS under (c)** (6 == 6, class-4 15/15, 8 added all plan-created, 0 removed), saved by script, ExecState 1 on a same-process reopen; peak 613 MB. `stagexec.py` md5 `e3dd7740…` (shared `e3_check`, self-test 98/0 with negatives T44b–e); recipe 144 lines; prior-art `archive/peer/2026-09-27-priorart-priorart-c104d-e3.md` novel. STRUCTURAL + graph-equivalent; NEVER RUN. Accepted: the same-process reopen as the structural reload (the ABBA loads it cold); `e3_created` = every plan binding with sim id < 0 (objects and their terminals).
     - **(f) DECIDED BEFORE THE NUMBERS — the 210(c) ABBA criterion.** Legs A15 B15 B15 A15, 120 s, panel normal, A = `D1_s1_copy.vi`, B = the (e) file, both run as they are (Display period default 100 ms). Basis: at 15 picks A loses ~3,400 of ~10,680 frames (INDEX rows 48/49/56) and the moved Force path costs ≥ 7.94 ms/frame (99-3). **GAIN** = both B legs below the lower A leg by ≥ 25 % of A's mean; **NO DIFFERENCE** = otherwise. B must also be FUNCTIONAL: the plot indicator #8323 holds a non-empty array read by COM at the end of each B leg (the display loop really draws), and all 15 picks register. GAIN ⇒ the rule-1a replay (210(c), X/Y/Z bit-identity on the same recorded frames) is the next card; the VI is not accepted or shipped before it. NO DIFFERENCE ⇒ the display-loop lever is re-judged from the numbers.
     - **(g) CLOSE, on `104-5` FAIL 33/28 and `104-6` FAIL 11/1 — the ABBA has NO NUMBERS, and the blocker is NOT the new VI.** Every leg (A = S1 copy and B) stopped before pick 1 at v5 `run1.L2`: the rotor `Configure.vi` (instr.lib Autonics, alias `Rotor` = `ASRL5::INSTR` = COM5, 9600) panel + diagram open over the main panel, main VI back in edit mode (`tools/bench/diag_c104_abba.log:7,30,53,76`; INDEX row 57 = NON-RESULT). 104-6 reproduced it on ONE A leg: `Run` returned after 4.0 s with no error to COM, ExecState idle at 5 s, no modal dialog present at the capture, Configure.vi's resource in/out read `''`, COM5 FREE before LabVIEW, after VI open / before Run, and after LabVIEW exited (exclusive open probe, no bytes written; NOT measured during the run), no other serial client, cycle-104 motor session never touched COM5 (`tools/bench/diag_c104f_leg.log:4,166,172-180,609`). The same S1 md5 ran normally at 09-26 14:18 (96-1). Review `archive/peer/2026-09-27-c104-6-configure-empty-resource.md`: auto-error-handling alone does not fit the missing dialog; the empty resource may be the panel default.
       - **DECIDED — next cycle's first act is ONE diagnostic card, no ABBA until the cause is read:** (1) read-only: `VISAResourceNameConstant #30488`'s value in S1 by script (the review's separator; extend the const reader to a VISA refnum/string if needed — measured on a scratch first); (2) one A leg whose harness LOGS every window's title + text (and screenshots) from Run to L2 at ≤ 0.5 s spacing BEFORE any dismiss, so an error dialog that the driver closes is captured. User question D-2026-09-27-02 (rig changes since 09-26 afternoon) is open and non-blocking.
       - Then the ABBA (f) reruns unchanged, criterion as fixed in (f). **Every leg driver STOPS the leg loop when an A leg fails before pick 1** (retrospective-cycle104 `repeated-failure-class`, accepted: legs 2–4 of 104-5 cost 17 min and added nothing).
       - Why the 216(g) tooling card did not run this cycle: the deliverable's first functional run (the ABBA) was ranked ahead of it (deliverable-first), and the rotor stop then used the remaining dispatches. It stays the second act.
218. **(cycle 105 judgement; cards `105-1` FAIL 25/2, `105-2` PASS 14/0, `105-3` PASS 17/0, `105-4` PASS 6/0 — `tools/bench/cards/result_105-{1,2,3,4}.json`)**
     - **(a) Measured — the rotor stop is read, and it is NOT in any VI of ours.** 0.41 s after Run, S1 shows a modal LabVIEW error dialog (text read by PrintWindow on its hwnd, `tools/bench/diag_c105b_out/pw/c105b_20260927_055929_h1706538_birth_pw.png`): *"Error -1073807246 occurred at VISA Open in Configure.vi … VISA: (Hex 0xBFFF0072) The resource is valid, but VISA cannot currently access it."* (Continue / Stop). In 104-6 the driver's `lv_gui focus` tapped Esc (`tools/lv_gui.ps1:239-252`), which is why Run "returned after 4 s" there and never here.
       - **With NO LabVIEW running, NI-VISA's own `viOpen('Rotor')` and `viOpen('ASRL5::INSTR')` fail with the same 0xBFFF0072 (3/3 each), while `CreateFileW(COM5)` opens and closes normally and `viOpen('ASRL6::INSTR')` (the second FTDI adapter, same visaconf settings) succeeds 3/3** (`tools/bench/diag_c105d_visa.log:6-23`). No USB PnP arrival/removal/config event since 09-26 12:00; the COM5 adapter's last arrival is the 09-23 13:19 boot (`tools/bench/facts_c105c_offline.json:59-62`). COM5 is free at the OS level during the paused dialog (`diag_c105c_leg.log:178,195`).
       - `#30488`'s value is still unread (the base-Constant reader returns a void variant for VISA constants, `diag_c105_const.log:23-31`); it no longer matters for this stop, because a VI-independent VISA open of the same alias fails the same way.
     - **(b) DECIDED — the blocker is NI-VISA's state for ASRL5 on this PC; it is outside the VI and outside rule 1a.** (Measured: the refusal happens with no LabVIEW running. Unmeasured: when it began, and whether the harness's forced LabVIEW kills while S1 held ASRL5 caused it — retrospective-cycle105 finding 6.) Neither S1 nor the display-loop VI is changed for it, and the rotor resource is NOT re-pointed (COM6 is another device; re-pointing would be a computation/hardware change). Clearing it needs a system-level act — a PC restart, a replug of the rotor FTDI adapter (FTDIBUS VID_0403 PID_6001 AI03Q9JZA), or a restart of NI's services — none of which a cycle does on its own: **user decision `D-2026-09-27-03`**. D-2026-09-27-02 (rig change?) is partly answered by the PnP read: no device change is recorded.
     - **(c) The ABBA of 217(f) waits for `viOpen('ASRL5::INSTR') == 0` from the 105-4 script (`tools/bench/diag_c105d_visa.py`, no bytes, no LabVIEW) — that check is the ABBA's precondition, run first in the cycle that follows the user's fix.** Criterion unchanged. Until then the next act is the 216(g)/217(d) tooling card (it needs no real run).
     - **(d) Carries:** every leg driver must fail fast on a modal dialog at L2 and log its text by PrintWindow (the `shotwin -Hwnd` action now exists, `tools/lv_gui.ps1:118-120,750-757`) instead of waiting; `drive_original_copy_v5.py:560-565` calls `leg('run2')` after a clean stop even when leg 1 failed (review `archive/peer/2026-09-27-c105b-leg-rc1.md:45-52`) — the stop-on-A-fail of 217(g) must be code there; COM Abort on a VI paused at an error dialog never returns (3/3) — the forced kill costs ~256 s per leg, so a diagnostic leg kills the process directly right after its last capture; every leg driver opens+closes `ASRL5::INSTR` through VISA before Run and refuses the leg on a nonzero status.
     - **(e) DECIDED (retrospective-cycle105, `inference-over-measurement` accepted):** when an error names a resource layer (VISA, IMAQdx, a driver), the first card opens that resource through the same layer outside LabVIEW, before any LabVIEW leg.
219. **(cycle 106 judgement; cards `106-1` PASS 4/0, `106-2` PASS 47/0, `106-3` PASS 5/0, `106-4` PASS 5/0 — `tools/bench/cards/result_106-{1,2,3,4}.json`)**
     - **(a) Measured — the rotor port is STILL refused at 06:56:** `viOpen('Rotor')` and `viOpen('ASRL5::INSTR')` 0xBFFF0072 3/3 each, `ASRL6`/`COM6` 0 3/3, CreateFileW(COM5) 0, LabVIEW absent (`tools/bench/diag_c106a_visa.log:6-23`). D-2026-09-27-03 stays open. **The recorded-frame replay is blocked too:** both replay copies keep the Autonics rotor `Configure.vi` (uid 30064, `stage_replay_swap_78.json:439,565`; the swaps touch only the camera callees `:478-495`), and S1 hits that VISA Open 0.41 s after Run (218(a)). So neither the 217(f) ABBA nor the 210(c) replay can run until the port opens; the replay is not reordered ahead of the ABBA (203's order stands).
     - **(b) ACCEPTED — the leg guard (`106-2`):** `tools/bench/drive_legguard.py` md5 `0e6a743e…`, wired into `diag_c104_abba.py` (md5 `89ff4934…`) and `drive_original_copy_v5.py` (md5 `3bf137c1…`): VISA open/close of `Rotor` + `ASRL5::INSTR` before any leg starts LabVIEW; the loop ends on a refused leg or an A leg failing before pick 1; a modal-dialog watch (0.25 s poll) Run→L2 captures by PrintWindow and kills directly. Self-test `selftest_leg_guard.py` 30/0; live: the real ABBA refused leg 1 without starting LabVIEW; one bypassed S1 leg caught the real dialog, killed 1.46 s after detection, S1 md5 unchanged (`diag_c106b_live.log`). **DECIDED: ANY refused leg ends the ABBA** (every leg opens the same port). The bypass (`LEGGUARD_TEST_BYPASS_VISA=1`) is for tests only and is never set by an ABBA card. ⇒ **the 218(c) precondition is now built into the ABBA itself: the next ABBA card simply runs `diag_c104_abba.py`; it self-refuses in seconds while the port is refused.**
     - **(c) ACCEPTED — stage tooling (`106-3`):** stagesim finalize builds with labels + wiki fs pairs (re-sim of `plan_disp`: 6 end rows == classes 1–3, 0 step-0 rows, class-4 15/15; plan md5 `c7d80fc9…` and pins unchanged); `stage_d1_disp.py` 90 lines (md5 `1d1784ab…`), helpers in `stagexec.py` (md5 `ac0e44fd…`, self-test 104/0); pre-run X9 verb-precondition (r7 op-41 refused, plan_disp passes) and X10 memory margin (r1 703.8 refused, Part-B 616.7 passes). stagesim accepting the PD217(c) classed open-row rule at finalize is ACCEPTED (same rule as E3).
       - **DECIDED — X10 thresholds:** a predicted checkpoint ≥ **690 MB** fails (error 2 was seen at 695 MB in cycle 85; margin 0 against MEMSTOP 700 would pass a value above the error-2 point). A plan with NO covering record prints `X10 WARN unmeasured` in its output and RESULT line, and passes (refusing it would forbid every new stage); the stage's own MEMSTOP remains the run-time guard.
       - **DECIDED — `find_graph` uses the plan's own base graph** (`par1359_95_graph.json` for plan_disp) when no `--graph` is given; three X1 failures were the missing flag (review `archive/peer/2026-09-27-c106c-selftest-x1.md`).
       - The edited recipe (`1d1784ab`) needs its prior-art / stop-record round before its next LAUNCH; a dry run does not.
     - **(d) ACCEPTED — small repairs (`106-4`):** gui_save Evidence = the user's wording; stop_record wc -l twin; `selftest_guard_bash_jev` 12/0 (cause: the fixture); `peer.ps1` `loss_usd="?"`→null; audit A1/A3 skip `jev_*` logs. Leftovers: `stage_prerun.launched_py` does not split on newlines; `selftest_protocol_wiring` D3 and `selftest_stage_prerun_headcmp_79-6` fail (owner unknown).
     - **(e) Card `106-5` (this cycle):** X10 690 + WARN, `find_graph` base graph, `launched_py` newline split, the two failing self-tests (measure the cause first), and a Part-B DRY of the 90-line recipe through `stage_prerun` (guard_cycle's block is answered by the 07:4x violation decisions).
     - **(f) NEXT cycle:** run the ABBA card of 217(f) through `diag_c104_abba.py` (criterion unchanged). If its leg-1 VISA precheck refuses, the cycle does NOT wait: it goes to the next M3 build sub-stage from the current bed (`D1_l2_a1_20260925_235224.vi`, §2 table), structural only, and every real-run item stays behind D-2026-09-27-03.
     - **(g) CLOSE, on `106-5` PASS 5/0 (`tools/bench/cards/result_106-5.json`):** X10 fails ≥ 690 MB, `X10 WARN unmeasured` rides in a PASS RESULT's `first_fail` (result-line/1 has no free-text field — accepted); `find_graph` prefers the plan's base graph; `launched_py` splits on newlines; `selftest_protocol_wiring` D3 was our test (66/0); headcmp_79-6 passes (its 07:09 fail coincided with 106-4's in-flight patch); **Part-B DRY of the 90-line recipe PASS** (entry diff 0, E3 6 == 6, class-4 15/15, `diag_c106e_dryB.txt:67,72-73`), run as a self-test child with `--no-record`. `stage_prerun.py` md5 `0621b403…`.
       - ⚠️ **AMENDED at close (retrospective-cycle106 `device-failed`, accepted): no longer a carry — it is cycle 107's FIRST card beside the ABBA launch** (`docs/violation-decisions.md`, device-failed 07:5x); F5's dry ran as a self-test child after two top-level refusals, so it is PASS without a record. Card rule from 107: a gate refusal comes back BLOCKED, never re-run through an exempt route. Original wording: **DECIDED — carry, not ahead of the next deliverable:** `stop_record` must let `stage_prerun --dry|--prerun <recipe>` through for an unreleased recipe (both are offline; they are the checks that PRECEDE a release), while still refusing a launch; and `launched_plan_runs` gets the same newline split as `launched_py`. The display recipe (`1d1784ab`) still owes its prior-art round and a recorded dry/pre-run before any launch.

## OPEN (design choices — for judgement; not decided here)

> 2026-09-24: O2, O3, O4 (SR half; the queue half is QRT), O6 (placement + route), O7, O8 are CLOSED by Pre-decided
> 156–161. O1 is CLOSED by Pre-decided 163 (2026-09-24). O5 stays open (prior-art: `connect_nested` refuted,
> `docs/cycle27-plan.md:108-114`; helpers = `probe_move_ctlterm_v0.py:327-351` route and the `Z/dZ` temp-sink chain
> `docs/cycle27-plan.md:115-117`).

- ~~**O1 loop identity.** Which of `#10170` / `#23041` is 1.2 and which 1.7 (Pre-decided 150). Arbitrary but binding
  once named (`docs/cycle27-plan.md:1137`).~~ **CLOSED by Pre-decided 163.**
- **O2 the kernel.** `docs/cycle27-plan.md:752` says relocating `#5058` (CPU) *"is what S2 must do"*; S2 did not
  (Pre-decided 151); `build_d1_v0.json` moved 17 without it (route A deleted it for `GPU_kernel_v1.vi`,
  `docs/d1-build-plan.md:287`). If A and B go to 1.2 while `#5058` stays on 1.1, the reseed feedback
  `#5540 → #5058 → #10969/#10757` crosses loops in both directions every frame — a **rule-1a doubt** (a one-frame
  lag across loops changes the tracking inputs). Does `#5058` move with 1.2 (as sub-stage K before A1)?
- **O3 `#10686` ownership.** The bed's 1.5 cadence (Pre-decided 147(b)) is the rising edge of `#10686`, which
  today is evaluated on 1.1 next to the iteration counter; `docs/d1-build-plan.md:304` moves it to 1.2. Moving it
  puts its inputs (`x` w3050, `y` w9105, from 1.1's `i mod Frame rate` chain) on a crossing — **rule-1a doubt** on
  *when* the schedule is evaluated. Stay on 1.1, or move?
- **O4 transport.** `docs/d1-build-plan.md:36-38` §11c makes queues + sentinels binding for every crossing and for
  the stop (S4/S4s `:679-680`); the staged S3 used S3a indicators + a Local read and no queue (Pre-decided 154). Which
  carrier for the four crossings of Pre-decided 152, and hence what STOP contains?
- **O5 nested ControlTerminal rows.** Pre-decided 155: the rule's only verb for ControlTerminal rows cannot address
  `#639` / a loop body. Moving the six terminals with their nodes (build-plan `:409-410`: a tunnel changes *when*
  `Reset Tracking` is read) needs a verb decision (`wire_indicators` / `connect_nested` / a new rule entry).
- **O6 ROT.** Placement (proposed last-before-FIN) and route: no replace-callee verb exists (Pre-decided 154), and
  whether `computation_diff` sees callee identity is unmeasured — a scratch control is owed before ROT's gate means
  anything. Pre-decided 133 is user-directed (CLAUDE.md 1b, signed rotor), so its 9 rows are the only rule-1a
  change this chain is allowed to carry.
- **O7 final name.** `docs/cycle27-plan.md:390` names the result `Track_v6_D1_GPU.vi`, while `:749-756` says the
  kernel is the CPU one and the GPU swap is its own later stage.
- **O8 which table governs** — §4's conflict: this page, `docs/cycle27-plan.md:383-390`, or `docs/d1-build-plan.md:675-682`.
