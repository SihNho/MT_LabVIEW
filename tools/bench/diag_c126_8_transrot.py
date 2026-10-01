r"""diag_c126_8_transrot - card 126-8 STEP 1 (OFFLINE, read-only, no LabVIEW/COM): PD256(e) on EXISTING graph dumps.
WHAT EXISTED FIRST: diag_c126_7_facts2.py (BFS on the P3a bed); diag_c126_8_probe.log (#4580 Value w4878 -> #2626 BuildArray
'element' in s3_loop15/k_s4/disp/l2a1/l2a2/l2a3, NO sink from l2b1 on). This script reads:
 (1) graph_s1/bed_20260923/24 (edge-form dumps; s1 = the copy nearest the original): vi path, md5, every edge touching
     #30117/#4580/#2626/#11608/#3097/#3160;
 (2) on graph_s3_loop15 and graph_l2a3_bed (terminal form): #2626's input rows (owner+term of each source), #2626's output sinks,
     #11608's inputs, and the #30117/#4580 Value sinks;
 (3) l2a3 -> l2b1 delta on #2626 (which input rows vanished; which nodes are new around it).
PREDICTION: s1 has #4580 Value -> #2626 element and #30117 Value -> #2626 (or #11608); l2b1 is the first bed where w4878 is sinkless.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c126_8_transrot.log -- py -u tools/bench/diag_c126_8_transrot.py"""
import collections, json, os, sys    # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, vigraph as V    # noqa: E402,E401
U = (30117, 4580, 2626, 11608, 3097, 3160)
facts = {}
for f in ("graph_s1_20260923.json", "graph_s1_20260924.json", "graph_bed_20260923.json", "graph_bed_20260924.json"):
    G = json.load(open(os.path.join(B, f), encoding="utf-8"))
    E = G["edges"]
    print("EDGEFORM", f, "vi", G.get("vi"), "md5", G.get("md5"), "method", str(G.get("method"))[:160], "n_edges", len(E), flush=True)
    print("   note", str(G.get("note"))[:300], flush=True)
    print("   edge sample", json.dumps(E[0])[:300] if E else None, flush=True)
    hit = []
    for e in E:
        s = json.dumps(e)
        if any(('"{0}"'.format(u) in s) or (": {0}".format(u) in s) or ("[{0}".format(u) in s) or (" {0}," in s and False) for u in U):
            hit.append(e)
    cls = G.get("cls") or {}
    print("   cls", dict((u, cls.get(str(u)) if isinstance(cls, dict) else None) for u in U), flush=True)
    for e in hit[:40]:
        print("   EDGE", json.dumps(e)[:300], flush=True)
    facts[f] = {"vi": G.get("vi"), "md5": G.get("md5"), "edges": hit[:40]}


def term_view(f):
    G = json.load(open(os.path.join(B, f), encoding="utf-8"))
    T = V.dedupe_rows(G["terminals"])[0]
    cls = dict((int(o["uid"]), o["class"]) for o in G["objs"])
    byw = collections.defaultdict(list)
    for r in T:
        if r["wire_uid"]:
            byw[r["wire_uid"]].append(r)
    return G, T, cls, byw


def ends(T, byw, cls, u, src):
    out = []
    for r in T:
        if r["owner_uid"] != u or bool(r["is_source"]) != src:
            continue
        other = [(k["owner_uid"], cls.get(k["owner_uid"]), k["term_name"]) for k in byw.get(r["wire_uid"], [])
                 if bool(k["is_source"]) != src] if r["wire_uid"] else []
        out.append((r["term_uid"], r["term_name"], r["wire_uid"], other))
    return out


for f in ("graph_s3_loop15_20260924.json", "graph_l2a3_bed_20260927.json", "graph_l2b1_20260927.json", "graph_ring_p3a_20261001_190155.json"):
    G, T, cls, byw = term_view(f)
    print("TERMFORM", f, "vi", G.get("vi"), flush=True)
    for u in (30117, 4580, 3097, 3160):
        print("   #{0} {1} OUT".format(u, cls.get(u)), ends(T, byw, cls, u, True), flush=True)
    print("   #2626 BuildArray IN ", ends(T, byw, cls, 2626, False), flush=True)
    print("   #2626 BuildArray OUT", ends(T, byw, cls, 2626, True), flush=True)
    print("   #11608 Bundler IN ", ends(T, byw, cls, 11608, False), flush=True)
    print("   #11608 Bundler OUT", ends(T, byw, cls, 11608, True), flush=True)
    facts[f] = {"2626_in": ends(T, byw, cls, 2626, False), "4580_out": ends(T, byw, cls, 4580, True), "30117_out": ends(T, byw, cls, 30117, True)}
a, b = facts["graph_l2a3_bed_20260927.json"]["2626_in"], facts["graph_l2b1_20260927.json"]["2626_in"]
print("DELTA #2626 IN l2a3 -> l2b1: gone", [x for x in a if x not in b], "new", [x for x in b if x not in a], flush=True)
json.dump(facts, open(os.path.join(B, "diag_c126_8_transrot_out.json"), "w", encoding="utf-8"), indent=1, default=str)
print(P.result_line(P.make_result(1, 0, None)), flush=True)
