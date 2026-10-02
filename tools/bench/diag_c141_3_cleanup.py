r"""diag_c141_3_cleanup - card 141-3 hygiene (no LabVIEW): delete the ONE scratch file of this card's scratch rerun after its records
(diag_c141_p4s01_scratch2.log + errorlist_scratch_c141_3.log), then check the bed md5, the in-between file md5, that no Error List
byte copy (_elc_*) and no scratch_c141* file is left, and that no LabVIEW process runs. Copied from diag_c141_2_cleanup.py.
PREDICTION: D scratch deleted; B bed md5 == 395118775a52; F D1_ring_p4s01_20261002_232547.vi md5 == dc61e193; E no _elc_/scratch_c141
file left in claudeDev; L no LabVIEW.exe.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c141_3_cleanup.log -- py -u tools/bench/diag_c141_3_cleanup.py"""
import hashlib, os, subprocess, sys                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(CD, "scratch_c141_p4s01_20261002_230228.vi")
BED, BEDM = os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"), "395118775a52bc90073f4449b99f899d"
FIN, FINM = os.path.join(CD, "D1_ring_p4s01_20261002_232547.vi"), "dc61e193e0376ce760f88fdfcda7087b"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                                 # noqa: E731
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
gate("B bed md5 unchanged", md5(BED) == BEDM, md5(BED))
gate("F in-between file md5 == launch record", md5(FIN) == FINM, md5(FIN))
left = sorted(f for f in os.listdir(CD) if f.startswith("_elc_") or f.startswith("scratch_c141"))
gate("E no _elc_ / scratch_c141 file left in claudeDev", not left, left)
tl = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
gate("L no LabVIEW process", "labview" not in tl.lower())
print("claudeDev files named c141 / p4s01:", sorted(f for f in os.listdir(CD) if "c141" in f or "p4s01" in f))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": FIN, "md5": FINM}])), flush=True)
sys.exit(0 if not G["fail"] else 1)
