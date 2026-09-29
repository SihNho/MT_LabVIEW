The saved VI is not shown to be defective; the evidence points at the gate criterion, not at a reference leak.

**What the log shows**

- Handles grow in steps only during operations that create or connect objects (k1 +85, k3 +79, k11 +58, k13 +75), while k4, k5, k10 and k12 add 0 or +1 (`tools/bench/stage_d1_qrt_pool.log:50,78,87,96,168,189,197,217`).
- The "read" and "pre" phases between operations are flat, within about ±9 (`stage_d1_qrt_pool.log:51-53,69-71,218`).
- After the work, with the VI closed, the count is 34139 against 33962 after the fresh restart, a residue of +177 (`stage_d1_qrt_pool.log:29,247,257`).
- VI Server references opened and closed are 9/9 (`tools/bench/cards/result_119-4.json:2`).
- Private memory rises in step with the handles, 553 MB to 613 MB (`stage_d1_qrt_pool.log:41,218`), which fits a diagram that is getting larger.

**Why this points at the gate**

- The ±100 figure in `CLAUDE.md` ("Reference hygiene", item 2) is an acceptance test for a new operation: 20 repeated runs must leave the count flat. It is not a limit on a build that adds objects.
- The card copied "handles +-100" into L4 (`tools/bench/cards/task_119-4.json:32`) from R2's gate, and R2 only deleted objects (`result_119-4.json:23,27`).
- The recipe itself has no handle gate; it only records the numbers (`result_119-4.json:2`, `stage_d1_qrt_pool.log:233`).
- All 21 recipe gates and 19 Error List gates passed, 7 new wires were added, and none were lost (`result_119-4.json:21-24,30`).

**Most plausible alternative**

One of the create or connect functions (the constant-wiring or tunnel route) leaks an internal reference on each call that the 9/9 counter does not see. The +177 residue after close is compatible with this. It is equally compatible with normal drift, since `CLAUDE.md` gives the baseline only as "~31,500", so the log alone does not separate the two.

**Discriminating test**

Open a byte copy of the saved pool VI in a fresh LabVIEW and run the same read-only passes with no edits, recording the handle count after open and after close without saving. No VI is run.

- If the handle count right after opening the larger VI already sits about 300 above the same reading for an R2 copy, and returns to baseline on close, the growth is diagram size and the gate is miscalibrated.
- If the counts match on open, the growth came from the editing calls. In that case run the stepping functions (k1, k3, k11, k13) 20 times each on a scratch VI under `tools/bench/handle_audit.py`.

I have not run this test; the conclusion above is a reading of the log.

ROOT CAUSE: The L4 "handles ±100" criterion was carried over from a delete-only stage and misapplied to a stage that creates objects, so the +322 is most likely LabVIEW's own handles for the new diagram objects (step-wise on create operations, flat between, refs 9/9) rather than a reference leak or a defect in the saved VI.
TEST: In a fresh LabVIEW, open byte copies of R2 and of the saved pool VI read-only with no edits and compare handle counts after open and after close; a difference of about 300 on open that vanishes on close confirms object-count growth, otherwise run the stepping functions 20 times each on a scratch VI under `handle_audit.py`.