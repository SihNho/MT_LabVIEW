I'd change NEXT. The Q&R gate is aimed at the right cost, but it builds the graph throttle inside the frame loop. The project's target design takes that graph out of the frame loop, so this would be a temporary structure to debug and then throw away.

**What NEXT asks for.** Cycle 98 would re-run `stage_d1_fgate.py` to step E3, save the broken copy through the GUI, and read LabVIEW's Error List, the broken wires, and the ExecState after Remove Bad Wires (STATUS.md:56-60; plan 206(h), d1-loop12-17-split-plan.md:1480-1494). The ABBA timing test and the rule-1a replay come after that (STATUS.md:63).

**The case for it:**
- The cost is measured. ForLoop #1359 feeds only the display indicator #8323, runs every frame, and takes about 9.4–10.9 ms per frame at 15 beads (plan:1402-1409).
- Reading the error instead of guessing a third time follows the "build the reader" rule. The retry cap and the failure budget are both spent (plan:1480-1487).

**The case against it:**
1. **It builds the wrong structure.** The target design (`docs/restructure-plan-4.6.md`) is:
   - The display runs as its own loop 6, "behind a 10–20 Hz gate" (`:45`).
   - It gets the newest data through a "local variable / 1-element queue" (`:55`).
   - It is not wired into the frame loop, because a wire between loops makes them run one after the other (`:48`).

   The Q&R gate nests two case structures inside the frame loop and inside #1359 (plan:1450-1457). Splitting out the loops later would take all of that apart again.
2. **A user ruling may already cover this.** My session memory, which I could not open from this checkout, lists a 2026-09-26 user ruling: Force-vs-Extension plots and similar display-only indicators are drawn by a separate display loop on its own clock, fed by local variables. A search of the checkout finds that ruling nowhere. Meanwhile D-2026-09-26-02 is still OPEN and still recommends the in-loop N = 9 gate (`tools/bench/decisions_pending.json:143-156`). If the ruling stands, NEXT contradicts it and the pending question is out of date.
3. **The break comes from the in-loop design.** ExecState went to 0 only after `move_into_frame` moved the gated nodes into the case frames (plan:1481-1482). A separate display loop doesn't use that path at all.
4. **The rule-1a argument carries over.** The graph chain reaches no saved data, motor call or kernel input (plan:1402-1406). Moving it to a slower-clocked display loop changes only scheduling, the same argument that made the N-gate safe (plan:1416-1417). The ring insert #8634 and its shift-register chain stay in the frame loop unchanged (plan:1411), and the ring array reaches the display loop through a local.

**Caveat.** Point 2 rests on memory outside this checkout, so it needs confirming first. If the user hasn't made that ruling, NEXT is defensible as it stands.

**What the next cycle should do instead:**
- Record the display-loop ruling in the plan.
- Replace or answer D-2026-09-26-02.
- Hand judgement a design card: publish #8634's ring array (the #1359 output that becomes tunnel 9227) through a local each frame; move the gated set from plan:1445-1447 plus BuildArray #11261 and indicator #8323 into a display loop with a ~10 Hz clock.
- Measure what that local write costs per frame at 15 beads before building.
- Keep the 206(h) Error List read only as a cheap check on the `move_into_frame` tool, not as the path to the deliverable.

VERDICT: change NEXT
NEXT ACT: Record the user's separate-display-loop ruling in the plan, close D-2026-09-26-02 against it, and dispatch a design card that moves #1359's graph chain and indicator #8323 out of the frame loop into a display loop fed by a local, with the per-frame cost of that local measured before any build.