# ---
# labview: none
# hardware: none
# ---
r"""diag_c147_c3_3_check - card 147-c3-3 before/after check (OFFLINE, no LabVIEW): the 18 card inputs hash as pinned in
tools/bench/cards/task_147-c3-3.json, tools/elrule.py a5ee7d5c + stage_prerun 61d6f590 (brief 147-c3-3 delta 1), the adopted s05 3f9ac26b,
s04 95e408ff, s03 282301ca and bed 39511877 unchanged, no LabVIEW process.
COPIED from tools/bench/diag_c147_a1_8_check.py (prior art) with this card's pins (read from the card, not typed).
PREDICTION CONTRACT: 18 pins == card md5s; 2 tool pins; 4 protected VIs; no LabVIEW.exe -> RESULT 25/0
(--after: the pred (census) and memory_model.json (one load_by_vi key) are rewritten on purpose -> reported as FACT)
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c147_c3_3_check.log -- py -u tools/bench/diag_c147_c3_3_check.py"""
import hashlib, json, os, subprocess, sys                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
CARD = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_147-c3-3.json"), encoding="utf-8"))
PINS = dict((i["path"], i["md5"]) for i in CARD["inputs"])
PINS["tools/elrule.py"] = "a5ee7d5c"
PINS["tools/stage_prerun.py"] = "61d6f590"
FILES = {"D1_ring_p4s05_20261008_002621.vi": "3f9ac26b69179eb53c202d90407ce7ee",
         "D1_ring_p4s04_20261007_215031.vi": "95e408ff14a406edd3f16b32ba7324f1",
         "D1_ring_p4s03_20261007_202957.vi": "282301ca",
         "D1_ring_p3b2b_20261002_130007.vi": "395118775a52bc90073f4449b99f899d"}
G = {"pass": 0, "fail": 0, "first": None}


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, d), flush=True)


AFTER = "--after" in sys.argv
for pth, want in PINS.items():
    got = md5(os.path.join(ROOT, pth))
    if AFTER and (pth.endswith("_pred.json") or pth.endswith("memory_model.json")):
        print("FACT {0} rewritten on purpose: now {1} (card pin {2})".format(pth, got, want), flush=True)
        continue
    gate("{0} md5 == {1}".format(pth, want[:8]), got.startswith(want), got)
for name, want in FILES.items():
    got = md5(os.path.join(CD, name))
    gate("{0} md5 unchanged ({1})".format(name, want[:8]), got.startswith(want), got)
    print("FACT {0} md5 {1} size {2}".format(name, got, os.path.getsize(os.path.join(CD, name))), flush=True)
tl = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
gate("no LabVIEW process", "labview" not in tl.lower(), [ln for ln in tl.splitlines() if "labview" in ln.lower()])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
