"""diag_c92b_md5.py - card 92-2 bookkeeping: md5 + size of the input VIs and a listing of related claudeDev files. Read-only."""
import hashlib, glob, os
cd = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
for n in ["D1_s1_t0_20260926_055551.vi", "OpCLFNThread_v0.vi", "D1_s1_copy.vi", "OpSetIndexMode_v0.vi"]:
    p = os.path.join(cd, n)
    print(hashlib.md5(open(p, "rb").read()).hexdigest(), os.path.getsize(p), n)
print(sorted(os.path.basename(x) for x in glob.glob(cd + r"\D1_s1_t0*") + glob.glob(cd + r"\OpCLFN*")))
