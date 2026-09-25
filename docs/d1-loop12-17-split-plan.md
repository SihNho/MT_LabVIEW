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
