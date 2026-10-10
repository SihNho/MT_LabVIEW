---
card: 164-3-1
date: 2026-10-10
status: current
---
# 164-3-1 facts (offline; no LabVIEW process before/after) - result FAIL 30/1 at END1 (`prep_c164_a3_1_mk.log:138`, BGRUN END rc=1 :140)
**Part 1 md5** (`prep_c164_a3_1_hash.log`, PASS 23/0 :58): all 19 card inputs equal to their pins (M gates :3-40). VIs (bytes, :41-45): 564d8cbe
D1_ring_p5s02c_20261010_125755 · f9ae7751 D1_ring_p5s02b_20261010_105511 · 94ffff94 D1_ring_p5s02a_20261010_023239 · 7f2582ae D1_ring_p5s01b_20261009_123319 ·
eb1d0f31 D1_ring_p4s09_20261009_060515. No mismatch. (hash.log:60 has a 'BGRUN KILLED (external)' line written AFTER 'BGRUN END rc=0' :59.)
**Part 2 wire gates on graph 3d5196ab, before the edit** (hash.log:47-57): w23460 = t23505 SRC #23501 LoopTunnel InnerTerminal; t23481 'x' / t23477 'y'
SINK #23042 Comparison -> W1 PASS :55. w23519 = t8494 SRC #8486 'x+1'; sinks t23514 #23501, t23450 #23417, t23241 #23172, t7606 #7201 -> outside the two
nodes {7606, 23241, 23450} -> W2 PASS :56, W2b == prediction :57.
**Part 3 compare** (`prep_c164_a3_1_cmp.log:24`, PASS 8/0; its first run :1-12 died on a brace in my own label, fixed, rerun): aside
plan_ring_p5s02r_in_pre164r3.json = 4d93c82d unmodified; r_in 4d93c82d -> **9dadb0c1**; 80 -> 82 actions; old list == new minus {dw_23460, rle_23519}
(deep equal, same order); fields op/id/wire_uid/why only (as plan_ring_p4_s07v18_prov148.json:184-187, plan_ring_p4_s01.json:148-151).
Numbering = 1-based position: A1..A53 unchanged; dw_23460 = A54; do_23042 A54->A55, do_23501 A55->A56; rle_23519 = A57; c_lr7..w_k4f +2 (A56->A58 ... ,
25 actions). No action refers to another by number (NUM gate); make_step_plan resolves positions by id (`prep_plan_flow_lib.py:87-89`).
**Census**: the maker reads group ranges from a census (`prep_plan_flow_lib.py:88-89`); prep_c164_a3_1_census.json bb30814a = prep_c156_a1_1_session.json with J's
actions + the 2 ids (mk.log:5). GRP [(53,62,10),(63,71,9)] :6.
**Part 4 plan** (`prep_c164_a3_1_mk.log`): START 581.8 = x10_start(564d8cbe) :33, limit 675. J: 10 rows, MAIN 633.3 (peak 628.2, N 10, R 6) :35 ·
J+K3: 19 rows, MAIN 647.8 (peak 642.7, N 15, R 9) :38. RULE plan = J+K3 A53..A71 :41. Previous 872822f3 kept as plan_ring_p5s02d_prev872822f3.json :7, :123.
plan_ring_p5s02d.json **725cd68e** written by stagesim.simulate; REALSIM :117 final True, failed null, 19 steps, provisional [], route check PASS, UNROUTABLE 0;
SB :118. Gates PASS: M0 :3, M1 :4, OWN/MAP/MAPALL :8-19, FRM 'True' -> #31517 :22, ROWS :27, STUB :32, C J :36, C J+K3 :39, X10 :40, SPLIT :42, PROBE :43,
TIE :45, S1 :46, C-OUT :119, IDS :120, X8 :121, X17 :122, RC 19 rows :127.
**Compile** J+K3 (:37): 15 ops - delete_wire[1], delete_wire[2], delete_object[3], delete_object[4], wire_remove_loose_ends[5], create[6], create[7], connect[8],
connect[9], stop[10], add_sr[11], create[12], connect[13], connect_term_uid/reb[14,15,16], connect_term_uid/reb[17,18,19]; checkpoints [0,1,2,6,7,11,12,14,15].
Route rows :102-116 (k2 dw_23460 delete_wire, k5 rle_23519 wire_remove_loose_ends).
**Part 5 sim end graph** (step_19_wire.json fe3357bc, mk.log:133-138; post.log ENDOBJ): w23460 terminal rows [] from step 2 on (:129) BUT the Wire object
{uid 23460, class Wire, pos [15676,11868]} is still in `objs` -> **END1 FAIL** :138 (my gate required no rows AND no object). w23519 = t8494 SRC + sinks t23450,
t23241, t7606 exactly (:134-137; t23514 gone at step 4 :131) = the prediction; END2 not evaluated (END1 fatal), the rows match.
Same for w23489 (dw_cond): 0 rows, Wire object still in `objs` (post.log). Code: op_delete_wire drops the Wire object only for a sourceless wire
(`tools/stagesim.py:1461-1463`); a source-carrying wire keeps it with 0 rows (:1446-1448).
**UNCHANGED** (`prep_c164_a3_1_post.log`, 16/0): stagekit dd57c1ca, stage_shared b688edd4, stagexec a4df7e15, stagesim 95a162ba, stage_prerun 7605116f,
prep_plan_flow_lib 34264f5e, memory_model 8fb432e4, graph 3d5196ab, EL 26d45c71, the 5 VIs above, aside copies 4d93c82d / 872822f3.
**Written**: plan_ring_p5s02d.json 725cd68e, plan_ring_p5s02d_prev872822f3.json, plan_ring_p5s02r_in.json 9dadb0c1, _pre164r3.json, prep_c164_a3_1_{hash,cmp,mk,post}.py,
_census bb30814a, _plan_in dc309d2c, _session 2aeaef24, sim/ring_p5s02d/** (step files + _probe).
OPEN: does "w23460 ABSENT" (PD399(a), docs/d1/ring-p5c.md:122-123) mean 0 terminal rows (met) or also no Wire object (not met: tools/stagesim.py:1461-1463)?
OPEN: plan_ring_p5s02d.json is now 725cd68e (final True) although this card ends FAIL; keep, or restore 872822f3 from the aside copy?
