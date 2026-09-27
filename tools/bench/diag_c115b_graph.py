"""diag_c115b_graph - card 115-2 R1: read-only look at graph_l2b3_20260928.json (keys, loop #637 register table, the 12 SR
uids' objs/rows) and the B3 plan's open_rows. No LabVIEW."""
import json, os
B = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(B, "graph_l2b3_20260928.json"), encoding="utf-8"))
print("keys", sorted(G.keys()), "vi", G.get("vi"), "md5", G.get("md5"))
SR = [9018, 9025, 29505, 29512, 1147, 1142, 5796, 5805, 119, 2972, 7311, 11001]
for L in G.get("loops") or []:
    if int(L.get("loop_uid", 0)) == 637:
        print("LOOP637", json.dumps(L)[:1500])
print("objs n", len(G.get("objs") or []), [o for o in G.get("objs") or [] if int(o["uid"]) in SR])
rows = [r for r in G["terminals"] if int(r["owner_uid"]) in SR]
print("rows", len(rows))
for r in rows:
    print("  ", r)
print("owners?", type(G.get("owners")), len(G.get("owners") or {}))
for k in ("fs_tunnel_pairs", "graph_summary"):
    print(k, type(G.get(k)), len(G.get(k) or []))
P = json.load(open(os.path.join(B, "plan_l2b3.json"), encoding="utf-8"))
print("context", P.get("context"), "open_rows n", len(P["open_rows"]))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
