"""card 80-6 scratch census (no LabVIEW): every 'Tunnel'-class node on D1_k and on S1 - rows, inner wiring; plus the
single-terminal wires owned by the joint closure."""
import collections, json, os, sys                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE); sys.path.insert(0, os.path.dirname(B))  # noqa: E702
import vigraph as V                                                                  # noqa: E402
gr = json.load(open(os.path.join(B, "l2a1_graph_k_80.json"), encoding="utf-8"))
T = V.dedupe_rows(gr["terminals"])[0]
F = json.load(open(os.path.join(B, "l2a1_facts_80.json"), encoding="utf-8"))
O = F["owners"]
by = collections.defaultdict(list)
byw = collections.Counter(r["wire_uid"] for r in T if r["wire_uid"])
for r in T:
    by[r["owner_uid"]].append(r)
tun = sorted(u for u, rs in by.items() if rs[0]["owner_class"] == "Tunnel")
print("Tunnel-class nodes on D1_k:", len(tun))
for u in tun:
    rs = by[u]
    print(" #{0} owner-map {1}: ".format(u, O.get(str(u))) + "; ".join("{0}{1} {2} w{3}(n{4}) F{5}".format(
        r["term_class"][:5], "S" if r["is_source"] else "K", repr(r["term_name"]), r["wire_uid"], byw.get(r["wire_uid"], 0),
        r["frame_diagram"]) for r in rs))
R = json.load(open(os.path.join(HERE, "l2a1_real_80.json"), encoding="utf-8"))
clo = set(R["runs"]["joint"]["closure_nodes"])
print("single-terminal wires on closure nodes:")
for r in T:
    if r["wire_uid"] and byw[r["wire_uid"]] == 1 and V.node_of(r) in clo:
        print("  w{0} t{1} #{2} {3} {4} {5}".format(r["wire_uid"], r["term_uid"], V.node_of(r), r["owner_class"], r["term_class"],
                                                   "src" if r["is_source"] else "snk"))
print("all single-terminal wires on D1_k:", sum(1 for w, n in byw.items() if n == 1))
