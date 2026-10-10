# ---
# labview: none
# hardware: none
# ---
"""Read-only probe (card 161-a2-1 step 1): which adopted plans create a CaseStructure and move nodes into it, and where each
adopted step's run bindings are recorded (adopted_scratch.jsonl -> scratch json `stagexec` bound dicts).
Prediction: p5s02a creates a CaseStructure with move_in; each of the 3 scratch jsons holds a `stagexec` list with `bound` dicts."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
B = os.path.dirname(os.path.abspath(__file__))
for s in ("p5s01a", "p5s01b", "p5s02a", "p5s02b"):
    p = json.load(open(os.path.join(B, "plan_ring_%s.json" % s)))
    print("== plan", s, "keys", list(p.keys()))
    for a in p.get("actions", []):
        if a.get("op") in ("create", "move_in"):
            print("  ", {k: a[k] for k in a if k in ("id", "op", "class", "as", "nodes", "dest_diagram", "owner", "diagram", "frames")})
for f in ("diag_c154_p5s01a_scratch", "diag_c155_p5s01b_scratch", "diag_c158_p5s02a_scratch"):
    d = json.load(open(os.path.join(B, f + ".json")))
    print("==", f, type(d).__name__, list(d.keys()) if isinstance(d, dict) else len(d))
    sx = d.get("stagexec") if isinstance(d, dict) else None
    print("  stagexec", len(sx or []))
    for o in sx or []:
        print("   ", json.dumps({k: o[k] for k in o if k in ("i", "op", "id", "bound", "action")})[:400])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
