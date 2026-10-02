The saved VI is not defective, and nothing here shows a leak. The FAIL is a mis-specified gate reading first-call cost. This is inferred from the log partition and has not yet been replayed warm. (`log` = `tools/bench/stage_d1_qrt_pool.log`.)

**The file is fine.** Every file-level gate passed: cdiff == R2's 16 rows, 7 new wires with 0 lost, and R2 md5 unchanged (`log:226-231,248`). The Error List is 53 == R2 + 0 (`result_119-4.json:24`). The level is structural and the VI was never run. The metric is the LabVIEW process's kernel HandleCount (`tools/bench/bench_prep.py:64-67`), which is blind to VI Server refnums (`tools/stagexec.py:64`), so it is not a property of a saved .vi. Refs are 9/9 (`log:245`).

**The +322 splits by first-of-kind, not by call count:**
- **First calls after k1:** drop_subvi +35, first create_primitive_nested +79, first Obtain +27, Enqueue +29, first wire_const +33, connect_nested_v1 (+purge) +58, connect_from_wire (+purge) +75. That sums to **+336** (`log:68,78,115,152,160,189,217`).
- **Repeats of an already-used op:** 0, 0, +2, +1, 0, which is **+3** (`log:87,96,134,168,197`). A per-call leak would show here.
- **The +648 open→save** also holds +94 for the initial read, +28 pre-reads and +85 for the first op (`log:37,41,50`). The last +124 comes from end-of-stage readers (`log:218→233`).

Cycle 97 saw the same pattern. First calls cost `OpConnectFromWire_v0` +74 and `OpConstWire_v1` +18, then 20-call repeats were flat (`tools/bench/diag_c97_tools_handles.log:35,125,128`). Create stage L2A3 grew +325 over 6 ops (`tools/bench/stage_d1_l2a3.log:41→161`). R2 repeated one warm delete op, so its HF gate was trivially flat (`tools/recipes/stage_d1_l2r2.py:98`). After the work the count fell to 34139 against 33962 post-restart (`log:29,247`).

**The gate contradicted a standing ruling.** PD176(a) says ±100 "does not apply to an editing stage", whose handles are "RECORDED, not gated" (`docs/d1-loop12-17-split-plan.md:458-462`). The recipe obeys that (`log:233`, like `tools/recipes/stage_d1_l2a3.py:91`). Card L4 (`tools/bench/cards/task_119-4.json:32`) carries the clause PD228(h) set for delete-only L2-R (`docs/d1-loop12-17-split-plan.md:2045`).

**Alternative explanation:** a real per-call leak, most plausibly in the junk-Invoke purges (k11 and k13, each confounded with a first call), drop_subvi, or Enqueue (one call each).

ROOT CAUSE: Card L4's "handles ±100" gate, a repeated-op hygiene test that PD176(a) exempts editing stages from, was applied to a create stage whose k1→k13 window contains the one-time first-call cost of seven first-of-kind calls (+336 versus +3 for repeats), so the +322 is first-call cost, not a leak or a defect in the saved VI.
TEST: In one fresh LabVIEW session run the 13-op plan on an R2 byte copy, then again on a second byte copy (no save, no launch), logging handles per op: first-call cost predicts the warm second pass stays within ±100 with every purge and connect op near 0, while a leak predicts about +300 again with those ops adding +25 to +75 each time.