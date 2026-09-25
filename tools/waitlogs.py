import os, re, sys, time
root = r"G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop"
logs = [os.path.join(root, p) for p in sys.argv[2:]]
deadline = time.time() + float(sys.argv[1])
pat = re.compile(r"BGRUN (END|TIMEOUT)")
def done(p):
    try:
        return bool(pat.search(open(p, encoding="utf-8", errors="replace").read()))
    except OSError:
        return False
while time.time() < deadline and not all(done(p) for p in logs):
    time.sleep(5)
keep = re.compile(r"BGRUN (END|TIMEOUT)|VERDICT|verdict|archive/peer|OUTCOME-VIOLATION|steer_|STOP|novel", re.I)
for p in logs:
    lines = open(p, encoding="utf-8", errors="replace").read().splitlines() if os.path.exists(p) else []
    print("==", os.path.basename(p), "done" if done(p) else "RUNNING")
    for ln in [l for l in lines if keep.search(l)][-10:]:
        print("  ", ln[:300])
