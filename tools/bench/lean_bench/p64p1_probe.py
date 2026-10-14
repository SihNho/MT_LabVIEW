r"""p64p1_probe - OFFLINE read of the stored bed graph (no LabVIEW): candidate donor nodes for the GetBuffFirst wrapper.
    py tools/bench/lean_bench/p64p1_probe.py              -> Build Array owners (input names) + any 'first call?' / '(0,1)' terminal
    py tools/bench/lean_bench/p64p1_probe.py <substr> ... -> every terminal row whose json contains a substring"""
import json, os, sys                                                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(os.path.dirname(HERE), "graph_ring_p6_20261012_212645.json")
d = json.load(open(G, encoding="utf-8"))
subs = [a.lower() for a in sys.argv[1:]]
if subs == ["--classes"]:
    import collections
    c = collections.Counter((r["owner_class"], r["term_class"], r["term_name"] if "Loop" in r["owner_class"] or "Term" in r["owner_class"] else "")
                            for r in d["terminals"])
    for k, v in sorted(c.items()):
        print(v, k)
    sys.exit(0)
if subs:
    for r in d["terminals"]:
        s = json.dumps(r).lower()
        if any(x in s for x in subs):
            print(json.dumps(r)[:300])
    sys.exit(0)
by = {}
for r in d["terminals"]:
    by.setdefault(int(r["owner_uid"]), []).append(r)
for u, rs in sorted(by.items()):
    names = sorted((r["term_name"], bool(r["is_source"])) for r in rs)
    ins = [n for n, src in names if not src]
    outs = [n for n, src in names if src]
    if any(o.startswith("appended") for o in outs) or any(n.lower() in ("first call?",) or "(0,1)" in n for n, _s in names):
        print(u, rs[0]["owner_class"], "diag", rs[0]["frame_diagram"], "IN", ins, "OUT", outs,
              "wired_in", sum(1 for r in rs if not r["is_source"] and r["wire_uid"]))
