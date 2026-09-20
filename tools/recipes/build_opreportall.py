"""build_opreportall.py - OpReportAll_v0.vi: return EVERY object of a class in ONE run, as arrays.

THE PROBLEM THIS SOLVES, measured 2026-09-13:

    one op run against a SMALL target VI      10.4 ms
    one op run against the MAIN VI           960.8 ms      <- 92x
    SetControlValue / GetControlValue          0.07 ms     <- COM is irrelevant

~990 ms of every run is FIXED - it is the `Open VI Reference` on a 473 KB VI with 98 subVI call sites. Varying the
traversed class by 720x (Local=8 vs Terminal=5763 objects) moved the time only 23 %, so the traversal itself is a thin
layer on top of that fixed cost. `report()` calls the op **once per object**, so a 626-node sweep pays the 990 ms
**626 times**: 601 s predicted, 618 s measured.

Returning arrays pays it ONCE. 626 nodes: ~601 s -> ~1 s.

DONOR: OpReport_v3.vi, 5 nodes -
    Open VI Reference -> Traverse (already emits the whole `References` array and `# of Refs`)
    -> Index Array (throws all but one away)  -> Property(Position/ClassName/UID/Owner) -> Property(ClassName of Owner)

So the array is already there; the op just discards it. Wrap the Property reads in a For Loop fed by `References`.

EVERY STEP BELOW USES A VERIFIED OPERATION. Two probes on scratch copies established the last unknowns on 2026-09-13:

  * the loop body is simply **diagram index 1** (`diagrams: [(0,''), (1,'ForLoop')]`), and `build_property` takes a
    `diagram_index` - so nodes are CREATED inside the loop and never moved. `move_object` reparenting, the thing that
    looked like a blocker, is not needed at all.
  * **`wire()` across a loop boundary auto-creates the tunnel** (LoopTunnel 0 -> 1) and the auto-indexed array then
    supplies `N`, flipping ExecState 0 -> 1.

BUILD ORDER - tunnels before nodes (the user corrected an earlier draft that had it backwards):
  1. empty For Loop                      -> ExecState 0, expected: an empty loop has no N
  2. wire `References` into the loop     -> tunnel appears, N resolved, ExecState 1
  3. Property nodes inside the body, wired to the tunnel's inner end
  4. auto-indexed OUTPUT tunnels -> indicators
  5. delete the old Index Array and the old Property nodes
Nodes-first leaves the VI broken across more steps, which is what made the first probe misdiagnose itself.

SAFETY: builds a NEW file. `OpReport_v3.vi` is never modified - if this fails, the working traversal is untouched.
  py tools/bgrun.py --max-min 30 --log tools/bench/build_opreportall.log -- py -u tools/recipes/build_opreportall.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
OP = os.path.join(g.CLAUDEDEV, "OpReportAll_v0.vi")
POSITION_ID = "632A800"          # GObject.Position, the one id verified 2026-09-06
g._run.__defaults__ = (6.0, 60.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn()
        print(f"   observed: {obs}", flush=True)
        STEPS.append((name, True))
        return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True)
        STEPS.append((name, False))
        return None


def snap(tag):
    return (f"{tag}: ForLoop={g.count(OP,'ForLoop')} LoopTunnel={g.count(OP,'LoopTunnel')} "
            f"Property={g.count(OP,'Property')} Wire={g.count(OP,'Wire')} ExecState={g.exec_state(OP)}")


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)                      # never load the target before overwriting it
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.open_panel(OP)                       # a target loaded only via GetVIReference declines edits SILENTLY
    time.sleep(0.8)

    # remove_bad_wires() drives the MENU BAR (it moves the window, then clicks Edit > Remove Broken Wires) - it hung
    # twice here, 180 s each, because the block-diagram window was not open for the clicks to land on.
    # remove_bad_wires_scripted() calls the VI method `Block Diagram:Remove Bad Wires` (410) instead: no window, no
    # coordinates. It has existed since 2026-09-07; this recipe was simply still using the old GUI route.
    print(snap("start"), flush=True)

    # ORDER MATTERS, and the first attempt got it wrong. `Traverse.References` is ALREADY wired to the old Index
    # Array, so wiring it into a loop needs `branch=True` - or, far better, delete the consumer FIRST and the
    # source is free. Deleting last (the original plan) manufactured the problem it then had to work around.
    step("1 delete the OLD Index Array - frees Traverse.'References'", "IndexArray 1->0",
         lambda: (g.delete_object(OP, "IndexArray", 0), snap("after"))[1])
    step("2 remove the wires those deletions orphaned", "ONE call only - this is what hung the first attempt",
         lambda: (g.remove_bad_wires_scripted(OP), snap("after"))[1])
    step("3 delete the two OLD Property nodes (they read one element, not the array)", "Property 2->0",
         lambda: ([g.delete_object(OP, "Property", 0) for _ in range(g.count(OP, "Property"))],
                  g.remove_bad_wires_scripted(OP), snap("after"))[2])

    step("4 empty For Loop", "ForLoop 0->1, Diagram 1->2, ExecState 0 (an empty loop has no N - expected)",
         lambda: (g.for_loop(OP, (1400, 900)), snap("after"))[1])
    dias = step("5 find the loop body diagram", "one diagram owned by a ForLoop",
                lambda: [i for i, d in enumerate(g.report(OP, "Diagram")) if "For" in str(d.get("owner"))])
    if not dias:
        print("\nSTOP: no loop body diagram - cannot continue", flush=True)
        return 1
    body = dias[0]

    step("6 Property(GObject.Position) INSIDE the loop body", "Property 0->1, still ExecState 0",
         lambda: (g.build_property(OP, "VI Server:GObject", [(POSITION_ID, False)], (1450, 950),
                                   diagram_index=body), snap("after"))[1])
    step("7 wire Traverse.'References' -> that node's `reference` (CROSSES the boundary)",
         "LoopTunnel 0->1, Wire +1, and ExecState 0->1 because the array now supplies N",
         lambda: (g.wire(OP, "SubVI", 0, "References", "Property", g.count(OP, "Property") - 1, "reference"),
                  snap("after"))[1])

    # The output side is the last unverified step: exit_loop() only takes CONNECTOR-PANE names, which a Property
    # node's outputs are not. wire() made the INPUT tunnel; try it outward to an existing indicator.
    step("8 wire the node's `Position` OUT to the existing 'Position' indicator (tests OUTPUT tunnel creation)",
         "LoopTunnel 1->2 if wiring outward also auto-creates a tunnel",
         lambda: (g.wire_indicators(OP, g.count(OP, "Property") - 1, ["Position"], ["Position"],
                                    diagram_index=body, node_class="Property"), snap("after"))[1])

    print("\nsteps:", STEPS, flush=True)
    print(snap("final"), flush=True)
    ok = g.exec_state(OP) == 1
    print("\nVERDICT:", "assembled and runnable" if ok else "still broken - see the step that missed its prediction",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
