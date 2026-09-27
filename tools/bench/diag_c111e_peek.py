"""diag_c111e_peek - card 111-5, OFFLINE read of graph_l2b1_20260927.json (B1 bed graph) for the B2 endpoint uids. No LabVIEW.
PREDICTION: the graph loads; every uid named in facts_c111b_l2b_rows.json B2-09..16 has >= 1 terminal row."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import hashlib  # noqa: E402
GP = os.path.join(ROOT, "tools/bench/graph_l2b1_20260927.json")
print("GRAPH MD5", hashlib.md5(open(GP, "rb").read()).hexdigest(), "(card input 8327f974cf150146b93b19f10e54afd5)")
G = json.load(open(GP, encoding="utf-8"))
print("KEYS", list(G.keys()))
for k, v in G.items():
    print("  ", k, (type(v).__name__, len(v)) if isinstance(v, (list, dict)) else repr(v)[:200])
T = G["terminals"]; O = dict((int(o["uid"]), o) for o in G["objs"])
print("ROW0", T[0]); print("OBJ0", G["objs"][0])
uids = [int(a) for a in (sys.argv[1:] or "8953 9227 10544 9603 9087 28124 29616 25582 25545 29911 403 2276 9306 6132 9018 9025 29505 29512".split())]
miss = 0
for u in uids:
    rows = [r for r in T if int(r["owner_uid"]) == u or int(r["term_uid"]) == u]
    miss += not rows
    print("==", u, O.get(u, {}).get("class"), {k: O.get(u, {}).get(k) for k in ("owner", "diagram", "label") if k in O.get(u, {})})
    for r in rows:
        print("    ", dict((k, r[k]) for k in r if k != "owner_uid"))
    ws = set(int(r["wire_uid"]) for r in rows if r["wire_uid"])
    for w in sorted(ws):
        print("      wire", w, "->", [(r["owner_uid"], r["owner_class"], r["term_name"], r["is_source"]) for r in T if r["wire_uid"] and int(r["wire_uid"]) == w])
print(protocol.result_line(dict(status="PASS" if not miss else "FAIL", gates={"pass": len(uids) - miss, "fail": miss}, first_fail=None if not miss else "uid without rows", artefacts=[])))
