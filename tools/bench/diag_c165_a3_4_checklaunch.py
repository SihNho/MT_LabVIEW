# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_165-3-4.json
# ---
"""Card 165-3-4: the launch gate on the FULL launch command text (stage_prerun.check_launch(cmd)). COPY of
diag_c164_a3_5_checklaunch.py; changed lines ONLY: card id (task_165-3-4.json), log c164_p5s02d -> c165_p5s02e, recipe p5s02d -> p5s02e;
the 'brief' variant dropped (brief_165-3-4.md:19 IS the working form). Calls only; touches no LabVIEW.
PREDICTION: units == [the scratch recipe]; ALLOW."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as P  # noqa: E402

CMD = ("py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c165_p5s02e_scratch.log "
       "-- py -u tools/recipes/stage_d1_ring_p5s02e_scratch.py --unverified-card tools/bench/cards/task_165-3-4.json")
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
