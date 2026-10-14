r"""p64p1_tidy - offline (no LabVIEW). p64p1_build run 2 stopped at its LAST step: os.replace cannot move the test log across drives
(C: claudeDev -> G: repo, WinError 17). This does that step: copy, compare bytes, delete the source; prints the 4 lines.
Then removes this session's superseded files (build run 1's 4 VIs, the never-edited FirstCallDonor copy), printing their md5 first.
    py tools/bench/lean_bench/p64p1_tidy.py"""
import hashlib, os, shutil                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
LEAN = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean"
SRC = os.path.join(LEAN, "obs", "getbuff_first.txt")
DST = os.path.join(HERE, "out_p64", "getbuff_first_functest_20261014_114246.txt")
OLD = ["GetBuffLog_20261014_113106.vi", "GetBuffFirst_20261014_113106.vi", "GetBuffFirst_test_paced_20261014_113106.vi",
       "GetBuffFirst_harness_paced_20261014_113106.vi", "FirstCallDonor_20261014_112649.vi",
       # the read-only probe's never-saved work copies (byte copies of get buff 9aaaef21)
       "scratch_p64p1_probe_gb_20261014_110021.vi", "scratch_p64p1_probe_gb_20261014_111418.vi", "scratch_p64p1_probe_gb_20261014_111541.vi"]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


if os.path.exists(SRC):
    shutil.copyfile(SRC, DST)
    same = open(SRC, "rb").read() == open(DST, "rb").read()
    print("COPY %s -> %s bytes equal %s" % (SRC, DST, same))
    if same:
        os.remove(SRC)
print("log path %s exists now: %s" % (SRC, os.path.exists(SRC)))
for ln in open(DST, encoding="utf-8"):
    print("LINE %r" % ln.rstrip("\n"))
for f in OLD:
    p = os.path.join(LEAN, f)
    if os.path.exists(p):
        print("REMOVE superseded %s md5 %s" % (f, md5(p)))
        os.remove(p)
