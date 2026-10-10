# ---
# labview: none
# hardware: none
# ---
"""Card 158-a2-2 invariants (OFFLINE, no LabVIEW): COPY of diag_c156_a2_1_inv.py (ab4ff13c, cards 156-a2-1/2, ran 60/0) with pins / names changed only.
Changed: card file task_158-a2-2.json; snapshot diag_c158_a2_2_inv_snap.json; stagekit 0d8f6d25, stagexec 7a712ccb, ring-p5.md 59a0c310 (card pins);
the failed work copy D1_ring_p5s02a_20261009_152721.vi cac5236b pinned only in mode 'before' (it is deleted after adoption); scratch glob
scratch_c15*_*. Lines 5-10, 23, 29, 31, 51-52, 57-60, 90.
(Duplication: the inv helper is re-copied per card; extraction is outside this card's write globs - OPEN in the facts.)
PREDICTION: every pinned md5 equals its pin; snapshot unchanged; 0 scratch files.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c158_a2_2_inv_<mode>.log -- py -u tools/bench/diag_c158_a2_2_inv.py <mode>"""
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
SNAP = os.path.join(B, "diag_c158_a2_2_inv_snap.json")
MAIN = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s02a.py")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"   # noqa: E731
PINS = {os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31",       # s09 bed (brief_158-a2-2.md:46); added after the 'before' run
        os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"): "7f2582ae",
        os.path.join(CD, "D1_ring_p5s01a_20261009_101219.vi"): "2482fe7b",
        os.path.join(CD, "D1_ring_p5s01b_20261009_123319.vi"): "7f2582ae",
        os.path.join(ROOT, "tools", "stagekit.py"): "0d8f6d25",
        os.path.join(ROOT, "tools", "addrcheck.py"): "207beb0d",
        os.path.join(ROOT, "tools", "stagexec.py"): "7a712ccb",
        os.path.join(ROOT, "tools", "stagesim.py"): "eb99c6ba",
        os.path.join(ROOT, "tools", "gscript.py"): "1a80236e",
        os.path.join(ROOT, "tools", "vigraph.py"): "a7eb58c7",
        os.path.join(ROOT, "tools", "stage_prerun.py"): "9decb20f",
        os.path.join(ROOT, "tools", "errorlist_check.py"): "2b466a89",
        os.path.join(ROOT, "tools", "elrule.py"): "a5ee7d5c",
        os.path.join(B, "fs_tunnel_naming_table.json"): "769ae8d0",
        os.path.join(B, "graph_ring_p5s01_20261009_125622.json"): "6716c499",
        os.path.join(B, "errorlist_expected_D1_ring_p5s01_20261009_124542.json"): "ffc4cf66",
        os.path.join(B, "plan_ring_p5s01a.json"): "ed62e8d6",
        os.path.join(B, "plan_ring_p5s01a_pred.json"): "2e84eb2c",
        os.path.join(B, "plan_ring_p5s01a_licence.json"): "323ac8e0",
        os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01a.py"): "aee20128",
        os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01a_scratch.py"): "3b02d9a7",
        os.path.join(B, "plan_ring_p5s01b.json"): "75a77a00",
        os.path.join(B, "plan_ring_p5s01b_pred.json"): "2f2cbcc3",
        os.path.join(B, "plan_ring_p5s01b_licence.json"): "e592cf7a",
        os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01b.py"): "6de2378d",
        os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p5s01b_scratch.py"): "9233749f",
        os.path.join(ROOT, "docs", "d1", "ring-p5.md"): "59a0c310"}
card = json.load(open(os.path.join(B, "cards", "task_158-a2-2.json"), encoding="utf-8"))
for inp in card["inputs"]:
    p = os.path.join(ROOT, inp["path"])
    if os.path.abspath(p) not in (os.path.abspath(MM), os.path.abspath(os.path.join(B, "adopted_scratch.jsonl"))):
        PINS[p] = inp["md5"]
if MODE == "before":
    PINS[MM] = "c87d170a"
    PINS[os.path.join(B, "adopted_scratch.jsonl")] = "dd0aa787"
    PINS[os.path.join(CD, "D1_ring_p5s02a_20261009_152721.vi")] = "cac5236b"
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
    print("FACT memory_model.json md5 {0}; adopted_scratch.jsonl md5 {1}".format(md5(MM), md5(os.path.join(B, "adopted_scratch.jsonl"))), flush=True)
print("FACT MAIN recipe md5 {0}; scratch recipe md5 {1}".format(md5(MAIN), md5(MAIN.replace(".py", "_scratch.py"))), flush=True)
print("FACT claudeDev D1_ring_p5s0* files {0}".format(
    [(os.path.basename(p), md5(p)[:8]) for p in sorted(glob.glob(os.path.join(CD, "D1_ring_p5s0*.vi")))]), flush=True)
left = [p for pat in ("_elc_*", "scratch_c15*_*") for p in glob.glob(os.path.join(CD, pat))]
gate("no _elc_* / scratch_c15*_* in claudeDev", not left, left)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if F == 0 else "FAIL", "gates": {"pass": P, "fail": F},
                              "first_fail": first, "artefacts": []}), flush=True)
sys.exit(1 if F else 0)
