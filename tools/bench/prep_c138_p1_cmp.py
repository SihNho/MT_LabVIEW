"""prep_c138_p1_cmp - card 138-P1 (offline): compile_plan(v8) vs compile_plan(v9) op by op, keyed by the action ids each op covers.
PREDICTION: only the ops covering p4_i_stopall (new) differ; any other op whose kind/variant changed is printed."""
import json
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX  # noqa: E402


def kinds(p):
    v = json.load(open(os.path.join(ROOT, "tools", "bench", p), encoding="utf-8"))
    A = v["actions"]
    out = {}
    for o in SX.compile_plan(v):
        key = tuple(A[n - 1]["id"] for n in o["acts"])
        out[key] = (o["kind"], o.get("variant"), o.get("route"))
    return out


k8, k9 = kinds("plan_ring_p4_v8.json"), kinds("plan_ring_p4_v9.json")
diff = [(key, k8.get(key), k9.get(key)) for key in sorted(set(k8) | set(k9)) if k8.get(key) != k9.get(key)]
for d in diff:
    print("OPDIFF", d)
bad = [d for d in diff if d[0] != ("p4_i_stopall",)]
print(protocol.result_line(protocol.make_result(1 if not bad else 0, 1 if bad else 0,
                                                None if not bad else "op route changed outside p4_i_stopall", [])))
