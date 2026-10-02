"""diag_c138_6_q1 - card 138-6 offline read of the bed graph JSON (no LabVIEW): classes, ArrayConstants, #10465 rows."""
import json, collections, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE)))
import protocol as P
G = json.load(open(os.path.join(HERE, "graph_ring_p3b2b_20261002_133824.json"), encoding="utf-8"))
print(type(G).__name__, list(G.keys())[:30] if isinstance(G, dict) else len(G))
for k, v in (G.items() if isinstance(G, dict) else []):
    if isinstance(v, list) and v and isinstance(v[0], dict):
        print(k, len(v), list(v[0].keys())[:20])
terms = G.get("terminals") or []
c = collections.Counter(t.get("owner_class") for t in terms)
print(c.most_common(80))
for t in terms:
    if t.get("owner_class") in ("ArrayConstant",):
        print("AC", t)
for t in terms:
    if t.get("owner_uid") == 10465:
        print("10465", t)
for t in terms:
    if t.get("wire_uid") == 25415:
        print("w25415", t)
print(P.result_line(P.make_result(1, 0, None, [])))
