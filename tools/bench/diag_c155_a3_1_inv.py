# ---
# labview: none
# hardware: none
# ---
"""Card 155-a3-1 invariants (OFFLINE, no LabVIEW): COPY of diag_c154_a3_3b_inv.py (card 154-a3-3b) with pins / names changed only.
Changed: card file task_155-a3-1.json; step-7 pins of brief_155-a3-1.md (stagekit aec03c6c, stagexec 53e17623, stagesim eb99c6ba, P5-1a VI
2482fe7b, P5-1a graph bd67a511, P5-1a plan/pred/licence/recipes, errorlist_check 2b466a89, elrule a5ee7d5c, fs_tunnel_naming_table 769ae8d0);
no violation-decisions pin (no edit there); memory_model 386a4cf4 ('before' only); snapshot diag_c155_a3_1_inv_snap.json; recipe =
P5-1b; scratch glob (_elc_*, scratch_c155_*). Lines 5-10, 18-46, 74-78.
PREDICTION: every pinned md5 equals its pin; snapshot unchanged; 0 scratch files.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c155_a3_1_inv_<mode>.log -- py -u tools/bench/diag_c155_a3_1_inv.py <mode>"""
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
SNAP = os.path.join(B, "diag_c155_a3_1_inv_snap.json")
MAIN = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01b.py")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"   # noqa: E731
PINS = {os.path.join(CD, "D1_ring_p5s01a_20261009_101219.vi"): "2482fe7b",
        os.path.join(ROOT, "tools", "stagekit.py"): "aec03c6c",
        os.path.join(ROOT, "tools", "addrcheck.py"): "207beb0d",
        os.path.join(ROOT, "tools", "stagexec.py"): "53e17623",
        os.path.join(ROOT, "tools", "stagesim.py"): "eb99c6ba",
        os.path.join(ROOT, "tools", "gscript.py"): "1a80236e",
        os.path.join(ROOT, "tools", "vigraph.py"): "a7eb58c7",
        os.path.join(ROOT, "tools", "stage_prerun.py"): "9decb20f",
        os.path.join(ROOT, "tools", "errorlist_check.py"): "2b466a89",
        os.path.join(ROOT, "tools", "elrule.py"): "a5ee7d5c",
        os.path.join(B, "fs_tunnel_naming_table.json"): "769ae8d0",
        os.path.join(B, "graph_ring_p5s01a_20261009_103621.json"): "bd67a511",
        os.path.join(B, "plan_ring_p5s01a.json"): "ed62e8d6",
        os.path.join(B, "plan_ring_p5s01a_pred.json"): "2e84eb2c",
        os.path.join(B, "plan_ring_p5s01a_licence.json"): "323ac8e0",
        os.path.join(B, "errorlist_expected_D1_ring_p5s01a_20261009_101219.json"): "aee0d9fe",
        os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01a.py"): "aee20128",
        os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01a_scratch.py"): "3b02d9a7",
        os.path.join(ROOT, "docs", "d1", "ring-p5.md"): "a4b596f0"}
card = json.load(open(os.path.join(B, "cards", "task_155-a3-1.json"), encoding="utf-8"))
for inp in card["inputs"]:
    p = os.path.join(ROOT, inp["path"])
    if os.path.abspath(p) != os.path.abspath(MM):
        PINS[p] = inp["md5"]
if MODE == "before":
    PINS[MM] = "386a4cf4"
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
print("FACT claudeDev p5s01a/p5s01b/p5s01 files {0}".format(sorted(os.path.basename(p) for p in glob.glob(os.path.join(CD, "D1_ring_p5s01*.vi")))), flush=True)
left = [p for pat in ("_elc_*", "scratch_c155_*") for p in glob.glob(os.path.join(CD, pat))]
gate("no _elc_* / scratch_c155_* in claudeDev", not left, left)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if F == 0 else "FAIL", "gates": {"pass": P, "fail": F},
                              "first_fail": first, "artefacts": []}), flush=True)
sys.exit(1 if F else 0)
