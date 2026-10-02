r"""diag_c141_2_cleanup - card 141-2 hygiene (no LabVIEW): delete the ONE scratch file of this card's scratch run after its record
(diag_c141_p4s01_scratch.log; the run stopped on gate TD so no Error List read and no launch follow), then check the bed md5 and
that no LabVIEW process runs. Copied from tools/bench/prep_c140_3_cleanup.py with names changed.
PREDICTION: D scratch deleted (exists before, gone after); B bed md5 == 395118775a52bc90073f4449b99f899d; L no LabVIEW.exe.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c141_2_cleanup.log -- py -u tools/bench/diag_c141_2_cleanup.py"""
import hashlib, os, subprocess, sys                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(CD, "scratch_c141_p4s01_20261002_223304.vi")
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
left = sorted(f for f in os.listdir(CD) if "c141" in f)
print("claudeDev files named c141:", left)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
