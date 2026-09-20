"""globals_direction_main.py - READ or WRITE at every access site of the main VI's global fields, by OpNodeTerms_v0.

docs/main-vi-state.md knows WHERE the seven access sites of `Global motor pos.vi` are (Trans position: diagrams
5/19/83, Rot position: 8/19/83, Focus position: 19) but not their direction. A global node has one data terminal;
`Terminal.Is Source?` TRUE = the node emits data = READ, FALSE = the node consumes data = WRITE (semantics verified
on primitives in tools/bench/test_opnodeterms.log T1b; diagram 19's three sites already measured there: all WRITE).
For each site: net_map the diagram (oracle for the Nodes[] index and the terminal tuple), run gscript.node_terms on
that node, record direction + wire UID. Output tools/bench/main_vi_globals_direction.json and a table.
Read-only against the main VI.
  py tools/bgrun.py --max-min 12 --log tools/bench/globals_direction_main.log -- py -u tools/bench/globals_direction_main.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

CACHE = json.load(open(os.path.join(HERE, "main_vi_netmap.json"), encoding="utf-8"))
TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
MAIN = TREE["vi"]
FIELDS = ("Trans position", "Rot position", "Focus position")
OUT = os.path.join(HERE, "main_vi_globals_direction.json")
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    sites = []
    for k, dg in CACHE["diagrams"].items():
        for uid, nd in dg["nodes"].items():
            for t, w in nd.get("terms", []):
                if t in FIELDS:
                    sites.append((int(k), int(uid), t, w))
    sites.sort()
    print(f"{len(sites)} access sites in the cache: {sites}", flush=True)
    results = []
    t0 = time.time()
    for k in sorted({s[0] for s in sites}):
        nodes, _ = g.net_map(MAIN, k, max_nodes=60, max_terms=24)
        by_uid = {u: (n, [(t, w) for _ti, t, w in terms]) for n, (u, _l, terms) in nodes.items()}
        for (dk, uid, field, wire) in [s for s in sites if s[0] == k]:
            if uid not in by_uid:
                results.append({"diagram": k, "uid": uid, "field": field, "error": "node not in walk"})
                print(f"   diagram {k} uid {uid} {field}: NOT IN WALK", flush=True)
                continue
            n, oracle = by_uid[uid]
            rows = g.node_terms(MAIN, k, n)
            data = [r for r in rows if r["name"]]
            ok = [(r["name"], r["wire"]) for r in rows][:len(oracle)] == oracle
            direction = None
            if len(data) == 1 and not data[0]["src_err"]:
                direction = "READ" if data[0]["is_source"] else "WRITE"
            results.append({"diagram": k, "owner": TREE["diagrams"][str(k)]["owner"], "uid": uid, "n": n, "field": field,
                            "wire": wire, "direction": direction, "rows": rows, "tuple_match": ok})
            print(f"   diagram {k:3d} ({TREE['diagrams'][str(k)]['owner']}) uid {uid:5d} n {n:2d} {field:15s} -> "
                  f"{direction}  (named terminals {len(data)}, tuple==walker {ok}, errs "
                  f"{[(r['name_err'], r['src_err'], r['conn_err'], r['wire_err']) for r in data]})", flush=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"vi": MAIN, "sites": results, "semantics": "Is Source? TRUE = READ, FALSE = WRITE"}, f, indent=1)
    print(f"\n{len(results)} sites in {time.time() - t0:.0f} s -> {OUT}", flush=True)
    print("\nfield            | WRITE sites (diagram)        | READ sites (diagram)", flush=True)
    for field in FIELDS:
        w = [str(r["diagram"]) for r in results if r["field"] == field and r.get("direction") == "WRITE"]
        rd = [str(r["diagram"]) for r in results if r["field"] == field and r.get("direction") == "READ"]
        un = [str(r["diagram"]) for r in results if r["field"] == field and not r.get("direction")]
        print(f"{field:16s} | {', '.join(w):28s} | {', '.join(rd)}{'   UNDECIDED ' + ', '.join(un) if un else ''}", flush=True)
    return 0 if all(r.get("direction") and r.get("tuple_match") for r in results) else 3


if __name__ == "__main__":
    sys.exit(main())
