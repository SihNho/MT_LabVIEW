# ---
# labview: none
# hardware: none
# ---
"""prep_c150_a1_1_probe - card 150-a1-1, read-only: print plan base fields and the s06 graph file's top-level shape. Offline, writes nothing."""
import json, os, sys  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
for f in ("plan_ring_p4_s06v18.json", "plan_ring_p4_s05v18.json", "plan_ring_p4_s07v18.json", "plan_ring_p4_s06v18_pred.json", "plan_ring_p4_s07v18_pred.json"):
    p = json.load(open(os.path.join(B, f), encoding="utf-8"))
    print(f, "base", json.dumps(p.get("base"))[:700])
    print("  keys", list(p.keys()))
    print("  finalized", json.dumps({k: v for k, v in (p.get("finalized") or {}).items() if k != "step_files"})[:500])
g = json.load(open(os.path.join(B, "graph_ring_p4s06_20261008_192149.json"), encoding="utf-8"))
print("graph", {k: (v if not isinstance(v, (list, dict)) else type(v).__name__ + str(len(v))) for k, v in g.items()})
print(sorted(os.listdir(os.path.join(B, "creation_map")))[-6:])
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
