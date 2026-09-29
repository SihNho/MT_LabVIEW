**No, NEXT should change.** Its diagnosis is valid but it points the next act at the wrong target. The two analysts who said "change" hold up on their core points. The analyst who said "keep" is right about rule 1a and wrong about the order of work.

**What survives checking**
- **The failure has now happened twice, with the same function.** Both stage runs reached ExecState 0 only after `move_into_frame`:
  - run 1: `tools/bench/fgate_97_stage.log:339-392`
  - run 2: `tools/bench/fgate_97_stage2.log:287`, then 0 after the moves (`docs/d1-loop12-17-split-plan.md:1481-1482`)
- **The plan says the function was never checked for this.** Its self-test "gated edge tables only, never ExecState or leftover wires after the move" (`d1-loop12-17-split-plan.md:1487-1488`).
- **The retrospective already set the rule.** "Any verb that edits a diagram is gated on ExecState read after the edit" (`STATUS.md:62`).
- **So a small scratch VI is the cheaper test** (Analyst 2): a loop, a case and a few wires, plus a negative case. It separates the two explanations (orphaned wires vs an illegal structure) without re-running a ~40 s-per-move, 620 MB stage (`fgate_97_stage.log:339-366`) or doing a GUI save. It also repairs a function that later loop splits will need.
- **The size of the saving is unmeasured.** The ~10 ms is site 4 − site 3, which covers the whole For loop #1359 (`d1-loop12-17-split-plan.md:1298`, `:1408`).
  - The ring insert #8634 and `Magnet2Force` #28083 stay ungated and run every frame (`:1411`, `:1444-1445`).
  - A review named ring-fill memory work as a possible cost (`:1399`).
  - "Removes nothing the lever needed" (`:1448-1449`) is an assertion, not a measurement.
  - This is the same pattern that sank par1359: built on this same figure, it came out +13 % worse and was booked as `inference-over-measurement` (`:1392-1398`).

**What does not survive**
- **Analyst 3 says NEXT's GUI read of the error list is the "reader" the rules require.** A scratch test that reads ExecState is also a reader, and it is cheaper.
- **Analyst 3's point that the cost sits in Median/FIR is plausible,** because the cost rises as the ring fills (`:1298`). But it has not been measured.
- **Nobody could show a user ruling in this checkout that moves the graph to a separate display loop.** The saved note on that sits outside the checkout. Two things in the checkout point the same way:
  - The master plan's row 1.6 puts display in its own 10–20 Hz UI loop (`docs/pre-rig-master-plan.md:92`).
  - The D1 plan moves #1359 to loop 1.2 anyway (`d1-loop12-17-split-plan.md:1300`).

  So a gate inside the S1 frame loop is at best a stopgap. That is a reason not to put a whole cycle into rebuilding it before the payoff is known.
- **Analyst 1's "delete the gated set on a scratch copy" test is still the right way to size the saving.** But it depends on a node-delete function this checkout may not have. I have not verified that it exists.

**What the next cycle should do**
- **One card:** the scratch-VI test of `move_into_frame` (ExecState and leftover wires after the move, with a negative case), then fix it and add an ExecState gate to its self-test.
- **In parallel, independent of that:** a timing-only ABBA on a scratch copy of S1 with the gated set cut out, judged against criterion 204(a) (`:1383-1386`).
- **Rebuild the gate only if** that saving clears 20 % and the tool is fixed. Otherwise the lever is in the ring insert or `Magnet2Force`, or the graph belongs in the display loop.

VERDICT: change NEXT
NEXT ACT: Run a minimal scratch-VI test of `move_into_frame` (ExecState and leftover wires after the move, with a negative case), fix the function, and alongside it measure the most the gate could save with a timing-only S1 copy that has the gated set removed, before rebuilding the #1359 gate.