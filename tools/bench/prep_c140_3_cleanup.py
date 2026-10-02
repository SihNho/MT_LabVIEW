r"""prep_c140_3_cleanup - card 140-3 item 4 hygiene (no LabVIEW): delete the ONE scratch file of this card's scratch run after its
records (diag_c140_3_scratch.log, errorlist_scratch_c140_3.log), then check the bed md5 and that no LabVIEW process runs.
PREDICTION: D scratch deleted (exists before, gone after); B bed md5 == 395118775a52bc90073f4449b99f899d; L no LabVIEW.exe.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c140_3_cleanup.log -- py -u tools/bench/prep_c140_3_cleanup.py"""
import hashlib, os, subprocess, sys                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(CD, "scratch_c140_3_ring_p4s01_20261002_205117.vi")
BED, BEDM = os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"), "395118775a52bc90073f4449b99f899d"
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, d), flush=True)


before = os.path.exists(SCR)
if before:
    os.remove(SCR)
gate("D scratch deleted", before and not os.path.exists(SCR), (before, os.path.exists(SCR)))
m = hashlib.md5(open(BED, "rb").read()).hexdigest()
gate("B bed md5 unchanged", m == BEDM, m)
tl = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
gate("L no LabVIEW process", "labview" not in tl.lower())
left = sorted(f for f in os.listdir(CD) if "c140_3" in f)
print("claudeDev files named c140_3:", left)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
