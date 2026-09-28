r"""diag_c119_c1 - card 119-1 C1 (PD234(k) DECIDED (1)): the pool donor is not an op. Byte-copy claudeDev\OpPoolDonor_v0.vi ->
claudeDev\DonorPool_v0.vi, prove md5 equal to the card's input md5, then remove OpPoolDonor_v0.vi. Files only - LabVIEW is never touched
(the donor is not loaded; a byte copy keeps the uids #101 names / #214 I32 of diag_c118_p1b_r2.log:10).
WHAT EXISTED: diag_c118_p1b.py donor() made the donor with shutil.copyfile (same route); no rename tool exists in gscript for a closed VI.
PREDICTION: K0 source md5 == fac6e4ab0fc4f7513d1a98df31e1f4e8; K1 copy md5 == source md5; K2 source removed, copy still present + same md5.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c119_c1.log -- py -u tools/bench/diag_c119_c1.py"""
import hashlib, os, shutil, sys                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                   # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SRC, DST, WANT = os.path.join(CD, "OpPoolDonor_v0.vi"), os.path.join(CD, "DonorPool_v0.vi"), "fac6e4ab0fc4f7513d1a98df31e1f4e8"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None   # noqa: E731
res, first = [], None


def gate(label, ok, got):
    global first
    res.append(bool(ok)); first = first or (None if ok else label)
    print("GATE {0:<70} {1} {2}".format(label, "PASS" if ok else "FAIL", got), flush=True)
    return ok


if gate("K0 source OpPoolDonor_v0.vi md5 == " + WANT, md5(SRC) == WANT, md5(SRC)):
    if not os.path.exists(DST):
        shutil.copyfile(SRC, DST)
    if gate("K1 DonorPool_v0.vi md5 == source md5", md5(DST) == md5(SRC), md5(DST)):
        os.remove(SRC)
        gate("K2 OpPoolDonor_v0.vi removed; DonorPool_v0.vi present with the same md5", not os.path.exists(SRC) and md5(DST) == WANT, (os.path.exists(SRC), md5(DST)))
arts = [{"path": DST, "md5": md5(DST)}] if md5(DST) else []
print(P.result_line(P.make_result(res.count(True), res.count(False), first, arts, "PASS" if all(res) and len(res) == 3 else "FAIL")), flush=True)
sys.exit(0 if all(res) and len(res) == 3 else 1)
