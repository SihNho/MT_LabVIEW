**No, change NEXT.** Showing the Force-vs-Extension graph less often is the right lever. Doing it inside the frame loop is the wrong place, so diagnosing and rebuilding that gated copy should not be the next act. ("plan" below means `docs/d1-loop12-17-split-plan.md`. Pre-decided 207 and 208 do not exist in this checkout; the plan ends at 206.)

1. **It can't meet the project's own display target.** Master-plan loop 1.6 says "panel updates do not enter the frame budget" (`docs/pre-rig-master-plan.md:92`). Goal M7 says "display gated outside the frame budget" (`docs/goalmap.json:158-164`). PD206(c) puts the `upd` boolean and both case structures inside frame loop #637 (plan:1450-1456).
   - On every update frame, the gated Median+FIR chain still runs in the frame loop. It is part of #1359's ~9.4–10.9 ms per frame at 15 beads (plan:1408-1409, plan:1448-1449).
   - That loop already takes 16.7 ms against an 11.1 ms camera period (`STATUS.md:110`). At 150 Hz the whole frame budget is 6.67 ms (`docs/camera-acquisition-facts.md:37`).
   - So it can't close M7 and would have to be rebuilt when loop 1.6 is.
2. **It uses only half of the user policy it cites.** PD205(d) quotes "10 Hz… runtime control" (plan:1418-1419). The recorded decision is a display *loop* at 10 Hz, on the principle that the display never adds cost to acquisition or tracking (`docs/questions-for-user-2026-09-14.md:88-90`). That came after the user said one frame lost to live display would justify moving the display out of LabVIEW (`docs/questions-for-user-2026-09-14.md:87-88`). D-2026-09-26-02 is still open and only asks about redraw rate; it never offers a separate loop (`tools/bench/decisions_pending.json:146-156`).
3. **It repeats a pattern the project already dropped.** For focus, the design in force is: the frame loop publishes local variables, the other loop runs on its own clock, and there is "no schedule boolean in the frame loop" (`CLAUDE.md:118-122`).
4. **It depends on the tool that just failed.** Case A sits inside For loop #1359 (plan:1450). `move_into_frame` turned ExecState from 1 to 0, and the retry cap and failure budget are both spent (plan:1480-1482). The tool's self-test never read ExecState (plan:1487-1488).

**Moving the graph to its own loop is a clean cut, already measured:**
- The gated set's only input from the per-frame path is w8811, #8634's ring row (plan:1448).
- Its only output is #8323. The only object that names it is a `Reinit To Dflt` writer (plan:1403-1406, plan:1440).
- #8634's ring insert keeps running every frame, so the history is unchanged (plan:1411, plan:1444-1445).
- The rule-1a check still applies, adapted to a separate loop: tra columns bit-identical, and #8323's final value equal after one last redraw (plan:1432-1434).
- Writing the ring history to a local variable every frame has a cost nobody has measured yet. The existing ABBA timing criterion would decide whether it is acceptable (plan:1383-1386).

Disclosure: a saved memory outside this checkout records a later user ruling in this same direction; the verdict above rests only on the checkout files cited.

VERDICT: change NEXT
NEXT ACT: Drop PD206's in-frame gate, then write, prior-art-review and build (on an S1 byte copy) a display loop 1.6 that reads the ring history through one local variable and runs #1359's gated set, BuildArray #11261 and #8323 on its own runtime-set ~10 Hz clock, leaving #8634's ring insert in the frame loop.