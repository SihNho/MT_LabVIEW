# ---
# labview: none
# hardware: none
# ---
r"""diag_c145_1_check - card 145-a1-1 before/after check (OFFLINE, no LabVIEW): the 7 card inputs md5 unchanged, s03 file 282301ca and
bed 39511877 unchanged, no LabVIEW process. Existing equivalent: diag_c144_2_check.py (card 144-a2-1, other file set); this one is the
same shape with card 145-a1-1's pins.
PREDICTION CONTRACT: 7 inputs == card md5s; s03 == 282301ca...; bed == 395118775a52bc90073f4449b99f899d; tasklist has no LabVIEW.exe.
-> RESULT 10/0 (--after: the pred is not re-checked, it is rewritten on purpose -> 9/0)
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c145_1_check.log -- py -u tools/bench/diag_c145_1_check.py"""
import hashlib, json, os, subprocess, sys                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
S03 = "D1_ring_p4s03_20261007_202957.vi"
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


card = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_145-a1-1.json"), encoding="utf-8"))
AFTER = "--after" in sys.argv
for i in card["inputs"]:
    if AFTER and i["path"].endswith("plan_ring_p4_s04v18_pred.json"):
        print("FACT pred rewritten by the census / EL scripts: now {0}".format(md5(os.path.join(ROOT, i["path"]))), flush=True)
        continue
    got = md5(os.path.join(ROOT, i["path"]))
    gate("input {0} md5 == card".format(i["path"]), got == i["md5"], got)
s03 = md5(os.path.join(CD, S03))
gate("{0} md5 unchanged (282301ca)".format(S03), s03.startswith("282301ca"), s03)
bed = md5(os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"))
gate("bed md5 unchanged", bed == "395118775a52bc90073f4449b99f899d", bed)
tl = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
gate("no LabVIEW process", "labview" not in tl.lower(), [l for l in tl.splitlines() if "labview" in l.lower()])
print("FACT s03 md5 {0}".format(s03), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
