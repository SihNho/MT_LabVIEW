"""p6fix_graph4 - offline, read-only: every Local node of the given names anywhere in the stored P6 bed graph (read or write),
its diagram and owner chain, and the other ends of its wire.
    py tools/bench/lean_bench/p6fix_graph4.py <graph json> <name> [...]"""
import json, sys                                                                         # noqa: E401
d = json.load(open(sys.argv[1], encoding="utf-8"))
T, OWN = d["terminals"], d["owners"]
by_wire = {}
for t in T:
    by_wire.setdefault(t["wire_uid"], []).append(t)


def chain(u):
    out, u = [], str(u)
    while u in OWN and len(out) < 8:
        out.append("%s#%s" % tuple(OWN[u]))
        u = str(OWN[u][1])
    return out


names = set(sys.argv[2:])
for t in T:
    if t["owner_class"] == "Local" and t["term_name"] in names:
        o = [x for x in by_wire.get(t["wire_uid"], []) if x is not t] if t["wire_uid"] else []
        print("%s %r %s w%s d%s %s -> %s" % (t["owner_uid"], t["term_name"], "READ" if t["is_source"] else "WRITE", t["wire_uid"],
                                            t["frame_diagram"], chain(t["frame_diagram"])[:4],
                                            "; ".join("%s %s %r d%s" % (x["owner_uid"], x["owner_class"], x["term_name"], x["frame_diagram"]) for x in o)))
