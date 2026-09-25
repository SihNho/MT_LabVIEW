# priorart-c81-l2a1-r5-stagexec

- **agent:** claude
- **role:** priorart
- **model:** claude-opus-5-5 (effort medium; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $1.5743  in 14 / out 5973 / cache-create 157491 / cache-read 974214  (66s, 16 turn(s))
- **date:** 2026-09-25 13:12:05
- **outcome:** ANSWERED (70s)
- **verdict-card:** VERDICT-CARD priorart-c81-l2a1-r5-stagexec verdict=novel -> tools\bench\cards\verdict_priorart-c81-l2a1-r5-stagexec.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id priorart-c81-l2a1-r5-stagexec, role priorart) ---
CLAIM: The work under review (cycle-start) is novel - not already built, measured, refuted or covered by an existing helper in this project's files.
ATTACHMENT: tools\recipes\stage_d1_l2a1.py (md5 e589dc746833aaaafe47f3eff4c22dc6)
--- END REVIEW CARD ---

PRIOR-ART REVIEW (trigger: cycle-start).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
---
type: plan
kind: stage-plan
status: current
parent: docs/connectivity-map-plan.md
date: 2026-09-24
tags: [d1, loop-split, decomposition, stage-plan]
---

# D1 ??the loop 1.2 / 1.7 splits still owed after S3 (decomposition plan, cycle 69 act 1)

Written by a material session from the files only (no LabVIEW opened). Design choices are NOT made here; they are
listed under `## OPEN` with their evidence. The CLAUDE.md "split and save" rules 1?? apply: every sub-stage below
leaves a file, the next sub-stage starts from that file in a fresh LabVIEW instance, re-wiring goes in batches of
10??5 rows, a stage that fails twice at the same place is decomposed again before any retry.

## 0. Where we are (measured)

- **Bed** = `claudeDev\D1_s3_loop15.vi`, md5 `1a11d92aacabf7ec844d65b8af19f39f` (`docs/connectivity-map-plan.md:100`,
  Pre-decided 147). S3 as re-cut moved ONLY loop 1.5's set (`#10407`, `#48`, `#3529`, `#3560`, `#3447` ??body
  `#23058` of `WhileLoop #23032`; `tools/bench/stage_d1_m4a.log:197` for `#10407`, the rowD wiki for the other four).
- **Owed:** the original S3 (`docs/d1-build-plan.md:675`) moved 23 objects ??**17 ??1.2, 5 ??1.5, 1 ??1.7** ??plus
  8 shift registers (`:677`) and 6 `ControlTerminal`s (`:677`, `:392-407`). The 1.2 and 1.7 parts are not scheduled
  by any current plan row.

## 1. Node sets (source: `tools/bench/build_d1_v0.json` key `moved`, = `docs/d1-build-plan.md:287-308`)

Cut rows = `build_d1_v0.json` key `cut` (2026-09-17 route-A run on a copy of the original; uids are the S1 uids ??
all 18 non-structure uids below read `frame_diagram 639` in both `docs/wiki/subvi/D1_s1_copy.json` and
`docs/wiki/subvi/D1_s3b_m3a3b_rowD_20260922_161040.json`; structures `#5540 #10445 #1359 #2222 #29874` own no
terminals of their own in the wiki and are located through their tunnels). **These counts are a PREDICTION to be
re-derived on the bed by P0**, not an address list.

| group | uids (label, build-plan line) | cut rows | of which unnamed |
|---|---|---:|---:|
| **A** reseed / selector chain | `#5540` Case (reseed) 쨌 `#9647` And 쨌 `#10247` Or 쨌 `#10445` Case 쨌 `#10950` Less? 쨌 `#17289` `min value` Property 쨌 `#10969` Array Max&Min 쨌 `#10757` Index Array (`:288-295`) | 26 | 5 |
| **B** forward slice | `#1359` For 쨌 `#2222` Case 쨌 `#2626` Build Array 쨌 `#6104` Index Array 쨌 `#8885` Multiply 쨌 `#9833` Index Array 쨌 `#11261` Build Array 쨌 `#29874` For (`:296-303`) | 38 | 13 |
| **C** schedule | `#10686` And (`:304`) + the two 짠5a-ter re-wire rows w10799 / w10990 (`:344-360`) | 3 + 2 | 0 |
| **W** writer (1.7) | `#376` `save trace.vi` (`:308`) | 12 | 0 |
| **K** kernel ??MOVES to 1.2 (Pre-decided 156) | `#5058` `Track N beads four-fold over-kernel-v3.vi` (`:287`) | 13 (key `cut`, uid 5058) | ??|

