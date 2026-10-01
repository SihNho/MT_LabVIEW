"""diag_c127_2_probe - card 127-2 OFFLINE read of the P3a graph JSON: how FlatSequenceOuterTunnel / SelectorTunnel rows
are filed (term_class, frame_diagram, owner_uid) and what the fs_tunnel_pairs entries look like. No LabVIEW, no COM.
PREDICTION: FSOT rows exist (116); each FSOT uid owns rows on 2 diagrams; fs_tunnel_pairs lists entries keyed by uid."""
import collections, json, os, sys    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P   # noqa: E402
G = json.load(open(os.path.join(ROOT, "tools/bench/graph_ring_p3a_20261001_190155.json"), encoding="utf-8"))
T = G["terminals"]
fo = [r for r in T if r["owner_class"] == "FlatSequenceOuterTunnel"]
by = collections.defaultdict(list)
for r in fo:
    by[r["owner_uid"]].append(r)
print("FSOT uids", len(by), "rows", len(fo))
for u in list(by)[:3]:
    print("FSOT", u, [(r["term_uid"], r["term_class"], r["is_source"], r["frame_diagram"], r["wire_uid"], r["term_name"]) for r in by[u]])
    print("  owner", G["owners"].get(str(u)))
print("keys", list(G.keys()))
fp = G.get("fs_tunnel_pairs") or []
print("fs_tunnel_pairs n", len(fp), fp[:2])
st = [r for r in T if r["owner_class"] == "SelectorTunnel"][:3]
print("SelTun", [(r["owner_uid"], r["term_uid"], r["term_class"], r["is_source"], r["frame_diagram"]) for r in st])
lt = [r for r in T if r["owner_class"] == "LoopTunnel"][:2]
print("LoopTun", [(r["owner_uid"], r["term_uid"], r["term_class"], r["is_source"], r["frame_diagram"]) for r in lt])
for d in (27219, 639, 23169, 536, 12938, 681):
    print("owner of", d, G["owners"].get(str(d)))
print(P.result_line(P.make_result(1, 0, None)))
