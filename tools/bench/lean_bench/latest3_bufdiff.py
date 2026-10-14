"""latest3_bufdiff - offline, read-only (lean task latest retry 2, open item b): where loop 1.1 computes the value it writes into
the `BufDiff` slot array. Walks UPSTREAM from the Replace Array Subset #29683 (p6fix_graph4: frame 2 of loop 1.1's seqlock) in the
stored bed graph, printing every node's input terminals and their sources, to the given depth.
    py tools/bench/lean_bench/latest3_bufdiff.py [graph json] [start uid] [depth]"""
import json, os, sys                                                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
G = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "graph_ring_p6_20261012_212645.json")
START = int(sys.argv[2]) if len(sys.argv) > 2 else 29683
DEPTH = int(sys.argv[3]) if len(sys.argv) > 3 else 6
d = json.load(open(G, encoding="utf-8"))
T = d["terminals"]
by_owner, by_wire = {}, {}
for t in T:
    by_owner.setdefault(t["owner_uid"], []).append(t)
    if t["wire_uid"]:
        by_wire.setdefault(t["wire_uid"], []).append(t)


def label(u):
    ts = by_owner.get(u, [])
    return "%s#%s" % (ts[0]["owner_class"] if ts else "?", u)


def src_of(t):
    return [x for x in by_wire.get(t["wire_uid"], []) if x["is_source"] and x is not t] if t["wire_uid"] else []


def walk(u, depth, seen, ind=""):
    ts = by_owner.get(u, [])
    print("%s%s d%s  out: %s" % (ind, label(u), ts[0]["frame_diagram"] if ts else "?",
                                ", ".join("%r->%s" % (t["term_name"], "; ".join(label(x["owner_uid"]) + ":" + repr(x["term_name"])
                                          for x in by_wire.get(t["wire_uid"], []) if not x["is_source"])) for t in ts if t["is_source"])))
    if u in seen or depth == 0:
        return
    seen.add(u)
    for t in ts:
        if not t["is_source"]:
            ss = src_of(t)
            print("%s  in %r <- %s" % (ind, t["term_name"], ", ".join("%s %r" % (label(s["owner_uid"]), s["term_name"]) for s in ss) or "(unwired)"))
            for s in ss:
                walk(s["owner_uid"], depth - 1, seen, ind + "    ")


def kids(u, depth, ind=""):
    """--kids: the objects owned by u (diagrams, tunnels, nodes), depth levels down, with each node's wired inputs' sources"""
    sub = sorted(set([int(k) for k, v in d["owners"].items() if str(v[1]) == str(u)] +
                     [t["owner_uid"] for t in T if str(t["frame_diagram"]) == str(u)]))
    for k in sub:
        if True:
            ts = by_owner.get(int(k), [])
            ins = ["%r<-%s" % (t["term_name"], ",".join(label(s["owner_uid"]) + ":" + repr(s["term_name"]) for s in src_of(t)))
                   for t in ts if not t["is_source"] and t["wire_uid"]]
            outs = ["%r->%s" % (t["term_name"], ",".join(label(x["owner_uid"]) + ":" + repr(x["term_name"])
                    for x in by_wire.get(t["wire_uid"], []) if not x["is_source"])) for t in ts if t["is_source"] and t["wire_uid"]]
            print("%s%s#%s  in[%s] out[%s]" % (ind, ts[0]["owner_class"] if ts else v[0] if False else "obj", k, "; ".join(ins), "; ".join(outs)))
            if depth > 1:
                kids(k, depth - 1, ind + "    ")


if __name__ == "__main__":
    print("graph", G, "keys", sorted(d.keys()))
    if "--obj" in sys.argv:                            # the stored record(s) of one object (e.g. a constant's value, if stored)
        objs = d["objs"]
        rec = objs.get(str(START)) if isinstance(objs, dict) else [o for o in objs if str(o.get("uid")) == str(START)]
        print(json.dumps(rec, default=str)[:2000])
        print("first obj record:", json.dumps(objs[0] if isinstance(objs, list) else next(iter(objs.items())), default=str)[:600])
    elif "--kids" in sys.argv:
        print("owner of %s: %s" % (START, d["owners"].get(str(START))))
        kids(START, DEPTH)
    else:
        walk(START, DEPTH, set())
