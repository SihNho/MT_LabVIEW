**No.** The lever is the right one: the Force-vs-Extension chain is display-only and costs about 10 ms per frame. But NEXT spends the cycle diagnosing a gate inside the frame loop, and the project's own design sends display work to a separate loop.

**Why not keep NEXT**

1. **The gate leaves the cost inside the frame loop.** The gated set includes Median and FIR (`docs/d1-loop12-17-split-plan.md:1448-1449`), which cost about 9.4–10.9 ms per frame at 15 beads (`:1408-1409`). The tracking loop already runs at 16.7 ms per iteration against the camera's 11.1 ms (`STATUS.md:110`). With N = 9, every ninth iteration still pays the full cost. The gate spreads the work out but does not take it out of the loop.
2. **It goes against the target design.** The master plan's loop 1.6 (display) accepts only "panel updates do not enter the frame budget" (`docs/pre-rig-master-plan.md:92`). The anatomy note says force-extension display work "does not need to run at frame rate at all" (`docs/frame-loop-anatomy.md:91-92`). CLAUDE.md sets the pattern: loops on their own clock, reading the latest value from a local variable (`CLAUDE.md:102-107`). A saved user ruling from 2026-09-26 also says pure-display plots such as Force vs Extension are drawn by a separate display loop on its own clock, fed by local variables. This checkout does not record that ruling: D-2026-09-26-02 is still `"open"` (`tools/bench/decisions_pending.json:143-156`), and the in-frame gate was built on the untested assumption that the user would say yes (`STATUS.md:66`).
3. **The diagnosis is only needed because of the in-frame design.** The ExecState 0 comes from moving nodes into case frames inside the For loop (#1359) and the frame loop's body (`split-plan.md:1480-1487`). The retry cap and failure budget are already spent (`:1480`). Diagnosing `move_into_frame` would fix a tool that a separate-loop design does not use.
4. **It builds on S1, a copy of the original, not on the current work VI** (`split-plan.md:1421`; `STATUS.md:54`). So even a working gate would be a side branch, not a step of the seven-loop restructure.

**What to do instead**

Write a short design decision for a display loop (loop 1.6):
- **Frame loop:** keeps the ring insert (#8634) and its shift-register chain (9227 → #9018 → #9025), plus the ungated `Magnet2Force`, running every frame so the saved history is identical (`split-plan.md:1411`, `:1444-1446`). It publishes the ring array through a local variable.
- **New While loop, about 100 ms per turn:** reads that local and runs the display-only nodes (IndexArray, Subtract, Median, FIR, Bundler), then BuildArray #11261 and indicator #8323.
- **Rule 1a still holds:** the output feeds only the graph, and no saved data, motor command or kernel input is touched (`split-plan.md:1402-1405`).

Put the design to the user as an amended D-2026-09-26-02. Then build it the same way as before: dry run, offline pre-run, one real run on an S1 copy, check ExecState after every edit (`STATUS.md:62`), then the ABBA frame-loss test (`split-plan.md:1430-1431`). Before accepting it, replay the same recorded frames through S1 and the new copy and require identical output files and the same final graph value.

VERDICT: change NEXT
NEXT ACT: Drop the in-frame N-frame gate diagnosis and write, put to the user, then dry-run a separate display loop (loop 1.6) that reads the ring history from a local variable on its own ~100 ms clock and runs the display-only nodes plus BuildArray #11261 and indicator #8323, leaving everything that writes saved data in the frame loop.