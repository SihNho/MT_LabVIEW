# ---
# labview: none
# hardware: none
# ---
r"""p64p2_tidy - remove the work files the FAILED wrapper build runs 1-3 left in claudeDev\bench\lean (each = the Stage's byte copy
of EMPTY_v0, never saved: removed ONLY if its md5 is EMPTY_v0's 6544be40); list every p64p2 file left. No LabVIEW.
    py tools/bench/lean_bench/p64p2_tidy.py [--do]"""
import glob, hashlib, os, sys                                                             # noqa: E401
LEAN = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean"
EMPTY_MD5 = "6544be40470e80763764089fd2767f2a"
STALE = ["ConfigureGrab_rate150_20261014_134914.vi", "ConfigureGrab_rate150_20261014_135311.vi", "ConfigureGrab_rate150_20261014_135704.vi"]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


for f in STALE:
    p = os.path.join(LEAN, f)
    if not os.path.exists(p):
        print("ABSENT %s" % f); continue                                                  # noqa: E702
    m = md5(p)
    act = "REMOVE" if m == EMPTY_MD5 else "KEEP (md5 is not EMPTY_v0's)"
    if m == EMPTY_MD5 and "--do" in sys.argv:
        os.remove(p); act = "REMOVED" if not os.path.exists(p) else "REMOVE FAILED"    # noqa: E702
    print("%s %s %s" % (act, m, f))
for p in sorted(glob.glob(os.path.join(LEAN, "*20261014_1400*.vi")) + glob.glob(os.path.join(LEAN, "*p64p2*"))):
    print("LEFT %s %s" % (md5(p), os.path.basename(p)))
print("obs line file exists: %s" % os.path.exists(os.path.join(LEAN, "obs", "configgrab_rate150.txt")))
