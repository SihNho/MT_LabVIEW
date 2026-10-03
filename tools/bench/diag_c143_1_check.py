r"""diag_c143_1_check - card 143-1 hygiene after the Error List miss (no LabVIEW, no edit, no delete): bed, s01 and the scratch-saved
session-2 file md5s; no _elc_ byte copy left in claudeDev; no LabVIEW process. Copied in shape from diag_c141_3_cleanup.py WITHOUT its
delete step: the scratch-saved file D1_ring_p4s02_20261003_110001.vi is kept un-adopted for the judgement session.
PREDICTION: B bed md5 == 395118775a52; F s01 md5 == dc61e193; S session-2 file md5 == 84cac487 (diag_c143_1_scratch.log:424);
E no _elc_ file; L no LabVIEW.exe.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c143_1_check.log -- py -u tools/bench/diag_c143_1_check.py"""
import hashlib, os, subprocess, sys                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
BED, BEDM = os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"), "395118775a52bc90073f4449b99f899d"
S01, S01M = os.path.join(CD, "D1_ring_p4s01_20261002_232547.vi"), "dc61e193e0376ce760f88fdfcda7087b"
S02, S02M = os.path.join(CD, "D1_ring_p4s02_20261003_110001.vi"), "84cac48781c7c915c8f0d7e8fb079341"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                                 # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, d), flush=True)


gate("B bed md5 unchanged", md5(BED) == BEDM, md5(BED))
gate("F s01 file md5 unchanged", md5(S01) == S01M, md5(S01))
gate("S scratch-saved session-2 file md5 == scratch record", md5(S02) == S02M, md5(S02))
left = sorted(f for f in os.listdir(CD) if f.startswith("_elc_") or f.startswith("scratch_c143"))
gate("E no _elc_ / scratch_c143 file left in claudeDev", not left, left)
tl = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
gate("L no LabVIEW process", "labview" not in tl.lower())
print("claudeDev files named p4s02:", sorted(f for f in os.listdir(CD) if "p4s02" in f))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": S02, "md5": S02M}])), flush=True)
sys.exit(0 if not G["fail"] else 1)
