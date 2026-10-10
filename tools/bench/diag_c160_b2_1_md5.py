# ---
# labview: none
# hardware: none
# ---
"""Card 160-b2-1: md5 of the pinned files (tools, plans, the four VI files as bytes; no LabVIEW). Prediction: all equal the pins."""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = [
    (os.path.join(ROOT, "tools", "stagekit.py"), "0b5bb678"),  # re-pinned 160-e5-1 from 1441bb4c
    (os.path.join(ROOT, "tools", "stagesim.py"), "a3261b56"),
    (os.path.join(ROOT, "tools", "stagexec.py"), "c4a6e0b6"),
    (os.path.join(ROOT, "tools", "stage_prerun.py"), "7605116f"),
    (os.path.join(ROOT, "tools", "bench", "plan_ring_p5s02b_in.json"), "56bfddd3"),
    (os.path.join(ROOT, "tools", "bench", "plan_ring_p5s02b.json"), "09ebc7a6"),
    (os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi"), "94ffff94"),
    (os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"), "eb1d0f31"),
    (os.path.join(CD, "D1_ring_p5s01a_20261009_101219.vi"), "2482fe7b"),
    (os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"), "7f2582ae"),
]
ok = 0
for p, pin in PINS:
    h = hashlib.md5(open(p, "rb").read()).hexdigest()
    good = h.startswith(pin)
    ok += good
    print("MD5", "ok " if good else "BAD", h, os.path.basename(p))
fail = len(PINS) - ok
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if not fail else "FAIL",
                              "gates": {"pass": ok, "fail": fail}, "first_fail": None if not fail else "md5", "artefacts": []}))
