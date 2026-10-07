# ---
# labview: none
# hardware: none
# ---
r"""diag_c144_2_check - card 144-a2-1 before/after check (OFFLINE, no LabVIEW): the 7 card inputs md5 unchanged, s02 file 84cac487 and
bed 39511877 unchanged, no LabVIEW process. Existing equivalents: diag_c143_1_check.py (cycle 143, other file set); this one is the
same shape with card 144-a2-1's pins.
PREDICTION CONTRACT: 7 inputs == card md5s; s02 == 84cac48781c7c915c8f0d7e8fb079341; bed == 395118775a52bc90073f4449b99f899d;
tasklist has no LabVIEW.exe.  -> RESULT 10/0
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c144_2_check.log -- py -u tools/bench/diag_c144_2_check.py"""
import hashlib, json, os, subprocess, sys                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
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


card = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_144-a2-1.json"), encoding="utf-8"))
AFTER = "--after" in sys.argv          # after the card: the pred was rewritten on purpose (census + EL measured) - not re-checked
for i in card["inputs"]:
    if AFTER and i["path"].endswith("plan_ring_p4_s03v18_pred.json"):
        print("FACT pred rewritten by diag_c144_2_census.py / diag_c144_2_elexp.py: now {0}".format(md5(os.path.join(ROOT, i["path"]))), flush=True)
        continue
    got = md5(os.path.join(ROOT, i["path"]))
    gate("input {0} md5 == card".format(i["path"]), got == i["md5"], got)
for name, want in (("D1_ring_p4s02_20261003_110001.vi", "84cac48781c7c915c8f0d7e8fb079341"),
                   ("D1_ring_p3b2b_20261002_130007.vi", "395118775a52bc90073f4449b99f899d")):
    got = md5(os.path.join(CD, name))
    gate("{0} md5 unchanged".format(name), got == want, got)
tl = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
gate("no LabVIEW process", "labview" not in tl.lower(), [l for l in tl.splitlines() if "labview" in l.lower()])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
