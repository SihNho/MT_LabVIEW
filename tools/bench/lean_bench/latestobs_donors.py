"""latestobs_donors - offline, read-only (lean task latest retry): list candidate donor nodes in the stored P6 bed graph by the
terminal-name sets of the primitives the observer needs (Tick Count, Array Max & Min, Equal?, Boolean To (0,1), Add Array
Elements, Build Array, Write Delimited Spreadsheet / Write To Spreadsheet File, numeric / path / boolean constants).
    py tools/bench/lean_bench/latestobs_donors.py [graph json] [substring ...]"""
import json, os, sys                                                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
av = sys.argv[1:]
G = av[0] if av and av[0].endswith(".json") else os.path.join(os.path.dirname(HERE), "graph_ring_p6_20261012_212645.json")
pats = [a for a in av if not a.endswith(".json")]
d = json.load(open(G, encoding="utf-8"))
print("keys", sorted(d.keys()))
by = {}
for t in d["terminals"]:
    by.setdefault(int(t["owner_uid"]), []).append(t)
seen = {}
for u, ts in sorted(by.items()):
    key = (ts[0]["owner_class"], tuple(sorted(set((t["term_name"], bool(t["is_source"])) for t in ts))))
    seen.setdefault(key, []).append((u, ts[0].get("frame_diagram"), sum(1 for t in ts if t["wire_uid"])))
for (cls, names), us in sorted(seen.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))):
    s = "%s %s" % (cls, " | ".join("%s%s" % (n, "*" if src else "") for n, src in names))
    if pats and not any(p.lower() in s.lower() for p in pats):
        continue
    print("%-4d %s  e.g. %s" % (len(us), s[:260], us[:4]))
