"""diag_c113e_offline - card 113-3 M0 helper: print the graph-dump rows of #11261 / #11608 / #11363 in the B2a bed and S1 (no LabVIEW)."""
import json
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in ("tools/bench/graph_l2b2a_20260928.json", "docs/wiki/subvi/D1_s1_copy.json"):
    G = json.load(open(os.path.join(R, f), encoding="utf-8"))
    print("==", f, sorted(G.keys())[:25])
    for r in G.get("terminals") or []:
        if int(r.get("owner_uid") or 0) in (11261, 11608, 11363) or int(r.get("term_uid") or 0) in (11270, 11273, 11369):
            print(json.dumps(r, default=str)[:400])
    for o in G.get("objects") or G.get("objs") or []:
        if int(o.get("uid") or 0) in (11261, 11608, 11363):
            print("OBJ", json.dumps(o, default=str)[:400])
