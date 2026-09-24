"""m8_wait.py - wait (no LabVIEW) until a log's last BGRUN END says rc=0, or a deadline. Card 74-1.
usage: py tools/bench/m8_wait.py <log> <max_s>"""
import os, sys, time
log, dl = sys.argv[1], float(sys.argv[2]); t0 = time.time()
while time.time() - t0 < dl:
    ends = [l for l in open(log, encoding="utf-8", errors="replace") if l.startswith("BGRUN END")]
    if ends and "rc=0" in ends[-1]:
        print("OK after %.0fs: %s" % (time.time() - t0, ends[-1].strip())); sys.exit(0)
    time.sleep(10)
print("DEADLINE %.0fs; last: %s" % (dl, ends[-1].strip() if ends else None))
peer = sorted(os.listdir("archive/peer"), key=lambda f: os.path.getmtime(os.path.join("archive/peer", f)))[-3:]
print("newest peer:", peer); sys.exit(1)
