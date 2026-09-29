**No.** The lever is sound, but NEXT's act is the wrong next step. NEXT says to re-run the whole gate build up to E3 on a fresh copy, save the broken file and read it (`STATUS.md:56-60`). Three things argue against that.

1. **The build has already failed twice at the same place.**
   - Run 1 ended with ExecState 0 before save (`tools/bench/fgate_97_stage.log:391-393`).
   - Run 2 was ExecState 1 after the wiring (`tools/bench/fgate_97_stage2.log:287`) and 0 after the moves (`:394-395`, `:409-411`).
   - The project rule says the next cycle's first act must then be a one-page decomposition plan, not another full run (`CLAUDE.md:486-490`).
   - Running to E3 repeats the whole 45-check build on the full S1 copy just to reach the one step that fails.

2. **The suspect is one new function, and it can be tested on its own.**
   - `move_into_frame` passed a self-test that compared wire tables only. It never read ExecState or looked for leftover wires (`docs/d1-loop12-17-split-plan.md:1486-1488`).
   - Both reviews point at cut wires the function leaves behind (`:1483-1484`).
   - A scratch VI would separate the two explanations cheaply. Put one case structure in a loop body, move one node into it, then read ExecState and the wire count. Repeat on a scratch copy after Remove Bad Wires.
   - That tells "function defect" apart from "illegal final structure" without the full build.

3. **The direction needs checking before more build effort.**
   - The gate keeps the graph work inside the frame loop and is built on S1 (`:1421`, `:1450-1457`), not on the current working VI (`STATUS.md:54`).
   - On every 9th frame, the full ~9.4–10.9 ms graph chain (`:1408`) still lands inside one 11.1 ms camera period (`STATUS.md:110`). The gate spreads the cost across frames; it does not remove it.
   - The target design puts display in its own loop, 1.6, where "panel updates do not enter the frame budget" (`docs/pre-rig-master-plan.md:92`; `docs/goalmap.json:159-164`).
   - The default N = 9 depends on user decision D-2026-09-26-02, which is still open (`tools/bench/decisions_pending.json:143-156`).
   - My saved memory also records a user ruling from 2026-09-26: the Force vs Extension plot belongs in a separate display loop, fed by local variables. I found no record of that ruling in this checkout, so it needs confirming.

**What stays right:** the cost is measured (`:1402-1409`), and N = 1 reproduces the original exactly, which gives a clean check that the computation is unchanged (`:1415`, `:1457`). If the scratch test clears the function, gating is still a valid interim step toward loop 1.6.

VERDICT: change NEXT
NEXT ACT: Write the one-page decomposition plan for the Force-graph change, test `move_into_frame` alone on a minimal scratch VI (reading ExecState and leftover wires, with a negative case), and have judgement decide between the in-frame-loop gate and moving the graph to display loop 1.6 before any further full build run.