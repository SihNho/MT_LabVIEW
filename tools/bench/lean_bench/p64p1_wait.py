r"""p64p1_wait - block until a regex appears in a log (or a time limit), then print the log lines matching a second regex.
No LabVIEW. py tools/bench/lean_bench/p64p1_wait.py <log> <until-regex> <show-regex> [max_s=500]"""
import re, sys, time                                                                     # noqa: E401
log, until, show = sys.argv[1], re.compile(sys.argv[2]), re.compile(sys.argv[3])
lim = float(sys.argv[4]) if len(sys.argv) > 4 else 500.0
t0 = time.time()
while time.time() - t0 < lim:
    try:
        txt = open(log, encoding="utf-8", errors="replace").read()
    except OSError:
        txt = ""
    if until.search(txt):
        break
    time.sleep(10)
for ln in txt.splitlines():
    if show.search(ln):
        print(ln[:900])
print("WAITED %.0f s, now %s" % (time.time() - t0, time.strftime("%H:%M:%S")))
