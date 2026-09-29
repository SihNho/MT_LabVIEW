**No, change NEXT.** The gate as designed runs inside the frame loop, and that goes against the display design already recorded in this checkout. Diagnosing and rebuilding it would spend cycles on a file the planned loop structure throws away. ("plan" below means `docs/d1-loop12-17-split-plan.md`. Pre-decided 207–208 do not exist here; the plan ends at 206(h), `plan:1480-1500`.)

**Why:**

1. **Every Nth frame still pays the full graph cost inside the frame loop.**
   - At 15 beads the frame loop takes 16.7 ms, against the 11.1 ms camera period (`plan:1286-1287`). The graph chain alone takes 9.4–10.9 ms of that (`plan:1298-1299`, `plan:1408-1409`).
   - With `upd = i mod N == 0` (`plan:1455-1456`), each update frame still carries all ~10 ms.
   - Milestone M7 requires the "display gated outside the frame budget" (`docs/goalmap.json:158-165`). Loop 1.6 in the master plan says "panel updates do not enter the frame budget" (`docs/pre-rig-master-plan.md:92`).
   - The user's 2026-09-14 policy is a separate display loop, 10 Hz by default, adjustable on the panel, that never adds cost to acquisition or tracking (`docs/questions-for-user-2026-09-14.md:86-90`).
   - Pre-decided 205(d) cites that policy (`plan:1418-1420`) and then builds the gate inside the frame loop anyway.

2. **The user already rejected this pattern for focus.** There, the frame loop publishes values by local variable, the focus loop runs on its own clock, and there is "no schedule boolean in the frame loop" (`CLAUDE.md:118-122`, `docs/goalmap.json:209`). `upd` is exactly such a boolean.

3. **The user was never asked where the gate goes.** D-2026-09-26-02 is still open and asks only about N (`tools/bench/decisions_pending.json:143-156`). The prior-art review said the same (`archive/peer/2026-09-26-priorart-c97-fgate.md:334`).

4. **It changes the S1 copy but splits no loop.** NEXT tags it as advancing M8, M3, R1 and R3 (`tools/bench/next.json:8`), but it splits no loop. A separate display loop is itself a loop split (R1, R3, M7). That also fits the steering card's demand for a deliverable build or run (`tools/bench/cards/steer_95.json:10`).

5. **The cut is already known, and the method is proven.**
   - The only wire into the graph-only nodes from the part that runs every frame is w8811 (`plan:1448`). Magnet2Force and the ring insert keep running every frame (`plan:1444-1447`).
   - The loop 1.5 split already worked with an indicator plus a local-variable read (`plan:1521`), and its replay gave bit-identical X/Y/Z (`docs/goalmap.json:178-179`).
   - By contrast, the new `move_into_frame` function is what broke ExecState (`STATUS.md:81`).

VERDICT: change NEXT
NEXT ACT: In a byte copy of S1, split out a display loop: the frame loop keeps #8634, Magnet2Force and the ring shift register every frame and writes the history to a hidden indicator, and a new display While loop on its own panel-set clock (default ~100 ms) reads it by local variable and runs the Pre-decided 206(b) node set plus BuildArray #11261 and #8323; then run the 15-pick ABBA and the rule-1a replay (tra bit-identical, #8323 equal after one last display pass), and re-ask D-2026-09-26-02 as "separate display loop, 10 Hz by default?".