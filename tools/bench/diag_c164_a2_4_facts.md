# 164-a2-4 facts (read-only; graph 3d5196ab = graph_ring_p5s02c_20261010_131658.json, single-line JSON, line 1)
## Wires
- w23519: source #8486 Function `x+1` t8494. Sinks: #23501 LoopTunnel t23514; #23417 LoopTunnel t23450; #23172 LoopTunnel t23241; #7201 Function `x` t7606. Only 1 of 4 sinks on #23501; none on #23042.
- w23460: source #23501 LoopTunnel inner t23505. Sinks: #23042 Comparison `x` t23481 and `y` t23477. All sinks on #23042.
- w23489: source #23042 Comparison `x = y?` t23472. Sink: t23456 owner #23405 (Diagram) (listed twice). Source on #23042.
- Source of w23460 (#23501 t23505) has no sink outside #23042; #23501 has 2 terminal records in the graph (t23514 in from w23519, t23505 out to w23460).
## P4 #10171 / error 1055
- diag_c140_2_facts.md:26-28: op 1 delete_wire w23310, op 2 delete_object #10171 ran (err ''); op 3 wire_remove_loose_ends w23255 -> 'error 1055: Property Node in OpWireRemoveLooseEnds_v0.vi', broken_before True.
- diag_c140_3_facts.md:13: w23255 = source LoopTunnel #23417 t23435 -> sinks only #10171 x t23292 / y t23283. :14 v15 order #2 p4_dw_23255, #3 p4_do_10171. :22 lost wires w23255, w23310.
- ring-p4.md:393-396 (stated as HYPOTHESIS): 1055 because w23255's only sinks were the just-deleted #10171, so RLE deleted the whole wire and the after-read used a dead reference.
## Plan rows (plan_ring_p5s02d.json actions; A54/A55 labels from plan_ring_p5s02d_pred.json:719,736)
- A53 dw_cond delete_wire w23489 (:136-138)
- A54 do_23042 delete_object #23042 (:142-144)
- A55 do_23501 delete_object #23501 (:148-150)
- A56 c_lr7 create Local LR7 read on diagram #23405 (:154-157)
- A57 c_eq7 create Comparison Equal? EQ7 on #23405, donor #10019 (:171-179)
- A58 w_eq7_x wire #31735 outer -> EQ7.x (:201-207)
- A59 w_eq7_y wire LR7.value -> EQ7.y (:211-214)
- A60 w_eq7_cond wire EQ7.`x = y?` -> #23041 cond (:218-223)
- No delete_wire of w23460 or w23519 in A53..A60.
OPEN: A-numbers for A53, A56..A60 inferred from action order (only A54/A55 labelled in pred file).
