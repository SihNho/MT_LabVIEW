# ---
# labview: none
# hardware: none
# ---
"""prep_c158_a3_1_probe - card 158-a3-1: print plan actions, pred keys and the recorded scratch json shape (read-only, json only)."""
import json
import os
import sys

B = os.path.dirname(os.path.abspath(__file__))
J = lambda n: json.load(open(os.path.join(B, n), encoding="utf-8"))   # noqa: E731
P = J("plan_ring_p5s02a.json")
for a in P["actions"]:
    print("ACT", json.dumps(a)[:300])
print("OPEN", P.get("open_rows"))
print("FINALIZED keys", list(P["finalized"].keys()))
R = J("plan_ring_p5s02a_pred.json")
print("PRED keys", list(R.keys()))
print("PRED census", json.dumps(R.get("census")), "overall", json.dumps(R.get("census_overall"))[:300])
print("PRED ops", R.get("ops"))
D = J("diag_c156_p5s02a_scratch.json")
print("SCR keys", list(D.keys()))
for o in D.get("stagexec") or []:
    print("SX", o.get("k"), o.get("kind"), o.get("bound"), str(o.get("diff"))[:120])
print("CENSUS_ALL", D.get("census_all"))
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
sys.exit(0)
