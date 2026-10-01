r"""diag_c126_5_facts2 - card 126-5, OFFLINE read-only (no LabVIEW, no COM): measured terminal tables for P3b's created nodes.
(1) IMAQ Copy rows in tools/bench/graph_harness_copyloop_c95.json (a LabVIEW-read graph holding an IMAQ Copy SubVI);
(2) 1-D IndexArray candidates and Local objects in the P3a graph (graph_ring_p3a_20261001_190155.json) with their rows;
(3) the For #23093 neighbourhood (tunnels on body 23169). Prints FACT lines; writes nothing. Ends with a RESULT line."""
import collections, json, os, sys
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
import protocol as P  # noqa: E402
H = json.load(open(os.path.join(B, "graph_harness_copyloop_c95.json"), encoding="utf-8"))
HT = H["terminals"] if isinstance(H, dict) else H
cp = sorted(set(r["owner_uid"] for r in HT if r["term_name"] in ("Image Src", "Image Dst")))
for u in cp:
    print("IMAQCOPY harness #{0}".format(u), [(r["term_uid"], r["term_name"], r["term_class"], int(bool(r["is_source"])), r["wire_uid"], r["owner_class"])
                                            for r in HT if r["owner_uid"] == u])
G = json.load(open(os.path.join(B, "graph_ring_p3a_20261001_190155.json"), encoding="utf-8"))
T, objs = G["terminals"], G["objs"]
cls_of = dict((int(o["uid"]), o.get("class")) for o in objs)
byo = collections.defaultdict(list)
for r in T:
    byo[r["owner_uid"]].append(r)
ia = [u for u, c in cls_of.items() if c == "IndexArray"]
sig = collections.Counter()
for u in ia:
    rs = byo[u]
    key = tuple(sorted((r["term_name"], int(bool(r["is_source"])), r["term_class"]) for r in rs))
    sig[key] += 1
for k, n in sig.most_common():
    ex = [u for u in ia if tuple(sorted((r["term_name"], int(bool(r["is_source"])), r["term_class"]) for r in byo[u])) == k][:4]
    print("INDEXARRAY sig x{0} e.g. {1}: {2}".format(n, ex, k))
for u in ia:
    rs = byo[u]
    if len(rs) == 3:
        print("  IA3 #{0} on {1}: {2}".format(u, rs[0]["frame_diagram"], [(r["term_uid"], r["term_name"], int(bool(r["is_source"])), r["wire_uid"]) for r in rs]))
for u, c in cls_of.items():
    if c == "Local":
        print("LOCAL #{0}".format(u), [(r["term_name"], int(bool(r["is_source"])), r["term_class"], r["frame_diagram"]) for r in byo[u]])
print("FOR 23093 body rows", sorted(set((r["owner_uid"], r["owner_class"]) for r in T if r["frame_diagram"] == 23169)))
for r in T:
    if r["frame_diagram"] == 13236 and r["owner_class"] in ("LoopTunnel", "Tunnel"):
        print("  FS2f13236 tunnel row", r["owner_uid"], r["owner_class"], r["term_class"], int(bool(r["is_source"])), r["wire_uid"])
for u in (23148, 26131):
    print("FORTUN #{0} {1}".format(u, cls_of.get(u)), [(r["term_uid"], r["term_name"], r["term_class"], int(bool(r["is_source"])), r["wire_uid"], r["frame_diagram"]) for r in byo[u]])
print("OWNER 13236", G["owners"].get("13236"), "OWNER 23093", [o for o in objs if int(o["uid"]) == 23093])
ok = bool(cp) and bool(ia)
print(P.result_line(P.make_result(int(ok), int(not ok), None if ok else "no IMAQ Copy / IndexArray rows")))
