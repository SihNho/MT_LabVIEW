# ---
# labview: none
# hardware: none
# evidence: tools/hooks/guard_cycle.py:572-589
# ---
"""Card 163-a2-1: read-only measurement of the two prior-art exemptions guard_cycle tries (stage_prerun.proven_pattern,
priorart_diff.scope) on the step-3 scratch recipe and its main recipe. Calls only; no LabVIEW, no review dispatched.
PREDICTION: none (measurement after guard_cycle refused the scratch launch for a missing prior-art review)."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun  # noqa: E402
import priorart_diff  # noqa: E402

for rel in ("tools/recipes/stage_d1_ring_p5s02c_scratch.py", "tools/recipes/stage_d1_ring_p5s02c.py"):
    fp = os.path.join(ROOT, rel)
    ok, stages, sig = stage_prerun.proven_pattern(fp)
    print("PROVEN {0} ok={1} stages={2} sig={3}".format(rel, ok, stages, json.dumps(sig, default=str)[:900]), flush=True)
    d = priorart_diff.scope(fp)
    print("DIFF {0} {1}".format(rel, json.dumps(d, default=str)[:900]), flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 0, "fail": 0}, "first_fail": None,
                              "artefacts": []}), flush=True)
