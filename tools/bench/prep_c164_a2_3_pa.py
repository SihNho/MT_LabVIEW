# ---
# labview: none
# hardware: none
# evidence: tools/hooks/guard_cycle.py:572-601
# ---
"""Card 164-a2-3: read-only measurement of the prior-art exemptions guard_cycle tries (stage_prerun.proven_pattern, priorart_diff.scope) and the
NEW structure classes it names (stage_prerun.new_structure_classes) on the step-4 recipe pair - the readers of guard_cycle.py:572-601, called,
not copied. No LabVIEW, no review dispatched. PREDICTION: none (decides whether prior_art_review.py is owed)."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun  # noqa: E402
import priorart_diff  # noqa: E402
from tools import protocol  # noqa: E402

owed = []
for rel in ("tools/recipes/stage_d1_ring_p5s02d_scratch.py", "tools/recipes/stage_d1_ring_p5s02d.py"):
    fp = os.path.join(ROOT, rel)
    ok, stages, sig = stage_prerun.proven_pattern(fp)
    print("PROVEN {0} ok={1} stages={2} sig={3}".format(rel, ok, stages, json.dumps(sig, default=str)[:900]), flush=True)
    d = priorart_diff.scope(fp)
    print("DIFF {0} {1}".format(rel, json.dumps(d, default=str)[:900]), flush=True)
    print("NEWCLASSES {0} {1}".format(rel, stage_prerun.new_structure_classes(fp)), flush=True)
    if not ok and not (d is not None and not d["review_needed"]):
        owed.append(rel)
print("OWED prior-art review for {0}".format(owed), flush=True)
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
