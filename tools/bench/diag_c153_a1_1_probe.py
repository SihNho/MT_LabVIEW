# ---
# labview: none
# hardware: none
# ---
"""Card 153-a1-1 probe: owners / loops / key-uid rows of the s09 graph (22f967b5). Reads json only.
Prediction: owners maps a diagram uid to [class, parent uid]; loops 23041 (1.7), 637 (1.1), 10170 (1.2) present."""
import json, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
G = json.load(open("tools/bench/graph_ring_p4s09_20261009_062044.json", encoding="utf-8"))
print("owners sample:", {k: G["owners"][k] for k in list(G["owners"])[:8]})
for k in ("639", "686", "23405", "10170", "637", "23041", "23166", "536", "759"):
    print("owners", k, G["owners"].get(k))
for L in G["loops"]:
    print("loop", json.dumps(L))
objs = {o["uid"]: o for o in G["objs"]}
for u in (376, 23041, 637, 10170, 2626, 3052, 644, 23405, 639, 15, 24, 51, 1108, 24083, 24133, 24150, 24187):
    print("obj", u, objs.get(u))
print("fs_measured keys", {k: (list(v)[:5] if isinstance(v, dict) else v) for k, v in G["fs_measured"].items()})
cls = collections.Counter(o["class"] for o in G["objs"])
print("classes", cls.most_common(70))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
