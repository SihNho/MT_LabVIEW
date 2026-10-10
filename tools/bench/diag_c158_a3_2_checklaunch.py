# ---
# labview: none
# hardware: none
# ---
"""Card 158-a3-2: the launch gate on the FULL launch command text (stage_prerun.check_launch(cmd)). COPY of diag_c158_a2_2_checklaunch.py
(card 158-a2-2, ran 3/0) with the command changed (lines 18-19: the retry's own log diag_c158_p5s02a_scratch.log = the recipe's LOG constant
stage_d1_ring_p5s02a_scratch.py:30, --retry-card task_158-a3-2.json, no --unverified-card) and the gate list (line 27: retry card read, no PB card name).
Calls only; touches no LabVIEW.
PREDICTION: units == [the scratch recipe]; retry_card returns this card; ALLOW."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as P  # noqa: E402

CARDID = sys.argv[1] if len(sys.argv) > 1 else "158-a3-2"      # card 158-a3-2b calls this helper with its own id (no copy)
CMD = ("py tools/bgrun.py --material --max-min 50 --retry-card tools/bench/cards/task_{0}.json --log tools/bench/diag_c158_p5s02a_scratch.log "
       "-- py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py".format(CARDID))
units = P.launched_stage_scripts(CMD)
rc_card = P.retry_card(CMD, "stage_d1_ring_p5s02a_scratch.py", set())          # call form of prep_c158_a3_1_checklaunch.py:35
ok, why = P.check_launch(CMD)
print("CMD " + CMD, flush=True)
print("UNITS {0}".format([P.rel(u) for u in units]), flush=True)
print("RETRY_CARD {0}".format(rc_card), flush=True)
print("{0} {1}".format("ALLOW" if ok else "REFUSE", why.strip()), flush=True)
g = [("units == 1 scratch recipe", len(units) == 1), ("check_launch ALLOW", ok)]
for lab, v in g:
    print("GATE {0} | {1}".format("PASS" if v else "FAIL", lab), flush=True)
nf = sum(1 for _, v in g if not v)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if nf == 0 else "FAIL", "gates": {"pass": len(g) - nf, "fail": nf},
                              "first_fail": next((lab for lab, v in g if not v), None), "artefacts": []}), flush=True)
sys.exit(1 if nf else 0)
