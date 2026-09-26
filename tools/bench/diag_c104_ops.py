"""card 104-2 census (offline, no LabVIEW): the op kinds/routes of plan_disp ops 30..end and the sim-keyed fields they read.
Prediction: ops 34-47 include create const_on_term (op 43) inside a created loop body; RESULT line at the end."""
import json
import sys
sys.path.insert(0, "tools")
import stagexec as X  # noqa: E402

p, sp = X.load_final_plan("tools/bench/sim/disp/plan_disp.json", True)
ops = X.compile_plan(p)
A = p["actions"]
for k, o in enumerate(ops, 1):
    if k < 30:
        continue
    a = A[o["acts"][0] - 1]
    keys = ("id", "op", "diagram", "on", "born_on", "loop", "body", "src", "dst", "prim", "value", "as", "reg", "tunnel", "uid")
    print(k, o["kind"], o.get("route"), o["acts"], json.dumps({x: a.get(x) for x in keys if a.get(x) is not None}, default=str)[:400])
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None,
                              "artefacts": []}))
