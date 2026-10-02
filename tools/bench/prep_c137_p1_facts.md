# Card 137-P1 facts (offline, read-only, 2026-10-02; no tool/plan/graph edited). Inputs: plan v3 d14c1bba, meta 8dd37a54, graph p3b2b 50595c62 (VI 395118775a), graph p3b1 6cfa6ecb (VI 9d7bf287), memory_model 50314079
## 1. Why stagesim stops at v3 step 102 (`p4_x_fd`)
- Raise: `tools/stagesim.py:681` in `resolve_addr` (`:672-681`): `rows = node_rows(st, uid)` is empty.
- `node_rows` = rows whose `V.node_of(r) == uid` (`tools/stagesim.py:542-543`); `node_of` returns the row's OWN `term_uid` when
  `term_class == "ControlTerminal"` (`tools/vigraph.py:57-60`, `FP_CLASS` `:52`). Documented convention: "a ControlTerminal row is
  its own node owned by its Diagram" (`tools/stagesim.py:122-123`).
- Plan address: src `{"uid": 686, "term_uid": 8936}` (`tools/bench/plan_ring_p4_v3.json:1465-1469`), i.e. the OWNER Diagram uid.
- Real graph row: `term_uid 8936 '# FD points', is_source True, wire 9000, owner_uid 686, owner_class Diagram, frame_diagram 686,
  term_class ControlTerminal` (graph_ring_p3b2b `terminals`, probe p1_a). All 5 rows owned by 686 are ControlTerminals
  (8936, 10225, 9850, 28844, 24016), so node 686 has 0 rows under node_of.
- Side that differs: the PLAN addressing. Graph loader is right (row present, owner 686); simulator owner index follows
  vigraph.node_of, and the real executor uses the same convention: `Addr.ct` "term_uid == its own uid, owner == its Diagram"
  (`tools/stagexec.py:1493-1496`; Nodes[] triple refused for a CT, `:1106-1109`).
- Same addressing form elsewhere in v3 (Diagram uid + a ControlTerminal term_uid): step 104 `p4_x_dt` {686, t28844} (`plan:1484`),
  step 115 `p4_rbA_re1` {23166, t3173} (`:1619`), 116 `p4_rbA_re2` {23166, t9519} (`:1632`), 143 `p4_rbD_sel_t25573` {23166, t25573}
  (`:1984`). Not replayed (node 23166 owns cond/i rows, so those would fail later in the term_uid filter, not at `:681` - inference).
  Step 5 `p4_w_stop12` {23166, t23246} is not a CT and resolved (`prep_c136_p2_sim.log:8` STEP 05 ok).

