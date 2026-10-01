r"""diag_c126_7_facts2 - card 126-7 (OFFLINE, read-only): follow-up to diag_c126_7_facts.log.
(e) full forward BFS (no depth cap, through tunnels: a tunnel's other-side source rows are owned by the same uid) from #30117 Value
    w30592, #4580 Value w4878, #3097 w3359, #3160 w3324 until #11608 / #2626 (record build) or exhaustion; prints the path found.
    Also every raw row on w4878 (the first diag found NO sink for it).
(f) both ends of #6810's error in (w1961) and error out (w653).
PREDICTION: #30117 and #4580 reach #11608 or #2626; #3097/#3160 end at globals 'Trans position'/'Rot position' only.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c126_7_facts2.log -- py -u tools/bench/diag_c126_7_facts2.py"""
import collections, json, os, sys    # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, vigraph as V    # noqa: E402,E401
G = json.load(open(os.path.join(B, "graph_ring_p3a_20261001_190155.json"), encoding="utf-8"))
RAW = G["terminals"]
T = V.dedupe_rows(RAW)[0]
cls = dict((int(o["uid"]), o["class"]) for o in G["objs"])
own = G["owners"]
byo, byw = collections.defaultdict(list), collections.defaultdict(list)
for r in T:
    byo[r["owner_uid"]].append(r)
    if r["wire_uid"]:
        byw[r["wire_uid"]].append(r)
TARGET = {11608, 2626}
n_ok = 0
for u in (30117, 4580, 3097, 3160):
    prev, q, hit = {u: None}, collections.deque([u]), None
    while q and hit is None:
        n = q.popleft()
        for r in byo.get(n, []):
            if not (r["is_source"] and r["wire_uid"]):
                continue
            for k in byw[r["wire_uid"]]:
                v = k["owner_uid"]
                if not k["is_source"] and v not in prev:
                    prev[v] = (n, r["wire_uid"], k["term_name"])
                    if v in TARGET:
                        hit = v
                        break
                    q.append(v)
            if hit is not None:
                break
    path = []
    v = hit
    while v is not None and prev.get(v):
        p = prev[v]
        path.append("#{0}({1})<-w{2}.{3!r}".format(v, cls.get(v), p[1], p[2]))
        v = p[0]
    n_ok += hit is not None
    print("TRACE #{0} {1}: reached {2} nodes; hit {3}; path(from target back) {4}".format(u, cls.get(u), len(prev) - 1, hit, path[:25]), flush=True)
    if hit is None:
        print("   reached (first 40):", [(v, cls.get(v)) for v in list(prev)[1:41]], flush=True)
print("RAW rows on w4878:", [r for r in RAW if r["wire_uid"] == 4878], flush=True)
print("RAW rows on w30592:", [(r["owner_uid"], r["owner_class"], r["term_name"], r["is_source"]) for r in RAW if r["wire_uid"] == 30592], flush=True)
for w in (1961, 653):
    print("#6810 error wire w{0}: {1}".format(w, [(r["owner_uid"], cls.get(r["owner_uid"]), r["term_name"], r["is_source"], r["frame_diagram"]) for r in byw[w]]), flush=True)
print("owners 6810/30117/4580/3097/3160:", dict((u, own.get(str(u))) for u in (6810, 30117, 4580, 3097, 3160, 759)), flush=True)
print(P.result_line(P.make_result(n_ok, 4 - n_ok, None if n_ok == 4 else "not every source reaches the record build")), flush=True)
