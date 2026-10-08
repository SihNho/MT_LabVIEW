# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_153-b1-1.md
# ---
"""diag_c153_b1_1_plan - card 153-b1-1: print the s09 plan's keys, context and actions (read-only, offline)."""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE)))
import protocol as P                                                                         # noqa: E402
p = json.load(open(os.path.join(HERE, "plan_ring_p4_s09v18.json"), encoding="utf-8"))
print(list(p.keys()))
print(p["stage"], p.get("final"))
print(json.dumps(p.get("context"))[:1200])
for i, a in enumerate(p["actions"], 1):
    print(i, json.dumps(a)[:500])
print("open_rows", json.dumps(p.get("open_rows"))[:300])
fz = p.get("finalized") or {}
print(json.dumps(dict((k, v if not isinstance(v, (list, dict)) else type(v).__name__) for k, v in fz.items()))[:1500])
print(P.result_line(P.make_result(1, 0, None)))
