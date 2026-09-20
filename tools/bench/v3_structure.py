"""v3_structure.py - structural read of PARALLEL_kernel_v3_withdead (SPEC copy): every diagram's nodes and wires, the loops,
SubVIs and control terminals with positions -> tools/bench/v3_structure.json + a printed summary, so the dead four-fold
code can be deleted precisely (the 'loop uid 248' guess removed 2 SubVIs and broke the VI).
  py tools/bgrun.py --max-min 20 --log tools/bench/v3_structure.log -- py -u tools/bench/v3_structure.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3_withdead.vi"); DST = os.path.join(g.CLAUDEDEV, "SPEC", "V3DEAD.vi")
OUT = os.path.join(HERE, "v3_structure.json")


def main():
    if os.path.exists(DST):
        os.remove(DST)
    shutil.copyfile(SRC, DST); g.report(DST, "SubVI"); g.open_panel(DST); time.sleep(1.0)
    res = {"fp": g.fp_labels(DST), "objects": {}}
    for cls in ("ForLoop", "WhileLoop", "SubVI", "Function", "IndexArray", "ControlTerminal", "Constant", "Diagram", "LoopTunnel", "Wire"):
        try:
            res["objects"][cls] = g.report(DST, cls)
        except Exception as e:
            res["objects"][cls] = str(e)[:100]
    for cls, v in res["objects"].items():
        print(f"{cls}: {len(v) if isinstance(v, list) else v}", flush=True)
    print("loops:", [(o["uid"], tuple(o["pos"]), o.get("owner")) for o in res["objects"]["ForLoop"]], flush=True)
    print("diagrams:", [(o["uid"], o.get("owner"), tuple(o["pos"])) for o in res["objects"]["Diagram"]], flush=True)
    print("SubVIs:", [(o["uid"], tuple(o["pos"]), o.get("owner")) for o in res["objects"]["SubVI"]], flush=True)
    print("FP:", res["fp"], flush=True)
    nd = len(res["objects"]["Diagram"]); res["diagrams"] = {}
    for d in range(nd):
        nodes, nets = g.net_map(DST, d, max_nodes=60, max_terms=24)
        res["diagrams"][d] = {"nodes": {str(k): v for k, v in nodes.items()}, "nets": {str(k): v for k, v in nets.items()}}
        print(f"diagram {d}: {len(nodes)} nodes; uids {[v[0] for v in nodes.values()]}", flush=True)
        for n, (uid, _, terms) in nodes.items():
            named = [(t, nm[:22].replace(chr(10), ' '), w) for t, nm, w in terms if nm]
            print(f"   node {n} uid {uid}: {named[:14]}", flush=True)
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, default=str); print("saved", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
