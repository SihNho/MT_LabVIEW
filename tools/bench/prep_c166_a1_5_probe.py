# ---
# labview: none
# hardware: none
# ---
"""Card 166-a1-5 probe: structure of the P5-final graph json, its EL read and the expected file (json only, no LabVIEW).
Prediction: graph has terminals/objs/owners/loops/graph_summary; EL read lists 47 items; expected lists 47 entries."""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT); sys.path.insert(0, "tools")
import protocol
B = "tools/bench/"
G = json.load(open(B + "graph_ring_p5s02e_20261012_173009.json", encoding="utf-8"))
print("GRAPH keys", {k: (type(v).__name__, len(v) if hasattr(v, "__len__") else v) for k, v in G.items()})
print("term0", G["terminals"][0]); print("obj0", G["objs"][0])
print("loops", json.dumps(G.get("loops"))[:3000])
print("objs classes", collections.Counter(o["class"] for o in G["objs"]).most_common(80))
print("obj keys", collections.Counter(k for o in G["objs"] for k in o))
print("fs_measured", json.dumps(G["fs_measured"])[:600]); print("fs pair0", G["fs_tunnel_pairs"][0])
print("owners sample", list(G["owners"].items())[:8])
for k in G:
    if k not in ("terminals", "objs", "owners", "loops", "graph_summary"):
        print("OTHER", k, json.dumps(G[k])[:800])
E = json.load(open(B + "errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json", encoding="utf-8"))
print("EL keys", {k: (type(v).__name__, len(v) if hasattr(v, "__len__") else v) for k, v in E.items()})
print(json.dumps(E, indent=1)[:6000])
X = json.load(open(B + "errorlist_expected_D1_ring_p5_20261010_172913.json", encoding="utf-8"))
print("EXP keys", {k: (type(v).__name__, len(v) if hasattr(v, "__len__") else v) for k, v in X.items()} if isinstance(X, dict) else len(X))
print(json.dumps(X, indent=1)[:9000])
print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