Shift registers still on the frame loop `#637` that belong to 1.2 / 1.7 (`tools/bench/graph_loops_m4b_20260924.json`,
loop 637 `left_of`; plan `docs/d1-build-plan.md:376-383`): 1.2 = `#1147/#1142`, `#5796/#5805`, `#119/#2972`,
`#7311/#11001`; 1.7 = `#15/#51` (accumulator), `#24/#1108` (error chain).
Control terminals that move into 1.2 ??**REWRITTEN 2026-09-24 by Pre-decided 158** from the measured six
(`tools/recipes/build_d1_routeb_v7.py:443-453`, `tools/bench/build_d1_routeb_v7_run10.log:23-31`; the old list at
`docs/d1-build-plan.md:401-406` wrongly carried two indicators): `Auto-Reset` #17472 (ctlterm #17487), `Reset Tracking`
#5605 (#5634) ??group A; `Z/dZ` #47 (#403), `Correction Factor` #9289 (#9306), `Force\nsmoothing\nhalf-width` #28148
(#28170, ??`#1359` t7), `Extension\nmedian filter\nhalf-width` #28996 (#29091, ??`#1359` t8 / `#29874` t6) ??group B.
`min value` #17257 and `Force (pN) vs Extension (nm) ` #8038 are INDICATORS (sinks of `#10969` / `#11261`), not moved
controls. `Diagram #639` holds **31** ControlTerminals (`build_d1_routeb_v7_run10.log:23`). The ctlterm uids are the
original's; P0 re-reads them on the bed.

## 2. Sub-stages (order RE-CUT 2026-09-24 by the cycle-69 judgement, Pre-decided 157: smallest-first, L7 before L2; each row = one saved artefact)

**Every sub-stage below SAVES its output file, and the next sub-stage opens THAT file in a FRESH LabVIEW instance
(Pre-decided 162).** Every row address is a uid (+ exact terminal name), re-read on the live file immediately before
use ??never a Traverse / node / diagram index (Pre-decided 158; `docs/d1-build-plan.md:356` is the old failure).

| id | does | input file | output file (under `claudeDev`) | rows | Jev PAIR / rule |
|---|---|---|---|---:|---|
| **P0** | read-only census of the bed: wiki + graph for md5 `1a11d92a`; re-derive every group's cut list, crossing list and new-carrier list; measure handles open?뭖lose (STATUS ACT 2); O1 node sets of `#10170`/`#23041`; ForLoop/WhileLoop left-SR TOP collisions (Pre-decided 159). **MEASURED ??see the P0 facts line under this table** | `D1_s3_loop15.vi` | `docs/wiki/subvi/D1_s3_loop15.json`, `tools/bench/graph_s3_loop15_<date>.json`, `tools/bench/split_rows_l2l7.json` (data, no VI) | 0 | ??|
| **P1** | pure-Python resolver (no LabVIEW): the 33 structure rows ??the TUNNEL uid that carries each (outer face on `#639`, + inner frame diagrams), by wire identity on the bed's terminal table, cross-checked against S1's; plus F3a (the 12 FlatSequenceFrame-cut ForLoop owner chains re-derived from the `frame_diagram` column). **MEASURED ??see the P1 facts line under the P0 facts** | `split_rows_l2l7.json`, `graph_s3_loop15_20260924.json`, `D1_s1_copy.json` wiki, `build_d1_v0.json` `cut` | `tools/bench/split_rows_l2l7.json` (new fields `p1_tunnel`, `resolved_by_p1`, `p1_wire_on_bed`, top-level `p1`; data, no VI) | 0 | ??|
| **L7-1a** | **SPLIT 2026-09-24 by Pre-decided 169**: move `#376` into body `#23405` of `#23041` + create the two new SR pairs; NO wiring; recipe `tools/recipes/stage_d1_l7_1a.py`, contract `tools/bench/l7_1a_predict.log` | `D1_s3_loop15.vi` | `D1_l7_1a_<ts>.vi` (GUI save, rule 6) | 0 | 0 / 0 |
| **L7-1b** | ??**DELIVERED 2026-09-24 06:1x (cycle 72 firefighter, run 3): `claudeDev\D1_l7_1_20260924_060431.vi` md5 `e5c7d68b56d018131f2ebf0df656fdd6`, `tools/bench/stage_d1_l7_1b_r3.log` 38/0, 761 s; all 9 rows wired, second pass by `verify_term_uid` Is Broken? False 횞4, PB = exactly the 8 predicted rows, PC1?밣C3 pass, ExecState 0 as predicted (L7-R rows open), input + bed md5 unchanged, refs 23/23, handles 34,146 at exit. r4's B4 is MEASURED: the new SR outer terminals kept their uids across the connect (#24205/#24291 resolved by uid after wiring).** Original brief: **Pre-decided 169/171**: from the saved L7-1a file, fresh LabVIEW: the 9 rows of the L7-1 row below (4 S1-mapped per 168 + 2 single-candidate per 165 + 3 tunnels per 166), corrected intent lines (171(1)); PB `computation_diff` FATAL before save (170(c)); runs in the same material dispatch as L7-1a when L7-1a passes (171(4)); recipe `tools/recipes/stage_d1_l7_1b.py` | `D1_l7_1a_<ts>.vi` | `D1_l7_1_<ts>.vi` | 9 | 4 S1-mapped / 5 rule |
| **L7-1** (superseded by the L7-1a/L7-1b rows above, kept for the row detail) | **REWRITTEN 2026-09-24 by Pre-decided 164** (was: "2 SR pairs move with their node; re-wire its 12 rows; w4517 made as a 1.1??.7 crossing here"): move `#376` into body `#23405` of `#23041`; create 1.7's TWO NEW SR pairs replacing `#15/#51` and `#24/#1108` (the old pairs stay on `#637` until L7-R), each new LEFT initialised off the same source as the original (`#4910` w4969, `#781` w3543); wire the 4 rows inside 1.7 (`#376` ??new SRs) by Jev PAIR; the 2 SR-init rows are RULE-SINGLE-CANDIDATE rows (Pre-decided 165); i6/i9/i11 (`#3644`/`#2294`/`#5096`) are re-made as NEW tunnels on `#23041` off the same outer feed (Pre-decided 166, `tunnel_outer` rule rows). Of `#376`'s 12 rows: in-1.7 4 쨌 top-level tunnel 3 (L7-1, 166) 쨌 cross-loop OPEN 3 (i5 w4517, i7 w3268, i8 w1397 ??queues, never made here) 쨌 L7-R 1 (i4) 쨌 split 1 (i3). Prediction `tools/bench/l7_1_prediction.json` (`tools/bench/l7_1_predict_r2.log`) | `D1_s3_loop15.vi` | `D1_l7_1_<ts>.vi` (GUI save if broken, CLAUDE.md 짠3 rule 6) | 9 (4 body + 2 init + 3 tunnel) | 4 / 5 |
| **L7-R** | ??**DELIVERED 2026-09-24 07:2x (cycle 73 material, run 2): `claudeDev\D1_s4_loop17.vi` md5 `4b621946492da3d2fbb96b6053e715ec`, 481,808 B, `tools/bench/stage_d1_l7_r_r2.log` 61/0, 459 s. Executed Pre-decided 175: PMV (move_in ControlTerminal on a scratch) PASS; A0 index 3 == uid 3182; 7 wires deleted by uid; #3052/#3453 moved into #23405; Jev top == S1-mapped on 4 rows (p 0.42/0.95/0.91/0.93); 2 re-feeds from the new RIGHT SRs; output tunnels #5204 (file progress ??#2048 'length' + #6384 'actual # data points') and #10404 (??#6384 'file # to append'), IndexMode 0 = #1929/#5020; 6 second passes Is Broken? False; retire 6 carriers (#1929/#5020 already gone with their wires); RBW 7 half-wires, no live edge. PB cdiff(S1,new) = exactly the w4517 row; PC1/PC2 = predicted; ExecState 1 warm, scripted save + re-read 1 (t5/t7 OPEN yet not required); cold not read (moves to QRT, 175). cdiff does NOT report the unwired 'frame index' (w3268) ??FIN finding. Contract `tools/bench/l7_r_predict.log`, recipe `tools/recipes/stage_d1_l7_r.py`.** Original row: retire `#15/#51`, `#24/#1108` on `#637` after live-consumer check; re-feed from 1.7's output tunnels. **CORRECTED 2026-09-24 (prior-art c70-l7-1-r2 A3.3; measured `tools/bench/l7_1_predict_r2.log:22-27`):** L7-1 leaves SIX consumers of `#376`'s outputs unsourced, not two ??`#6384` `error in` / `file # to append` / `actual # data points`, `#2048` `array` / `length`, `#3453` `file progress` (an indicator on 1.1). Which stage owns `#2048` and `#3453`, and the third `#6384` input, is OPEN (judgement). RBW; save by script | `D1_l7_1_<ts>.vi` | **`D1_s4_loop17.vi`** | retire + 6 (ownership OPEN) | 0 / all |
| **K** | ??**DELIVERED 2026-09-25 10:0x (cycle 79): `claudeDev\D1_k_20260925_100155.vi` md5 `6cf5b077??, `tools/bench/stage_d1_k_r2.log` 35/0; design Pre-decided 177??78(i).** Original row: move the CPU kernel `#5058` `Track N beads four-fold over-kernel-v3.vi` into the 1.2 body (Pre-decided 156; name-gated, `docs/cycle27-plan.md:754-755`); re-wire its 13 rows | `D1_s4_loop17.vi` | `D1_k_<ts>.vi` (GUI save if broken) | 13 | P0 recounts |
| **L2-A1** | move group A (8) + the `Auto-Reset` / `Reset Tracking` control terminals into the 1.2 body; add 1.2's 4 SR pairs; re-wire batch 1 (incl. w10990 `#10757`??#10407`, the only row left of old L2-C ??Pre-decided 161) | `D1_k_<ts>.vi` | `D1_l2_a1_<ts>.vi` (broken by design ??GUI Ctrl+S, CLAUDE.md 짠3 rule 6) | 13 | 3 / 10 |
| **L2-A2** | re-wire batch 2 of group A (`min value` #17257 is an INDICATOR fed by `#10969` ??a sink row, not a moved control, Pre-decided 158) | `D1_l2_a1_<ts>.vi` | `D1_l2_a2_<ts>.vi` | 13 | 3 / 10 |
| ~~**L2-C**~~ | **REMOVED by Pre-decided 161**: `#10686` stays on 1.1, so w10799 `#10686`??#10407` stays as S3 left it; w10990 moved into L2-A1 | ??| ??| 0 | ??|
| **L2-B1..B3** | move group B (8, incl. ForLoops `#1359` / `#29874` with their own SRs) + the FOUR controls `Z/dZ` #47, `Correction Factor` #9289, `Force\nsmoothing\nhalf-width` #28148 (??`#1359` t7), `Extension\nmedian filter\nhalf-width` #28996 (??`#1359` t8 / `#29874` t6); `Force (pN) vs Extension (nm) ` #8038 is an INDICATOR fed by `#11261` (sink row); rows from `d1_rewire_sources.json` cross-checked against `build_d1_v0.json` (Pre-decided 158); gate per Pre-decided 159 | previous | `D1_l2_b1_<ts>.vi` ??`?쫇2?? ??`?쫇3?? | 13/13/12 + the two control rows | 2 / 36 over the three |
| **L2-R** | retire the 4 old 1.2 carriers on `#637` after a live-consumer check (Pre-decided 142's pattern), junk purge, Remove Bad Wires, save by script | `D1_l2_b3_<ts>.vi` | **`D1_s5_loop12.vi`** | retire rows | 0 / all |
| **QRT** | (+ Pre-decided 175: the two OWED 1.7 input rows t5 w4517 `#2626`??#376 'current frame data array in'` and t7 w3268 `#637` i??#376 'frame index'` get a queue here ??no planned queue carries them; + Pre-decided 177(e): the OWED 1.2 input row w3040 `#6810 'Image Out'`??#5058 'Image In'`) the queue RESOLUTION TABLE (`docs/cycle27-plan.md:930-933`, 34(g)): for each of the eight queues the `(uid, exact terminal name, diagram)` on `D1_s5_loop12.vi`, or the stage that must run first. A document, no LabVIEW write (Pre-decided 156) | `D1_s5_loop12.vi` ??read only | the table (doc) | 0 | ??|
| **STOP** | 1.2 / 1.7 conditional terminals driven by the stop design (build-plan S4/S4s, `:679-680`), inputs from QRT | `D1_s5_loop12.vi` | `D1_s6_stop.vi` | from QRT | ??|
| **ROT** | Pre-decided 133: repoint the 9 rotor call sites to `claudeDev\SetCommand_signed.vi` md5 `ec87a2657b158722082ca00c7074f114` by `SubVI.Replace` 635E001, measured first on a scratch copy together with the Baseline/Ring constants (Pre-decided 160) | `D1_s6_stop.vi` | `D1_s7_rotor.vi` | 9 (+ constants per the scratch measurement) | 0 / 9 |
| **FIN** | census, ExecState 1 warm + cold, final save ??the GPU top level is the default final file (Pre-decided 161) | `D1_s7_rotor.vi` | GPU top level (name after the GPU-swap stage, never "GPU" before it, `docs/cycle27-plan.md:756`) | 0 | ??|

**P0 facts (MEASURED 2026-09-24 01:34??1:39, `tools/bench/p0_c69_census.py` ??`tools/bench/p0_c69_census.log`, 10 pass /
0 fail, `BGRUN END rc=0 after 284s` `:219`; bed md5 `1a11d92a?? before and after `:7`/`:204`; scratch deleted, files left []
`:213`; data `tools/bench/split_rows_l2l7.json`, `tools/bench/graph_s3_loop15_20260924.json`):**
- **(1) O1:** body `#23166` is owned by WhileLoop `#10170` and body `#23405` by `#23041` (`:23`, `:27`); each holds ONLY its
  scaffold ??`#10171` Comparison + `#23417` LoopTunnel, and `#23042` Comparison + `#23501` LoopTunnel (`:24`, `:28`); **0 plan
  L2/L7 nodes in either** (`:25`, `:29`). All 19 plan nodes (L2's 18 incl. `#5058`, L7's `#376`) are owned by `Diagram #639`
  (loop `#637`, 1.1) (`:31-67`). Nothing on the bed binds either loop to 1.2 or 1.7 ??O1 stays a naming choice. **(O1 CLOSED 2026-09-24 by Pre-decided 163: 1.2 = `#10170`, 1.7 = `#23041`.)**
- **(2) SR TOPs:** ForLoops `#1359` and `#29874` hold **0 shift registers** (loop table + `:86-87`), and **no ForLoop is nested
  inside any plan node** (owner chains of all 17 ForLoops, `:68-129`). Touched loops: `#637` ??12 lefts, TOPs all distinct,
  **0 collisions** (`:140`); `#10170` / `#23041` ??0 SRs (`:131`, `:133`). **J4 row: no TOP collision in any touched loop**
  (`:158`). The bed's ONLY TOP collision is loop 1.5's body `#23058` (`#23880`/`#23796` at TOP 2826, `:153`) ??machine-paired
  already (`graph_loops_m4b_20260924.json`), and not touched by L2/L7.
- **(3) handles:** 33,985 sixty s after restart ??**54,395 after opening the bed** (+20,410; `:20`) ??**34,331 after closing it**
  (+346 over base; `:195`). Pre-decided 147(c)'s ~54.4k is the OPEN level, confirmed.
- **(4) rows:** `build_d1_v0.json` `cut` and `d1_rewire_sources.json` give the SAME 92 rows over the 19 owed uids ??**0
  disagreements** (`:159-160`; 92 = A 26 + B 38 + C 3 + W 12 + K 13). **59 resolve on the live graph by uid + terminal name;
  33 do not** (`:161`), and all 33 are on the five STRUCTURES `#5540` (7), `#10445` (4), `#1359` (9), `#2222` (7), `#29874` (6)
  (`:162-194`): a structure owns no terminal rows of its own (they sit on its tunnel uids), so the uid+name resolver cannot
  address them ??the structures themselves are present on `#639` (`:31`, `:37`, `:47`, `:49`, `:61`). Those 33 rows need
  tunnel-uid addressing before any stage uses them.

**P1 facts (MEASURED 2026-09-24 02:43??2:46, pure Python, no LabVIEW; `tools/bench/p1_c70_resolve.py` ??
`tools/bench/p1_c70_resolve.log` run 2 `:51-100` 7 pass / 0 fail `BGRUN END rc=0` `:100`; `tools/bench/p1_c70_f3a.py` ??
`tools/bench/p1_c70_f3a.log` run 2 `:40-79` 5/0 `BGRUN END rc=0` `:79`):**
- **(1) rows: 92/92 resolved, 0 ambiguous, 0 unresolved** (`p1_c70_resolve.log:97`; tally name 59 + tunnel 33). Each of
  the 33 structure rows is the OUTER face (on `#639`) of exactly one tunnel; the bed tunnel uid equals S1's for all 33
  (`:88`). Tunnels per structure (`:89-93`): `#5540` ??`5603 5967 5680 5702 5725 5825 6016` (t0..t6; inner frames
  `5582/5592`) 쨌 `#10445` ??`10465 10584 10750 11336` (inner `10453/10459`) 쨌 `#1359` ??`9087 9227 9503 10004 10177
  11363 31051 31137 28370` (t1..t9; inner `7911`) 쨌 `#2222` ??`2276 2451 2765 2992 3176 6132 7091` (t0..t6; inner
  `2235/2265`) 쨌 `#29874` ??`29172 29777 29911 30135 29616 30896` (t1..t6; inner `29894`). Five rows had TWO tunnel
  candidates on their wire and were decided by the inner-frame match with the structure's other tunnels (bed and S1
  agree): `#1359` t3 w30592 (??503, not 20497), t4 w28847 (??0004) / `#29874` t4 w28847 (??0135), `#1359` t8 w31166
  (??1137) / `#29874` t6 w31166 (??0896). Inner-frame sets are one per structure and pairwise disjoint (`:94-95`).
  Two NAME-resolved rows have an S1 wire uid absent on the bed: `#10757` t1 w10990, `#10686` t0 w10799 (`:96`).
  Run 1 (`:1-50`) failed its S1 gate only because the S1 check skipped the inner-frame pass (script defect, fixed).
- **(2) F3a:** every one of the 17 P0 ForLoop chains reaches TopLevelDiagram `#536` (`p1_c70_f3a.log:61`); the cut
  frames are frames of the two top-level flat sequences ??`{686, 81548, 113, 124, 759, 1817, 3121, 3628, 4866, 5031}`
  and `{13236, 15041, 21134, 25769, 12960, 14840, 19687, 19887, 20261, 26117}`, owner `#536` (`:44-60`; every
  FlatSequenceInnerTunnel reports its sequence's owner diagram as a third frame, 238 of them `#536`, `:41`); 167
  directed edges agree with the derived tree, 0 contradictions (`:42`). **No ForLoop is nested inside any L2/L7 plan
  structure** (`:62`). Left SRs: `#637` body `#639` 12 lefts, TOPs all distinct; ForLoops nested below `#639` =
  `1359 2457 4810 29617 29874`, their lefts `#2603` 1 쨌 `#29629` 2 (TOPs 1675/1620) 쨌 `#7911` 0 쨌 `#29894` 0, no TOP
  collision; `#10170`/`#23041` bodies 0 lefts, nothing nested (`:63-77`). **J4: no two ForLoop left SRs in the
  affected loops share a TOP.**

**Why L2 before L7 ??SUPERSEDED by Pre-decided 157** (kept for the record): `#376` t5 `current frame data array in` is fed by w4517 from
`#2626` (group B) (`build_d1_v0.json` key `cut`, rows `[2626,0,??4517]` and `[376,5,??4517]`). If L7 ran first,
w4517 would be re-made as a 1.1??.7 crossing and re-made AGAIN as 1.2??.7 at L2-B. L2 first makes it once.
**Why ROT late:** the 9 sites' frame diagrams are `#28036 #27425 #27076 #19033 #18718 #18317 #28412` (both wikis),
none of them `#639` or `#23058`, so no split touches them; placing ROT after the splits keeps every split stage's
`computation_diff(S1,new)` prediction at **0 rows**, while ROT's own prediction is exactly its 9 rows. (A choice of
order ??judgement may move it; O6.)

**Jev PAIR vs rule rows.** Pipeline per `docs/connectivity-map-plan.md:93,96` (Pre-decided 143/146):
`tools/jev_candidates.py` enumerates the legal pairs ??`tools/jev_pairs.py` `decide` (PAIR at the thresholds in
`tools/bench/jev_menu_thresholds.json`; op by `op_rule`, `tools/jev_pairs.py:181-220`, Jev OP only when the rule
has no entry) ??`write_record` ??`stagekit.Stage.from_decision` (`tools/stagekit.py:830`).
- **rule rows** = both endpoints are fixed by the S1 edge (same uid + terminal on both sides): same-loop, constant,
  control, tunnel (`tunnel_outer`, Pre-decided 146; FSIT sink ??`fs_inner_tunnel_connect`) and source-side rows,
  plus every `retire`/`delete` row.
- **Jev PAIR rows** = one endpoint is a NEW carrier created in that stage (the new SR pairs; a new crossing carrier)
  so its terminal is chosen among candidates ??**and the legal candidate set has ?? pairs (Pre-decided 165, 2026-09-24):
  a new-carrier row with EXACTLY ONE legal pair whose source equals the S1 edge's source is a RULE row
  (`RULE-SINGLE-CANDIDATE`)**. Counts above = the v0 run's `from-sr`/`to-sr` rows per group
  (A 3+3, B 2, W 2+2); P0 recomputes them on the bed.

## 3. Pass criteria per sub-stage (Pre-decided 132 applied: every predicted value names what already determines it)

| sub-stage | gate | predicted | determined by an earlier step? ??treatment |
|---|---|---|---|
| all | input md5 = the previous stage's output md5; pins unchanged | equal | hygiene, not evidence ??kept |
| P0 | bed md5 after the read | `1a11d92a?? | ??kept |
| P0 | re-derived cut rows vs `build_d1_v0.json` | per group 26/38/3/12 **minus/plus the rows M3a?밠4 changed** (the S3a indicator branches on w10799 / w10990, the retired 1.5 carriers) | the v0 file determines the base ??predict the DIFFERENCE, list it |
| L7-1a | `diff(bed,new)` (Pre-decided 169) | nodes_added = exactly the 4 new SR uids, nodes_removed = [], every removed uid-edge touches `#376` **except an edge admitted by Pre-decided 172** (listed by edge in the prediction, its wire uid survives with every sink, its source is a tunnel whose only inside source was the moved node ??here `#1929:2043??2048:3182`, `#1929:2043??6384:6480`, `#5020:5050??6384:6511`), no uid-edge added; bed md5 unchanged (`tools/bench/l7_1a_predict.log`) | not determined by an earlier step ??the gate (no rows wired) |
| L7-1a, L7-1b, K, L2-A1, A2, B1, B2 | `ExecState` | 0 (rows still open) | determined by the stage's own design ??**NOT a gate**; broken intermediate saved by GUI (rule 6), never run |
| same | `computation_diff(S1,new)` (MACHINE SR pairing, `tools/vigraph.py:333-388`) | = exactly the not-yet-re-wired ledger rows of this group | not determined ??the gate. **L2-B1..B3 (ForLoop SRs of `#1359`/`#29874` move): only if P0 showed no two ForLoop left SRs in the affected loops share a TOP; otherwise the gate lists the TOP-collision rows as predicted artefacts (Pre-decided 159)** |
| same | `diff(prev,new)` | = owner changes of the moved uids + the batch's re-made edges + the new SR objects, nothing else, **plus removed edges admitted by Pre-decided 172's three conditions (listed by edge). From L7-1b on, the three `#1929`/`#5020` ??`#2048`/`#6384` edges are BASELINE: absent in the input and must stay absent (L7-R rows; re-adding one fails the gate ??`tools/bench/l7_1b_predict.log` PC3)** | op semantics predict the SHAPE, not the rows ??gate on the row list |
| same | `WhileLoop` 6, `Local` 8, `ControlTerminal` 114 | delta 0 | determined by S2 / move semantics ??delta tripwire only, not evidence |
| L2-A1 (was L2-C) | w10990 wired, `Is Broken?` False (ordered second pass, cycle27 42(b)); w10799 untouched | False | not determined ??gate |
| L2-R, L7-R | live consumers on each retired carrier (`sources_of`/`reach4`, completed graph) | 0 | not determined ??gate, BEFORE the delete |
| L2-R, L7-R | `ExecState` warm, then cold in a restarted LabVIEW | 1 | NOT implied by RBW (RBW can bare a register, Pre-decided 132 / `docs/cycle27-plan.md:3705-3715`) ??gate |
| L2-R, L7-R | `computation_diff(S1,new)` | 0 rows | not determined ??gate |
| L2-R, L7-R | handles open?뭖lose vs P0's measured post-load level | 짹100 | P0 determines the baseline ??gate on the delta |
| ROT | `computation_diff(S1,new)` | exactly 9 rows, each the callee identity at the 9 uids | **unmeasured whether `computation_diff` sees callee identity at all** ??a control first (O6) |
| FIN | cold `ExecState`, original md5 unchanged | 1, `2a78e17c?? | ??gate |

## 4. S3w-a?쫊 vs S4?밪6 ??the conflict, stated (not resolved)

- `docs/cycle27-plan.md:388` S3 = `D1_s3_moved.vi`, *"21 nodes + 8 control terminals moved"*; `docs/d1-build-plan.md:675`
  S3 = *"23 objects reparented"* and `:677` *"6 ControlTerminals"* (count corrected 2026-09-17 at `:394-397`).
- `docs/cycle27-plan.md:389` S3w-a?쫊 = re-wiring *"??5 rows of the 66"*; `docs/d1-build-plan.md:676` S3b =
  *"109 terminals over 24 uids"* and `build_d1_v0.json` key `cut` = 109 rows.
- `docs/cycle27-plan.md:390` S4?밪6 = `D1_s4_census.vi` ??`Track_v6_D1_GPU.vi` (*census, ExecState 1, saved*);
  `docs/d1-build-plan.md:679-682` S4 / S4s = the sentinel stop design, S5 = purge + ExecState 1 + save,
  S6 = cold reopen. Same labels, different content: the build plan's S4 is a design stage (stop), cycle 27's S4
  is a census.
- The S3 actually built (S3a, S3b M3a-1 ??M4) followed neither: it moved 1.5 only, carried 1.5's inputs by S3a
  indicators + a Local read (not queues), and retired carriers (Pre-decided 142) instead of batch re-wiring.
- This plan uses new ids (P0, L2-*, L7-*, STOP, ROT, FIN) so it collides with neither label set.

## L7-R facts (cycle 73, measured)

Measured offline (no LabVIEW) by `tools/bench/c73_l7r_facts.py` -> `tools/bench/c73_l7r_facts.log` over the S1 wiki
(`docs/wiki/subvi/D1_s1_copy.json`, md5 3e3d23ce?? and the S3 graph (`tools/bench/graph_s3_loop15_20260924.json`,
md5 1a11d92a??. No L7-1 graph is on disk; L7-1 = S3 + the edits in `tools/bench/stage_d1_l7_1a.log:92` and
`tools/bench/stage_d1_l7_1b_r3.log:346`. Diagram ids: 639 = `#637` body (1.1), 23405 = `#23041` body (1.7), 686 = the
frame holding both loops. Facts only; no design choice is made here.

| # | fact | source |
|---|---|---|
| M1 | 8 CDIFF rows, S1 wire / S1 source ??sink: w4517 `#2626 BuildArray 'appended array'` (639) ??`#376 'current frame data array in'`; w1397 `#3052 ControlReferenceConstant 'File # Saved'` (639) ??`#376 'saved file refnum'`; w3957 `#15` outer ??`#2048 'array'` (eff. `#376 'total data array out'`); w4337 `#1929` outer ??`#2048 'length'` AND `#6384 'actual # data points'` (eff. `#376 'file progress'`); w5274 `#376 'file progress'` ??`#3453` (and `#1929` inner); w1899 `#24` outer ??`#6384 'error in'` (eff. `#376 'error out'`); w5073 `#5020` outer ??`#6384 'file # to append'` (eff. `#376 'file number to append out'`) | `c73_l7r_facts.log` M1 block |
| M1 | In L7-1: `#376` sits on 23405 (1.7); `#2048`, `#6384` on 686; `#3453`, `#2626`, `#3052` on 639 (1.1); tunnels `#15/#24/#1929/#5020` still on `#637`. Removed by L7-1a: w4517, w1397, w5274(??3453), w3268, and `#1929/#5020` ??`#2048/#6384` (PD172). w3957 and w1899 are NOT in the removed list (their `#15`/`#24` inner sides lost `#376`) | `stage_d1_l7_1a.log:92,97`; `stage_d1_l7_1b_r3.log:206,346` |
| M2 | `#2048` GrowableFunction (Array Subset, `d1-build-plan.md:367`), 686 in S1/S3/L7-1; in: array??#15`, index??#2064 'index'` (w5314), length??#1929`; out subarray w4564 ??`#6384 'data array'` only | log M2 |
| M2 | `#6384` SubVI `save N xyz traces.vi`, 686; in: actual # data points??#1929`, base path??#4693` (eff. `#29551 path`), cal cluster path??#1748` (eff. `#3391`), data array??#2048`, desired #??#2484` (eff. `#1766`), error in??#24`, file # to append??#5020`; out error out w1920 ??`#4774 'error out'` | log M2 |
| M2 | `#3453` ControlTerminal `file progress`, owned by Diagram#639 (1.1); one input w5274 ??`#376 'file progress'`; no outputs | log M2; `d1-build-plan.md:220` |
| M2 | `#1929` LoopTunnel on `#637`: inner ??`#376 'file progress'`, outer ??`#2048 'length'`, `#6384 'actual # data points'`. `#5020` LoopTunnel on `#637`: inner ??`#376 'file number to append out'`, outer ??`#6384 'file # to append'` | log M2 |
| M2 | Planned node sets: `build_d1_v0.json` `moved` puts only `#376` in 1.7 plus SR rows `total data array out` (`#15/#51`) and `error out` (`#24/#1108`); `#2048`, `#6384`, `#3453` appear in no 1.7 set. `d1-build-plan.md:365-370` 짠5b: `#6384`, `#2048` stay on diagram 19 ("none moves"), fed "off 1.7's output tunnels instead" | `build_d1_v0.json:14,132,946-958`; `d1-build-plan.md:365-370,308` |
| M3 | S1, `#376` outputs ??`#376` inputs: reached `error in` via `error out` ??`#24` ??SR ??`#1108` ??`error in`, and `total data array in` via `#15` ??SR ??`#51`. With SR edges excluded: none. From `#2048`/`#6384`/`#3453` outputs: none | log M3 |
| M4 | `#376` terminal order (S1 wiki): t0 OUT error out, t1 OUT total data array out, t2 IN error in (??#1108`), t3 OUT file progress, t4 OUT file number to append out, t5 IN current frame data array in (w4517), t6 IN cal cluster path (??#3644`), t7 IN frame index (w3268), t8 IN saved file refnum (w1397), t9 IN file size (??#2294`), t10 IN total data array in (??#51`), t11 IN selected path (??#5096`) | log M4 |
| M4 | t5 source `#2626` BuildArray on 639 (runs every `#637` iteration; `d1-build-plan.md:299` moves it ??1.2). t7 source = a terminal of diagram 639 itself (w3268: 2 source rows, 8 sinks incl. `#1114 'index i'`), a per-iteration value. t8 source `#3052` ControlReferenceConstant on 639 (a constant; `d1-build-plan.md:319` keeps it in 1.1). t3/t4 are OUTPUTS (consumers above) | log M4; `graph_s1_20260924.json` flags[0] |
| M5 | Queues into 1.7: `Q_res` DBL[] / `Q_good` Bool[] / `Q_rmeta` DBL, "the kernel's own outputs", unbounded, lossless FIFO (`d1-build-plan.md:574`); sentinels written by 1.2, exited on by 1.7 (`:653-654`); resolution table: `Q_res` src `#637 'x,y,z array out'`, `Q_good` `#637 'Bead is good? array out'`, `Q_rmeta` `#637 'current image number'`, all state A on `#686` (`:602-604`). `docs/cycle27-plan.md:930-933` names no queue; it says the owed work is a resolution table per queue | as cited |
| M6 | A delete-by-wire-uid verb exists: `stagekit.Stage.delete_wire(wire_uid)` (`tools/stagekit.py:527`) ??`build_opfsinnertunnelconnect_v0.del_wire` (`tools/recipes/build_opfsinnertunnelconnect_v0.py:336`, Wire-traverse index then `g.delete_object(verify=False)`); the row executor maps action `delete_wire` to it (`stagekit.py:861`). Used with a uid-census gate in `tools/bench/bench_map_20260923/b_endtoend.py:60-63` | as cited |

## Pre-decided (continues `docs/connectivity-map-plan.md`; only facts measured from files)

148. **Owed node sets** are `build_d1_v0.json` key `moved`: 17 ??1.2, 1 ??1.7 (1.5's 5 are done); cut rows
     A 26 쨌 B 38 쨌 C 3 쨌 W 12 (67 + 12), key `cut`. They are the prediction; P0's census on the bed is the address list.
149. **1.2/1.7's six shift registers are still on `#637`** in the bed (`graph_loops_m4b_20260924.json`, loop 637):
     `#1147 #5796 #119 #7311 #15 #24` (rights), paired `#1142 #5805 #2972 #11001 #51 #1108`.
150. **Loops b `#10170` (body `#23166`) and c `#23041` (body `#23405`) exist and are unassigned**
     (`docs/cycle27-plan.md:1081-1083`, `:1134-1138`: *"b and c are assigned when their node sets are named"*).
     **SUPERSEDED 2026-09-24 by Pre-decided 163 (assigned: 1.2 = `#10170`, 1.7 = `#23041`).**
151. **The kernel `#5058` is still on the frame loop** (`frame_diagram 639`, 16 terminals, 13 wired, rowD wiki);
     it is coupled to group A in BOTH directions: `#5540` t2/t6 ??`#5058` (w5637, w5975) and `#5058` t8 ??w121 ??
     `#10969`, `#10757`; and to group B: `#5058` t4 ??w505 ??`#2222`, `#2626` (`build_d1_v0.json` key `cut`).
152. **Cross-loop edges of the owed sets** (key `cut`): w10990 `#10757` ??`#10407` (1.2??.5); w10799 `#10686` ??
     `#10407` (1.2??.5); w4517 `#2626` ??`#376` (1.2??.7); w3268 frame index (iteration terminal of `#637`) ??`#376` t7.
153. **Rotor call sites** = SubVI uids `28094 27466 27194 27165 1566 35648 33882 33114 34890`, all `SetCommand.vi` from
     `instr.lib\Autonics Motor` (both wikis, `graph_summary.subvi_calls`). Their Traverse diagram indices moved
     24??9 ??115??18 between S1 and rowD, so `docs/motor-call-site-census.md:89`'s indices are NOT addresses; the uids are.
154. ~~**No replace-callee verb is recorded**: 0 hits for replace-subVI in `docs/toolkit-capabilities.md`,
     `docs/NAMES.md`, `tools/gscript.py`.~~ **CORRECTED 2026-09-24 (Pre-decided 160):** the search was too narrow ??
     `SubVI.Replace` method `635E001` is recorded at `docs/vi-server-ids.json:117` (UNVERIFIED, unbuilt, not unknown). Queue verbs DO exist (`docs/toolkit-capabilities.md:32`, `test_opqueue.log`
     7/7); the staged recipes `tools/recipes/stage_d1_*.py` contain 0 queue calls.
155. **`op_rule` maps every ControlTerminal row to `connect_ctl`** (`tools/jev_pairs.py:194-195`), and
     `connect_ctl` addresses the TOP-LEVEL diagram only (`tools/jev_pairs.py:157`); the six moving control terminals
     sit on `Diagram #639`. The v0 run's 6 control rows failed with error 5001 (`build_d1_v0.json` key
     `rewire.failed`) and its 18 tunnel rows had no route (`rewire.noroute`) ??the latter class now has
     `fs_inner_tunnel_connect` / `tunnel_outer` (`docs/connectivity-map-plan.md:96`).

## Pre-decided ??ADDED 2026-09-24 (cycle 69 judgement)

Decided by the cycle-69 judgement session on `archive/peer/2026-09-24-priorart-c69-split-plan.md`; applied to 짠1?벬?
above by a material session. These close O1's framing, O2, O3, O4's shift-register half, O6's placement/route, O7, O8.

156. **(J1) O2 and O4 are SETTLED** by `docs/cycle27-plan.md:749-757`, `:903-908` and `:94-107`, `:930-933`: the CPU
     kernel `#5058` MOVES (sub-stage K); shift registers MOVE WITH THEIR NODES (`SR_QUEUE_AUTHORISED` stays False). The
     queue RESOLUTION TABLE (34(g)) is still owed and is the plan row **QRT, which comes BEFORE STOP**.
157. **(J2) Order = `docs/cycle27-plan.md:903-908` 34(e), smallest-first: L7 stages come before L2 stages.** 짠2 is
     re-ordered to P0 ??L7-1 ??L7-R ??K ??L2-A1/A2 ??L2-B1..B3 ??L2-R ??QRT ??STOP ??ROT ??FIN. The old "Why L2 before
     L7" paragraph is superseded; its cost (w4517 made twice) is accepted.
158. **(J3) The control set and L2-B are REWRITTEN from the measured six controls**
     (`tools/recipes/build_d1_routeb_v7.py:443-453`, `tools/bench/build_d1_routeb_v7_run10.log:23-31`): Auto-Reset,
     Reset Tracking, Z/dZ, Correction Factor, Force smoothing `#28148`, Extension median `#28996`. `min value` and
     Force-vs-Extension are INDICATORS; `Diagram #639` holds 31 ControlTerminals. Every stage's row list is
     cross-checked against the independent census `tools/bench/d1_rewire_sources.json` (queue endpoints included);
     **every disagreement with `build_d1_v0.json` becomes a listed row, never a silent drop.** Every row ??the old
     L2-C rows included ??is UID-addressed, never index-addressed (`docs/d1-build-plan.md:356` is the old failure).
159. **(J4) A stage whose moved set contains a ForLoop shift register may not use `computation_diff` as a pass gate
     unless P0 has shown that no two ForLoop left SRs in the affected loops share a TOP** (`tools/vigraph.py:336-337`
     TOP pairing). Otherwise that stage's gate lists the TOP-collision rows explicitly as predicted artefacts.
160. **(J5) ROT stays AFTER the splits.** Its route is `SubVI.Replace` `635E001` (`docs/vi-server-ids.json:117`),
     which must first be MEASURED on a scratch copy, together with the Baseline/Ring constants at the nine sites
     (`docs/rotor-sign-diagnosis.md:124-126`). Pre-decided 154's "0 hits" line is corrected in place.
161. **(J6) O3: `#10686` stays on loop 1.1**, because Pre-decided 147(b) already reads it there for loop 1.5's cadence
     (so L2-C is removed; w10990 moves into L2-A1). **O7: the GPU top level is the default final file** (user
     2026-09-16); CPU comes later. **O8: THIS plan governs the remaining splits** and supersedes
     `docs/cycle27-plan.md:383-390` S3w-a?쫊 and `docs/d1-build-plan.md:679-682` S4?밪6 as stage tables (one-line
     superseded pointers added at both places).
162. **(J7) Route B v0?뱕7 died re-wiring this same set in memory. The difference that has to hold: each sub-stage
     SAVES its file and the next sub-stage starts from that file, in a FRESH LabVIEW instance.** Stated per stage in
     짠2's header line; a stage script that re-wires on an unsaved in-memory predecessor is the route-B failure again.

163. **(cycle 70 judgement) O1 CLOSED: loop 1.2 = WhileLoop `#10170` (body `#23166`); loop 1.7 = WhileLoop `#23041`
     (body `#23405`).** Evidence: S2's planned positions 1.2=(2600,2600) / 1.5=(2600,3400) / 1.7=(2600,4200)
     (`tools/recipes/build_d1_routeb_v7.py:793`, `tools/recipes/stage_d1_s2.py:432`); `#23041` sits at (2600,4200)
     (`tools/bench/stage_d1_s2_loops.log:75`); `docs/cycle27-plan.md:1137` already swapped 1.2??.5 by assigning
     `#23032` to 1.5, so 1.2 takes the remaining `#10170`.
164. **(cycle 70 judgement) L7-1 carrier scope.** Inputs to 1.7 that come from a PARALLEL loop (1.1 `#637`, or the
     future 1.2) are carried by QUEUES per `docs/d1-build-plan.md:308` 짠11b.3 ??never an indicator/Local (lossy for
     saved data = rule 1a). L7-1 therefore does NOT wire those rows; it leaves them OPEN and lists them. L7-1 DOES:
     move `#376` into body `#23405`; create 1.7's two new SR pairs replacing `#15/#51` (accumulator) and `#24/#1108`
     (error chain) on `#23041`, each new LEFT SR's initial value wired from the SAME top-level source that initialises
     the original pair (read on the live bed; top-level ??loop is a tunnel/SR-init row, not a crossing); wire every row
     whose both ends are inside 1.7 after the move (`#376` ??its SRs). The two re-feeds of `#6384` from 1.7 output
     tunnels and the retirement of the old pairs stay in L7-R.
165. **(cycle 70 judgement, after `tools/bench/stage_d1_l7_1.log:124-126`) SINGLE-CANDIDATE RULE.** A new-carrier row whose
     legal candidate set has EXACTLY ONE pair, and whose source uid+terminal equals the source of the corresponding S1 edge
     (acc_init: `#781 'initialized array'` via the original init wire w3543 ??the new left SR's outer terminal; likewise
     err_init: `#4910 'error out'` via w4969), is a RULE row: executed without a Jev PAIR decision, logged
     `RULE-SINGLE-CANDIDATE`. Jev PAIR decides only when there are ?? legal candidates; the 0.75 threshold is NOT lowered.
     Gate P2a becomes: every row with ?? candidates acts at threshold; every single-candidate row matches its S1 source.
     Prior evidence of the same class (cited 2026-09-24 per prior-art c70-l7-1-r2 A4):
     `archive/peer/2026-09-23-bench-map-b-endtoend.md:67,72` ??w7337's ONLY candidate, the physically correct one, scored
     p 0.464, likely because the intent line named a terminal that no longer exists on the live object (run 1's acc_init
     destination read `'total data array out'` on the new left SR, `tools/bench/stage_d1_l7_1.log:124`).
166. **(cycle 70 judgement) i6 (`#3644`), i9 (`#2294`), i11 (`#5096`) are OWNED BY L7-1**: values entering from top-level
     frame `#686` through tunnels on `#637` are re-made as NEW tunnels on `#23041` (`tunnel_outer`, rule rows, Pre-decided
     146) from the SAME outer source that feeds each original tunnel (re-read on the live file). Same class as SR-init:
     top-level ??loop, read at loop start, not a parallel crossing.
167. **(cycle 70 judgement) Outcome review `archive/peer/2026-09-24-outcome-review-20260924.md` disposition**: same five
     violations as 2026-09-21; the user answered the repeated verdict (2026-09-20 "怨꾩냽") and by the 2026-09-23 amendment a
     repetition of the same verdict does not stop the runner ??escalation marked in STATUS. "ROT first": not adopted,
     Pre-decided 160 keeps ROT after the splits; ROT's scratch measurement (`SubVI.Replace` 635E001 + whether
     `computation_diff` sees callee identity, O6) is parallel-safe and scheduled right after L7-R. "Supervised run of
     `D1_s3_loop15.vi`": needs the user present or rig 遺꾪빐 (it drives motors outside `motor_gate`) ??on record as STATUS
     OPEN 58; not done unattended.
168. **(cycle 70 judgement, after `tools/bench/stage_d1_l7_1_r2.log:85-90`) S1-MAPPED RULE ??Jev VERIFIES, does not
     gate on p.** A new-carrier row whose sink is determined by the stage's own old?뭤ew carrier mapping (old SR `#24` ??
     new R`#24083`/L`#24133`; `#15` ??R`#24150`/L`#24187`) together with the S1 edge's source uid+terminal is a RULE row,
     even with ?? legal candidates. Jev PAIR still runs on it as a CHECK: if Jev's top candidate == the S1-mapped pair
     the row is wired (log `RULE-S1-MAPPED p=<p> margin=<m>`, whatever p is); if Jev's top candidate differs, the run
     STOPS. Reason: `err_R` scored 0.756 (run 1) and 0.742 (run 2) with margin ??.57 both times ??the threshold sits inside
     run-to-run spread on a row whose answer is already fixed by the original. The 0.75/0.15 act threshold is unchanged
     for rows with no S1 counterpart.
169. **(cycle 70 judgement; CLAUDE.md "split and save" rule 3 ??the same stage failed twice at the same gate P2a with no
     saved artefact) L7-1 is SPLIT:** **L7-1a** = move `#376` into body `#23405` + create the two new SR pairs, NO wiring,
     then SAVE `claudeDev\D1_l7_1a_<ts>.vi` (broken by design ??GUI Ctrl+S, CLAUDE.md 짠3 rule 6); gate = `diff(bed,new)`
     = `#376` owner change + 4 new SR objects only, bed md5 unchanged. **L7-1b** = open THAT file in a fresh LabVIEW, wire
     the 9 rows (4 S1-mapped per 168 + 2 single-candidate per 165 + 3 top-level tunnels per 166), save
     `claudeDev\D1_l7_1_<ts>.vi`; gate = `computation_diff(S1,new)` = exactly the 8 rows of `tools/bench/l7_1_predict_r2.log`.
     Runs 1 and 2 did L7-1a cleanly twice (`stage_d1_l7_1.log:80-90`, `stage_d1_l7_1_r2.log:71-81`) and threw it away.
170. **(cycle 70 judgement, on `archive/peer/2026-09-24-c70-l7-1-jev-threshold.md` ??"half right") ACCEPTED, three
     conditions on 168/169:** (a) BEFORE L7-1a, run the review's offline test (a)??e) (`jev_pairs.ask_pair`, n=10??0, ??0
     calls, ??0.005) ??`err_R` spread, `acc_init` current vs CORRECTED intent line (the line must name the sink
     `#24187` 'total data array out' / the register as carrying `#376`'s output), `err_init` with the sink name blanked,
     and the negative swap case `#4910 'error out'` ??acc LEFT; record the five means/spreads. (b) The intent lines of
     every L7-1b row are corrected per (a)'s finding before L7-1b runs. (c) In L7-1b gate PB (`computation_diff`,
     recipe `:102`) is made `fatal=True` and runs BEFORE the save; a stage never saves over a failed PB. If (e) scores
     ??.75, the Jev argmax check in 168 is recorded as guarding nothing and the S1-mapped rows rest on PB alone.
     **MEASUREMENT for 170(a) (cycle 71 material, 2026-09-24 03:49, no LabVIEW; `tools/bench/jev_l7_1_offline.log:40-49`,
     `tools/bench/jev_l7_1_offline.json`, 88 Jev calls ??$0.007; not a decision):** (a) `err_R` as-is n=12: mean 0.755,
     min 0.71 / max 0.80, sd 0.026, top == S1-mapped 11/11, margin mean 0.575 (min 0.48) 쨌 (b) `acc_init` current line
     n=10: 0.584, 0.55/0.62, sd 0.021 (1 candidate) 쨌 (c) `acc_init` CORRECTED line (exact text `:16`) n=10: **0.906**,
     0.90/0.91, sd 0.005 쨌 (d) `err_init` sink name blanked n=10: 0.803, 0.79/0.82, sd 0.008 (was 0.848 named) 쨌
     (e) NEGATIVE `#4910 'error out'` ??acc LEFT outer, corrected line, n=10: **0.098**, 0.09/0.11, sd 0.007.
171. **(cycle 71 judgement, on the 170(a) measurement above) L7-1b INTENT LINES AND ROW MODE ??decided.**
     (1) **Every L7-1b intent line takes the CORRECTED form of case (c):** it names the sink by the terminal name
     as it reads on the LIVE object in the L7-1a file, re-read from that file. It never uses the old object's
     terminal name. For a register it says which node's output it carries (`#376`'s output for the accumulator,
     the error chain for the error pair). The sink name is never blanked: (d) blanked 0.803 < named 0.848. Reason:
     the current line to the corrected line took `acc_init` from 0.584 to 0.906 with sd 0.005, so the run-1 failure
     was the question's wording, not the row.
     (2) **The Jev argmax check in 168 is KEPT as a real guard**: the negative swap (e) scores 0.098, far below 0.75,
     so the check does separate a wrong source. 170(c)'s fallback ("rests on PB alone") does NOT apply.
     (3) **Row modes are unchanged from 165/166/168.**
       - S1-mapped rows are wired when Jev's top == the mapped pair, whatever p is (err_R: 0.755 짹 0.026, top ==
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
     - The edges are `1929:2043??048:3182`, `1929:2043??384:6480` and `5020:5050??384:6511`.
     - Wires w4337 and w5073 keep their uids and all three sinks, and all 7 terminal rows survive, which excludes
       (a) wire cut and (c) row dropped.
     - The tunnels' outer terminals turned non-source because `#376`, their only inside source, left `#637`. This is
       the documented undirected-tunnel behaviour, i.e. the review's (b).
     **The contract is tightened, NOT loosened** (the review warned that "touches `#376` or its tunnels" would admit
     real cuts). From now on a `diff` may remove an edge that does not touch the moved node ONLY if it is listed by
     edge in the prediction, AND its wire uid survives with every sink, AND its source is a tunnel whose only inside
     source was the moved node. For L7-1b and later stages these three edges are part of the BASELINE: they are
     absent from the L7-1a graph, and re-driving `#1929`/`#5020` would ADD an edge, which the L7-1b PC2 gate must
     catch. **`#1929`/`#5020` ??`#2048`/`#6384` are L7-R rows**: L7-R feeds them from 1.7 or replaces the tunnels.
     This is the same class as the "two re-feeds of `#6384`" in Pre-decided 164, and it is counted in L7-R's row list.
     Side fact kept for L7-R: the old `#15`/`#51` pair's name reads '' after the move (`diag_c71_l7_1a_tunnels.log:71-72`).
173. **(cycle 71 judgement, on `tools/bench/stage_d1_l7_1b.log:301-314`) Terminals are addressed by TERMINAL UID after
     their first resolution, never by name again ??a TOOL change in `tools/stagekit.py` (the user's 2026-09-24 tool
     permission; this class recurs, since shift-register terminal names change on move and on wiring:
     `diag_c71_l7_1a_tunnels.log:71-72`, `stage_d1_l7_1b.log:274`).**
     - **What the run showed:** all 9 rows were wired as decided. Every S1-mapped row had Jev's top == the mapped
       pair (p 0.884??.928), and the second-pass `Is Broken?` read False on 3 rows. The run then died in OUR
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
       addressing accepts unwired terminals", is REJECTED: `match_term_uid` maps uid ??node terminal index THROUGH
       the wire, so an unwired terminal has nothing to match on.
     - **Remedy:**
       - Stage the uids in a separate field (e.g. `verify_term_uid`) that only the second pass, `Is Broken?` and the
         gates read. First wiring never sees `term_uid`.
       - stagekit self-test: add a case where an end carrying `verify_term_uid` on an UNWIRED terminal is wired by
         name first, then verified by uid.
     - **STATUS: BUILT (cycle 72 firefighter, 2026-09-24 05:5x):** `tools/stagekit.py:690-696` ??`address` takes the
       uid path ONLY on `verify_term_uid`; the candidate field `term_uid` is ignored, so first wiring always resolves
       by name. Recipe `tools/recipes/stage_d1_l7_1b.py:96` passes `verify_term_uid` on the four second-pass ends.
       Self-test `tools/bench/selftest_stagekit.log` 47/0 (new I8 unwired end with `term_uid` wired by NAME 쨌 I9
       verified by `verify_term_uid` after the wire + rename 쨌 I10 `term_uid` alone never selects uid). Offline dry run
       of the recipe's ACTUAL rows (retrospective-cycle71 F2a): `tools/bench/dryrun_l7_1b_address.py` ??
       `dryrun_l7_1b_address.log`, 15 ends, PASS (the four r2 uids resolve by name; verify ends by uid only after the
       wire; an unwired verify end raises). 173's LIMIT text "L7-1b is not affected" was WRONG (r2 proved it) and is
       superseded by this entry.
     - **Budget:** L7-1b has now failed twice at DIFFERENT stages of our own tooling (r1 name-after-wire, r2
       uid-before-wire). Both are script defects with measured causes. So the "same stage failing twice at the same
       place" re-split trigger (CLAUDE.md split-and-save 3) does NOT fire: the row set and the saved L7-1a input are
       unchanged. The NEXT cycle starts a fresh failure budget for L7-1b run 3.

175. **(cycle 73 judgement, on "L7-R facts (cycle 73, measured)" above) L7-R DESIGN ??decided.**
     - **Loop-exit re-feeds, so rule 1a holds.** `#2048` (Array Subset) and `#6384` (`save N xyz traces.vi`) are on the top-level
       frame `#686` and read `#637`'s EXIT values. They are re-fed from `#23041`'s exit values of the same `#376` outputs:
       `#2048 'array'` ??the new acc RIGHT SR `#24150` outer (was `#15`, w3957) 쨌 `#6384 'error in'` ??the new err RIGHT SR
       `#24083` outer (was `#24`, w1899) 쨌 `#2048 'length'` + `#6384 'actual # data points'` ??a NEW output tunnel on `#23041` fed
       by `#376 'file progress'` (was `#1929`, w4337) 쨌 `#6384 'file # to append'` ??a NEW output tunnel fed by `#376 'file number
       to append out'` (was `#5020`, w5073). Each new tunnel's indexing mode must EQUAL its original's (`#1929`/`#5020`, read on
       the live file). The last iteration's value is the same value provided 1.7 runs `#376` on the same input sequence. That is
       the queue's job (QRT), so equivalence is structural here and functional only after QRT.
       `d1-build-plan.md:365-370` 짠5b already said "off 1.7's output tunnels".
     - **`#3453` `file progress` (an indicator on 639)**: its ControlTerminal MOVES into body `#23405` and is re-wired from
       `#376 'file progress'`. This is display-only, and the graph edge is unchanged. The route is `move_in` on a
       ControlTerminal, the O5 class. The prediction run measures it FIRST, on a dated scratch copy in the same LabVIEW
       instance, before the stage touches the work copy. If `move_in` refuses a ControlTerminal the run STOPS (a gate,
       not a branch) and judgement picks the route.
     - **`#3052` (`saved file refnum`, t8)** is a constant, not a per-frame crossing. It MOVES into `#23405`, and w1397's
       row is re-made inside 1.7, but only if `#376` is its ONLY consumer. That is measured in the contract; any other
       consumer ??STOP.
     - **t5 (w4517, `#2626` ??`current frame data array in`) and t7 (w3268, `#637` i ??`frame index`) stay OPEN.** Both
       change every frame and cross parallel loops, so by 164 they are queues. No planned queue carries them (M5), and
       `#2626`'s final home is 1.2 (group B). They are **added to the QRT row as owed rows**, and 1.7 becomes whole at QRT
       + STOP, not at L7-R. L7-R does NOT build a queue.
     - **Retire** (plan 짠3 rows, live-consumer check BEFORE each delete on the completed graph):
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
     - The cold ExecState 1 + cdiff 0 criterion of 짠3 for L7-R moves to the stage that makes the t5/t7 queues.

176. **(cycle 73 judgement, on `tools/bench/stage_d1_l7_r_r2.log` 61/0 ??`claudeDev\D1_s4_loop17.vi` md5 `4b621946??) L7-R ACCEPTED; four rulings.**
     - **(a) Handles.** The 짹100 criterion is the reference-hygiene test for REPEATED OP CALLS (CLAUDE.md, 20 calls flat).
       It does not apply to an editing stage: a stage that creates objects holds more handles while the VI is open.
       For editing stages the handle numbers are RECORDED, not gated (load / before-save / exit). A leak is judged
       only by the 20-call test on the ops involved. 짠3's "handles open?뭖lose 짹100" rows are superseded for L7/L2/K
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
     - **(d)** 짠3's L7-R rows `:159-160` (cold ExecState 1, cdiff 0) are superseded by 175: that criterion moves to the
       stage that builds the t5/t7 queues (QRT/STOP).

177. **(cycle 79 judgement, on `tools/bench/k_facts_79.log:91-169` run 3, `BGRUN END rc=0`, offline; result card
     `tools/bench/cards/result_79-1.json`) STAGE K DESIGN ??decided.** Input `claudeDev\D1_s4_loop17.vi` md5 `4b621946??,
     output `claudeDev\D1_k_<ts>.vi` (GUI save if ExecState 0, rule 6). `#5058` has 16 terminals, 13 wired; the bed wire
     equals the S1 wire on all 13 (`:97-146`). t5/t6/t10 stay UNWIRED (defaults, the same as the original).
     - **(a) MOVE:** `#5058` ??body `#23166` of `#10170` (1.2) by `move_in`.
     - **(b) SR pair `#119/#2972` is KERNEL-ONLY** (F3 `:150-161`: left `#2972` ??`#5058` t13 only; right `#119` ??w121
       from `#5058` t8 only). By 156 (SRs move with their nodes) K creates ONE new SR pair on `#10170`:
       - t8 ??new RIGHT and new LEFT ??t13 are S1-MAPPED rows (168/171, Jev argmax check).
       - The new LEFT's initial value comes from the same source as `#2972`'s, FSIT `#6239` on `#686`. That is a
         RULE-SINGLE-CANDIDATE row (165).
       - The old `#119/#2972` is NOT deleted in K. It is retired in L2-R with the other carriers, after the
         live-consumer check.
       - The three MIXED pairs stay in L2-A1: `#1147/#1142` (A+B+K), `#5796/#5805` (A+K) and `#7311/#11001` (no K).
     - **(c) Six top-level rows are re-made as NEW input tunnels on `#10170` (166, rule rows):** t2, t9, t11, t12, t14
       and t15. Each takes the SAME outer FSIT source on `#686` as its `#637` tunnel
       (`#2580`??#3862` 쨌 `#2396`??#2932` 쨌 `#4432`??#5287` 쨌 `#3656`??#3675` 쨌 `#3920`??#5659` 쨌 `#4031`??#5952`).
       Each new tunnel's IndexMode must EQUAL its original's, read on the live file (rule 1a: whole-array parameters
       stay non-indexed).
       - The old `#637` tunnels stay for any other inside consumer. A tunnel left with none is an L2-R retire row.
     - **(d) The two `#639` sinks of t8** (`Pos within cal image`, `Pos: Diffraction Pattern`; 79-1 OPEN 1) are handled
       like `#3453` in 175:
       - The contract first MEASURES each one's class. It must be a ControlTerminal that is an indicator, with w121 as
         its only source.
       - If so, it MOVES into `#23166` and is re-wired from t8 (rule row, display only).
       - Any other finding ??STOP (a gate, not a branch), and judgement decides.
     - **(e) Rows left OPEN by K** (the gate lists them one by one; none of them is wired in K):
       - t0 ??`#5680` and t7 ??`#6016` (tunnels of `#5540`, group A) go to L2-A1.
       - t3 ??`#5796` right goes to L2-A1, with that pair.
       - t4 w505 ??`#2626`, `#2765` (group B) and `#1147` right go to L2-A1/L2-B.
       - t8's sinks `#10969` and `#10757` (group A) go to L2-A1.
       - **t1 `Image In` ??`#6810 'Image Out'`** stays on 1.1 and crosses 1.1??.2 every frame. By 164 it is a
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
       11 wired rows (1 init + 2 S1-mapped + 6 tunnels + 2 indicator rows), inside the 10??5 batch size.
178. **(cycle 79 judgement, on result `79-3` FAIL 27/2 ??`tools/bench/sim_k_split.log:69`, review
     `archive/peer/2026-09-25-c79-sim-k-split.md` ANSWERED) three rulings. The failures are OUR gate definitions; the
     K design is unchanged.**
     - **(a) Contract measured, 177(d) holds:** `#3173`/`#9519` are indicator ControlTerminals whose sole source is t8
       w121, and the six originals have IndexMode 0 (`k_contract_79.log:28,31-42`). So they move, and the new tunnels
       are IndexMode 0.
     - **(b) The simulator gates are corrected as the review proposed (짠4):**
       - A0 becomes an OWNERSHIP check: `#5058` is owned by `#23166`, and `#23166` by `#10170`. Pixel offsets are
         never compared exactly.
       - P3 credits t3 by an end-graph source check (t3 is unwired; the old `#5796` right has no source) plus a
         negative control: a fake t3??#2626` edge must FAIL the gate.
       - A THIRD offline simulator run is AUTHORISED. The failure budget restarts on card 79-4. This is not the "same
         stage fails twice at the same place" trigger: run 1 failed on a data-file overwrite, run 2 on two gate
         definitions.
     - **(c) PB = the 10 rows the simulator lists** (`sim_k_split.log:24-33`): `#376`횞2 (L7), `#2626 'array'`,
       `#5696`/`#6085 'x,y,z array'`, `#10757`/`#10969 'array'`, and `#5058` t0/t1/t7. t3 has NO row of its own; its
       only S1 computation consumer is `#5058` t0, through the mixed pair `#5796/#5805` and the selector tunnels. So
       `#5058` t0's row covers it, and the end-graph source check in (b) proves it separately. ACCEPTED.
     - **(d) 177(b)'s "Jev argmax check" is WITHDRAWN** for `#119/#2972`. That pair is a register chain, and CLAUDE.md
       짠3 "Stages are SIMULATED", decision 3, puts chains under RULE-CHAIN-S1 (copied from S1, never asked of Jev;
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
         (`c79-k-x4.md:68-76`) are compared with the S1 graph. Present in S1 too ??a reader modelling artefact that is
         harmless to cdiff; absent from S1 ??a finding for the next cycle.
     - **(g) (cycle 79 judgement, on result `79-5` BLOCKED: `tools/bench/stage_d1_k_prerun_79-5.log:145-148`) TOOL
       NECESSARY ??the launch gate learns the simulator's own plan format.** `stage_prerun.plan_files`
       (`tools/stage_prerun.py:674-692`) accepts only a `decisions` row file. The simulator (CLAUDE.md 짠3 decision 7)
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
       - Remedy: measure the real graph after ops 1?? headless (is_source / wire uid of 2789/2792/5910/6253/2811).
       - Then widen the stagesim rule until its step-3 graph EQUALS that read, with a self-test on this case.
       - Then re-simulate, re-finalize and re-pre-run K. Run 2 is launched only if those pass (a gate).
       - `tools/stage_prerun.py` now pre-runs finalized `stageplan/1` files (79-6 T1?밫3; self-test 9/9).
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
       - ?뵷 **THE BED IS NOW `D1_k_20260925_100155.vi`.**
       - ?뵶 **CORRECTED the same cycle by retrospective-cycle79 (`archive/peer/2026-09-25-retrospective-cycle79.md:244-254`):
         ACCEPTANCE IS CONDITIONAL.** Both `wire_indicators` ops (plan actions 26/27, t8 ??`#3173`/`#9519`) raised
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
     - **(a) K STANDS ??the conditional in 178(i) is lifted.** `tools/bench/k_ind_read_80.log:40-45`: on `D1_k`,
       `#3173` and `#9519` are sinks of wire **23807**, whose single source is `#5058` term 5171 `'pos in cal image out'`.
       Its third sink is the K replacement register `RightShiftRegister #23508`. The labelled case on `D1_s4_loop17`
       reads the same source through w121 (`:28-35`), so the source is the same one. There are exactly 2 ControlTerminals
       with those labels, so `wire_indicators` made no duplicates (`:39,44`). w23807 survived Remove Bad Wires on a
       scratch (`:68-71`). The op's `target BROKEN after wiring` was the ExecState-0 false alarm that 178(i) described.
       Level: STRUCTURAL, never run.
       ?좑툘 The material session called RBW survival a proxy because "no read-only Is Broken? op exists". That contradicts
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
       ??DONE in the same cycle (80-4): `errorlist_check.py:309,323-336`, self-test 5/5, and an offline re-verdict of
       the cycle-80 json gives OK (`tools/bench/errorlist_recheck_80.log`). `stagexec` selftest T01-T15 passes 15/0.
180. **(cycle 80 judgement, on result `80-5` PASS 27/0: `tools/bench/l2a1_facts_80.log`, `??l2a1_tunflip_80.log`/
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
       짠3's L2-A1 row "w10990 wired" becomes "`#10757 'element'` ??`#23541` wired (179(b) reader), `#10686`/w10799
       untouched".
     - **(d) Reset controls:** `Auto-Reset` `#17487` and `Reset Tracking` `#5634` are ControlTerminals on `#637`'s
       diagram whose only other ends are group-A members (`l2a1_facts_80.log:279-323`). They move with group A, per
       짠2, and their rows are gated by the 179(b) reader.
     - **(e) Mixed pairs** `#1147/#1142`, `#5796/#5805`, `#7311/#11001` are initialised from `#686` (w2731/w5812/w11253),
       and their outers are unwired (`:324-341`). L2-A1 creates 1.2's four register pairs from these, under
       RULE-CHAIN-S1 (init source = the same `#686` FSIT; never asked of Jev).
181. **(cycle 80 judgement, on results `80-6` PASS 13/0 and `80-7` PASS 35/0) 180(a)??c) are DELIVERED. L2-A1 may now
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
     - **(c) 180(c) is CONFIRMED** (`tools/bench/ct23541_facts_80.log` C1?밅4):
       - `#23541` is the indicator `'index'` on `#639`, with a sole writer (w23556 from `#10757 'element'`).
       - Its only reader is Local `#23523`, in WhileLoop `#23032`, feeding `#10978`.
       - `#23541` moves with `#10757` into the 1.2 body.
     - **(d) L2-A1's row set** = group A (8) + `#17487` + `#5634` + `#23541`. It adds 1.2's register pairs from the three
       mixed pairs under RULE-CHAIN-S1. Its re-wires are:
       - K's open rows t0, t3, t4, t7, and t8??#10969`/`#10757`;
       - the reconnect table the refit simulator computes, including the 3 member edges at `#10247`.
       Gates: frame-keyed cdiff; the 179(b) reader on every ControlTerminal row; the 181(b) frame-uid check.
       PB = the simulator's finalized open-row list. There is no whitelist (179(c)); a `sink_gates` entry is allowed
       only for a ControlTerminal sink that the reader gates.

182. **(cycle 81 judgement, on results `81-2` BLOCKED and `81-3` FAIL 4/1: `tools/bench/sim_l2a1_81.log:15-23,59`,
     `tools/bench/l2a1_partners_81.log`, review `archive/peer/2026-09-25-hyp-sim-l2a1-81.md`) the five `#639` partners
     are decided and the simulator failure is split in two.**
     - **(a) Constants `#10739` (??#10950 'y'`, w10850) and `#10929` (??#10757 'index'`, w10947) MOVE with their only
       consumer.** Each is the sole source of a single group-A sink (`l2a1_partners_81.log:21,25`). A diagram constant
       has no state, so where it sits is scheduling only (rule 1a).
     - **(b) Indicator `#17272 'min value'` MOVES with `#10969`, on the 181(c) precedent.** Its sole writer is `#10969`
       (w17287), it has 0 Locals/Globals, and its only reader is the labelled Property `#17289`, which is itself
       group A (`:27-32`). The row is gated by the 179(b) reader.
     - **(c) `#10382 Not` (x ??`#9647`, w9921) and `#11529 Less?` (x ??w11389 from the group-A side) STAY on 1.1.**
       Both feed `#10886` there (`:6-13`). These are 1.2??.1 crossings, and PD156??61 (O4 closed) send every such
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
     `tools/bench/sim/l2a1/stageplan_l2a1.json` md5 `73e95bc7??. It may be built.**
     - **(a) The un-flip rule is ACCEPTED as measured.** On a D1_k scratch, re-sourcing the outers from the new 1.2
       register turns the inners of `#5702`/`#5725` back into sources, and the output tunnels `#5680`/`#6016` flip back
       in cascade. `stagesim.py:374` reproduces this (`selftest_stagesim_unflip_81` 8/0; the old self-tests still pass).
       `#5825`/`#10750` are modelled by the same rule but were not read. The run's per-step comparison E1 is the
       backstop (181(a)3).
     - **(b) The source of the re-wired outers is the new 1.2 register (plan row `sr2_L0`), not `5817` on `#637`.**
       This is what 180(e) + RULE-CHAIN-S1 mean: the mixed pairs become 1.2's registers, and the tunnels inside 1.2
       read them there. The other choice would be a cross-loop wire.
     - **(c) PB row `(9703,'x')` is QRT-owed, the same class as 182(c).** It is the S1 edge `#10978` inner ??`#9703`,
       whose outer was fed from `#10757` (w23556), so it is a 1.2??.1 crossing. PB = the 9 rows at
       `sim_l2a1_81b.log:73`. Of these, `5058 'Image In'` and the `376`/`2626`/`5696`/`6085` rows are K's
       and the earlier stages' open rows carried forward.
     - **(d) `sink_gates`** = `rw_10988_17272` only (ControlTerminal `#17272`, gated by the 179(b) reader).
     - **(e) (after result `81-6` BLOCKED at stagexec X3) `move_in` rows carry `pos` from the PLAN, never from the
       recipe.** `sim_l2a1_81b.py:56` omitted the field that `sim_k_split.py:70-72` sets. The builder sets
       `pos` = each node's base position (K's convention). The stageplan is re-simulated and re-finalized, and it gets
       a new md5, which supersedes `73e95bc7??. A scratch probe with the same `pos` compiled 42 ops with every STEPX
       diff 0 (result 81-6). This is decision 8 of "Stages are SIMULATED": a recipe never re-types row content.

184. **(cycle 81 judgement, on result `81-6` FAIL: `tools/bench/prerun_l2a1_81b.log` X4) the finalized stageplan is
     now `tools/bench/sim/l2a1/stageplan_l2a1.json` md5 `329d89ee??, which supersedes `73e95bc7?? (183(e) re-sim 18/0,
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
     Ops 1??7 had step diff 0. Nothing was saved and D1_k is unchanged. The failure is a real-vs-simulated READER
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
     Then dry ??pre-run ??run 2 of 2. If run 2 fails, a third run needs a judgement retry card.

## OPEN (design choices ??for judgement; not decided here)

> 2026-09-24: O2, O3, O4 (SR half; the queue half is QRT), O6 (placement + route), O7, O8 are CLOSED by Pre-decided
> 156??61. O1 is CLOSED by Pre-decided 163 (2026-09-24). O5 stays open (prior-art: `connect_nested` refuted,
> `docs/cycle27-plan.md:108-114`; helpers = `probe_move_ctlterm_v0.py:327-351` route and the `Z/dZ` temp-sink chain
> `docs/cycle27-plan.md:115-117`).

- ~~**O1 loop identity.** Which of `#10170` / `#23041` is 1.2 and which 1.7 (Pre-decided 150). Arbitrary but binding
  once named (`docs/cycle27-plan.md:1137`).~~ **CLOSED by Pre-decided 163.**
- **O2 the kernel.** `docs/cycle27-plan.md:752` says relocating `#5058` (CPU) *"is what S2 must do"*; S2 did not
  (Pre-decided 151); `build_d1_v0.json` moved 17 without it (route A deleted it for `GPU_kernel_v1.vi`,
  `docs/d1-build-plan.md:287`). If A and B go to 1.2 while `#5058` stays on 1.1, the reseed feedback
  `#5540 ??#5058 ??#10969/#10757` crosses loops in both directions every frame ??a **rule-1a doubt** (a one-frame
  lag across loops changes the tracking inputs). Does `#5058` move with 1.2 (as sub-stage K before A1)?
- **O3 `#10686` ownership.** The bed's 1.5 cadence (Pre-decided 147(b)) is the rising edge of `#10686`, which
  today is evaluated on 1.1 next to the iteration counter; `docs/d1-build-plan.md:304` moves it to 1.2. Moving it
  puts its inputs (`x` w3050, `y` w9105, from 1.1's `i mod Frame rate` chain) on a crossing ??**rule-1a doubt** on
  *when* the schedule is evaluated. Stay on 1.1, or move?
- **O4 transport.** `docs/d1-build-plan.md:36-38` 짠11c makes queues + sentinels binding for every crossing and for
  the stop (S4/S4s `:679-680`); the staged S3 used S3a indicators + a Local read and no queue (Pre-decided 154). Which
  carrier for the four crossings of Pre-decided 152, and hence what STOP contains?
- **O5 nested ControlTerminal rows.** Pre-decided 155: the rule's only verb for ControlTerminal rows cannot address
  `#639` / a loop body. Moving the six terminals with their nodes (build-plan `:409-410`: a tunnel changes *when*
  `Reset Tracking` is read) needs a verb decision (`wire_indicators` / `connect_nested` / a new rule entry).
- **O6 ROT.** Placement (proposed last-before-FIN) and route: no replace-callee verb exists (Pre-decided 154), and
  whether `computation_diff` sees callee identity is unmeasured ??a scratch control is owed before ROT's gate means
  anything. Pre-decided 133 is user-directed (CLAUDE.md 1b, signed rotor), so its 9 rows are the only rule-1a
  change this chain is allowed to carry.
- **O7 final name.** `docs/cycle27-plan.md:390` names the result `Track_v6_D1_GPU.vi`, while `:749-756` says the
  kernel is the CPU one and the GPU swap is its own later stage.
- **O8 which table governs** ??짠4's conflict: this page, `docs/cycle27-plan.md:383-390`, or `docs/d1-build-plan.md:675-682`.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---
<!-- STOP line removed 2026-09-25 on the user's word ("?몄젣?ㅽ듃 ?댄썑 ?щ꼫 ?쒖옉"); full ingest archived + 9 contradictions resolved (archive/ingest/2026-09-25-full-20260925-protocol-simulator.md). -->

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??**`archive/2026-09-19-status-cycle47-relocate.md` (latest ??T2's block diff and what it closes, the readable-ORIGINAL correction, the five killed retrospectives)** + `archive/2026-09-19-status-cycle39-judgement.md` + `archive/2026-09-18-status-cycle34-n1.md` + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
??**DELIVERED:** ?윟?윟 **D1 S3 loop 1.5 = `claudeDev\D1_s3_loop15.vi` md5 `1a11d92aacabf7ec844d65b8af19f39f`** (482,312 B; byte copy of `D1_s3b_m4b_20260924_004214.vi`, kept; `tools/bench/promote_d1_s3_loop15.log` 5/0; ExecState 1 warm+cold, `computation_diff(S1,쨌)` 0 rows; STRUCTURAL + graph-equivalent under ASSUMPTION A, NEVER RUN; `docs/connectivity-map-plan.md` Pre-decided 147) 쨌 D0 (cycle 31) 쨌 N1 ACCEPTED (cycle 34) 쨌 D1 **S1** `claudeDev\D1_s1_copy.vi` md5 `3e3d23ce?? 쨌 D1 **S2** `claudeDev\D1_s2_loops.vi` md5 `6ff19497?? 쨌 D1 **S3a** both halves (`??boolcarrier_b3_20260921_010034.vi` md5 `dc14dd00??, `ExecState` 1, `Is Broken?` False) 쨌 D1 **S3b rows 1 and 2**. ?뵷 **THE CURRENT BED IS `claudeDev\D1_k_20260925_100155.vi`, md5 `6cf5b077?? (stage K, cycle 79, 2026-09-25; ExecState 0 by design) ??every next stage starts FROM THAT FILE; `D1_s4_loop17.vi` md5 `4b621946?? (L7-R) is its input, kept; every other "bed" named below in this line is HISTORY (`D1_s3_loop15.vi` md5 `1a11d92a?? is kept as the S3 deliverable).** ??**M3a-1 DELIVERED (cycle-63 firefighter, run 5, 2026-09-22 01:0x): `claudeDev\D1_s3b_m3a_BROKEN_20260922_005732.vi` md5 `6b3c1f3c??, 22 gates pass / 0 fail, bytes DIFFER from the bed.** ??**M3a-2 DELIVERED AND INDEPENDENTLY VERIFIED (cycle 64, 2026-09-22 02:3x??2:5x): `claudeDev\D1_s3b_m3a2_20260922_023029.vi` md5 `3842f5e6f128226235dc78353f26ef44`, 303,823 B, 25 gates pass / 0 fail on the build and 15/0 on a separate read-only check anchored at the REGISTER UID. ?뵷 EVERY NEXT STAGE STARTS FROM THAT FILE.** ?뵶 **M3a-3b (ROW D) IS **NOT** DELIVERED ??NO FILE. ?좑툘 CORRECTED 2026-09-22 15:4x (prior-art `archive/peer/2026-09-22-priorart-c87-rowd-stagekit.md` A3): the standing reason given here ??*"its W1 gate measures that NO writer on disk can address a `FlatSequenceInnerTunnel` terminal sink (`tools/bench/c78_rowd_writer.log`)"* ??HAS BEEN FALSE SINCE CYCLE 82. `OpFsInnerTunnelConnect_v1.vi`'s `Wire Source` half IS the FSIT `LeftTerm` property node (`tools/bench/build_d1_m3a3b_d3.log:28`, `term_uid=7488`/`uid_back=7468` on 20/20 calls at `:58-60`), and `tools/bench/diag_c86_norbw.log:87`/`:97` records it WRITING wire 25324 onto `#7488`. THE REAL REASON ROW D HAS NO FILE IS THAT NO RUN HAS YET SAVED ONE. ?윟 **CYCLE-86's MEASUREMENT OUTCOME, never recorded until now: `tools/bench/diag_c86_norbw.log` (14:46) answered plan entry 111a YES on a byte-identical scratch of the bed with Remove Bad Wires rebound to a raising guard ??after `del_wire(7506)` `#7468` STILL RESOLVES (`uid_back=7468`, `:74`), `#7488` comes back BARE (`wire_a=0`, `:76`), the inner wire 7448 survives (`:77`), the connect then writes wire 25324 onto BOTH ends (`wire_delta 1`, `:87`/`:97`) and the net ends with ONE source owner `RightShiftRegister #23868`, `#4334` off, PD85 0, `Is Broken?` False (`:105-110`). It SAVED NOTHING and deleted its scratch (`:113`), and the log has NO `BGRUN END` (truncated mid-cell-B), so D5/D6/D7 were never reached.** THE BED IS STILL `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e??, 306,951 B.** Both initial-value rows land the predicted source (`FlatSequenceInnerTunnel #4194` ??LEFT `#23880`; `#3974` ??LEFT `#23909`), the originals stay on their nets, `Wire.Is Broken?` False in a separate ordered pass, PD85 violations 0 on every walk. Still BROKEN BY DESIGN and NEVER RUN (34(f)); `ExecState` 0's cause is formally OPEN and is neither gated on nor reasoned from. The artefact is BROKEN BY DESIGN (uninitialised SRs ??initial values are stage M3a-2) and is NEVER RUN (34(f)). Two root causes were repaired and MEASURED on the way: the identity reader `wire_source_owner` (history-echo, now error-checked + uid-echo-verified, acceptance `diag_c68_echo_accept.log` 8/0) and `gscript._lv_gui` (unquoted spaced args = PowerShell parse error, so NO Evidence-carrying GUI action had EVER dispatched ??`archive/peer/2026-09-22-c72-guisave-foreground-r2.md`). The bed is byte-unchanged and all four md5 pins hold. S3-as-37(g)-defined is WITHDRAWN (cycle 53). **Read `docs/cycle27-plan.md` Pre-decided 84??0 BEFORE 78??3 (78/80/81/82 are WITHDRAWN)**, then 46, 42, 43, 44. Full chronicle VERBATIM ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠2; banner VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠3; facts `??cycle31-d0-delivered.md` 짠1?벬? (read **짠4** before the first D1 click).
?좑툘 **SUPERSEDED, NOT A BED ??`claudeDev\D1_s3b_m3a3b_rowD_20260922_153612.vi`, md5 `c9d38bb194013ac7b916d073466078c7`, 307,093 B.** It is KEPT on disk (a real saved intermediate the user can open) but NO stage starts from it: it was saved carrying an unpurged second-pass junk `Invoke` (`Node` 636, `Diagram #686` 28 nodes). The Row-D bed is whatever the CLEAN re-run leaves ??**tell the two apart by this md5, never by the timestamp** (the `_REJECTED_?? rename is refused by the permission layer, as it was for `D1_s3b_m3a3_20260922_075611.vi`). Written 2026-09-22 16:1x as prior-art `archive/peer/2026-09-22-priorart-c87b-rowd-clean.md` A1's release.
?넅 **USER RULE 17:5x = `docs/cycle27-plan.md` Pre-decided 9 ??EVERY GUI action is capture ??locate ??act ??capture ??confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.


## START HERE
1. **Cycle plan = `docs/cycle27-plan.md`** (cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **짠A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`. ?넅 **2026-09-18 (user, TRIAL): codex's roles ??claude roles** ??failed prediction = `-Agent claude -Role hypothesis` SINGLE arm (`-Dual` only for a second opinion on our own tools); `-Kind fact`/`-Kind prose` with no `-Agent` ??fable/low thin; `outcome_review.py` ??fable/medium thin. Check routing free with `-DryRun`.
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌 `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**. ?좑툘 `BUILD_RE` also fires on a plain `cp a.py tools/recipes/b.py` ??quote both paths (cycle23-close 짠3).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  relocated_c81: lock keys owner_c74m8s3/owner_c74m8/owner_c73l7r/owner_c72ff/relocated_c72/owner_step6/owner_step5b2/owner_step5b/owner_step4b/owner_step4/step4_delivered/owner/v1_delivered/purpose/step3_delivered/owner_s1s2/purpose_step1_delivered/purpose_s2_delivered/known_limit_s3/purpose_s1s2/relocated_c68 RELOCATED VERBATIM -> `archive/2026-09-25-status-cycle81-relocate.md` 짠1
```
?뵷 **THE WHOLE CHAINED `purpose:` NARRATIVE ("PREVIOUS PURPOSE, unchanged and still true ????, cycles up to 64, 12,560 bytes on one line) RELOCATED VERBATIM (rule 4) ??`archive/2026-09-22-status-cycle64-locknotes.md` 짠1** ??nothing deleted, nothing rewritten; the `purpose:` key above now states only the CURRENT state.
?뵷 **ALL 50 HISTORICAL LOCK-BLOCK ENTRIES (cycles 48??7: 48 `owner_*`/`lock_*` keys, the superseded `status:` line, and the `motor:` key) RELOCATED VERBATIM (rule 4) ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠1** ??that file also carries the three older `lock_relocated_*` pointers (into `??cycle5556-relocate.md`, `??cycle54-relocate.md`, `??cycle5153-relocate.md`, `??cycle49-relocate.md`, `??cycle48-lockkeys.md`). **Motor state, unchanged and still true:** limits LEFT ON since 2026-09-18 15:37 (PI TMN 0 / TMX 39 in RAM, ASI SL/SU 짹2 mm), ports closed. ?좑툘 The motor clause quoted in this line is HISTORICAL; the live motor state is the rig-state line below.
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED** (machine key `rig-state:` below)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE (user 2026-09-23 14:2x "?ㅽ뿕 留덉묠")** = camera ?? motors/ASI ONLY through `tools/motor_gate.py` inside the envelope, LabVIEW allowed 쨌 ?ㅽ뿕以?= ??????and no LabVIEW use (was the state 12:3x??4:2x; header corrected 2026-09-23 23:4x by the cycle-68 material session). ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state change**.
Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`. **No beads on the rig.**
?넅 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies** (user, 2026-09-18 15:2x at the
rig). PI `SPA 1 0x15/0x30` ??TMN 0 / TMX 39 (RAM, **never WPA**) 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525, Y ??.7744?╈닋0.7744 (persistent, **never SS Z**),
written+verified by `py tools/motor_gate.py --session start|end` from the user-editable `tools/bench/motor_limits.json`; `--execute` refuses without the session file (tools/bench/motor_session.json, present ONLY while a session is open) **and** a fresh matching readback.
The gate still refuses ?ㅽ뿕以? every ASI home/zero/save, PI GOH/FRF/DFH/RON/POS/SPA/WPA and all rotor motion (self-test `selftest_motor_gate2.py` 85/85, 2026-09-24; FAIL-exit self-test 10/10).
rig-state: 議곕┰   <!-- 2026-09-24 20:xx USER GRANT: "?밸텇媛??닿? 留먰븯湲??꾧퉴吏??紐⑦꽣 ?묒냽 ?덉슜?? ?ㅻ쭔 ?먯젏 ?뺤씤 諛?紐⑦꽣 由щ컠, ??媛吏??瑗??뺤씤 ?꾩슂" ??motors (PI, rotor, ASI) may be driven by the gate AND by a running main VI while the rig stays assembled, until the user withdraws it; PI reference + verify at session start and limits set/released with readback are never skipped; "?ъ씠??醫낅즺?섍퀬?쒕뒗 ?쒕?濡?LabVIEW ?꾨뒗寃??딆? 留먭쾬 (?뱁엳 移대찓?쇨? 怨꾩냽 Acquisition ?섎㈃ 湲곌퀎??醫뗭? ?딆쑝??" = runner end hook closes LabVIEW and verifies the process is gone. Earlier: 2026-09-23 14:2x user: "?ㅽ뿕 留덉묠. ?ㅼ떆 ?몄뀡 ?ㅼ뼱媛??臾닿??? ??rig stays assembled; motors/ASI only through motor_gate inside the envelope, LabVIEW allowed. Before: ?ㅽ뿕以?13:43 ("吏湲??ㅽ뿕以묒씠??) ??limits RELEASED and read back (PI 0..52, ASI 짹500, `tools/bench/motor_session_end_20260923c.log`), PI referenced at 0 (FNL, 13:36), servo on; no motor/ASI/camera/LabVIEW use until the user says otherwise. Earlier 13:3x, on the user's order ("?덇? ?쒕쾲 PI 紐⑦꽣 ?吏곸뿬蹂쇰옒? 0?쇰줈 ?대룞, 5珥??뺤?, 30?쇰줈 ?대룞, 5珥??뺤?, 0?쇰줈 ?대룞"): PI test moves through the gate to diagnose "PI doesn't respond to the main VI". Before that: ?ㅽ뿕以? restored 2026-09-23 13:11 after ONE `motor_gate.py --session end` on the user's order ("寃뚯씠?몃줈 ?댁쨾"): limits RELEASED and read back ??PI TMN 0 / TMX 52, ASI SL/SU 짹500 mm, position unchanged (`tools/bench/motor_session_end_20260923.log`). Set ?ㅽ뿕以?2026-09-23 12:3x on the user's words ("?닿? 怨??ㅽ뿕???쒖옉?섎땲 ??LabVIEW ?쒖슜? ?섏? 留먮룄濡?) ??no motor, no ASI, no camera, and NO LabVIEW use at all until the user announces otherwise. Previous: 議곕┰, set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand ??the three ??lines VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md` 짠4
??tunnel ops BUILT + FUNCTIONALLY VERIFIED (38/38, ?좑툘 **do NOT re-run the recipe, run 1 is the record**) 쨌 ??the "ZERO runnable experimental VIs" gap is BROKEN ??`tools/bench/drive_original_copy_v5.py` drives a plain copy of the original unattended end to end, twice 쨌 ??N1 accepted ??the GPU kernel is cleared for D1. **Order is D0 ??D1 ??D2** (`docs/cycle27-plan.md` Pre-decided 1). Prose VERBATIM ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠3; earlier ??`archive/2026-09-18-status-cycle22-close.md` 짠2.

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; the five CLOSED items (32 쨌 55 쨌 56 쨌 51/52/52a 쨌 53's mechanical half) VERBATIM in `archive/2026-09-19-status-cycle46-relocate.md` 짠5, which forwards to `??026-09-18-status-cycle36-relocate.md` 짠5?벬?. ?좑툘 Two riders survive there: 32 is NOT to be closed unilaterally (the next outcome review judges it), and `audit_cycle` C4 still understates spend (retrospective-cycle31 F4). Only the live items below.
38/39/41. ?윞 **LIVE PART ONLY: `SR_QUEUE_AUTHORISED` stays False for good; `TEMP_SINK_AUTHORISED` is True for the `Z/dZ` row only** (Pre-decided 13 + 13a), and `Z/dZ` is now MEASURED WIRED (Pre-decided 19). `VI.Get Errors` 452 NOT built and `docs/d1-route-b-plan.md` 짠10 NOT AUTHORISED. ??the stall-watchdog liveness item is CLOSED by cycle 40's repair. Full text + run-3 history ??`archive/2026-09-19-status-cycle40-close.md` 짠2.
53. ?뵶 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** ??i.e. that 0??9 still fences the intended physical window. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠9; dispositions `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. ?뵶 **TWO RULES YOU MUST FOLLOW, reasoning relocated ??`archive/2026-09-19-status-cycle40-close.md` 짠3.** (a) **The retrospective is the LAST thing a session runs** ??`guard_bash.py:226-227` marks the session retro-done on ANY `retrospective.py` in command position, and `guard_session` then refuses every later dispatch; nothing clears the mark. (b) **Dispatch in the FOREGROUND and wait; when something must run in the background, HOLD THE TURN OPEN until it lands** ??a `claude -p` session cannot take results as they arrive, and ending the turn kills the child. Repair named, deliberately NOT BUILT.
42/43/46/47. ?윞 **LIVE PART ONLY** ??42 ?좑툘 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed (?좑툘 A4 counts a whole DAY, so it charges the previous cycle's files to this one ??retrospective-cycle40 F4) 쨌 46 ??**CLOSED 2026-09-23 ??FALSE PREMISE**: `SetCommand_signed.vi` IS on disk (`claudeDev\SetCommand_signed.vi`, md5 `ec87a265??, hardware-verified 2026-09-14); the "no disk" claim was a search-scope artefact. The real remaining item is the stage-2 repoint of the nine rotor call sites (Pre-decided 133) 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry.** 43 and 48/48a/49/50 ??CLOSED. Full text ??`archive/2026-09-19-status-cycle40-close.md` 짠4.
57. ?윞 **NEEDS JUDGEMENT RATIFICATION (cycle 68, material):** `guard_peer.py` now (a) formats its refusal through a drive-safe `_rel()` ??the same helper `guard_cycle.py:518` has carried since 2026-09-17; without it the hook RAISED instead of refusing when the failing log sat on another drive (`tools/bench/jev_discharge.log:21-26`, rc=99) ??and (b) skips a failing log whose LAST `BGRUN START` command is a **Jev script**, the other half of the user's 2026-09-22 "Jev??硫댁젣" exemption (until now wired only into `RUNNER_RE`, the COMMAND side, so a Jev self-test bundle's fixture text ??`STOP:`/`FAIL` by construction ??armed the gate against every other run). Scoped by the COMMAND, never the filename. Self-test `tools/bench/selftest_guard_peer_jev.py` **17 pass / 0 fail**, two new cases: C7 (a newer Jev log does not become the blocking log) and C7b (a non-Jev build that merely MENTIONS a Jev script still gates).
58. ?윞 **FOR THE USER ??three known limits of the new autofocus loop (loop 1.5) in `D1_s3_loop15.vi`** (decision: `docs/connectivity-map-plan.md` Pre-decided 147(b)). The new loop starts an autofocus when the "focus now" signal switches from off to on. (1) If **Frame rate** is set to 1 the signal is on every frame, so the new loop focuses once instead of every frame. (2) If you run the VI again without reopening it, the first autofocus can be skipped when the previous run stopped on a focus frame. (3) If loop 1.5 falls more than one frame (~11 ms) behind, that one scheduled autofocus is skipped; focus values are not saved data. Tell us if any of these matters for your experiments.

## NEXT
?뵶?뵶?뵶 **FIRST ACT (cycle 81, device-failed threshold 1, retrospective-cycle80 `archive/peer/2026-09-25-retrospective-cycle80.md:266`) = the cycle-start Error List hook re-uses the saved raw JSON when the bed md5 is unchanged.** It re-verdicts that JSON offline with the current checker, and does a GUI read only when the md5 changes. Self-test both branches.
Also small, in the same material card:
- The card-flag hook exempts the pure-Python `stagexec.py selftest`. In 80-4 a `labview: read` flag was used to get past the hook.
- Check `Wire.Is Broken?` 6371004: does a read-only op exist (CLAUDE.md says BUILT; 80-2 said none)?
- Relocate STATUS (160 lines).
Caveat carried: the stagesim refit's truth fixture is a reconstruction (old sim 짹 the recorded compare), not a real terminal table. Replaying K now needs 2 `sink_gates` declarations.
?뵶?뵶 **THEN (cycle 81) = STAGE L2-A1 from the bed `claudeDev\D1_k_20260925_100155.vi` md5 `6cf5b077??, following `docs/d1-loop12-17-split-plan.md` Pre-decided 179??81** (machine copy `tools/bench/next.json`; advances M3/R1/R3).
(1) Material, small task: register the 80-6 `move_in` params in `tools/bench/opmodels/move_in.json` `sim` (PD181(a)1).
(2) Simulate and finalize the L2-A1 `stageplan/1` on D1_k.
- Rows are set by PD181(d): group A (8) + `#17487` + `#5634` + `#23541`, plus 1.2's register pairs from the 3 mixed pairs (RULE-CHAIN-S1).
- Re-wires: K's open rows t0/t3/t4/t7/t8, plus the simulator's reconnect table.
- The gate is the frame-keyed cdiff (`vigraph.computation_diff_frame`) plus the frame-uid-set check (PD181(b)).
- If the plan orphans a wired class-`Tunnel`, measure that branch on a scratch first (PD181(a)2).
(3) Write a ??20-line `tools/recipes/stage_d1_l2a1.py` on stagekit/stagexec. There is no whitelist; `sink_gates` is allowed only for ControlTerminal sinks, which the 179(b) reader `tools/bench/diag_ctlterm_read_80.py` gates. Then dry ??pre-run ??prior-art ??one run (retry cap 2).
Still owed: `selftest_launch_gate.py` has 8 stale cases (C2-C6, M4-M6).
?뵷 **CYCLES 68??0 DONE records, old FIRST ACT paragraphs and carries RELOCATED VERBATIM ??`archive/2026-09-25-status-cycle81-relocate.md` 짠2** (card 81-1). Still-live items there, one line each:
- ?윞 FOR THE USER: `.claude/settings.json` guard_session matcher `Agent|Task` ??`Agent|Task|SendMessage` (only you can apply it); `git commit` at cycle close needs your approval-list entry (짠2).
- ?뵶 Rule: desk-check PREDICTED VALUES, not only gates ??Pre-decided 132 (짠2).
- ?윞 Carries not ahead of the deliverable: cp949 print helper in stagekit, audit A1 vs `jev_gate.log`, bgrun END guarantee under a tree kill (짠2).
- ?좑툘 Per-session cap 180 min: write `## NEXT` by minute 150; every new stage/diagnostic ??20 lines on stagekit (짠2).
- Still the user's to overturn: N1 on the pre-bead-loss window, bead-4 FLIP mask, harness records 60 controls and sets none, `background VIs_COPY` untouched (짠2).

## Where to look ??**`docs/handover-2026-09-22.md` (???몄뀡? ?닿쾬遺??** 쨌 `CLAUDE.md` 쨌 `docs/secrets-and-handover.md` (API keys, ?ъ슜??援먯껜 泥댄겕由ъ뒪?? 쨌 `docs/jev-integration-plan.md` (Jev ?쎌엯 ?먮━, 2026-09-22) 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.

## RUNNER STOPPED history (2026-09-22 09:58, 2026-09-24 07:29, 2026-09-25 01:02, 2026-09-25 10:30) ??`archive/2026-09-25-status-cycle81-relocate.md` 짠3


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"priorart-c81-l2a1-r5-stagexec","verdict":"<one of: novel | settled-already>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

The run-1 failure is now covered, so I'm writing up the verdict. The attached recipe is unchanged from run 1 (md5 `e589dc74…`), and the new element is the PD185 addressing tool added to `stagexec`.

## Verdict: novel

This is run 2 of 2 of the L2-A1 recipe. Nothing blocks it: the one prior failure of this exact recipe now has a measured cause, a built fix, and a pre-run that passes on the fixed toolchain.

### Part A: the direction

- **A1, already settled:** no finding. PD185 (`docs/d1-loop12-17-split-plan.md`, cycle 81) decided the next sequence: build the addressing tool, then dry run, then pre-run, then run 2 of 2. This run is that sequence being carried out, not a question already answered elsewhere.
- **A2, already refuted:** no finding.
  - Route B's in-memory re-wire failure (PD162) does not apply. The recipe starts from the saved `D1_k` file and saves its own output (`tools/recipes/stage_d1_l2a1.py:2-3,101,115`).
  - The 178(f) "tool task when L2 shows the X4 class" condition, which r3 blocked on (`archive/peer/2026-09-25-priorart-c81-l2a1-r3.md:951,975-976`), was released. Pre-run `81c` passed (`tools/bench/prerun_l2a1_81c.log:209`, rc=0), and r4 then returned novel (`archive/peer/2026-09-25-priorart-c81-l2a1-r4.md:986`).
- **A3, contradicted:** nothing new that blocks. The stale stageplan md5 in PD183 (`73e95bc7`, superseded by `329d89ee`) was already reported by r2 and r3 (`…-r3.md:953`). It is record-keeping only; the recipe's L0 gate pins `329d89ee` (`stage_d1_l2a1.py:41`).
- **A4, unread evidence:** none that bears on this. The recipe header does not cite the run-1 failure or PD185. The toolchain does, though: `tools/stagexec.py:253-258` cites `stage_d1_l2a1.log:302`, `l2a1_faces_81.log` and `build_d1_m3a1.log:1145-1154`.

### Part B: the artefact

- **B1, already built:** no. `tools/bench/stage_d1_l2a1.log:327` is the only run (`BGRUN END rc=1`), and it saved no `D1_l2_a1_*` file (`tools/bench/cards/result_81-7.json`, fact "no D1_l2_a1_* saved").
- **B2, already failed:** yes, once. It does not block this run because the cause has been dealt with.
  - **Where it stopped:** run 1 stopped at real op 18 `sr1_L0` with `ADDRESS: node #5825 not in Diagram[21] (#23166).Nodes[]` (`stage_d1_l2a1.log:302`; `result_81-7.json`).
  - **What caused it:** the real reader does not list border SelectorTunnels in `Nodes[]`, while the offline simulator did. A PRIME step that could not prove every wired end also did not stop the run.
  - **Why the fix holds:**
    - `stagexec` now routes SelectorTunnel ends through their owner structure's `Terminals[]`, in both the real and simulated readers. FlatSequenceInnerTunnel ends stop with their correct route named. An unprovable PRIME end now stops the run before op 1 (`tools/stagexec.py:253-271`, `:373`, `:497-499`).
    - The route was measured on a `D1_k` scratch: each of the five L2-A1 sink ends has exactly one matching face on its owner (`tools/bench/l2a1_faces_81.log:35-51`, 13 pass / 0 fail, `BGRUN END rc=0` at `:74`).
    - The new self-tests T16–T20 pass, 21 pass / 0 fail overall (`tools/bench/selftest_stagexec_81.log:16-23`).
    - Pre-run `81d` on the fixed toolchain passes: `PRIME … unprovable []`, `BGRUN END rc=0` (`tools/bench/prerun_l2a1_81d.log:20,209`).
- **B3, helper exists:** no hand-rolled work. The recipe reuses `stagexec` `Executor`/`LVBackend` with `sink_gates`, the 179(b) panel-terminal reader through `allterms.read_terms`, `vigraph.computation_diff_frame`, `Stage.cfw_second_pass`, and `Stage.save(broken_ok)`. Its second-pass filter follows K's precedent (`stage_d1_l2a1.py:75` vs `tools/recipes/stage_d1_k.py:81`).
- **B4, already measured:** no. The real end state of L2-A1 (frame-keyed PB, frame-uid sets, the CT reader on the real file) has never been measured, because run 1 stopped at op 18.

### Side note (not a blocking finding)

Pre-run `81d` proved 18 terminal indexes at PRIME, where `81c` proved 34 (`prerun_l2a1_81d.log:20` vs `prerun_l2a1_81c.log:20`). That drop is expected if SelectorTunnel and FSIT ends no longer go through the node route. Still, the run should check that its PRIME count against the real `D1_k` matches `81d` before op 1.

PRIOR-ART: novel

VERDICT {"schema":"verdict/1","id":"priorart-c81-l2a1-r5-stagexec","verdict":"novel","alternative":"Run 1's cause (SelectorTunnel not in Nodes[]) could recur for an end class the 5-end faces read did not cover; the fixed stagexec's PRIME stop (stagexec.py:497-499) would then halt before op 1 rather than mid-run.","discriminating_test":"Run 2's PRIME line on real D1_k must read 'unprovable []' with the same count as prerun_l2a1_81d.log:20 (18); any unprovable end stops before op 1.","violations":[],"sources":["tools/bench/stage_d1_l2a1.log:302","tools/bench/cards/result_81-7.json","tools/stagexec.py:253-271","tools/bench/l2a1_faces_81.log:35-51","tools/bench/selftest_stagexec_81.log:16-23","tools/bench/prerun_l2a1_81d.log:20","archive/peer/2026-09-25-priorart-c81-l2a1-r4.md:986"],"note":"Recipe md5 e589dc74 unchanged since run 1; the only failure of this build is addressed by PD185's measured owner-Terminals[] route plus PRIME stop, and prerun 81d passes. Run 2 = PD185's scheduled retry 2 of 2."}

## Sources

(extract from answer)

## What was done with it

Verdict: novel. This review covers the PD185 stagexec change (owner route, FSIT stop, PRIME stop; self-test 21/0, gate self-test 13/0). The recipe sha c0f25031 is unchanged. Card 81-8 now does L2-A1 run 2 of 2.
