"""ui_thread_cost.py - what does a `Value` property node cost per frame, and how much worse does a busy panel make it?

THE QUESTION THIS ANSWERS, and why it is now the top open measurement. Reading `ASI_adjust focus-subvi.vi` showed that
the only cost the frame loop pays UNCONDITIONALLY on every iteration is **two `Value` property node reads** (uids 46
and 108 on its top-level diagram) - the serial VIs and the fixed Wait are all inside a case gated by the focus keys.
A `Value` property node always executes in the **UI thread**, so its latency is not a constant: it queues behind
whatever else the UI thread is doing, panel redraws included. That is a precise mechanism for the user's own report -
*"현재는 화면에 이미지 프린트하면 프레임 딜레이가 말도 안되게 느려져서 아예 연결을 해제해놨거든"* - and it is the
difference between a per-frame cost of tens of microseconds and one that eats a visible share of the 6.00 ms budget
measured for 150 Hz.

DESIGN. A purpose-built VI (in claudeDev, never an original) holds a numeric control, a control reference to it, and a
For Loop that reads `Value` N times, bracketed by the millisecond timer. The same VI is then run under three
conditions, which is the whole experiment:

  (a) panel CLOSED          - the floor: what the property node costs with nothing to contend with;
  (b) panel OPEN, idle      - adds the UI thread being alive and the control being drawn;
  (c) panel OPEN, redrawing - a graph updated in a parallel loop, i.e. the condition the rig is actually in when the
                              image display is connected. This is the one the user hit.

The contrast (c) - (a) IS the cost of having a live display, expressed in the same milliseconds as the frame budget.

STATUS: SCAFFOLD. The measurement design and the reasoning are recorded here so the next session executes rather than
re-derives. Building the VI needs a control reference and a timed loop; `g.create_control`, `g.build_property` and
`g.for_loop` cover the parts, but the reference-to-control wiring has not been done by script before in this project
and is the step to prove first.

READ-ONLY with respect to originals; the harness lives in claudeDev, where saving is permitted.
  py tools/bgrun.py --max-min 25 --log tools/bench/ui_thread_cost.log -- py -u tools/bench/ui_thread_cost.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

HARNESS = os.path.join(g.CLAUDEDEV, "UITHREAD_cost_v0.vi")
N_READS = 2000
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    print(__doc__.split("STATUS:")[0].strip()[:400], "...\n", flush=True)
    print("SCAFFOLD ONLY - not yet implemented. The pieces and the order to build them:", flush=True)
    for line in (
        "1. new VI in claudeDev with a DBL control 'x' (g.create_control or a copied donor FP object)",
        "2. a control REFERENCE to 'x' on the diagram, wired to a Property Node with property 'Value'",
        "   - this is the step never done by script here; prove it on a scratch VI before trusting the timings",
        "3. a For Loop of N=%d around the property node, with Tick Count before and after" % N_READS,
        "4. run three ways: panel closed / panel open idle / panel open with a graph redrawing in a parallel loop",
        "5. report ms per read for each, and (c)-(a) as 'the cost of a live display' against the 6.00 ms budget",
    ):
        print("   " + line, flush=True)
    print("\nWhy the third condition matters most: it is the only one that reproduces what the user actually ran into,\n"
          "and the first two exist to separate 'property nodes are slow' from 'the UI thread is busy'.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
