# ---
# labview: none
# hardware: none
# ---
"""Card 164-3-3 peek (read-only): print the top-level structure of one sim step file, one real graph file and one plan,
so the measurement script reads the right keys. Prediction: all three load as JSON dicts; no file is written."""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import protocol

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def show(tag, path):
    d = json.load(open(os.path.join(ROOT, path), encoding="utf-8"))
    print(tag, path, type(d).__name__, list(d)[:30] if isinstance(d, dict) else len(d))
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, list) and v:
                print(" ", tag, k, len(v), json.dumps(v[0])[:300])
            elif isinstance(v, dict):
                print(" ", tag, k, "dict", list(v)[:15])
    return d


show("STEP", "tools/bench/sim/ring_p5s02b/step_20_wire.json")
show("GRAPH", "tools/bench/graph_ring_p5s02b_20261010_111905.json")
p = show("PLAN", "tools/bench/plan_ring_p5s02b.json")
for k in ("finalized", "sim", "steps"):
    if k in p:
        print("PLAN key", k, json.dumps(p[k])[:600])
print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
