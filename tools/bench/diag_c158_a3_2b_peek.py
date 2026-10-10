# ---
# labview: none
# hardware: none
# ---
"""diag_c158_a3_2b_peek - card 158-a3-2b (OFFLINE, json only): print the actions of plan_ring_p5s02r_in.json (one compact line each) and the
top-level keys of plan_ring_p5s02a.json, to see how step-2 actions (24..) reference step-1 objects. Reads only.
PREDICTION: 70+ actions; actions 1..23 == plan_ring_p5s02a.json's actions.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c158_a3_2b_peek.log -- py -u tools/bench/diag_c158_a3_2b_peek.py"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
A = json.load(open(os.path.join(B, "plan_ring_p5s02r_in.json"), encoding="utf-8"))
S1 = json.load(open(os.path.join(B, "plan_ring_p5s02a.json"), encoding="utf-8"))
print("KEYS in-plan", list(A), "| step1", list(S1), flush=True)
print("STEP1 base", json.dumps(S1.get("base")), "| final", json.dumps(S1.get("finalized") or S1.get("final"))[:600], flush=True)
for i, a in enumerate(A["actions"], 1):
    print("A{0:02d} {1}".format(i, json.dumps(a, separators=(",", ":"))[:420]), flush=True)
eq = A["actions"][:23] == S1["actions"]
print("FACT actions 1..23 of the in-plan == step-1 plan actions: {0}".format(eq), flush=True)
print(protocol.result_line(protocol.make_result(1 if eq else 0, 0 if eq else 1, None if eq else "step1 prefix", [])), flush=True)
