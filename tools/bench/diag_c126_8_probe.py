r"""diag_c126_8_probe - card 126-8 STEP 1 (OFFLINE, read-only): which existing graph dump is closest to the ORIGINAL.
Prints, per graph dump, its scalar metadata (vi path, md5, date) and whether #30117/#4580/#3097/#3160/#11608/#2626 exist and
how #4580 Value's wire is wired. No LabVIEW, no COM.
PREDICTION: some dump (s1/bed 0923) names a copy of the original; #4580 exists in it.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c126_8_probe.log -- py -u tools/bench/diag_c126_8_probe.py"""
import glob, json, os, sys    # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P    # noqa: E402
n = 0
for f in sorted(glob.glob(os.path.join(B, "graph_*.json"))):
    try:
        G = json.load(open(f, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print("SKIP", os.path.basename(f), e)
        continue
    if not isinstance(G, dict) or "terminals" not in G:
        print("NOGRAPH", os.path.basename(f), list(G)[:8] if isinstance(G, dict) else type(G))
        continue
    n += 1
    meta = dict((k, G[k]) for k in G if isinstance(G[k], (str, int, float)))
    for k in ("meta", "vi", "source", "header"):
        if isinstance(G.get(k), dict):
            meta[k] = dict((a, b) for a, b in G[k].items() if isinstance(b, (str, int, float)))
    cls = dict((int(o["uid"]), o["class"]) for o in G.get("objs", []))
    have = dict((u, cls.get(u)) for u in (30117, 4580, 3097, 3160, 11608, 2626))
    v4580 = [(r["term_uid"], r["wire_uid"]) for r in G["terminals"] if r["owner_uid"] == 4580 and r["term_name"] == "Value"]
    sinks = []
    for _t, wu in v4580:
        if wu:
            sinks += [(r["owner_uid"], cls.get(r["owner_uid"]), r["term_name"]) for r in G["terminals"] if r["wire_uid"] == wu and not r["is_source"]]
    print("GRAPH", os.path.basename(f), "objs", len(cls), "terms", len(G["terminals"]), "meta", json.dumps(meta)[:400], flush=True)
    print("   have", have, "#4580 Value", v4580, "sinks", sinks[:6], flush=True)
print(P.result_line(P.make_result(n, 0, None)), flush=True)
