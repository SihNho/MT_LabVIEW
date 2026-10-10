# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a2-3.md
# ---
"""prep_c164_a2_3_checklaunch - card 164-a2-3 (OFFLINE): the launch gate stage_prerun.check_launch on the FULL step-4 scratch command (recipe form
of diag_c163_a2_2_checklaunch.py), twice: (1) --unverified-card = THIS card (task_164-a2-3.json names no DRY-UNVERIFIED-OK gate: it is not a
launch card), (2) --unverified-card = task_163-a2-2.json, the step-3 launch card whose rules name `DRY-UNVERIFIED-OK: CEN2 new-object census`,
as a STAND-IN for the step-4 launch card that does not exist yet. Calls only; touches no LabVIEW; launches nothing.
PREDICTION: units == [the scratch recipe] both; (1) REFUSE naming DRY-UNVERIFIED-OK; (2) ALLOW."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stage_prerun as P  # noqa: E402
import prep_c156_a1_1_lib as L  # noqa: E402  Gate (shared)

BASE = ("py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c164_p5s02d_scratch.log "
        "-- py -u tools/recipes/stage_d1_ring_p5s02d_scratch.py --unverified-card tools/bench/cards/{0}")
g = L.Gate(fatal_default=False)
print("FACT scratch log exists before: {0}".format(os.path.exists(os.path.join(ROOT, "tools", "bench", "diag_c164_p5s02d_scratch.log"))), flush=True)
res = {}
for card in ("task_164-a2-3.json", "task_163-a2-2.json"):
    cmd = BASE.format(card)
    units = P.launched_stage_scripts(cmd)
    ok, why = P.check_launch(cmd)
    res[card] = (ok, why)
    print("CMD " + cmd, flush=True)
    print("UNITS {0}".format([P.rel(u) for u in units]), flush=True)
    print("{0} {1}".format("ALLOW" if ok else "REFUSE", why.strip()), flush=True)
    g("units == 1 scratch recipe ({0})".format(card), len(units) == 1 and P.rel(units[0]).endswith("stage_d1_ring_p5s02d_scratch.py"))
ok1, why1 = res["task_164-a2-3.json"]
g("(1) own card: REFUSE only for the missing DRY-UNVERIFIED-OK gate", (not ok1) and "DRY-UNVERIFIED-OK" in why1, why1[:300])
g("(2) stand-in launch card task_163-a2-2.json: ALLOW", res["task_163-a2-2.json"][0], res["task_163-a2-2.json"][1][:300])
sys.exit(g.result())
