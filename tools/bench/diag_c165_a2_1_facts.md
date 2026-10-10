---
card: 165-2-1
date: 2026-10-10
status: current
---
# 165-2-1 facts (offline; no LabVIEW) - result FAIL 22/1 at SB: route check UNROUTABLE 2 rows (w_k3f, w_k4f) (`prep_c165_a2_1_mk.log:101`, BGRUN END rc=1 :103)
**Part 1 md5** (`prep_c165_a2_1_hash.log`, PASS 23/0): all 22 card inputs == pins; VI D1_ring_p5s02d_20261010_152518.vi 6dcd5c3d506f6994 (bytes only). Judgement values
stagexec 6ea6637f, r_in 0b895983, graph 2a5fa0c4, EL c74200f2, memory_model ff0fabca, stagekit dd57c1ca, stagesim 95a162ba, stage_prerun 7605116f all EQUAL. No drift.
**Part 2 precedent** `diag_c127_1_fsinner.log`: :81 `OP connect_term_uid S_rat1 #32516 <- #32868 -> err ''`; :82 result `wire_uid 32859, broken False, src_echo 32868`;
:83 `CENSUS S_rat1 {}`; :84 `Is Broken? False ... new wires []`; :89 census in [{}, {'Wire': 1}]; :91-92 S_rar1 #32590 <- #32868 -> wire 32859; :93 census {};
:101-102 S_raf1 #32650 <- #32868 -> wire 32859. Covers: a connect_term_uid from an already-wired source branches onto its existing wire (terms 3 -> 4, :85/:95).
Does not cover: the face classes (source there a Flat Sequence inner face; here SelectorTunnel #31803 outer t31815; sink here an unwired LoopTunnel inner face). No scratch-VI card.
**Part 3** `tools/bench/cards/result_160-c3-2.json` 0df5a91e: status PASS (guard_write refused SKIP: enum ['PASS','FAIL','BLOCKED','WAITING']), gates 0/0, note per PD401(c).
`prep_c165_a2_1_close.log`: validate `OK result/1` + WARN CLOCK-UNMEASURED (no bind line, no cost.minutes); `open_card_pins(tools/stagexec.py) -> []` (PASS 2/0).
**Part 4 plan** (`prep_c165_a2_1_mk.log`): census K3f ['w_k3f'] -> ['dw_10362','w_k3f'], K4f ['w_k4f'] -> ['dw_25232','w_k4f'] (:5-6; prep_c165_a2_1_census.json f9c8aaf5).
GRP [(72,73,2),(74,82,9),(83,84,2)] :7 - the actions are A72..A84 in r_in 0b895983 (the brief's A70/A80 numbering predates the 4 added rows).
Binding: OWN :9 new:CQ7/.f0/.f1 <- p5s02a, new:OK3 <- p5s02d; creation map plan_ring_p5s02d_97837e2a_20261010_152955.jsonl :17; `new:OK3 -> sim -18 -> real #31803` :18
== step-4 record `diag_c164_p5s02d_scratch.log:208` (`bound {-18: 31803}`); CQ7 #31308, f0 #31506, f1 #31517 :12-14. No other new:* used (OK4/SK4/KI4/IK4 are made in step 5).
START 609.8 = x10_start(6dcd5c3d) (603.9 + 5.9) :36, limit 675.
| prefix | rows | ops | checkpoints | delete_wire ops | MAIN | peak | log |
|---|---|---|---|---|---|---|---|
| K3f | 2 | delete_wire, connect | [0,1,2] | [1] | 642.6 | 637.5 | :37-39 |
| K3f+K4 | 11 | + add_sr, create, connect, cterm/reb x2 | [0,1,3,4,6,7] | [1] | 657.1 | 652.0 | :40-42 |
| K3f+K4+K4f | 13 | + delete_wire, branch (9 ops) | [0,1,3,4,6,7,8,9] | [1,8] | 665.0 | 659.9 | :43-45 |
RULE plan = K3f+K4+K4f A72..A84 :47; C gates PASS (every delete_wire a checkpoint) :39,:42,:45; SPLIT :48; PROBE :49; TIE :51 (24 open pairs); S1 :52; STUB :35.
Stubs in 2a5fa0c4: w10362 rows [(5204,'file progress',sink)] sourceless; w25232 rows [(10404,'file number to append out',sink)] sourceless :32-33.
**SB FAIL** :101: REALSIM 13/13 steps ok (:54-66, failed null, provisional []) BUT route check FAIL, UNROUTABLE 2:
`ROUTE 2 connect ['w_k3f']: connect_term_uid UNROUTABLE ADDRESS: 1 wired end(s) not addressable at base: ADDRESS: #8776 is an INNER face of LoopTunnel #5204:
only the outer face's owner route is measured (l2a1_faces_81.log)` :68/:92; same for `ROUTE 9 branch ['w_k4f']` #24342 / #10404 :75/:99. FINALIZE REFUSED :76.
Text source: `tools/stagexec.py:1934` (`_triple`, FACE_ROUTED owner, term_class != OuterTerminal). Not diagnosed further (return at first unexpected result).
plan_ring_p5s02e.json WAS WRITTEN by stagesim.simulate with **final False** (20bde81a, :100) - not a usable plan; no previous plan existed (:4, :8).
plan_ring_p5s02e_in.json b5b35f8a written by the maker (name = <stem>_in, gate L0 form stagekit.py:3015-3022; no copy of r_in made). Probe in a97de1b2.
Gates NOT reached: C-OUT, IDS, X8, X17, PD401(b) file, Part 5 end-graph check (step files sim/ring_p5s02e/step_00..13 exist, not read).
**PD401(b) prediction (not written to a plan field - none exists; maker stopped before writing prep_c165_a2_1_pd401b.json):** per pair dw_10362+w_k3f / dw_25232+w_k4f:
face t8776 / t24342 wire 0 after delete_wire; after connect census in [{}, {'Wire': 1}], face on OK3.outer (t31815, w31792) / OK4.outer net, Is Broken? False.
**UNCHANGED** (`prep_c165_a2_1_hash_post.log` 23/0 after the run): stagekit, stagexec, stagesim, stage_prerun, stage_shared, memory_model, graph 2a5fa0c4, EL, r_in 0b895983,
plan_ring_p5s02d 97837e2a, VI 6dcd5c3d; maker M0 also pinned VIs 564d8cbe / 94ffff94 / f9ae7751 (start only, U gate not reached). No tool / hook / doc edit.
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| prep_c165_a2_1_mk.log | no JEV-LADDER row (grep jev_gate.log) | - | recorded, returned | FAIL 22/1 SB UNROUTABLE 2 |
OPEN: stagexec 6ea6637f's loop_inner_face_sink compiles A73/A84 (C gates PASS) but the route check's base ADDRESS check (stagexec.py:1929-1935) refuses the INNER face - tool fix owed (outside this card)?
OPEN: plan_ring_p5s02e.json 20bde81a (final False) is on disk; keep or delete before the retry?
OPEN: prep_c164_a3_1_mk.py is a module-level script (importing it re-runs step 4); its argument set was followed in one make_step_plan call, census extension inline (prep_c165_a2_1_mk.py:44-53).
