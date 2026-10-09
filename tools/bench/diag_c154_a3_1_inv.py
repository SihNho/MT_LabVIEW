# ---
# labview: none
# hardware: none
# offline-args: (none)
# evidence: tools/bench/cards/brief_154-a3-1.md
# ---
"""diag_c154_a3_1_inv - card 154-a3-1 step 7 (offline, reads files + the process list only; never opens a VI): invariant md5s
of the brief's pin list vs the pins, git status of tools/hooks + tools/recipes + the stored P4 plan/pred files, and the count
of running LabVIEW processes (tasklist, read only). PREDICTION: every pin holds; stage_prerun = 9decb20f (the X17 edit);
no hooks/recipes/P4 plan or pred file modified; 0 LabVIEW processes.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c154_a3_1_inv.log -- py -u tools/bench/diag_c154_a3_1_inv.py"""
import hashlib, os, subprocess, sys                                                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = {"tools/stagekit.py": "604529e8", "tools/addrcheck.py": "207beb0d", "tools/stagexec.py": "1bab9cf9", "tools/stagesim.py": "78b8d5a1",
        "tools/gscript.py": "1a80236e", "tools/vigraph.py": "a7eb58c7", "tools/bench/memory_model.json": "6f2b5687",
        os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31", "tools/bench/graph_ring_p4s09_20261009_062044.json": "22f967b5",
        os.path.join(CD, "DonorQueue_v0.vi"): "81dba822", "tools/bench/donor_queue_v0.json": "15269b6c", "docs/d1/ring-p5.md": "9c5ba571",
        "tools/stage_prerun.py": "9decb20f"}
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


got = dict((k, hashlib.md5(open(k if os.path.isabs(k) else os.path.join(ROOT, k), "rb").read()).hexdigest()) for k in PINS)
gate("I1 every pinned md5 holds", all(got[k].startswith(v) for k, v in PINS.items()), dict((os.path.basename(k), got[k][:8]) for k in got))
st = subprocess.run(["git", "status", "--short", "--", "tools/hooks", "tools/recipes", "tools/bench/plan_ring_p4*", "tools/bench/pred_ring_p4*"],
                    cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
mod = [x for x in st if not x.endswith(".log")]
gate("I2 no tools/hooks / tools/recipes / stored P4 plan or pred file modified (logs excluded)", not mod, st)
tl = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout.lower().splitlines()
lv = [x for x in tl if "labview" in x]
gate("I3 no LabVIEW process", not lv, lv)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
