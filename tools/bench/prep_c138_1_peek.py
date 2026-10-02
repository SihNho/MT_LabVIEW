"""prep_c138_1_peek - card 138-1 read-only helper: print plan v7 actions lo..hi and graph rows of given owner uids."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = json.load(open(os.path.join(ROOT, "tools", "bench", "plan_ring_p4_v7.json")))
A = p.get("actions") or p.get("rows")
mode = sys.argv[1]
if mode == "plan":
    print(sorted(p.keys()))
    lo, hi = int(sys.argv[2]), int(sys.argv[3])
    for i, a in enumerate(A, 1):
        if lo <= i <= hi:
            print(i, json.dumps(a)[:600])
elif mode == "summary":
    S = json.load(open(os.path.join(ROOT, "tools", "bench", "sim", "c138_1_v7", "ring_p4_v3", "summary.json")))
    print("final", S["final"], "failed", S["failed"], "undecided", S["undecided"], "n_candidates", S["n_candidates"])
    print("end_cdiff_rows", len(S["end_cdiff_rows"] or []), "open_rows", len(S["open_rows"]), "open_rows_match", S["open_rows_match"])
    print("first_divergent", json.dumps(S["first_divergent"])[:300])
    print("classed ok", (S["open_rows_classed"] or {}).get("ok"), json.dumps(S["open_rows_classed"])[:900])
    st = S["steps"]
    print("steps", len(st), "last", st[-1].get("n"), st[-1].get("id"), "errors", [s.get("n") for s in st if s.get("error")])
    print("cdiff per step (n: rows)", [(s.get("n"), len(s.get("cdiff_rows") or [])) for s in st if s.get("n") in (1, 157, 158, 159, 165, 171, 172)])
    print("end rows not in open rows", sorted(set(S["end_cdiff_rows"] or []) - set("|".join(map(str, x)) for x in S["open_rows"]))[:30])
elif mode == "name":
    g = json.load(open(os.path.join(ROOT, "tools", "bench", "graph_ring_p3b2b_20261002_133824.json")))
    pat = sys.argv[2]

    def walk(x, path):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, path + [k])
        elif isinstance(x, list):
            for i, v in enumerate(x):
                if isinstance(v, (dict, list)) or (isinstance(v, str) and pat in v):
                    if isinstance(v, str):
                        print(path + [i], json.dumps(x)[:400])
                    else:
                        walk(v, path + [i])
        elif isinstance(x, str) and pat in x:
            print(path, x[:200])
    walk(g, [])
    for r in g["terminals"]:
        if pat in str(r.get("term_name")):
            print("ROW", json.dumps(r))
    for a in p["actions"]:
        if "LRN5" in json.dumps(a):
            print("PLAN", json.dumps(a)[:500])
elif mode == "graph":
    g = json.load(open(os.path.join(ROOT, "tools", "bench", "graph_ring_p3b2b_20261002_133824.json")))
    print(sorted(g.keys()))
    want = set(int(x) for x in sys.argv[2:])
    for r in g["terminals"]:
        if int(r["owner_uid"]) in want or int(r.get("term_uid") or 0) in want or int(r.get("wire_uid") or 0) in want:
            print(json.dumps(r))
    for o in g.get("objs") or []:
        if int(o["uid"]) in want:
            print("OBJ", json.dumps(o))
    own = g.get("owners") or {}
    for u in want:
        if str(u) in own:
            print("OWNER", u, own[str(u)])
