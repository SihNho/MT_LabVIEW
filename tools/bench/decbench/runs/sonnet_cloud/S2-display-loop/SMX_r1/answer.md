**Keep NEXT.** The gate is the only lever the measurements support, and reading the break is the rule-compliant way to fix it.

**Why the lever**
- At 15 picks the frame loop runs 16.7 ms against an 11.1 ms camera period. ForLoop #1359's output grows +760 µs/bead, the kernel only +188 (`archive/benchmarks/INDEX.md:76`). The kernel swap (`STATUS.md:165`), the minimised panel (−16 %, `STATUS.md:155`) and the parallel #1359 (+13 % worse, `docs/d1-loop12-17-split-plan.md:1391-1395`) are all spent.
- #1359's output feeds only indicator #8323 and its own ring: no writer, motor or kernel (`split-plan.md:1402-1409`).
- My arithmetic: lost frames ≈ 1 − 11.1/period reproduces 1,672 (11 picks) and ~3,400 (15 picks) of ~10,675 (`split-plan.md:1283-1287,1391`). N = 9 brings the mean period under 11.1 ms if the gated set costs ≥ ~6.3 ms of the ~10 ms between sites 3 and 4.
- R4 (no frame loss) has not moved (`docs/goalmap.json:48,193`). Moving #1359 into loop 1.2 "does not make it cheaper" (`split-plan.md:1300`).

**Why read, not guess**
- The break is narrow: E1 = 1, E3 = 0, cdiff 0 rows, equal edge tables (`tools/bench/fgate_97_stage2.log:287,361,385,394,407`).
- Both earlier explanations were inference (`archive/peer/2026-09-26-c97-fgate-es0-r2.md:56-67`). Retrospective 97 names the missing ExecState read and orphan-wire reader (`retrospective-cycle97.md:248,272`).
- A cheap cure is plausible: `move_in` severs wires and leaves stubs (`docs/cycle27-plan.md:846`, `docs/toolkit-capabilities.md:822`).

**Riders**
1. Remove Bad Wires can delete good wires (`docs/NAMES.md:1194-1198`), so ExecState 1 after it proves nothing alone. Re-run the edge tables and cdiff on the scratch. If they hold, continue from that saved file rather than re-running the stage.
2. NEXT wants the "unchanged" recipe (md5 690269c0) plus a `gui_save`. The recipe stops at F6a (`tools/recipes/stage_d1_fgate.py:98`) and restarts LabVIEW (`:117`) with no save hook. Add one and redo dry and pre-run.
3. Time-box it. The outcome review's fallback was "unchanged ⇒ L2-A1 stage 2" (`archive/peer/2026-09-26-outcome-review-20260926.md:196`). If no replay-verified, ABBA-measured gated file exists by the end of cycle 100, go back.
4. D-2026-09-26-02 is open (`tools/bench/decisions_pending.json:143-156`). A "no" kills only this lever, so build under rule 2c. A gated frame still costs ~17 ms once in nine. Whether the camera ring absorbs that is unrecorded (`docs/camera-acquisition-facts.md:668-674`), so the N = 9 ABBA decides. A display loop (`docs/restructure-plan-4.6.md:45`) is the fallback.

Also: the plan ends at Pre-decided 206 (`split-plan.md:1438-1500`); 207–208 don't exist. `tools/bench/next.json:8` lists advances M3/R1/R3, but this act advances R4/M10.

VERDICT: keep NEXT
NEXT ACT: Run the cycle-98 diagnosis card (rerun stage_d1_fgate.py to E3, gui_save the broken file, read its Error List, loose wires with owners, and edge tables plus ExecState after Remove Bad Wires on a scratch copy), then fix move_into_frame and go to the N = 9 ABBA and N = 1 replay.