# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_162-a1-2.json
# ---
"""Card 162-a1-2: the launch gate on the FULL launch command text (stage_prerun.check_launch(cmd)). COPY of
diag_c162_a1_1_checklaunch.py with ONLY the card id in CMD changed (task_162-a1-1.json -> task_162-a1-2.json). Calls only; touches no LabVIEW.
PREDICTION: units == [the scratch recipe]; ALLOW."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as P  # noqa: E402

LOGNAME = sys.argv[1] if len(sys.argv) > 1 else "diag_c161_p5s02b_scratch.log"
FORM = sys.argv[2] if len(sys.argv) > 2 else "brief"   # brief: --unverified-card before --log (bgrun argparse rejects it, rc 2);
# recipe: --unverified-card after the recipe path, as diag_c156_p5s02a_scratch.log:1,285 (the form that launched)
if FORM == "recipe":
    CMD = ("py tools/bgrun.py --material --max-min 50 --log tools/bench/{0} "
           "-- py -u tools/recipes/stage_d1_ring_p5s02b_scratch.py --unverified-card tools/bench/cards/task_162-a1-2.json".format(LOGNAME))
else:
    CMD = ("py tools/bgrun.py --material --max-min 50 --unverified-card tools/bench/cards/task_162-a1-2.json --log tools/bench/{0} "
           "-- py -u tools/recipes/stage_d1_ring_p5s02b_scratch.py".format(LOGNAME))
units = P.launched_stage_scripts(CMD)
ok, why = P.check_launch(CMD)
print("CMD " + CMD, flush=True)
print("UNITS {0}".format([P.rel(u) for u in units]), flush=True)
print("{0} {1}".format("ALLOW" if ok else "REFUSE", why.strip()), flush=True)
g = [("units == 1 scratch recipe", len(units) == 1), ("check_launch ALLOW", ok)]
for lab, v in g:
    print("GATE {0} | {1}".format("PASS" if v else "FAIL", lab), flush=True)
nf = sum(1 for _, v in g if not v)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if nf == 0 else "FAIL", "gates": {"pass": len(g) - nf, "fail": nf},
                              "first_fail": next((lab for lab, v in g if not v), None), "artefacts": []}), flush=True)
sys.exit(1 if nf else 0)
