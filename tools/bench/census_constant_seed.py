"""census_constant_seed.py - READ-ONLY: which NI scripting example carries a property node whose class is Constant
(data terminal 'Value' with a Constant-typed 'reference' input)? That node's `reference` input is the seed for a
Constant-typed refnum control (the row-28 trick), which unblocks OpConstValue_v0 (Constant.Value 634AC00) - needed to
read the four selector constants of the original's reseed Case (step E). Prints every Property Node of each example's
diagrams with its data terminal name and the label of the node feeding its 'reference'.
  py tools/bgrun.py --max-min 8 --log tools/bench/census_constant_seed.log -- py -u tools/bench/census_constant_seed.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

D = os.path.join(g.CLAUDEDEV, "NIScriptingExamples")
# backslashes: a forward slash inside the 'vi path' made the op's Open VI Reference fail -> 1055 (run 1, 03:54)
FILES = [r"Finding and Modifying Objects\Obtaining Known Object Reference.vi",
         r"Finding and Modifying Objects\Navigating Nodes and Wires.vi",
         r"Finding and Modifying Objects\Obtaining Unknown Object References.vi",
         r"Finding and Modifying Objects\Tagging.vi",
         r"Finding and Modifying Objects\Navigating Structures.vi",
         r"Structures\VI Scripting with Structures - Case Structure.vi"]
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    for f in FILES:
        p = os.path.join(D, f)
        print(f"\n######## {f}", flush=True)
        for dia in range(0, 6):
            try:
                labels = {r["uid"]: r["label"] for r in g.node_labels(p, dia)}
            except Exception as e:
                if dia == 0:
                    print(f"   EXC {str(e)[:100]}", flush=True)
                break
            if not labels:
                break
            rows_by = {}
            for n in range(80):
                u, rows = g.node_terms_uid(p, dia, n)
                if not u:
                    break
                rows_by[u] = rows
            for u, rows in rows_by.items():
                if labels.get(u) != "Property Node":
                    continue
                data = [r["name"] for r in rows if r["i"] >= 4]
                ref = next((r for r in rows if r["name"] == "reference" and not r["is_source"]), None)
                feeder = None
                if ref and ref["wire"]:
                    feeder = next(((labels.get(uu), rr["name"]) for uu, rr2 in rows_by.items() for rr in rr2 if rr["is_source"] and rr["wire"] == ref["wire"]), None)
                print(f"   d{dia} PN uid {u}: data {data}; reference <- {feeder}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
