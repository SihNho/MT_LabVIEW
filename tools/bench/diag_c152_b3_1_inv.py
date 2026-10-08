# ---
# labview: none
# hardware: none
# ---
"""Card 152-b3-1 invariants (OFFLINE, no LabVIEW): COPY of diag_c151_a1_1_inv.py (ffbc0579) with the card id, the brief-152-b3-1 step-8 pin list
(s08 f99e8414 + bed; stage tools incl. addrcheck 207beb0d, stagesim 128bacfb, fs_tunnel_naming_table 769ae8d0, derived graph e26b4d90,
ring-p4d.md cf2ffa4a) and every card input md5 read from tools/bench/cards/task_152-b3-1.json (never typed). argv[1] = 'before' | 'after'.
memory_model a28b6dd7 is a card input and pinned in 'before' only (the card adds ONE load_by_vi entry; 'after' records its md5).
Scratch glob: _elc_*, _c152b31_*, scratch_c152_*. Changed vs the copy source: lines 5-11 (docstring), PINS (21-38), card file, scratch globs.
PREDICTION: every pinned md5 equals its pin; 0 scratch files.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c152_b3_1_inv_<mode>.log -- py -u tools/bench/diag_c152_b3_1_inv.py <mode>"""
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
MM = os.path.join(ROOT, "tools", "bench", "memory_model.json")
PINS = {os.path.join(CD, "D1_ring_p4s08_20261009_031503.vi"): "f99e8414",
        os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"): "39511877",
        os.path.join(ROOT, "tools", "stagekit.py"): "604529e8",
        os.path.join(ROOT, "tools", "addrcheck.py"): "207beb0d",
        os.path.join(ROOT, "tools", "stagexec.py"): "1bab9cf9",
        os.path.join(ROOT, "tools", "gscript.py"): "1a80236e",
        os.path.join(ROOT, "tools", "elrule.py"): "a5ee7d5c",
        os.path.join(ROOT, "tools", "stage_prerun.py"): "c739eb86",
        os.path.join(ROOT, "tools", "vigraph.py"): "13be0847",
        os.path.join(ROOT, "tools", "stagesim.py"): "128bacfb",
        os.path.join(ROOT, "tools", "errorlist_check.py"): "2b466a89",
        os.path.join(ROOT, "tools", "bench", "fs_tunnel_naming_table.json"): "769ae8d0",
        os.path.join(ROOT, "tools", "bench", "graph_ring_p4s08_20261009_033522.json"): "44858dbf",
        os.path.join(ROOT, "tools", "bench", "graph_ring_p4s08_20261009_033522_fsowner.json"): "e26b4d90",
        os.path.join(ROOT, "docs", "d1", "ring-p4d.md"): "cf2ffa4a"}
card = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_152-b3-1.json"), encoding="utf-8"))
for inp in card["inputs"]:
    p = os.path.join(ROOT, inp["path"])
    if os.path.abspath(p) != os.path.abspath(MM):
        PINS[p] = inp["md5"]
if MODE == "before":
    PINS[MM] = "a28b6dd7"
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
print("FACT claudeDev p4s08/p4s09 files {0}".format(sorted(os.path.basename(p) for p in glob.glob(os.path.join(CD, "D1_ring_p4s0[89]_*.vi")))), flush=True)
left = [p for pat in ("_elc_*", "_c152b31_*", "scratch_c152_*") for p in glob.glob(os.path.join(CD, pat))]
ok = not left
P, F = P + ok, F + (not ok)
first = first or (None if ok else "scratch left")
print("GATE {0} | no _elc_* / _c152b31_* / scratch_c152_* in claudeDev | {1}".format("PASS" if ok else "FAIL", left), flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if F == 0 else "FAIL", "gates": {"pass": P, "fail": F},
                              "first_fail": first, "artefacts": []}), flush=True)
sys.exit(1 if F else 0)
