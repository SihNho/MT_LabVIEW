# ---
# labview: none
# hardware: none
# ---
"""Card 153-a1-1: print md5 of the invariant files (before/after). Reads files only.
Prediction: every md5 prefix equals the brief's pinned value (brief_153-a1-1.md:35)."""
import hashlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = [
    ("tools/stagekit.py", "604529e8"), ("tools/addrcheck.py", "207beb0d"),
    ("tools/stagexec.py", "1bab9cf9"), ("tools/gscript.py", "1a80236e"),
    ("tools/stage_prerun.py", "c739eb86"), ("tools/stagesim.py", "128bacfb"),
    ("tools/vigraph.py", "13be0847"),
    (os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"), "eb1d0f31"),
    ("tools/bench/graph_ring_p4s09_20261009_062044.json", "22f967b5"),
    ("tools/bench/errorlist_expected_D1_ring_p4s09_20261009_060515.json", "5146f980"),
    ("tools/bench/memory_model.json", "6f2b5687"),
]
ok = bad = 0
for p, pin in PINS:
    fp = p if os.path.isabs(p) else os.path.join(ROOT, p)
    try:
        h = hashlib.md5(open(fp, "rb").read()).hexdigest()
    except OSError as e:
        h = "MISSING"
    good = h.startswith(pin)
    ok += good; bad += (not good)
    print(("OK  " if good else "DIFF"), h, pin, p)
import json
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if bad == 0 else "FAIL",
                              "gates": {"pass": ok, "fail": bad}, "first_fail": None, "artefacts": []}))
