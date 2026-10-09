# ---
# labview: none
# hardware: none
# ---
"""Card 154-a3-3b invariants (OFFLINE, no LabVIEW): COPY of diag_c154_a3_3_inv.py. Changed: card file task_154-a3-3b.json; MAIN recipe
pinned normally from the card (aee20128, no retired-pin branch); docs/violation-decisions.md pinned to its post-fix md5 6497e984 (card pin
34da9f4f is the pre-fix bytes; brief step 0 changes exactly one line, quoted by diag_c154_a3_3b_diff.log); snapshot diag_c154_a3_3b_inv_snap.json.
Step-8 pins, P4 recipe/plan + tools/hooks/** snapshot, scratch glob (_elc_*, scratch_c154_*) and memory_model 6f2b5687 ('before' only) unchanged.
PREDICTION: every pinned md5 equals its pin; snapshot unchanged; 0 scratch files.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c154_a3_3b_inv_<mode>.log -- py -u tools/bench/diag_c154_a3_3b_inv.py <mode>"""
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
B = os.path.join(ROOT, "tools", "bench")
MM = os.path.join(B, "memory_model.json")
VD = os.path.join(ROOT, "docs", "violation-decisions.md")
SNAP = os.path.join(B, "diag_c154_a3_3b_inv_snap.json")
MAIN = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01a.py")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"   # noqa: E731
PINS = {os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31",
        os.path.join(CD, "DonorQueue_v0.vi"): "81dba822",
        os.path.join(ROOT, "tools", "stagekit.py"): "604529e8",
        os.path.join(ROOT, "tools", "addrcheck.py"): "207beb0d",
        os.path.join(ROOT, "tools", "stagexec.py"): "1bab9cf9",
        os.path.join(ROOT, "tools", "stagesim.py"): "78b8d5a1",
        os.path.join(ROOT, "tools", "gscript.py"): "1a80236e",
        os.path.join(ROOT, "tools", "vigraph.py"): "a7eb58c7",
        os.path.join(ROOT, "tools", "stage_prerun.py"): "9decb20f",
        os.path.join(ROOT, "tools", "errorlist_check.py"): "2b466a89",
        os.path.join(B, "fs_tunnel_naming_table.json"): "769ae8d0",
        os.path.join(B, "graph_ring_p4s09_20261009_062044.json"): "22f967b5",
        os.path.join(B, "donor_queue_v0.json"): "15269b6c",
        os.path.join(ROOT, "docs", "d1", "ring-p5.md"): "9c5ba571"}
card = json.load(open(os.path.join(B, "cards", "task_154-a3-3b.json"), encoding="utf-8"))
for inp in card["inputs"]:
    p = os.path.join(ROOT, inp["path"])
    if os.path.abspath(p) not in (os.path.abspath(MM), os.path.abspath(VD)):
        PINS[p] = inp["md5"]
PINS[VD] = "6497e984"
if MODE == "before":
    PINS[MM] = "6f2b5687"
P = F = 0
first = None


def gate(label, ok, d=""):
    global P, F, first
    P, F = P + bool(ok), F + (not ok)
    first = first or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, d), flush=True)


for p, pin in PINS.items():
    m = md5(p)
    gate("md5 {0} == {1}".format(os.path.basename(p), pin), m.startswith(pin), m)
files = sorted(set(glob.glob(os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p4*.py")) + glob.glob(os.path.join(B, "plan_ring_p4*.json"))
                   + [p for p in glob.glob(os.path.join(ROOT, "tools", "hooks", "**", "*"), recursive=True)
                      if os.path.isfile(p) and os.path.basename(p) != "material_marker.log"]))
cur = dict((os.path.relpath(p, ROOT).replace("\\", "/"), md5(p)) for p in files)
if MODE == "before":
    json.dump({"main_recipe": md5(MAIN), "files": cur}, open(SNAP, "w", encoding="utf-8"), indent=1)
    print("FACT snapshot {0} files -> {1} md5 {2}".format(len(cur), os.path.relpath(SNAP, ROOT), md5(SNAP)), flush=True)
else:
    sn = json.load(open(SNAP, encoding="utf-8"))
    ch = sorted(k for k in set(cur) | set(sn["files"]) if cur.get(k) != sn["files"].get(k))
    gate("P4 recipes / plans / preds + tools/hooks/** unchanged vs snapshot ({0} files)".format(len(sn["files"])), not ch, ch)
    print("FACT memory_model.json md5 {0}".format(md5(MM)), flush=True)
print("FACT MAIN recipe md5 {0}; scratch recipe md5 {1}".format(md5(MAIN), md5(MAIN.replace(".py", "_scratch.py"))), flush=True)
print("FACT claudeDev p4s09/p5s01a files {0}".format(sorted(os.path.basename(p) for p in glob.glob(os.path.join(CD, "D1_ring_p4s09_*.vi"))
                                                           + glob.glob(os.path.join(CD, "D1_ring_p5s01a_*.vi")))), flush=True)
left = [p for pat in ("_elc_*", "scratch_c154_*") for p in glob.glob(os.path.join(CD, pat))]
gate("no _elc_* / scratch_c154_* in claudeDev", not left, left)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if F == 0 else "FAIL", "gates": {"pass": P, "fail": F},
                              "first_fail": first, "artefacts": []}), flush=True)
sys.exit(1 if F else 0)
