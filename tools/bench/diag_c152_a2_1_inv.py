# ---
# labview: none
# hardware: none
# offline-args: before
# evidence: tools/bench/cards/brief_152-a2-1.md
# ---
"""Card 152-a2-1 invariants (OFFLINE, no LabVIEW): COPY of diag_c152_a1_1_inv.py with names changed only - card id 152-a2-1,
the brief-152-a2-1 step-1 pin list (stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun
c739eb86, vigraph 13be0847, stagesim 748bbf30, s08 f99e8414, graph 44858dbf, derived e26b4d90) and every card input md5 read from
tools/bench/cards/task_152-a2-1.json (never typed). argv[1] = 'before' | 'after'. In 'after' mode the ONE authorised change is
tools/stagesim.py: its gate PASSES when its md5 DIFFERS from 748bbf30 (new md5 printed). Scratch glob: _elc_*, scratch_c152_*.
PREDICTION: before = every pinned md5 equals its pin; after = same except stagesim differs; 0 scratch files.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c152_a2_1_inv_<mode>.log -- py -u tools/bench/diag_c152_a2_1_inv.py <mode>"""
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
SIM = os.path.join(ROOT, "tools", "stagesim.py")
PINS = {os.path.join(CD, "D1_ring_p4s08_20261009_031503.vi"): "f99e8414",
        os.path.join(ROOT, "tools", "stagekit.py"): "604529e8",
        os.path.join(ROOT, "tools", "addrcheck.py"): "207beb0d",
        os.path.join(ROOT, "tools", "stagexec.py"): "1bab9cf9",
        os.path.join(ROOT, "tools", "gscript.py"): "1a80236e",
        os.path.join(ROOT, "tools", "stage_prerun.py"): "c739eb86",
        os.path.join(ROOT, "tools", "vigraph.py"): "13be0847",
        SIM: "748bbf30",
        os.path.join(ROOT, "tools", "bench", "graph_ring_p4s08_20261009_033522.json"): "44858dbf",
        os.path.join(ROOT, "tools", "bench", "graph_ring_p4s08_20261009_033522_fsowner.json"): "e26b4d90"}
card = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_152-a2-1.json"), encoding="utf-8"))
for inp in card["inputs"]:
    PINS[os.path.join(ROOT, inp["path"])] = inp["md5"]
P = F = 0
first = None
for p, pin in PINS.items():
    m = hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"
    same = m.startswith(pin)
    want_change = MODE == "after" and os.path.normcase(p) == os.path.normcase(SIM)
    ok = (not same and m != "MISSING") if want_change else same
    P, F = P + ok, F + (not ok)
    first = first or (None if ok else os.path.basename(p))
    print("GATE {0} | md5 {1} {2} {3} | {4}".format("PASS" if ok else "FAIL", os.path.basename(p),
                                                    "!=" if want_change else "==", pin, m), flush=True)
left = [p for pat in ("_elc_*", "scratch_c152_*") for p in glob.glob(os.path.join(CD, pat))]
ok = not left
P, F = P + ok, F + (not ok)
first = first or (None if ok else "scratch left")
print("GATE {0} | no _elc_* / scratch_c152_* in claudeDev | {1}".format("PASS" if ok else "FAIL", left), flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if F == 0 else "FAIL", "gates": {"pass": P, "fail": F},
                              "first_fail": first, "artefacts": []}), flush=True)
sys.exit(1 if F else 0)
