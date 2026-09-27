"""diag_c114c_peek - card 114-2: OFFLINE structure peek (no LabVIEW): plan_l2b3 open rows/actions, graph_l2b2b nets 5174/5336/28392,
expected Error List shape. Read-only; prints only."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = json.load(open(os.path.join(R, "tools/bench/plan_l2b3.json"), encoding="utf-8"))
print(list(P.keys()))
print("OPEN", P["open_rows"])
print("ACTIONS", json.dumps(P["actions"])[:3000])
print("FIN", json.dumps(P["finalized"])[:1200])
G = json.load(open(os.path.join(R, "tools/bench/graph_l2b2b_20260928.json"), encoding="utf-8"))
print(list(G.keys()))
print(G["terminals"][0]); print(G["objs"][0]); print(type(G["loops"]), str(G["loops"])[:300])
for w in (5174, 5336, 28392):
    print("NET", w, [(r["owner_uid"], r["owner_class"], r["term_uid"], r["term_name"], r["is_source"]) for r in G["terminals"] if int(r["wire_uid"] or 0) == w])
for t in (28378, 2996, 3193):
    print("SINK", t, [(r["owner_uid"], r["owner_class"], r["term_uid"], r["term_name"], r["is_source"], r["wire_uid"]) for r in G["terminals"] if int(r["term_uid"]) == t])
E = json.load(open(os.path.join(R, "tools/bench/errorlist_expected_D1_l2_b2b_20260928_015450.json"), encoding="utf-8"))
print(list(E.keys())); print(json.dumps(E["expected"][:3])[:1500])
print("RESULT {}")
