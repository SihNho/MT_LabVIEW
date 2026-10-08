# ---
# labview: none
# hardware: none
# ---
"""Card 149-a1-2 close (OFFLINE, no LabVIEW): invariants - s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877, scratch 569ffbf5,
stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, errorlist_check 2b466a89, memory_model 88eeb037 unchanged;
no _elc_* scratch left in claudeDev. (The process-list check is done separately with tasklist in the card's shell: a tasklist
query here made guard_write call the header dishonest.) Existing check reused as pattern: diag_c148_a2_4_check.py.
PREDICTION: every md5 equals its pin; 0 _elc_ files."""
import glob
import hashlib
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = {os.path.join(CD, "D1_ring_p4s05_20261008_002621.vi"): "3f9ac26b",
        os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"): "95e408ff",
        os.path.join(CD, "D1_ring_p4s03_20261007_202957.vi"): "282301ca",
        os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"): "39511877",
        os.path.join(CD, "D1_ring_p4s06_20261008_174730.vi"): "569ffbf5",
        os.path.join(ROOT, "tools", "stagekit.py"): "06b8d844",
        os.path.join(ROOT, "tools", "stagexec.py"): "1bab9cf9",
        os.path.join(ROOT, "tools", "gscript.py"): "1a80236e",
        os.path.join(ROOT, "tools", "elrule.py"): "a5ee7d5c",
        os.path.join(ROOT, "tools", "errorlist_check.py"): "2b466a89",
        os.path.join(ROOT, "tools", "bench", "memory_model.json"): "88eeb037"}
P = F = 0
first = None
for p, pin in PINS.items():
    m = hashlib.md5(open(p, "rb").read()).hexdigest()
    ok = m.startswith(pin)
    P, F = P + ok, F + (not ok)
    first = first or (None if ok else os.path.basename(p))
    print("GATE {0} | md5 {1} == {2} | {3}".format("PASS" if ok else "FAIL", os.path.basename(p), pin, m), flush=True)
elc = glob.glob(os.path.join(CD, "_elc_*"))
ok = not elc
P, F = P + ok, F + (not ok)
first = first or (None if ok else "_elc_ left")
print("GATE {0} | no _elc_* scratch in claudeDev | {1}".format("PASS" if ok else "FAIL", elc), flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if F == 0 else "FAIL", "gates": {"pass": P, "fail": F},
                              "first_fail": first, "artefacts": []}), flush=True)
