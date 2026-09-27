"""diag_c112b_insp - card 112-2: READ-ONLY look at the B2a ends in the saved-B1 base graph (no LabVIEW, nothing written).
Which rows own the 7 B2a ends, which structure owns each tunnel (owners map), which loop each register sits on, and the
parent diagram of loop #10170 / #1359 / #29874 / case #2222 - the facts the (v) owner route and the uid addressing need.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c112b_insp.log -- py -u tools/bench/diag_c112b_insp.py"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "graph_l2b1_20260927.json"), encoding="utf-8"))
print(sorted(G.keys()))
for k, v in G.items():
    print(k, type(v).__name__, len(v) if isinstance(v, (list, dict)) else repr(v)[:160])
T = G["terminals"]
print("row keys", sorted(T[0].keys()))
objs = dict((int(o["uid"]), o) for o in G.get("objs") or [])
own = G.get("owners") or {}


def rows_of(u):
    return [r for r in T if int(r["owner_uid"]) == u]


for u in (9087, 9227, 29616, 29911, 2276, 9603, 10544, 25545, 25582, 8953, 28124, 403):
    o = objs.get(u, {})
    print("--- owner", u, o.get("class"), repr(o.get("owner"))[:60])
    for r in rows_of(u):
        print("   ", r["term_uid"], repr(r["term_name"]), "src" if r["is_source"] else "snk", "w", r["wire_uid"],
              r.get("term_class"), "fd", r["frame_diagram"], "own_map", own.get(str(int(r["frame_diagram"] or 0))))
print("loops:")
for L in G.get("loops") or []:
    if int(L["loop_uid"]) in (10170, 1359, 29874):
        print("  ", json.dumps(L)[:700])
print("owners map entries for the structures:")
for k, v in own.items():
    if int(v[1] or 0) in (10170, 1359, 29874, 2222):
        print("  diag", k, "->", v)
for u in (10170, 1359, 29874, 2222):
    print("obj", u, objs.get(u))
    print("   rows with owner_uid == it:", [(r["term_uid"], r["term_name"], r["is_source"], r["wire_uid"], r["frame_diagram"])
                                          for r in rows_of(u)][:12])
tl = [o for o in objs.values() if o["class"] == "TopLevelDiagram"]
print("TopLevelDiagram objs:", tl[:3])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
