"""diag_c112a_regs - card 112-1: read-only facts from the L2-B1 bed graph for the B2a rows (no LabVIEW).
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c112a_regs.log -- py -u tools/bench/diag_c112a_regs.py"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "graph_l2b1_20260927.json"), encoding="utf-8"))
T = G["terminals"]
print("keys", sorted(G.keys()))
for L in G.get("loops") or []:
    if int(L.get("loop_uid") or 0) in (10170, 637, 1359, 29874):
        print("LOOP", json.dumps(L)[:600])
own = G.get("owners") or {}
print("owners n", len(own), "sample", list(own.items())[:3])
for k, v in own.items():
    if int(v[1] or 0) in (10170, 1359, 29874, 2222):
        print("OWNER frame", k, "->", v)
for o in G.get("objs") or []:
    if o.get("class") in ("TopLevelDiagram",) or int(o.get("uid") or 0) in (10170, 1359, 29874, 2222, 2276, 8953, 28124, 403):
        print("OBJ", json.dumps(o)[:300])
WANT = (9603, 10544, 25545, 25582, 8953, 28124, 9227, 29616, 9087, 29911, 403, 2276)
for r in T:
    if r["owner_uid"] in WANT and (r["owner_uid"] not in (8953, 28124) or r["is_source"]):
        print("ROW", json.dumps(r))
for r in T:
    if r["owner_uid"] in (1359, 29874, 2222) and r.get("term_class") in ("", "Terminal", None):
        print("NODE-ROW", r["owner_uid"], r["frame_diagram"], r["owner_class"])
        break
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
