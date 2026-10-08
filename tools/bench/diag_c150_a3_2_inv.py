# ---
# labview: none
# hardware: none
# ---
"""Card 150-a3-2 invariants (OFFLINE, no LabVIEW): COPY of diag_c149_a3_2_inv.py with the card id, the brief-150-a3-2 step-8 pin list
(stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, s06 graph a3ecb92b added; s04/s03 kept) and every card input md5 read from
tools/bench/cards/task_150-a3-2.json (never typed). argv[1] = 'before' | 'after'. memory_model 8eec443c is pinned in 'before' only (the card
adds ONE load_by_vi entry; 'after' records its md5). Scratch glob: _elc_*, _c150a32_*, scratch_c150_* in claudeDev.
PREDICTION: every pinned md5 equals its pin; 0 scratch files.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c150_a3_2_inv_<mode>.log -- py -u tools/bench/diag_c150_a3_2_inv.py <mode>"""
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
MM = os.path.join(ROOT, "tools", "bench", "memory_model.json")
PINS = {os.path.join(CD, "D1_ring_p4s06_20261008_174730.vi"): "569ffbf5",
        os.path.join(CD, "D1_ring_p4s05_20261008_002621.vi"): "3f9ac26b",
        os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"): "95e408ff",
        os.path.join(CD, "D1_ring_p4s03_20261007_202957.vi"): "282301ca",
        os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"): "39511877",
        os.path.join(ROOT, "tools", "stagekit.py"): "06b8d844",
        os.path.join(ROOT, "tools", "stagexec.py"): "1bab9cf9",
        os.path.join(ROOT, "tools", "gscript.py"): "1a80236e",
        os.path.join(ROOT, "tools", "elrule.py"): "a5ee7d5c",
        os.path.join(ROOT, "tools", "stage_prerun.py"): "c739eb86",
        os.path.join(ROOT, "tools", "vigraph.py"): "13be0847",
        os.path.join(ROOT, "tools", "stagesim.py"): "748bbf30",
        os.path.join(ROOT, "tools", "errorlist_check.py"): "2b466a89"}
card = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_150-a3-2.json"), encoding="utf-8"))
for inp in card["inputs"]:
    p = os.path.join(ROOT, inp["path"])
    if os.path.abspath(p) != os.path.abspath(MM):
        PINS[p] = inp["md5"]
if MODE == "before":
    PINS[MM] = "8eec443c"
P = F = 0
first = None
for p, pin in PINS.items():
    m = hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"
    ok = m.startswith(pin)
    P, F = P + ok, F + (not ok)
    first = first or (None if ok else os.path.basename(p))
    print("GATE {0} | md5 {1} == {2} | {3}".format("PASS" if ok else "FAIL", os.path.basename(p), pin, m), flush=True)
if MODE != "before":
    print("FACT memory_model.json md5 {0}".format(hashlib.md5(open(MM, "rb").read()).hexdigest()), flush=True)
print("FACT claudeDev p4s06/p4s07 files {0}".format(sorted(os.path.basename(p) for p in glob.glob(os.path.join(CD, "D1_ring_p4s0[67]_*.vi")))), flush=True)
left = [p for pat in ("_elc_*", "_c150a32_*", "scratch_c150_*") for p in glob.glob(os.path.join(CD, pat))]
ok = not left
P, F = P + ok, F + (not ok)
first = first or (None if ok else "scratch left")
print("GATE {0} | no _elc_* / _c150a32_* / scratch_c150_* in claudeDev | {1}".format("PASS" if ok else "FAIL", left), flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if F == 0 else "FAIL", "gates": {"pass": P, "fail": F},
                              "first_fail": first, "artefacts": []}), flush=True)
sys.exit(1 if F else 0)
