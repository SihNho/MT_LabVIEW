"""diag_c127_2_chain - card 127-2 OFFLINE: why stagesim's diagram chain from For body #23169 does not reach the FS frame's
chain (maker run plan_ring_p3b_make_c127_2.log: 'no common diagram of #23169 and #-3'). Reads the P3a graph's owners map
and stagesim's graph tree parent for the diagrams on 126-6 B3's measured route (diag_c126_6_cross.log:77-78).
PREDICTION: owners has structure->diagram rows for some structures; the tree parent misses at least one link on the B3 route."""
import collections, json, os, sys    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS   # noqa: E402,E401
G = json.load(open(os.path.join(ROOT, "tools/bench/graph_ring_p3a_20261001_190155.json"), encoding="utf-8"))
st = SS.base_state(G)
par = SS.graph(st)["tree"]["parent"]
own = st["owners"]
for d in (23169, 27219, 639):
    print("tree chain", d, SS._diag_chain(st, d, dict((int(k), int(v)) for k, v in par.items() if v is not None)))
for u in ("23093", "12938", "681", "637", "22694", "23169", "639"):
    print("owners", u, own.get(u), "tree", par.get(int(u)))
fr = [(k, v) for k, v in own.items() if v[0] in ("FlatSequence", "Sequence") and int(v[1]) in (12938, 681)]
print("frames of FS 12938/681", fr)
for k, _v in fr:
    print("  frame", k, "tree parent", par.get(int(k)))
for d in (13236, 686, 536):
    print("RUN2 owners", d, own.get(str(d)), "fsot_parent", SS._fsot_parent(st, d),
          "fsot partners", sorted(set(int(r["frame_diagram"] or 0) for r in st["terminals"] if r["owner_class"] == "FlatSequenceOuterTunnel"
                                      and r["owner_uid"] in set(x["owner_uid"] for x in st["terminals"] if x["owner_class"] == "FlatSequenceOuterTunnel" and int(x["frame_diagram"] or 0) == d))))
    o = own.get(str(d))
    print("RUN2   struct owner", o and own.get(str(o[1])))
for d in (13236, 686, 26117, 3628):
    fu = set(x["owner_uid"] for x in st["terminals"] if x["owner_class"] == "FlatSequenceInnerTunnel" and int(x["frame_diagram"] or 0) == d)
    dsets = collections.Counter(tuple(sorted(set(int(r["frame_diagram"] or 0) for r in st["terminals"] if r["owner_uid"] == u))) for u in fu)
    print("RUN3 FSIT on", d, "n", len(fu), "diagram sets", dsets.most_common(6))
    print("RUN3   pairs", [(p["term_a"], p["term_b"]) for p in (G.get("fs_tunnel_pairs") or []) if p["uid"] in fu][:3])
print("RUN3 objs 12938/681/13236/686/536", [o for o in G["objs"] if int(o["uid"]) in (12938, 681, 13236, 686, 536)])
print("owners rows with class Diagram:", sum(1 for v in own.values() if v[0] == "Diagram"), "of", len(own))
print(P.result_line(P.make_result(1, 0, None)))
