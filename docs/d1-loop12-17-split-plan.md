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
| **L7-1** | **REWRITTEN 2026-09-24 by Pre-decided 164** (was: "2 SR pairs move with their node; re-wire its 12 rows; w4517 made as a 1.1→1.7 crossing here"): move `#376` into body `#23405` of `#23041`; create 1.7's TWO NEW SR pairs replacing `#15/#51` and `#24/#1108` (the old pairs stay on `#637` until L7-R), each new LEFT initialised off the same source as the original (`#4910` w4969, `#781` w3543); wire the 4 rows inside 1.7 (`#376` ↔ new SRs). Of `#376`'s 12 rows: in-1.7 4 · cross-loop OPEN 3 (i5 w4517, i7 w3268, i8 w1397 — queues, never made here) · L7-R 1 (i4) · split 1 (i3) · top-level tunnel 3 (i6/i9/i11, unwired; no stage owns them yet — OPEN). Prediction `tools/bench/l7_1_prediction.json` | `D1_s3_loop15.vi` | `D1_l7_1_<ts>.vi` (GUI save if broken, CLAUDE.md §3 rule 6) | 4 + 2 init | 6 / 0 |
| **L7-R** | retire `#15/#51`, `#24/#1108` on `#637` after live-consumer check; re-feed `#6384`'s two inputs from 1.7's output tunnels; RBW; save by script | `D1_l7_1_<ts>.vi` | **`D1_s4_loop17.vi`** | retire + 2 | 0 / all |
| **K** | move the CPU kernel `#5058` `Track N beads four-fold over-kernel-v3.vi` into the 1.2 body (Pre-decided 156; name-gated, `docs/cycle27-plan.md:754-755`); re-wire its 13 rows | `D1_s4_loop17.vi` | `D1_k_<ts>.vi` (GUI save if broken) | 13 | P0 recounts |
| **L2-A1** | move group A (8) + the `Auto-Reset` / `Reset Tracking` control terminals into the 1.2 body; add 1.2's 4 SR pairs; re-wire batch 1 (incl. w10990 `#10757`→`#10407`, the only row left of old L2-C — Pre-decided 161) | `D1_k_<ts>.vi` | `D1_l2_a1_<ts>.vi` (broken by design → GUI Ctrl+S, CLAUDE.md §3 rule 6) | 13 | 3 / 10 |
| **L2-A2** | re-wire batch 2 of group A (`min value` #17257 is an INDICATOR fed by `#10969` — a sink row, not a moved control, Pre-decided 158) | `D1_l2_a1_<ts>.vi` | `D1_l2_a2_<ts>.vi` | 13 | 3 / 10 |
| ~~**L2-C**~~ | **REMOVED by Pre-decided 161**: `#10686` stays on 1.1, so w10799 `#10686`→`#10407` stays as S3 left it; w10990 moved into L2-A1 | — | — | 0 | — |
| **L2-B1..B3** | move group B (8, incl. ForLoops `#1359` / `#29874` with their own SRs) + the FOUR controls `Z/dZ` #47, `Correction Factor` #9289, `Force\nsmoothing\nhalf-width` #28148 (→ `#1359` t7), `Extension\nmedian filter\nhalf-width` #28996 (→ `#1359` t8 / `#29874` t6); `Force (pN) vs Extension (nm) ` #8038 is an INDICATOR fed by `#11261` (sink row); rows from `d1_rewire_sources.json` cross-checked against `build_d1_v0.json` (Pre-decided 158); gate per Pre-decided 159 | previous | `D1_l2_b1_<ts>.vi` → `…b2…` → `…b3…` | 13/13/12 + the two control rows | 2 / 36 over the three |
| **L2-R** | retire the 4 old 1.2 carriers on `#637` after a live-consumer check (Pre-decided 142's pattern), junk purge, Remove Bad Wires, save by script | `D1_l2_b3_<ts>.vi` | **`D1_s5_loop12.vi`** | retire rows | 0 / all |
| **QRT** | the queue RESOLUTION TABLE (`docs/cycle27-plan.md:930-933`, 34(g)): for each of the eight queues the `(uid, exact terminal name, diagram)` on `D1_s5_loop12.vi`, or the stage that must run first. A document, no LabVIEW write (Pre-decided 156) | `D1_s5_loop12.vi` → read only | the table (doc) | 0 | — |
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
  so its terminal is chosen among candidates. Counts above = the v0 run's `from-sr`/`to-sr` rows per group
  (A 3+3, B 2, W 2+2); P0 recomputes them on the bed.

## 3. Pass criteria per sub-stage (Pre-decided 132 applied: every predicted value names what already determines it)

| sub-stage | gate | predicted | determined by an earlier step? → treatment |
|---|---|---|---|
| all | input md5 = the previous stage's output md5; pins unchanged | equal | hygiene, not evidence — kept |
| P0 | bed md5 after the read | `1a11d92a…` | — kept |
| P0 | re-derived cut rows vs `build_d1_v0.json` | per group 26/38/3/12 **minus/plus the rows M3a–M4 changed** (the S3a indicator branches on w10799 / w10990, the retired 1.5 carriers) | the v0 file determines the base ⇒ predict the DIFFERENCE, list it |
| L7-1, K, L2-A1, A2, B1, B2 | `ExecState` | 0 (rows still open) | determined by the stage's own design ⇒ **NOT a gate**; broken intermediate saved by GUI (rule 6), never run |
| same | `computation_diff(S1,new)` (MACHINE SR pairing, `tools/vigraph.py:333-388`) | = exactly the not-yet-re-wired ledger rows of this group | not determined — the gate. **L2-B1..B3 (ForLoop SRs of `#1359`/`#29874` move): only if P0 showed no two ForLoop left SRs in the affected loops share a TOP; otherwise the gate lists the TOP-collision rows as predicted artefacts (Pre-decided 159)** |
| same | `diff(prev,new)` | = owner changes of the moved uids + the batch's re-made edges + the new SR objects, nothing else | op semantics predict the SHAPE, not the rows — gate on the row list |
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
