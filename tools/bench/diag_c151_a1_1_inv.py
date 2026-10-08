# ---
# labview: none
# hardware: none
# ---
"""Card 151-a1-1 invariants (OFFLINE, no LabVIEW): COPY of diag_c150_a3_2_inv.py with the card id, the brief-151-a1-1 step-8 pin list
(s07 b3f86b32 + s06 569ffbf5 + bed; stage tools; graph 71935a84 comes from the card inputs) and every card input md5 read from
tools/bench/cards/task_151-a1-1.json (never typed). argv[1] = 'before' | 'after'. memory_model b4a6eec6 is a card input and pinned in
'before' only (the card adds ONE load_by_vi entry; 'after' records its md5). Scratch glob: _elc_*, _c151a11_*, scratch_c151_*, scratch_c150_p4s08*.
PREDICTION: every pinned md5 equals its pin; 0 scratch files.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c151_a1_1_inv_<mode>.log -- py -u tools/bench/diag_c151_a1_1_inv.py <mode>"""
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
MM = os.path.join(ROOT, "tools", "bench", "memory_model.json")
PINS = {os.path.join(CD, "D1_ring_p4s07_20261008_222709.vi"): "b3f86b32",
        os.path.join(CD, "D1_ring_p4s06_20261008_174730.vi"): "569ffbf5",
        os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"): "39511877",
        os.path.join(ROOT, "tools", "stagekit.py"): "604529e8",   # brief step 8 says 06b8d844 = pre-chat-T6; T6 commit 771a39a1 (merged 9dbd384b) changed it; inv_before run 1 measured 604529e8

        os.path.join(ROOT, "tools", "stagexec.py"): "1bab9cf9",
        os.path.join(ROOT, "tools", "gscript.py"): "1a80236e",
        os.path.join(ROOT, "tools", "elrule.py"): "a5ee7d5c",
        os.path.join(ROOT, "tools", "stage_prerun.py"): "c739eb86",
        os.path.join(ROOT, "tools", "vigraph.py"): "13be0847",
        os.path.join(ROOT, "tools", "stagesim.py"): "748bbf30",
        os.path.join(ROOT, "tools", "errorlist_check.py"): "2b466a89"}
card = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_151-a1-1.json"), encoding="utf-8"))
for inp in card["inputs"]:
    p = os.path.join(ROOT, inp["path"])
    if os.path.abspath(p) != os.path.abspath(MM):
        PINS[p] = inp["md5"]
if MODE == "before":
    PINS[MM] = "b4a6eec6"
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
print("FACT claudeDev p4s07/p4s08 files {0}".format(sorted(os.path.basename(p) for p in glob.glob(os.path.join(CD, "D1_ring_p4s0[78]_*.vi")))), flush=True)
left = [p for pat in ("_elc_*", "_c151a11_*", "scratch_c151_*", "scratch_c150_p4s08*") for p in glob.glob(os.path.join(CD, pat))]
ok = not left
P, F = P + ok, F + (not ok)
first = first or (None if ok else "scratch left")
print("GATE {0} | no _elc_* / _c151a11_* / scratch_c151_* / scratch_c150_p4s08* in claudeDev | {1}".format("PASS" if ok else "FAIL", left), flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if F == 0 else "FAIL", "gates": {"pass": P, "fail": F},
                              "first_fail": first, "artefacts": []}), flush=True)
sys.exit(1 if F else 0)
