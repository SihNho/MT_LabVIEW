# ---
# labview: none
# hardware: none
# ---
"""selftest_fntest_exempt - card chat-F3 (fp-42): stage_prerun.fntest_release / check_launch FNTEST-EXEMPT, offline.
Cases (written to %TEMP%, never run): (1) the real tools/bench/fntest_g1.py is exempt; (2) a byte copy of it named
fntest_t1.py launches (check_launch allow); (3) the same literal but a save target outside claudeDev\\fntest -> refused and
the refusal names it; (4) the same literal under a non-fntest basename -> refused; (5) a bed-chain literal -> refused;
(6) no literal -> refused exactly as before (no FNTEST text). Nothing imports COM; check_launch only reads records.
py -u tools/bench/selftest_fntest_exempt.py"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as P                                                           # noqa: E402

SRC = open(os.path.join(HERE, "fntest_g1.py"), encoding="utf-8").read()
TMP = tempfile.mkdtemp(prefix="fntest_selftest_")
res = []


def put(name, text):
    p = os.path.join(TMP, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def launch(p):
    return P.check_launch('py tools/bgrun.py --material --max-min 5 --log x.log -- py -u "{0}"'.format(p))


def gate(label, ok, detail=""):
    res.append(bool(ok))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


d, ok, why = P.fntest_release(os.path.join(HERE, "fntest_g1.py"))
gate("1 real fntest_g1.py declared + exempt", d and ok, why)
p2 = put("fntest_t1.py", SRC)
gate("2 byte copy fntest_t1.py: check_launch allows", launch(p2)[0], launch(p2)[1])
bad = SRC.replace('SV = os.path.join(FNDIR, "fntest_g1_save.vi")', 'SV = os.path.join(CD, "fntest_g1_save.vi")')
gate("3a mutation applied", bad != SRC)
p3 = put("fntest_t2.py", bad)
a3, w3 = launch(p3)
gate("3 save outside fntest -> refused, reason named", not a3 and "FNTEST declared but NOT exempt" in w3 and "save() target" in w3, w3)
p4 = put("probe_t3.py", SRC)
a4, w4 = launch(p4)
gate("4 non-fntest basename -> refused", not a4 and "basename is not fntest_" in w4, w4)
p5 = put("fntest_t4.py", SRC.replace('"fntest_g1.log"', '"D1_ring_p4s02_x.vi"'))
a5, w5 = launch(p5)
gate("5 bed-chain literal -> refused", not a5 and "bed chain" in w5, w5)
p6 = put("fntest_t5.py", SRC.replace('FNTEST = "per-function scratch test"', 'NOTE = "x"'))
a6, w6 = launch(p6)
gate("6 no literal -> refused as before, no FNTEST text", not a6 and "FNTEST" not in w6 and "has no dry" in w6, w6)
n_ok = sum(res)
print("RESULT {{\"schema\":\"result-line/1\",\"status\":\"{0}\",\"gates\":{{\"pass\":{1},\"fail\":{2}}}}}".format(
    "PASS" if n_ok == len(res) else "FAIL", n_ok, len(res) - n_ok), flush=True)
sys.exit(0 if n_ok == len(res) else 1)
