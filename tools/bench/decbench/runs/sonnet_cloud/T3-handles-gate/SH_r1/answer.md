Checking the logs now. I have enough to answer.

**The saved VI is not defective, and I see no reference leak.** The +322 comes from handles held by objects that were created in memory, and the card's ±100 bar was borrowed from a stage that only deleted.

- **Growth tracks the creates.** In `stage_d1_qrt_pool.log` the steps that create objects add handles: k1 +85 (line 50), k3 +79 (78), k8 +29 (152), k9 +33 (160), k11 +58 (189) and k13 +75 (217). The steps k4, k5, k10 and k12 add 0 to 1 handle each (lines 87, 96, 168, 197). A leak would show growth on every operation, and this doesn't.
- **The reference counter is clean.** VI Server refs were opened 9 and closed 9, with 0 live and 0 cached op-VIs (`stage_d1_qrt_pool.log:~245`, gate H5).
- **The +648 is the same growth over the whole run.** The 15 created rows are a new For loop with its own diagram, an IMAQ Create subVI, constants, tunnels and wires. The "post-open → before-save" figure (line 233) is that growth plus the purge of junk Method nodes. The log counts 640 → 642 nodes by the end.
- **R2's ±100 result doesn't transfer.** R2 only deleted objects (`stage_d1_l2r2.log:298-299`), so its flat count says nothing about a creating stage. The card copied "handles ±100" into L4 (`task_119-4.json`, L4) without that distinction. The creating recipe has no steady-state gate of its own, as `result_119-4.json` notes ("no HF gate in recipe").
- **The residual after closing is small.** The count was 33962 after the restart (line 29) and 34139 after the work (line 247), +177. The 45xxx METER figures are measured with the bed's 174 diagrams open (line 36). The only caveat is that 34139 was read after the work copy was closed, and the baseline was taken before it was opened. That leaves the +177 unattributed.
- **The handle count is not a clean leak meter.** `handle_growth_matrix.log` shows +45.7 handles per run on `exec_state(main)`, and all of it was released after 30 s idle (−2812).

**Most plausible alternative:** a scripting op that leaves a hidden refnum open, which the 9/9 counter wouldn't see. It is less likely because the growth stops on non-creating steps. It is not excluded, because `toolkit-capabilities.md:484-485` says the handle count is blind to VI Server refnums.

**ROOT CAUSE:** The +322 steady-state handle growth is the cost of the 8 creates and purged junk nodes being live in the open VI, and the card's ±100 gate was copied from the delete-only R2 stage, so it is a miscalibrated gate rather than a defect in the saved VI.

**TEST:** Run the same 13 ops on an R2 byte copy, then close it without saving, idle 30 s and read the handle count against a control that opens and closes an R2 byte copy with no ops: a gap within ±100 means no leak, while a persistent gap above that sends the stage to `handle_audit.py` per op.