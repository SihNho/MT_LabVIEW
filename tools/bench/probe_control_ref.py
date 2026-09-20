"""probe_control_ref.py - can a control REFERENCE be created and wired to a Value property node, by script?

This is the one unproven step blocking the top open measurement. The frame loop's only unconditional per-frame cost is
two `Value` property node reads, each of which runs in the UI thread, and nobody has measured what that costs when the
panel is busy - which is the mechanism behind the user's "displaying the image destabilises frames". Building the
timing harness needs a control reference wired into a property node, and this project has never done that by script.

Rather than assume it works and discover otherwise halfway through a build, this probes the pieces in order and reports
which rung the ladder breaks on. Each step is a prediction; the point is to find the first miss cheaply.

  1. make a scratch VI in claudeDev                                 - copy a small op as the base
  2. what does `g.build_property` accept for the Control class?     - does a `Value` property node even build?
  3. is there a way to obtain a control reference on the diagram?   - the candidates, in order of likelihood:
       (a) OpFPLabels_v0's existing chain: Front Panel -> Panel.Controls[] -> Index Array -> a Control refnum.
           That already EXISTS and already yields a Control reference at runtime, which may be all the harness needs -
           the harness does not require a statically-wired reference, only a way to read `Value` in a loop.
       (b) a front-panel Control Reference object, which would need an FP-object creator the fleet does not have.
  Route (a) is very likely sufficient and needs no new capability at all: OpFPLabels already reads `Control.Label`
  through exactly this chain, so swapping the property from `Label` to `Value` is a one-property change.

If (a) holds, the timing harness is not a new build at all - it is OpFPLabels_v0 with a different property and a loop,
and the measurement can proceed immediately.

READ-ONLY against originals; everything happens on copies in claudeDev.
  py tools/bgrun.py --max-min 15 --log tools/bench/probe_control_ref.log -- py -u tools/bench/probe_control_ref.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

FPLABELS = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
g._run.__defaults__ = (6.0, 60.0)


def main():
    g._lv = None
    print("=== step 1: does OpFPLabels_v0 exist and what is it made of?", flush=True)
    if not os.path.exists(FPLABELS):
        print("   MISSING - the whole route (a) argument rests on this VI", flush=True); return 3
    counts = {c: g.count(FPLABELS, c) for c in ("Property", "IndexArray", "SubVI", "Node", "Wire")}
    print("   counts:", counts, flush=True)

    print("\n=== step 2: its property nodes, with their properties as terminal names", flush=True)
    nodes, _ = g.net_map(FPLABELS, diagram_index=0, max_nodes=40, max_terms=16)
    prop_uids = {o["uid"] for o in g.report(FPLABELS, "Property")}
    for i, (uid, lbl, terms) in nodes.items():
        names = [nm for _, nm, _ in terms if nm]
        tag = "PROPERTY" if uid in prop_uids else "         "
        print(f"   {tag} node[{i}] uid {uid:<6} {names}", flush=True)

    print("\n=== step 3: the front-panel objects it exposes (its own pane)", flush=True)
    for uid, lbl, ind in g.fp_labels(FPLABELS, max_n=40):
        print(f"   {'indicator' if ind else 'CONTROL  '} {lbl!r}", flush=True)

    print("\n=== VERDICT INPUTS", flush=True)
    print("   If one of the property nodes above reads `Label` off a Control refnum that came from\n"
          "   Panel.Controls[] -> Index Array, then route (a) holds: the same chain reads `Value` instead, and the\n"
          "   UI-thread timing harness is a one-property edit of an op that already works - no new capability, no\n"
          "   front-panel object creation, no unproven wiring.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
