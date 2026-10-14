"""latest_graph - offline, read-only (lean task latest): the pick (RingPickSlot #29719) and check (RingSeqCheck #29724) call sites
in loop 1.2 of the stored P6 bed graph - every terminal, its wire, and the other ends of that wire (two hops through tunnels).
    py tools/bench/lean_bench/latest_graph.py [graph json] [uid ...]"""
import json, os, sys                                                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
av = sys.argv[1:]
G = av[0] if av and av[0].endswith(".json") else os.path.join(os.path.dirname(HERE), "graph_ring_p6_20261012_212645.json")
UIDS = [int(x) for x in av[1:]] if len(av) > 1 else [29719, 29724, 16483, 30001]
d = json.load(open(G, encoding="utf-8"))
T = d["terminals"]
by_wire, by_owner = {}, {}
for t in T:
    if t["wire_uid"]:
        by_wire.setdefault(t["wire_uid"], []).append(t)
    by_owner.setdefault(int(t["owner_uid"]), []).append(t)


def ends(t):
    return [x for x in by_wire.get(t["wire_uid"], []) if x is not t] if t["wire_uid"] else []


def fmt(x):
    return "%s %s %r%s d%s" % (x["owner_uid"], x["owner_class"], x["term_name"], " src" if x["is_source"] else "", x.get("frame_diagram"))


for u in UIDS:
    ts = by_owner.get(u, [])
    print("=== #%d (%s) %d terminals" % (u, ts[0]["owner_class"] if ts else "?", len(ts)))
    for t in ts:
        e = ends(t)
        print("  %-22r %s w%s -> %s" % (t["term_name"], "OUT" if t["is_source"] else "IN ", t["wire_uid"], "; ".join(fmt(x) for x in e)))
        for x in e:
            if "Tunnel" in x["owner_class"] or "ShiftRegister" in x["owner_class"] or x["owner_class"] in ("LoopTunnel", "SelectorTunnel"):
                for y in by_owner.get(int(x["owner_uid"]), []):
                    if y is x:
                        continue
                    print("      via %s: %s -> %s" % (x["owner_uid"], fmt(y), "; ".join(fmt(z) for z in ends(y))))
