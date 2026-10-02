The saved VI is not defective. The L4 gate failed because a rule meant for a different situation was applied to this stage. It is a gate false positive: the handle growth comes from the 13 create/connect ops building new diagram objects, and the evidence does not show a reference leak.

**The evidence**

- **A `.vi` file can't hold handles.** The handle count belongs to the running LabVIEW process. The saved file is static bytes, and every structural gate on it passed: cdiff, 7 new wires with 0 lost, Error List 53 + 0 (`tools/bench/stage_d1_qrt_pool.log:226-231`, `:262`).
- **VI Server references were all closed.** 9 opened, 9 closed, 0 live (`stage_d1_qrt_pool.log:245-246`).
- **The growth follows object creation, not op calls.**
  - Read steps never grow (`:51,69,79,…,218` show d +0 to +2).
  - The growth is all in op steps that build objects: For loop with a new frame diagram, k1 +85 (`:45,50`); array constant, k3 +79 (`:78`); queue and enqueue nodes, k6 +27 and k8 +29 (`:115,152`).
  - Connects that create a temporary helper Invoke node #23267 grow too: k11 +58 and k13 +75 (`:176,189,204,217`).
  - Creates of the same op class with nothing large behind them stay flat: I32 constant k4 +0 and ring constant k5 +0 (`:87,96`), plain connects k10 +1 and k12 +0 (`:168,197`). A leak inside the op wrapper would charge every call. These don't.
- **There is a measured precedent.** `handle_audit.log:7` shows "10x drop_subvi + revert: +51", so creating objects grows handles even after a revert.
- **The ±100 number was borrowed.** It is R2's HF gate, and R2 was a delete-only stage whose reads stayed flat at about 45730–45755 (`stage_d1_l2r2.log:8,298-299`). It also echoes CLAUDE.md's op-acceptance rule, "20 runs leave the handle count flat (±100)" (`CLAUDE.md:225`). That rule tests the same op called repeatedly, not a stage that adds about 10 objects. The card copied it unchanged into L4 (`task_119-4.json:32`), and the result itself flags the mismatch (`result_119-4.json:27`).

**The plausible alternative** is a real per-call leak in specific creator or connect ops, for example the connect path that creates and deletes Invoke #23267, or the gui_save path. The log can't fully rule this out. Process-level counts went from 33962 after restart to 34139 at exit (+177, `:29,247,257`), but that window includes the GUI save, and R2's run ended below its own baseline (`stage_d1_l2r2.log:27,321`).

**Cheapest test.** In one fresh, bgrun-wrapped LabVIEW, re-run the already-passing scratch build (L2) on an R2 byte copy, then close it without saving. Read the handle count three times: after open, after the 13 ops, and after close.
- If the count after close returns to within ±100 of the after-open value, the +322 belonged to the VI's in-memory objects.
- If it stays about +300 above, the ops leak.

This needs no artefact edit, no save and no cold load of the broken saved file. If the ops do leak, a follow-up check is to call the k11/k13 connect 20 times and confirm with `handle_audit.py`.

If the test shows the handles are freed, log L4 to `gate_fp_queue.jsonl` and change the card's L4 for create stages to "handles returned to post-open after close".

ROOT CAUSE: L4 applied the ±100 steady-state handle threshold from the delete-only R2 stage and the repeated-op rule to a create stage, where LabVIEW's handle count grows with each new diagram object (For frame, queue nodes, constants, helper Invoke), while references balanced 9/9 and reads stayed flat, so the gate is a false positive and the saved VI is not defective.
TEST: Re-run the scratch build on an R2 byte copy in a fresh LabVIEW, close it without saving, and compare handle counts after open, after the ops and after close: back to the after-open count ±100 means object-owned handles (gate false positive), about +300 left over means an op-level leak.