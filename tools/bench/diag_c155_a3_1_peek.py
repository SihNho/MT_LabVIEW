# ---
# labview: none
# hardware: none
# ---
"""Card 155-a3-1 (OFFLINE, read-only): print the P5-1b plan's actions, the pred's Error List block and the P5-1a graph plan keys,
so the copied helper scripts take their constants from the files. RESULT line at the end."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
B = os.path.join(ROOT, "tools", "bench")
p = json.load(open(os.path.join(B, "plan_ring_p5s01b.json"), encoding="utf-8"))
for a in p["actions"]:
    print({k: a[k] for k in a if k in ("id", "op", "class", "wire_uid", "prim", "src", "dst", "case", "frame", "sr", "loop", "label")})
print(list(p.keys()))
pr = json.load(open(os.path.join(B, "plan_ring_p5s01b_pred.json"), encoding="utf-8"))
el = pr.get("errorlist") or {}
print({k: el.get(k) for k in ("predicted_total", "alternative_total", "brief_hand_prediction")})
print((el.get("per_class") or {}).get("predicted"))
d = json.load(open(os.path.join(B, "diag_c154_a3_3_graph_plan.json"), encoding="utf-8"))
print({k: (v if k != "decisions" else len(v)) for k, v in d.items() if k != "edits"})
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 0, "fail": 0}, "first_fail": None, "artefacts": []}))
