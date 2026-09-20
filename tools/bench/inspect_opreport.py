"""inspect_opreport.py - read OpReport_v3's own diagram, so a name-reading op can be grafted onto it.

Goal: answer "which VI does this subVI node call?", which the toolkit currently cannot do. The readable properties are
`SubVI.VI Name` **635E401** and `SubVI.VI Path` **635E403** (labviewwiki, registered in docs/vi-server-ids.json on
2026-09-12). Both need a SubVI-class reference, and the only thing that yields one for NESTED nodes is the Traverse that
OpReport_v3 already performs — `Nodes[]` on the top-level diagram sees top-level nodes only, and the main VI's frame loop
is three levels down.

So the plan is the same graft that produced OpConPane_v0: copy the op, add a Property Node of class `VI Server:SubVI`
reading 635E401, feed it the reference the traverse already produces, put an indicator on its output. This script only
LOOKS, so the graft can be written against facts instead of guesses.

Read-only; OpReport_v3 is one of our own ops in claudeDev and is not modified here.
  py tools/bgrun.py --max-min 15 --log tools/bench/inspect_opreport.log -- py -u tools/bench/inspect_opreport.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
g._run.__defaults__ = (6.0, 45.0)


def main():
    g._lv = None
    if not os.path.exists(OP):
        print("STOP: not found", OP, flush=True); return 3
    print("target:", OP, os.path.getsize(OP), "bytes", flush=True)
    counts = {c: g.count(OP, c) for c in ("Node", "SubVI", "Property", "Invoke", "IndexArray",
                                          "Function", "Constant", "Diagram", "CaseStructure", "ForLoop", "Wire")}
    print("counts:", {k: v for k, v in counts.items() if v}, flush=True)
    print("front panel:", [l for _, l, _ in g.fp_labels(OP)], flush=True)
    try:
        print("top-level styles:", [(i, s, t) for i, s, t in g.node_info(OP, max_n=60)], flush=True)
    except Exception as e:
        print("node_info:", str(e)[:140], flush=True)
    for d in range(counts.get("Diagram", 1)):
        try:
            nodes, _ = g.net_map(OP, diagram_index=d, max_nodes=60, max_terms=24)
        except Exception as e:
            print(f"  diagram {d}: net_map failed {str(e)[:100]}", flush=True); continue
        if not nodes:
            continue
        print(f"  --- diagram {d}: {len(nodes)} node(s)", flush=True)
        for i, (uid, lbl, terms) in nodes.items():
            print(f"     uid {uid:<6} {lbl!r} terms={[nm for _, nm, _ in terms if nm][:16]}", flush=True)
    print("\nDONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
