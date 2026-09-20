"""sweep_nodeterms_main.py - a complete, junk-free net map of the main VI WITH terminal direction, by OpNodeTerms_v0.

For every diagram k (tools/bench/diagram_tree_main.json: owner + Nodes[] uid list, 170 diagrams, 635 nodes) and
every node index n < len(uids): gscript.node_terms(MAIN, k, n) -> [(name, is_source, wire, errs)]. ~0.8 s per node.
Node uid: from the tree's uid list at index n (the tree was built from the same Nodes[] order); cross-checked per
node against tools/bench/main_vi_netmap.json where that cache has the node (names + wire uids per index; the cache
is 'at least' - it truncated on some diagrams) - every disagreement is recorded, none absorbed.
Output tools/bench/main_vi_nodeterms.json:
    {"vi", "diagrams": {k: {"owner", "nodes": [{"n", "uid", "terms": [{"i","name","is_source","wire","errs"}]}]}},
     "mismatches": [...], "stats": {...}}
Read-only against the main VI (never opened). Progress line per diagram.
  py tools/bgrun.py --max-min 25 --log tools/bench/sweep_nodeterms_main.log -- py -u tools/bench/sweep_nodeterms_main.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
CACHE = json.load(open(os.path.join(HERE, "main_vi_netmap.json"), encoding="utf-8"))
MAIN = TREE["vi"]
OUT = os.path.join(HERE, "main_vi_nodeterms.json")
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    out = {"vi": MAIN, "diagrams": {}, "mismatches": [], "stats": {}}
    # class census first (cheap, one run each): global and local-variable nodes by Traverse class (peer (d): the
    # scripting class for locals is 'Local'); recorded, compared later with what the sweep finds by terminal shape.
    for cls in ("Global", "Local", "LocalVariable", "Property", "Invoke"):
        try:
            rows = g.report_all(MAIN, cls)
            out["stats"][f"class_{cls}"] = [o["uid"] for o in rows]
            print(f"class {cls!r}: {len(rows)} objects", flush=True)
        except Exception as e:
            print(f"class {cls!r}: {str(e)[:80]}", flush=True)
    t0 = time.time()
    n_nodes = n_terms = n_checked = 0
    for k in sorted(TREE["diagrams"], key=int):
        uids = TREE["diagrams"][k]["uids"]
        cache_nodes = CACHE["diagrams"].get(k, {}).get("nodes", {})
        drows = []
        for n, uid in enumerate(uids):
            try:
                node_uid, rows = g.node_terms_uid(MAIN, int(k), n)
            except Exception as e:
                out["mismatches"].append({"diagram": int(k), "n": n, "uid": uid, "why": f"EXC {str(e)[:120]}"})
                continue
            # Peer (a)/(c): identity is measured, not cached - the op returns the node's own UID; 0 = index out of
            # range (distinguishable from a real node with zero terminals).
            if not node_uid:
                out["mismatches"].append({"diagram": int(k), "n": n, "uid": uid, "why": "node index out of range (UID 0)"})
                print(f"   diagram {k} n {n}: OUT OF RANGE - tree lists {len(uids)} nodes; stopping this diagram", flush=True)
                break
            if node_uid != uid:
                out["mismatches"].append({"diagram": int(k), "n": n, "tree_uid": uid, "node_uid": node_uid,
                                          "why": "Nodes[] order differs from the Step-0 tree"})
            terms = [{"i": r["i"], "name": r["name"], "is_source": r["is_source"], "wire": r["wire"],
                      "errs": [r["name_err"], r["src_err"], r["conn_err"], r["wire_err"]]} for r in rows]
            while terms and not terms[-1]["name"] and not terms[-1]["wire"]:
                terms.pop()                                   # trailing empties (past the end of Terminals[])
            drows.append({"n": n, "uid": node_uid, "tree_uid": uid, "terms": terms})
            n_nodes += 1; n_terms += len(terms)
            c = cache_nodes.get(str(uid))
            if c is not None:
                n_checked += 1
                mine = [(t["name"], t["wire"]) for t in terms]
                theirs = [(t, w) for t, w in c.get("terms", [])]
                # the cache stored only NAMED terminals with their wire; compare on that subset, in order
                mine_named = [(nm, w) for nm, w in mine if nm]
                if mine_named[:len(theirs)] != theirs:
                    out["mismatches"].append({"diagram": int(k), "n": n, "uid": uid, "op": mine_named, "cache": theirs})
        out["diagrams"][k] = {"owner": TREE["diagrams"][k]["owner"], "nodes": drows}
        print(f"diagram {k:>3} ({TREE['diagrams'][k]['owner'] or 'top'}): {len(drows)} nodes, "
              f"{sum(len(d['terms']) for d in drows)} terminals  ({time.time() - t0:.0f} s)", flush=True)
    out["stats"].update({"nodes": n_nodes, "terminals": n_terms, "checked_against_cache": n_checked,
                         "mismatches": len(out["mismatches"]), "seconds": round(time.time() - t0)})   # (run 1 overwrote the class lists here)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(f"\n{n_nodes} nodes, {n_terms} terminals, {n_checked} checked against the old cache, "
          f"{len(out['mismatches'])} mismatches, {time.time() - t0:.0f} s -> {OUT}", flush=True)
    for m in out["mismatches"][:20]:
        print("   MISMATCH", json.dumps(m, ensure_ascii=False)[:300], flush=True)
    return 0 if not out["mismatches"] else 3


if __name__ == "__main__":
    sys.exit(main())
