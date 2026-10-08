# ---
# labview: none
# hardware: none
# ---
"""Card 149-a3-2 invariants (OFFLINE, no LabVIEW): COPY of diag_c149_a3_1_inv.py with the card id and the scratch glob widened to this card's
byte copies (_c149a32_*, scratch_c149_a3_2_*). argv[1] = 'before' | 'after'. Pins: s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877,
s06 569ffbf5, stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, errorlist_check 2b466a89; memory_model 88eeb037 is pinned
in 'before' only (the card adds ONE load_by_vi entry; 'after' records its md5).
PREDICTION: every pinned md5 equals its pin; 0 scratch files.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c149_a3_2_inv_<mode>.log -- py -u tools/bench/diag_c149_a3_2_inv.py <mode>"""
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
MM = os.path.join(ROOT, "tools", "bench", "memory_model.json")
PINS = {os.path.join(CD, "D1_ring_p4s05_20261008_002621.vi"): "3f9ac26b",
        os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"): "95e408ff",
        os.path.join(CD, "D1_ring_p4s03_20261007_202957.vi"): "282301ca",
        os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"): "39511877",
        os.path.join(CD, "D1_ring_p4s06_20261008_174730.vi"): "569ffbf5",
        os.path.join(ROOT, "tools", "stagekit.py"): "06b8d844",
        os.path.join(ROOT, "tools", "stagexec.py"): "1bab9cf9",
        os.path.join(ROOT, "tools", "gscript.py"): "1a80236e",
        os.path.join(ROOT, "tools", "elrule.py"): "a5ee7d5c",
        os.path.join(ROOT, "tools", "errorlist_check.py"): "2b466a89"}
if MODE == "before":
    PINS[MM] = "88eeb037"
P = F = 0
first = None
for p, pin in PINS.items():
    m = hashlib.md5(open(p, "rb").read()).hexdigest()
    ok = m.startswith(pin)
    P, F = P + ok, F + (not ok)
    first = first or (None if ok else os.path.basename(p))
    print("GATE {0} | md5 {1} == {2} | {3}".format("PASS" if ok else "FAIL", os.path.basename(p), pin, m), flush=True)
if MODE != "before":
    print("FACT memory_model.json md5 {0}".format(hashlib.md5(open(MM, "rb").read()).hexdigest()), flush=True)
left = [p for pat in ("_elc_*", "_c149a32_*", "scratch_c149_a3_2_*") for p in glob.glob(os.path.join(CD, pat))]
ok = not left
P, F = P + ok, F + (not ok)
first = first or (None if ok else "scratch left")
print("GATE {0} | no _elc_* / _c149a32_* / scratch_c149_a3_2_* in claudeDev | {1}".format("PASS" if ok else "FAIL", left), flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if F == 0 else "FAIL", "gates": {"pass": P, "fail": F},
                              "first_fail": first, "artefacts": []}), flush=True)
sys.exit(1 if F else 0)
