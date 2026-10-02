r"""diag_c134_5_cleanup - card 134-5 rule 1 / pass 4: delete the scratch-b FINAL file (md5 recorded first, must equal the scratch log's
SAVED ARTEFACT md5 5e384978...), keep session a's in-between file (6cc69221) and check the bed (9d7bf287) unchanged; LabVIEW not running.
Touches no LabVIEW (file system + tasklist only).
PREDICTION: K1 scratch final md5 == 5e384978f9ad93121dfbf47e0c368c09 then deleted; K2 in-between md5 6cc69221 kept; K3 bed md5 9d7bf287;
K4 no LabVIEW process.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c134_5_cleanup.log -- py -u tools/bench/diag_c134_5_cleanup.py"""
import hashlib, os, subprocess, sys                                                    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                       # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
FIN, FIN_MD5 = os.path.join(CD, "scratch_c134_5_ring_p3b2b_20261002_112928.vi"), "5e384978f9ad93121dfbf47e0c368c09"   # stage_d1_ring_p3b2b_scratch_c134_5.log:336
AF, AF_MD5 = os.path.join(CD, "scratch_c133_6_ring_p3b2a_20261002_093837.vi"), "6cc6922192b3e330f163561bb95a8115"
BED, BED_MD5 = os.path.join(CD, "D1_ring_p3b1_20261002_060910.vi"), "9d7bf28738b7c154280e5e7c2c9d4961"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None   # noqa: E731
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


m = md5(FIN)
print("  FACT scratch final {0} md5 {1}".format(FIN, m), flush=True)
if m == FIN_MD5:
    os.remove(FIN)
gate("K1 scratch final md5 == the saved artefact's, then deleted", m == FIN_MD5 and not os.path.exists(FIN), m)
gate("K2 in-between file kept, md5 6cc69221", md5(AF) == AF_MD5, md5(AF))
gate("K3 bed md5 9d7bf287 unchanged", md5(BED) == BED_MD5, md5(BED))
tl = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
gate("K4 no LabVIEW process", "labview" not in tl)
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, [])), flush=True)
sys.exit(0 if ff is None else 1)
