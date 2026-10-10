# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c161_p5s02b_scratch.json
# ---
"""diag_c162_a1_2_peek - card 162-a1-2 (OFFLINE, read-only): print the keys of the step-2 scratch json and its term_identity / census_all
blocks, so the graph-read plan maker reads named fields, not guesses. PREDICTION: keys print; nothing written."""
import json
import os
import sys

B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
import protocol  # noqa: E402

d = json.load(open(os.path.join(B, "diag_c161_p5s02b_scratch.json"), encoding="utf-8"))
print("KEYS", sorted(d.keys()))
for k in ("term_identity", "census_all"):
    v = d.get(k) or {}
    print("BLOCK", k, sorted(v.keys()) if isinstance(v, dict) else type(v))
    if isinstance(v, dict):
        for kk, vv in v.items():
            print("  ", kk, str(vv)[:500])
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