## 2. v3 session table from MEASURED loads (memory_model keys; stage_prerun.py:2001-2019)
Peak = start + R*read_mb 2.53 + N*(edit_mb 0.58 + other_mb 0.8) + final_read_mb 17.4; start = load + op0_read_mb 5.9; R = k0 +
BIND ops (create/local/tunnel/add_sr/connect_term_uid, `tools/stagexec.py:1757`) + last op. My (N,R) per session reproduce all 18
of the meta's sessions (0 mismatches; meta `steps` `plan_ring_p4_v3_meta.json:149-500`). Units kept whole (as in the meta); 164 ops.
Loads: fresh 567.7 (`diag_c136_4_mem.log:114`), bed copy 576.5 (`:42`), bed 600.2 (`diag_c136_1_graph.log:24`). Empty-session
peak 593.5 / 602.3 / 626.0. Start held CONSTANT per session (in-between files' loads are unmeasured).

| load | stop | opt-1 sessions per 40-step (steps 1..5) | opt-1 total | opt-2 (one P4 file) total |
|---|---|---|---|---|
| 567.7 | 675 | 2,2,1,1,1 | 7 | 6 |
| 567.7 | 690 | 2,1,1,1,1 | 6 | 5 |
| 576.5 | 675 | 2,2,2,1,1 | 8 | 7 |
| 576.5 | 690 | 2,1,1,1,1 | 6 | 6 |
| 600.2 | 675 | 3,2,3,2,2 | 12 | 11 |
| 600.2 | 690 | 2,2,2,2,1 | 9 | 8 |
- At load 600.2 / stop 675 unit U05 (13 creates, N13 R14) alone peaks 676.9 > 675: a whole-unit packing cannot meet the planning stop.
- D-2026-10-02-04 (`tools/bench/decisions_pending.json:330-342`; 4 of 6 used per `:333`): opt 1 = 5 P4 files + 1 P5 = 6 new
  broken files (10 total), in-between session files deleted = sessions - 5; opt 2 = 1 P4 + 1 P5 = 2 new (6 total), deleted =
  sessions - 1; opt 3 = extra run-to-ExecState-1 cycles, not computable offline.
- Context: same bytes load 576.5 (copy) vs 600.2 (bed), 23.7 MB apart; 136-4 measured 1.92 MB/read over 40 reads
  (`diag_c136_4_mem.log:86`) vs read_mb 2.53; with the 0.543 MB/op growth fit (SD 10.6) prep gave 18 sessions, 14 over 675
  (`tools/bench/prep_c136_p2_p4v3.md:40,45-53`).

## 3. Unmeasured route classes (meta `routes_unmeasured`, `plan_ring_p4_v3_meta.json:501-860`): 24 classes, 113 actions
137-1 coverage per the v2 annotations in each class (U1-U3 and W1-Or run in a SCRATCH VI, not in base body 23166 - context differs):
| class (meta line) | n | example | 137-1 route |
|---|---|---|---|
| C05 create @ W1 body (:564) | 6 | p4_sel_mask | U1 (p4_sel_mask) + U2 (p4_k_max); 4 none |
| C12 connect @ W1 body (:655) | 8 | p4_w_gt_sel | U3 (p4_w_gt_sel); 7 none |
| C07 create primitive Or @ W1 body (:593) | 1 | p4_or_w1 | W1-Or |
| C13 stop @ W1 border (:674) | 1 | p4_w_or_cond | W1-Or (Or out -> While cond) |
| C24 connect_term_uid @ FS4 frame (:851) | 2 | p4_x_n2_order | U5 (1 of 2) |
| C21 connect_term_uid @ base body 23166 (:815) | 3 | p4_x_fd | U6 = p4_x_n2_out (1 of 3); p4_x_fd, p4_x_dt none |
| C17 connect @ 23166 (:719) | 37 | p4_w_pool_in | none |
| C04 create @ 23166 (:538) | 16 | p4_w1 | none |
| C18 branch @ 23166 (:766) | 9 | p4_w_n1_gt | none (3 = S-SELB) |
| C19 wire_sr @ 23166 (:786) | 7 | p4_w_last_gt | none |
| C09 tunnel @ W1 border (:618) / C10 in_group @ W1 border (:631) | 3/3 | p4_t_last / p4_t_last_in | none |
| C08 create @ FS4 frame (:604) | 3 | p4_lr_num_b | none (1 = S-FSW) |
| C01 local_read @ 23166 (:503) / C14 in_group @ 23166 (:685) / C20 move_in @ 23166 (:803) | 2/2/2 | p4_lr_stop12 / p4_t_n1_out / p4_mv_10068 | none |
| C02 stop @ 23166 (:516) | 1 | p4_w_stop12 | none (cond MODE read is 137-2, not a route run) |
| C03 const_donor @ FS #681 f4866 (:527) / C06 local_read @ W1 (:582) / C11 in_group @ W1 (:644) | 1/1/1 | p4_c_bufdiff / p4_lr_stop_w1 / p4_t_last_out | none |
| C15 tunnel @ #10170 border (:697) / C16 branch @ #10170 border (:708) / C23 connect @ FS4 (:840) | 1/1/1 | p4_t_pool / p4_x_pool / p4_w_n2_arr | none (C15/C16 = S-TUN) |
| C22 decide (:829) | 1 | p4_dec_reseed | n/a (judgement, no route) |
- Covered by 137-1: 7 of 113 actions, 2 classes fully (C07, C13), 4 partly (C05 C12 C21 C24); 17 classes none + C22.
- Cheapest measurement, per class: the meta's own line "on a bed byte copy, ONE <op> @ <context>, census before/after + Is Broken?"
  (R01..R24 in each class entry). The 9 base-body-23166 classes (C01 C02 C04 C14 C17 C18 C19 C20 C21) share one context, so one
  byte-copy run with one action each covers the classes of 78 of the 105 uncovered actions (113 - 7 covered - 1 decide).

## 4. One-sided wires P3b-1 graph vs P3b-2b graph (`prof()` copied from `errorlist_expect_p3b2.py:33-38`)
- Source-only: P3b-1 {4878, 10187, 12256, 29787}; P3b-2b {10187, 12256, 29787}. In P3b-1 not P3b-2b = {4878}; new in P3b-2b = {}.
- Sink-only: {10166, 28684, 29766} in both; difference empty both ways.
- 4878 in P3b-1 = 1/0, its one row t4728 'Value' of Property #4580 (source); absent in P3b-2b. 3268 (2/7), 30592 (1/1), 28437 (1/2)
  are TWO-sided in P3b-1 and absent in P3b-2b: never in a one-sided set, so the set difference cannot contain one of them.
- Answer to review c135e §4 (`archive/peer/2026-10-02-c136-3-c135e-elmismatch.md:78-81`): the difference is exactly {4878}, nothing
  new. It does NOT equal "{4878 + one of 3268/30592/28437}"; the second removed loose-end item (22 -> 20) is not visible in terminal
  profiles (dangling branch carries no uid, `errorlist_expect_p3b2.py:8-9`). Refutation clause (`:81`, "any other difference") is
  met literally; the "nothing new" falsifier (`:72`) is NOT met (no new one-sided wire).

OPEN: (a) plan form vs simulator: re-address the 5 CT ends by own uid, or teach the sim the owner form (PD301(e) says sim fix later,
alone). (b) Does §4's {4878} alone + no new wire settle c135e, given the 2nd item is invisible to prof()?
