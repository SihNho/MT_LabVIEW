# ---
# labview: none
# hardware: none
# ---
"""Card 158-a3-2: print priorart_diff.scope() of the scratch recipe (which approved sibling, which changed lines) - read only, no LabVIEW.
PREDICTION: a sibling is found; the changed lines are the 158-a3-1 log-name / OPCENSUS / retry-card prints."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import priorart_diff  # noqa: E402

s = priorart_diff.scope(os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s02a_scratch.py"))
print(json.dumps(s, default=str, indent=1)[:6000], flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if s else "FAIL", "gates": {"pass": int(bool(s)), "fail": int(not s)},
                              "first_fail": None if s else "no scope", "artefacts": []}), flush=True)
