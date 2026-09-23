"""Cycle 68 D-a: promote the accepted S3b-M4 artefact by a BYTE COPY (no LabVIEW).

Prior art checked: no promotion helper exists (glob tools/bench/*promot*, grep shutil.copy) — plain copy.
Prediction contract:
  P1 target claudeDev\\D1_s3_loop15.vi does NOT exist before (else STOP, copy nothing)
  P2 source md5 == 1a11d92aacabf7ec844d65b8af19f39f
  P3 copy md5 == source md5, sizes equal; source still present and unchanged
"""
import hashlib, os, shutil, sys

D = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SRC = os.path.join(D, "D1_s3b_m4b_20260924_004214.vi")
DST = os.path.join(D, "D1_s3_loop15.vi")
EXP = "1a11d92aacabf7ec844d65b8af19f39f"


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


fails = 0


def gate(label, ok, detail=""):
    global fails
    fails += 0 if ok else 1
    print(("PASS " if ok else "FAIL ") + label + (" | " + detail if detail else ""), flush=True)


exists = os.path.exists(DST)
gate("P1 target absent before copy", not exists, DST)
if exists:
    print("STOP: target exists, nothing copied; target md5 " + md5(DST))
    sys.exit(1)
s0 = md5(SRC)
gate("P2 source md5", s0 == EXP, s0 + " size " + str(os.path.getsize(SRC)))
if s0 != EXP:
    print("STOP: source md5 mismatch, nothing copied")
    sys.exit(1)
shutil.copyfile(SRC, DST)
d = md5(DST)
gate("P3a copy md5 == source", d == s0, d + " size " + str(os.path.getsize(DST)))
gate("P3b source unchanged", md5(SRC) == EXP)
gate("P3c sizes equal", os.path.getsize(SRC) == os.path.getsize(DST))
print("SUMMARY %d fail" % fails)
sys.exit(1 if fails else 0)
