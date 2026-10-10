# ---
# labview: none
# hardware: none
# ---
"""Card 158-a2-2: the launch gate on the FULL launch command text (stage_prerun.check_launch(cmd)). COPY of diag_c156_a2_2_checklaunch.py
(card 156-a2-2, ran 3/0) with the card path changed only (line 17). The log stays the recipe's own LOG constant diag_c156_p5s02a_scratch.log
(stage_d1_ring_p5s02a_scratch.py:27): scratch_tail reads METER lines from that path (stagekit.py:2227) and adopt_scratch its LAST segment.
Calls only; touches no LabVIEW.
PREDICTION: units == [the scratch recipe]; named == ['PB frame-keyed cdiff']; ALLOW."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as P  # noqa: E402

CMD = ("py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c156_p5s02a_scratch.log -- py -u "
       "tools/recipes/stage_d1_ring_p5s02a_scratch.py --unverified-card tools/bench/cards/task_158-a2-2.json")
units = P.launched_stage_scripts(CMD)
named, why_n = P.unverified_card_names(CMD)
ok, why = P.check_launch(CMD)
print("CMD " + CMD, flush=True)
print("UNITS {0}".format([P.rel(u) for u in units]), flush=True)
print("NAMED {0} {1}".format(named, why_n), flush=True)
print("{0} {1}".format("ALLOW" if ok else "REFUSE", why.strip()), flush=True)
g = [("units == 1 scratch recipe", len(units) == 1), ("card names PB", named == ["PB frame-keyed cdiff"]), ("check_launch ALLOW", ok)]
for lab, v in g:
    print("GATE {0} | {1}".format("PASS" if v else "FAIL", lab), flush=True)
nf = sum(1 for _, v in g if not v)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if nf == 0 else "FAIL", "gates": {"pass": len(g) - nf, "fail": nf},
                              "first_fail": next((lab for lab, v in g if not v), None), "artefacts": []}), flush=True)
sys.exit(1 if nf else 0)
