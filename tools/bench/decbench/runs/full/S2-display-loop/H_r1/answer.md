**No, not as written.** The target is right: the Force vs Extension graph costs about 10 ms per frame at 15 beads. The way NEXT gets there is the wrong design, so the next cycle should build a separate display loop instead of fixing the in-loop gate.

**Why the target is right**
- At 15 beads, most of the per-bead cost sits in ForLoop #1359, and its only useful output is the indicator #8323 'Force (pN) vs Extension (nm)'. Nothing from it reaches the saved data, the motors or the tracking kernel (docs/d1-loop12-17-split-plan.md:1402-1409).
- Parallelising #1359 made things worse and was rejected (:1391-1394).
- So cutting how often this graph is drawn is the lever.

**Why the design is wrong**
1. **It rests on an unanswered question.** The N-frame gate depends on the user's answer to D-2026-09-26-02, which is still "open" (tools/bench/decisions_pending.json:143-156). STATUS treats "N = 9" only as an assumption (STATUS.md:66).
2. **The user has since ruled on a different design.** My saved note from 2026-09-26 records that the Force vs Extension plot, and other display-only indicators, are drawn by a separate display loop on its own clock, fed by local variables. It is not a Quotient & Remainder gate inside the frame loop.
3. **That ruling matches the project's standing rules.** Control signals between loops go by local variable, and a loop that doesn't need to follow every frame runs on its own clock (CLAUDE.md:102-109). The seven-loop plan already treats display as its own loop (docs/restructure-plan-4.6.md:386).
4. **NEXT would spend a cycle on the wrong problem.** Its first act is diagnosing why `move_into_frame` breaks the gated copy (ExecState 0 after the moves; STATUS.md:56-63, plan :1480-1494). That is a tool fault that only exists because of the in-frame case design. More work on it moves the deliverable only if the gate design survives, which the user's ruling says it does not.

**What the next cycle should do instead**
- Keep the ring insert #8634 and its shift-register chain on every frame, unchanged. The Magnet2Force reasoning in :1444-1447 still applies.
- Have the frame loop publish the ring history (the #8634 output) as a local variable.
- Add a new display While loop with its own wait. It reads that local and runs exactly the set the plan already identified (:1445-1447): #8741, #8764, #29009 Median, #28233 FIR, #11310 Bundler, then BuildArray #11261 and #8323.
- These are the same nodes on the same inputs; only when they run changes, so rule 1a holds. The acceptance steps carry over: same recorded frames through both, every tra column bit-identical, and #8323's final value equal after a final redraw (:1432-1434). The timing test is the ABBA from :1430.
- Record the ruling as the answer to D-2026-09-26-02 in decisions_pending.json.
- Keep the diagnosis of the broken `move_into_frame` tool as a lower-priority tooling item. It should not be the cycle's first act.

**Two points to check against the files**
- The checkout itself does not contain the display-loop ruling; it comes from my saved notes. It should be confirmed against the user's record before the plan is rewritten.
- If the user wants starting any new build to wait for their explicit go-ahead, the next cycle should stop at a written plan entry and not launch a build.

VERDICT: change NEXT
NEXT ACT: Write and pre-run offline a plan entry that moves #1359's display-only nodes (#8741…#11310, #11261, #8323) into a new display loop on its own clock, fed by a local variable holding the ring history (#8634 output) that the frame loop keeps updating every frame, with the same ABBA and N = 1 replay acceptance.