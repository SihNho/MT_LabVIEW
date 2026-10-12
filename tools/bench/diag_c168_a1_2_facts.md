---
card: 168-a1-2
status: current
date: 2026-10-12
---
# Facts 168-a1-2 - ONE scratch of 75773b0d: RBW, delete #11261, ExecState, full Error List, graph, save gates F-S1..F-S5 (nothing saved)

Log `tools/bench/diag_c168_a1_2_rbwdel.log` (L below): RESULT PASS 24/0 (L:405-407), BGRUN END rc=0 222 s (L:409). Script `diag_c168_a1_2_rbwdel.py`
5280f98d; plan `diag_c168_a1_2_plan.json` 49de796b (decision rows + the uids 11261 / 2626, so prerun X5/X6 pass); lib `prep_c168_a1_2_lib.py` 88ddf8d6.

1. Hashes: before 8/0 (`diag_c168_a1_2_hash_before.log`), after 8/0 (`diag_c168_a1_2_hash_after.log:11`): 20 card inputs + 7 VI pins equal.
2. Launch: dry PASS-UNVERIFIED on exactly A0/A1/R1/D1 (`diag_c168_a1_2_rbwdel_dry4.log`), prerun PASS 15/0 (`_prerun2.log`), X10 predicted
   peak 678.9 MB, model fail_above 680 (`_prerun2.log` X10 line); launched with `--unverified-card` (L:1). First dry FAILED R1/D1 on the wrong graph:
   gate-fp **fp-100** logged (find_graph picked graph_ring_p6rbw_20261012_191349.json, whose header md5 says 75773b0d but is the RBW'd copy;
   `_dry.log`); dries 2-4 used `--graph graph_ring_p5s02e_20261012_173009.json`; R1 put on one line and D1's reads moved into the gate
   statement (statement-scoped taint, stage_prerun.py:809,1042). No gate turned into a row.
3. ExecState: BEFORE RBW 0 (L:28-29 A0 PASS); AFTER RBW 0 (L:34-35 A1 PASS); AFTER delete of #11261 **1** (L:43, ROW).
4. Wires: RBW 2091 -> 2066 = 25 bad wires (L:34-36 R1 PASS). Delete via Stage.delete_object("BuildArray", 11261): gone [11261], err ''
   (L:40-42, D0 PASS); after: Wire objects 2066, #11261 not in the BuildArray list (L:45-46 D1 PASS) = the predicted 2066 (p6_buildarray.md:116).
5. Graph `tools/bench/graph_ring_p6rbwd_20261012_205248.json` md5 57f33e7c65ac63bb7d50cd2c72608982: 6221 rows, 10830 objs, 2066 Wire objs,
   25 loops, 23 FS, #11261 not in objs (L:334). e5_check: `ok True deleted_wires_present [] deleted_nodes_present [] uid_reused 0 rule identity
   (class, owner class, owner uid, pos)` (L:329-330); W22, G1, FS1 PASS (L:331-333).
6. Error List `tools/bench/errorlist_D1_ring_p6rbwd_20261012_205248.json` md5 f71773bcacfc4e253b8977af6a7d88b0 (raw 61735347): **0 items**,
   window N 0, class_counts {}, ExecState 1, errors [] (L:362); the list shows category 'No VIs with errors' (L:357, OCR reads 'Vls'),
   zero capture `errorlist_shots/errwin_205453_b0.png`; Esc closed it (L:359). No item, so no text/uid to list. EL1-EL3 PASS (L:363-365).
   (After RBW alone, 167 read 1 item: "Build Array 'Build Array': Contains unwired or bad terminal", diag_c167_a1_1_rbw.log:350.)
7. Save gates as FACTS (rows, no save):
   - F-S1 PASS: ExecState after the delete 1 (L:371).
   - F-S2 PASS: 0 items, window N 0 (L:373).
   - F-S3 PASS: #2626 t2832<-#30300 (w30418), t4160<-#30119 (w30270), t4165<-#30216 (w30274), t4168<-#4594 (w30522) = 7815af09 sources (L:375).
   - F-S4 PASS: #5204 IndexMode 0, I32, sig 00134003000d...'file progress'; #10404 IndexMode 0, I32, sig 001f4003001966...'file number to append
     out' - equal to stored 7f2582ae (diag_c166_a1_1_tun.json tunnels.p5s01); out wires 4337 / 9636, outer faces source (L:368-369, 377).
   - F-S5 FAIL (criterion used here: diff row set == closure R+DISP cdiff sinks): frame cdiff 30 rows; closure R+DISP 32 rows (L:379).
     Only in the diff: `10068|ParameterTerminal|x|0`, `29240|ParameterTerminal|x|0`, `8323|ControlTerminal|Force (pN) vs Extension (nm) |0`.
     Only in closure R/DISP (with cdiff sink): `11261|Terminal|array|0`, `11261|Terminal|element|0` (the deleted node). Closure R/DISP rows with no
     cdiff sink (not comparable): t17272, t28786, t8323 (all DISP). On 7815af09 the same compare gives only_diff 2, R/DISP-not-in-diff 0
     (`prep_c168_a1_2_lib_selftest.log` T4).
8. MEM: 600.3 / 600.4 / 600.4 / 611.7 / 586.3 / 588.2 MB, peak 611.7 <= 675 (L:383-384).
9. Hygiene: scratch `scratch_c168_a1_2_rbwdel_20261012_205248.vi` deleted (L:392); no scratch_c168* left in claudeDev; refs opened 9 == closed 9
   (L:390); handles 34002 after restart (L:18), 45686 after load (L:27) -> 43218 (L:382), 33957 at exit (L:402); files left [] (L:401);
   `LabVIEW gone at exit: True` (L:408); tasklist: no LabVIEW process. Input md5 unchanged (L:385). No original opened, no motor/camera, no save.
10. Extracted into prep_c168_a1_2_lib (self-test 6/0, `prep_c168_a1_2_lib_selftest.log`); old inline copies left as record:
    `diag_c167_a1_1_rbw.py:44-49` (mem), `:52-84` (el_read), `diag_c166_a1_1_tun.py:42-50` (tunnel read), `diag_c167_a1_3_closure.py:144-147` (frame cdiff).
11. No gate failed: no Jev ladder row, no peer.
