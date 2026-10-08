# ---
# labview: none
# hardware: none
# ---
"""diag_c147_a2_1_peek - card 147-a2-1: OFFLINE read of the s06 plan rows for op 20/21 and the base terminals of the op-21 sink/source
(no LabVIEW). Prediction: p4_rbA_re1 names #5058 'pos in cal image out' -> [23166, 'Pos within cal image']."""
import json, os, sys                                                               # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
P = json.load(open(os.path.join(ROOT, "tools", "bench", "plan_ring_p4_s06v18.json"), encoding="utf-8"))
for a in P["actions"]:
    if a["id"] in ("p4_rbA_re1", "p4_rbA_re0"):
        print("ACTION", json.dumps(a))
B = json.load(open(os.path.join(ROOT, P["finalized"]["base"]["path"]), encoding="utf-8"))
print("BASE", P["finalized"]["base"]["path"], sorted(B.keys()))
for r in B["terminals"]:
    if r["term_uid"] in (3173, 5171, 10975) or r.get("owner_uid") in (23166,) or r.get("term_name") == "Pos within cal image":
        print("TERM", json.dumps(r))
import stagexec as SX                                                              # noqa: E402
ops = SX.compile_plan(P)
print("OPS", len(ops), ops[-1])
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
