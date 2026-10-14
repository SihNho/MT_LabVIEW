"""p6fix_graph2 - offline, read-only: every Local read on loop 1.2's body (d23166) and in diagrams nested under it, with the
wire's sinks, from the stored P6 bed graph. Diagram nesting from the graph's `owners` map (uid -> [owner class, owner uid]).
    py tools/bench/lean_bench/p6fix_graph2.py <graph json> [body diagram uid=23166]"""
import json, sys                                                                         # noqa: E401
d = json.load(open(sys.argv[1], encoding="utf-8"))
BODY = int(sys.argv[2]) if len(sys.argv) > 2 else 23166
T, OWN = d["terminals"], d["owners"]
print("owners sample:", list(OWN.items())[:6])
print("owners[%d] =" % BODY, OWN.get(str(BODY)))


def chain(u):
    out, seen = [], set()
    u = str(u)
    while u in OWN and u not in seen:
        seen.add(u)
        c, p = OWN[u]
        out.append((c, p))
        u = str(p)
    return out


diags = sorted(set(int(t["frame_diagram"]) for t in T if t.get("frame_diagram") is not None))
nested = [x for x in diags if x == BODY or any(int(p) == BODY for _c, p in chain(x))]
print("diagrams under body %d: %s" % (BODY, nested))
by_wire = {}
for t in T:
    by_wire.setdefault(t["wire_uid"], []).append(t)
for t in T:
    if t["owner_class"] in ("Local", "GlobalVariable") and t.get("frame_diagram") in nested:
        sinks = [x for x in by_wire.get(t["wire_uid"], []) if x is not t] if t["wire_uid"] else []
        print("%s %s %r %s w%s d%s -> %s" % (t["owner_uid"], t["owner_class"], t["term_name"], "READ" if t["is_source"] else "WRITE",
                                             t["wire_uid"], t["frame_diagram"],
                                             "; ".join("%s %s %r" % (x["owner_uid"], x["owner_class"], x["term_name"]) for x in sinks)))
