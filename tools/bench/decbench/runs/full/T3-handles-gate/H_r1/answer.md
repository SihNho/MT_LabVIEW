**The saved VI is almost certainly not defective. The gate is: "handles ±100" was applied to one build that adds objects, but it was written as a leak test for repeating one operation.**

**Evidence**
- **Where the rule comes from.** CLAUDE.md:225 accepts a new operation only if 20 runs leave the handle count flat (±100). That is a repeat-and-return test. Card 119-4 copied the number as a one-shot limit on a stage that creates about 8 nodes and 7 wires (task_119-4.json:32; log:35, 226). The previous stage, R2, passed this gate because it only deleted things (result_119-4.json:23, 27).
- **Growth only when something is created.**
  - Every `read` and `pre` meter reading is flat: at most +2 or −9, and 0 at k13 (log:51, 53, 69, 79, 218).
  - The steps come only from ops that add objects: For Loop +85 (log:45, 50), nested constant +79 (log:78), connect with a new node +75 (log:204, 217).
  - Ops that create nothing are flat: k4 +0, k5 +0, k10 +1, k12 +0 (log:87, 96, 168, 197).
  - A reference leak in the scripting ops would also show up in the read ops, which call the same COM path. It doesn't.
- **The client side is clean.** VI Server references opened/closed are 9/9 with 0 live (log:245–246).
- **The file can't hold a leak anyway.** A handle leak lives in the LabVIEW process, not in a saved .vi. The saved file's content passed every structural gate: cdiff == R2's 16 rows, 7 new wires and 0 lost, Error List 53 + 0 (log:226–231; result:22, 24).
- **Little is left once the work ends.** A separate handle count reads 33962 after the restart and 34139 after the work, so +177 (log:29, 247). That fits LabVIEW keeping newly loaded subVIs in memory (IMAQ Create, the donor VI; log:55, 75). Why the in-stage meter reads about 45.6k while this count reads about 34k is not explained in the log.

**Most plausible alternative**
One of the create/connect scripting ops leaks references internally, for example a Traverse or GetOutputs reference that is never closed. Python's 9/9 counter would not see that. It would also grow by roughly the same amount per call, so the per-op pattern alone can't rule it out.

**Cheapest test**
Run one of the steps that grew, for example `create for` (k1, +85), 20 times on a scratch byte-copy of R2, deleting the new node each time. Read the handle count before and after, which is exactly the acceptance test in CLAUDE.md:225.
- Flat within ±100 means the growth is objects that exist, not a leak. Then the L4 gate is a false positive: log it with `tools/gate_fp.py` and fix the card's criterion.
- About +80 per iteration means the op leaks. The fix then belongs in the scripting op, not in the saved VI.

You can also check first without LabVIEW: compare the deltas already logged against how many objects each op created.

ROOT CAUSE: The card applied CLAUDE.md's "flat ±100 over 20 repeated runs" leak criterion as a one-shot limit on a build that adds objects, so the +322 handles follow the new nodes and wires (flat on reads and on ops that create nothing, refs 9/9), not a defect in the saved VI.
TEST: On a scratch copy of R2, run the `create for` op 20 times, deleting the new node after each, and compare handle counts: flat within ±100 means the gate was a false positive, while about +80 per iteration means the scripting op leaks.