"""find_property_nodes.py - locate every Property/Invoke node in the main VI by DIAGRAM, without walking diagrams.

The diagram-by-diagram scan was the wrong tool. `tools/bench/diagram_tree_main.json` (Step 0, 2026-09-12) already maps
**diagram index -> the UIDs of the nodes on it**, for all 170 diagrams. So one Traverse pass per class gives the UIDs of
every Property node, and a dictionary lookup says which diagram each one lives on. That replaces an hour of scanning
with about a minute, and it reaches diagrams 41-169 which the scan was never going to get to.

Why Property nodes specifically: the camera geometry in this VI is not set by any IMAQdx "set attribute" VI - the byte
scan proved only six IMAQdx VIs are referenced and none of them writes attributes - so whatever touches `Width`/`Height`
must be a property node. The front panel carries `Width` and `Height` as INDICATORS holding 640 and 512, which is the
user's reported halving recorded inside the VI.

Once a candidate diagram is known, `net_map` on that ONE diagram gives the node's terminal names, which for an IMAQdx
property node are the attribute names and their ORDER.

READ-ONLY: Traverse reads only; never modifies, never saves, never runs the VI. No hardware.
  py tools/bgrun.py --max-min 15 --log tools/bench/find_property_nodes.log -- py -u tools/bench/find_property_nodes.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
TREE = os.path.join(HERE, "diagram_tree_main.json")
OUT = os.path.join(HERE, "property_node_map.json")
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    tree = json.load(open(TREE, encoding="utf-8"))["diagrams"]
    where = {}                                   # node uid -> (diagram index, owning structure class)
    for dia, info in tree.items():
        for uid in info["uids"]:
            where.setdefault(int(uid), (int(dia), info["owner"]))
    print(f"diagram tree: {len(tree)} diagrams, {len(where)} distinct node UIDs\n", flush=True)

    found = {}
    for cls in ("Property", "Invoke"):
        try:
            objs = g.report(WORK, cls)
        except Exception as e:
            print(f"{cls}: FAILED {str(e)[:140]}", flush=True); continue
        print(f"=== {cls}: {len(objs)} nodes", flush=True)
        rows = []
        for o in objs:
            uid = o["uid"]
            dia, owner = where.get(uid, (None, "NOT IN TREE"))
            rows.append({"uid": uid, "diagram": dia, "owner": owner, "pos": o.get("pos")})
        rows.sort(key=lambda r: (r["diagram"] is None, r["diagram"] or 0, r["uid"]))
        for r in rows:
            print(f"   uid {r['uid']:<7} diagram {str(r['diagram']):<6} owner {r['owner']:<18} pos {r['pos']}", flush=True)
        found[cls] = rows
        # how the nodes are spread tells us where to spend a net_map
        by_dia = {}
        for r in rows:
            by_dia[r["diagram"]] = by_dia.get(r["diagram"], 0) + 1
        print(f"   per diagram: {dict(sorted(by_dia.items(), key=lambda kv: -kv[1]))}\n", flush=True)

    json.dump(found, open(OUT, "w", encoding="utf-8"), indent=1)
    print("written to", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
