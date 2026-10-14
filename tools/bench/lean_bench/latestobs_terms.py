"""latestobs_terms - offline, read-only: every terminal (order as stored) of the given owner uids, or of every owner of a class,
in a stored graph json.   py tools/bench/lean_bench/latestobs_terms.py [graph json] (uid | class) ..."""
import json, os, sys                                                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
av = sys.argv[1:]
G = av.pop(0) if av and av[0].endswith(".json") else os.path.join(os.path.dirname(HERE), "graph_ring_p6_20261012_212645.json")
d = json.load(open(G, encoding="utf-8"))
by = {}
for t in d["terminals"]:
    by.setdefault(int(t["owner_uid"]), []).append(t)
want = set()
for a in av:
    if a.isdigit():
        want.add(int(a))
    else:
        want |= set(u for u, ts in by.items() if ts[0]["owner_class"] == a)
for u in sorted(want):
    ts = by.get(u, [])
    print("#%d %s d%s: %s" % (u, ts[0]["owner_class"] if ts else "?", ts[0].get("frame_diagram") if ts else "?",
                              " | ".join("%s%s w%s %s" % (t["term_name"], "*" if t["is_source"] else "", t["wire_uid"],
                                                        t.get("type") or t.get("term_type") or "") for t in ts)))
if not av:
    print(sorted(d["terminals"][0].keys()))
