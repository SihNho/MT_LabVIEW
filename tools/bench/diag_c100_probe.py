r"""diag_c100_probe - card 100-1, OFFLINE (no LabVIEW): read the S1 graph files for every uid the display-loop rows
(tools/bench/cards/rows_spec_100.md R1-R8) bind, so the rows are taken from a named file, never re-typed from memory.

WHAT EXISTED FIRST: tools/bench/par1359_95_graph.json (S1 terminal table, md5 of D1_s1_copy 3e3d23ce, used by 99-1/99-2
facts), tools/bench/graph_s1_20260924.json (S1 vigraph, cls map), tools/bench/sim/l2a1/graph_k_80_owners.json (the
stageplan base format). Nothing is built; this only prints.

PREDICTION CONTRACT: every uid in UIDS appears as an owner_uid or term_uid in par1359_95_graph.json (gate per uid);
the graph's `md5` field == 3e3d23cefd3a334001aa9d6156bf1aee.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol  # noqa: E402

P = os.path.join(HERE, "par1359_95_graph.json")
G2 = os.path.join(HERE, "graph_s1_20260924.json")
K = os.path.join(HERE, "sim", "l2a1", "graph_k_80_owners.json")
UIDS = [637, 639, 686, 25380, 25392, 8603, 4866, 25261, 25116, 1359, 7911, 8741, 8764, 8775, 8795, 27716, 28180,
        28233, 29009, 11310, 31051, 31137, 11363, 11261, 9227, 9018, 9025, 9087, 8634, 11608, 11576, 8323, 8476,
        24444, 30896, 11639, 642, 1114]
WIRES = [9215, 9097, 8811, 10908, 12256, 11352, 7931, 31059, 31166, 3457, 1737, 24106, 9407, 1731]

npass = nfail = 0


def gate(label, ok, detail=""):
    global npass, nfail
    npass, nfail = npass + bool(ok), nfail + (not ok)
    print("GATE {0} {1} {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


d = json.load(open(P, encoding="utf-8"))
print("KEYS par1359_95_graph:", list(d.keys()))
gate("G0 md5", d.get("md5") == "3e3d23cefd3a334001aa9d6156bf1aee", d.get("md5"))
T = d["terminals"]
print("N terminals", len(T), "row keys", sorted(T[0].keys()))
for k, v in d.items():
    if k != "terminals":
        s = json.dumps(v)
        print("KEY", k, type(v).__name__, len(v) if hasattr(v, "__len__") else "", s[:300])
own = {}
for r in T:
    own.setdefault(r["owner_uid"], []).append(r)
byterm = {r["term_uid"]: r for r in T}
bywire = {}
for r in T:
    if r.get("wire_uid"):
        bywire.setdefault(r["wire_uid"], []).append(r)
for u in UIDS:
    rows = own.get(u, [])
    ok = bool(rows) or u in byterm
    gate("U{0}".format(u), ok, "as owner {0} rows; as term {1}".format(len(rows), u in byterm))
    if u in byterm:
        print("   TERMROW", json.dumps(byterm[u]))
    for r in rows:
        print("   #{0} {1} t{2} {3!r} src={4} w{5} fd{6} {7}".format(u, r["owner_class"], r["term_uid"], r["term_name"],
                                                               r["is_source"], r["wire_uid"], r.get("frame_diagram"),
                                                               r.get("term_class")))
for w in WIRES:
    rows = bywire.get(w, [])
    print("WIRE w{0}: {1}".format(w, [(r["owner_uid"], r["owner_class"], r["term_uid"], r["term_name"], r["is_source"],
                                       r.get("frame_diagram")) for r in rows]))
g2 = json.load(open(G2, encoding="utf-8"))
print("KEYS graph_s1_20260924:", list(g2.keys()))
cls = g2.get("cls", {})
for u in UIDS:
    print("CLS", u, cls.get(str(u)))
for k in g2:
    if k not in ("cls", "method"):
        v = g2[k]
        print("G2KEY", k, type(v).__name__, (len(v) if hasattr(v, "__len__") else ""), json.dumps(v)[:400])
gk = json.load(open(K, encoding="utf-8"))
print("KEYS graph_k_80_owners:", list(gk.keys()) if isinstance(gk, dict) else type(gk))
for k in (gk if isinstance(gk, dict) else {}):
    v = gk[k]
    print("GKKEY", k, type(v).__name__, (len(v) if hasattr(v, "__len__") else ""), json.dumps(v)[:400])
print(protocol.result_line(protocol.make_result(npass, nfail)), flush=True)
