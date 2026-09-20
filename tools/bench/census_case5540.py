"""census_case5540.py - READ-ONLY (main VI opened by reference only, never edited/saved): the selector chain of the
frame loop's reseed Case #5540 and the Case's own terminals - what exactly the original compares before it replaces
the fed-back x,y,z / good flags (stage-2 plan item 3; rule 1a: reproduce case-for-case, never an equivalent).
Upstream per docs/frame-loop-wire-graph.md: #9647 And, #10247 Or, #10950 Less?, #17289 Property `min value`.Value.
Prints every terminal (name, direction, wire) of those nodes + #5540 on diagram 43, the labels of diagram 43's nodes
whose outputs feed them, and the two frames' node lists (diagrams owned by #5540).
  py tools/bgrun.py --max-min 8 --log tools/bench/census_case5540.log -- py -u tools/bench/census_case5540.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

MAIN = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
DIA = 43
# the FULL selector slice (peer ...-stage2-step-e-reseed-case-plan): the lost-bead term (Less? <- min value <- Array
# Max & Min <- pos in cal image out) AND the periodic auto-reset term (# of Auto-Reset, Quotient & Remainder, Equal?,
# Not/And) - plus every node whose output feeds any of them (second hop printed below)
WANT = {5540, 9647, 10247, 10950, 17289, 9879, 10068, 10019, 10969}
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    labels = {r["uid"]: r["label"] for r in g.node_labels(MAIN, DIA)}
    rows_by = {}
    for n in range(400):
        u, rows = g.node_terms_uid(MAIN, DIA, n)
        if not u:
            break
        rows_by[u] = (n, rows)
    wires_in = {}
    for u in WANT:
        if u not in rows_by:
            print(f"uid {u}: NOT on diagram {DIA}", flush=True); continue
        n, rows = rows_by[u]
        print(f"\n#{u} {labels.get(u)!r} (n{n}):", flush=True)
        for r in rows:
            print(f"   {r['i']:>3} | {r['name']!r:<30} | {'S' if r['is_source'] else 's'} | wire {r['wire']}", flush=True)
            if not r["is_source"] and r["wire"]:
                wires_in[r["wire"]] = (u, r["name"])
    print("\nSources of those input wires (same diagram):", flush=True)
    for u, (n, rows) in rows_by.items():
        for r in rows:
            if r["is_source"] and r["wire"] in wires_in:
                tgt = wires_in[r["wire"]]
                print(f"   wire {r['wire']}: #{u} {labels.get(u)!r}.{r['name']!r} -> #{tgt[0]}.{tgt[1]!r}", flush=True)
    dias = g.report_all(MAIN, "Diagram")
    frames = [i for i, d in enumerate(dias) if str(d.get("owner")) == "CaseStructure"]
    print(f"\nCaseStructure-owned diagrams on the VI: {len(frames)} (cannot tell which belong to #5540 from owner class alone)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
