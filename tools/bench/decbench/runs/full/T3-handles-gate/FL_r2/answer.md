**No, the saved VI is not shown to be defective. The failing gate is a wrong acceptance criterion, not a reference leak.**

**What the evidence says**

- The "handles ±100" tolerance comes from the reference-hygiene rule, where it means a repeated operation leaves the count flat: "20 runs leave the handle count flat (±100)", with growth judged against the baseline and never as an absolute number (CLAUDE.md, "Reference hygiene" item 2).
- Card 119-4 applied that tolerance to a single pass of a stage that only adds objects (task_119-4.json:32; "additions only", task_119-4.json:84).
- The recipe itself has no such gate. It only records the number: "no HF gate in recipe" (result_119-4.json:2) and "PH handles RECORDED" (stage_d1_qrt_pool.log:233). All 21 recipe gates passed (result_119-4.json:21).
- The ±100 figure was carried over from R2, which only deleted objects (result_119-4.json:23, 27).
- Growth is stepwise and tied to the operations that create things. The count rises during "op" lines (+85, +79, +58, +75 at stage_d1_qrt_pool.log:50, 78, 189, 217) and stays flat during reads and idle steps (d +0 at :87, :96, :168, :197).
- Memory grows alongside it, from 553 to 613 MB (stage_d1_qrt_pool.log:41, 218). That fits new diagram objects (20 named constants, queues, 7 wires; result_119-4.json:21-22) held in the open VI.
- VI Server references were 9 opened and 9 closed (result_119-4.json:2).
- After the work the count fell back to 34139, against 33962 after the fresh restart, a net +177 (stage_d1_qrt_pool.log:29, 247, 257). Most of the growth was released.

In any case, a handle count belongs to the LabVIEW process, not to the file. A leak would be a defect in a scripting function, not in the saved VI, whose structural gates all passed (result_119-4.json:22, 24, 30).

**Most plausible alternative**

One of the create or connect functions leaks a few handles per call, for example an internal reference the 9/9 counter does not track. A single pass cannot separate this from the legitimate cost of new objects. The residual +177 has not been attributed either way.

**Cheapest discriminating test**

Use the rule's own protocol on a throwaway VI: call the create/connect functions from this stage 20 times in one LabVIEW instance, deleting the created objects each time (or closing without saving), and read the handle count per iteration with `tools/bench/handle_audit.py` (CLAUDE.md, "Reference hygiene" item 2).

- Flat within ±100 after the first iteration: the growth is object cost, and the card criterion should be reworded for create stages.
- Linear growth per iteration: a leak in that function, to be repaired before the next stage.

This check is structural only. The VI has ExecState 0 by design and has never been run (result_119-4.json:30).

ROOT CAUSE: The card applied the ±100 flat-handle tolerance, defined for repeated operations and inherited from a delete-only stage, to a single pass of an object-creating stage whose process handle count rises legitimately with the new objects, so the failure is a mis-specified gate and not a reference leak in the saved VI.
TEST: Run the stage's create/connect functions 20 times on a throwaway VI in one LabVIEW instance, deleting the created objects each iteration, and check with handle_audit.py whether the handle count stays flat within ±100 (object cost) or grows linearly per iteration (function leak).