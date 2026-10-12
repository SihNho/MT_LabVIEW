# ---
# labview: none
# hardware: none
# ---
r"""diag_c170_a2_4_graph - card 170-a2-4: OFFLINE look into the stored P6 graph JSON (fbc7b7ee) to find the node that holds the ring's
slot count (counter mod 20, U13 / ring-p4b.md:21). Prints the obj schema, every Quotient & Remainder node and what feeds its 'y'
terminal (source terminal, owner class, and every obj field of that owner). Facts only; no gate beyond 'graph read'.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c170_a2_4_graph.log -- py -u tools/bench/diag_c170_a2_4_graph.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                         # noqa: E402

G = json.load(open(os.path.join(HERE, "graph_ring_p6_20261012_212645.json"), encoding="utf-8"))
print("FACT top keys", {k: (len(v) if hasattr(v, "__len__") else v) for k, v in G.items() if k != "vi"})
print("FACT obj sample", json.dumps(G["objs"][0])[:400])
print("FACT obj keys union", sorted(set(k for o in G["objs"] for k in o)))
print("FACT term keys union", sorted(set(k for t in G["terminals"] for t2 in [t] for k in t2)))
objs = dict((int(o["uid"]), o) for o in G["objs"])
by_owner = {}
for t in G["terminals"]:
    by_owner.setdefault(t["owner_uid"], []).append(t)
by_wire = {}
for t in G["terminals"]:
    if t.get("wire_uid") is not None:
        by_wire.setdefault(t["wire_uid"], []).append(t)
qr = sorted(u for u, ts in by_owner.items() if any(t["term_name"] == "x-y*floor(x/y)" for t in ts))
print("FACT Q&R owners", qr)
for u in qr:
    for t in by_owner[u]:
        if t["term_name"] in ("y", "x"):
            src = [s for s in by_wire.get(t.get("wire_uid"), []) if s["is_source"]]
            for s in src:
                print("FACT Q&R #%d %s <- term %s %r owner #%s %s obj %s" % (u, t["term_name"], s["term_uid"], s["term_name"], s["owner_uid"],
                      s["owner_class"], json.dumps(objs.get(int(s["owner_uid"])))[:400]))
vals = [o for o in G["objs"] if any(k for k in o if "val" in k.lower())]
print("FACT objs with a value-like field", len(vals), json.dumps(vals[:3])[:600])
print(P.result_line(P.make_result(1, 0, None, [])))
