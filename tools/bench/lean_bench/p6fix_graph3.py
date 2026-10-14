"""p6fix_graph3 - offline, read-only: for each given node uid print its terminals and, per wire, every other end
(owner uid, class, terminal name, diagram); diagrams' owner chains for the listed diagrams.
    py tools/bench/lean_bench/p6fix_graph3.py <graph json> node <uid> [...] | diag <uid> [...] | ondiag <diag uid>"""
import json, sys                                                                         # noqa: E401
d = json.load(open(sys.argv[1], encoding="utf-8"))
T, OWN = d["terminals"], d["owners"]
by_wire = {}
for t in T:
    by_wire.setdefault(t["wire_uid"], []).append(t)
mode = sys.argv[2]
for a in sys.argv[3:]:
    if mode == "node":
        print("node", a)
        for t in T:
            if str(t["owner_uid"]) == a:
                o = [x for x in by_wire.get(t["wire_uid"], []) if x is not t] if t["wire_uid"] else []
                print("  %s %r %s w%s d%s -> %s" % (t["owner_class"], t["term_name"], "src" if t["is_source"] else "snk", t["wire_uid"],
                                                    t["frame_diagram"], "; ".join("%s %s %r d%s" % (x["owner_uid"], x["owner_class"], x["term_name"], x["frame_diagram"]) for x in o)))
    elif mode == "diag":
        u, ch = a, []
        while u in OWN and len(ch) < 12:
            ch.append(tuple(OWN[u]))
            u = str(OWN[u][1])
        print("diag", a, ch)
    elif mode == "ondiag":
        own = sorted(set((t["owner_uid"], t["owner_class"]) for t in T if str(t["frame_diagram"]) == a))
        print("diag", a, len(own), own)
