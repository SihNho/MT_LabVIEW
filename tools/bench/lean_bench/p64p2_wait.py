# ---
# labview: none
# hardware: none
# ---
r"""p64p2_wait - block until a regex appears in the LAST run of a bgrun log (text after its last `BGRUN START`), or a time
limit, then print that run's lines matching a second regex. No LabVIEW.
    py tools/bench/lean_bench/p64p2_wait.py <log> <until-regex> <show-regex> [max_s=500]"""
import re, sys, time                                                                     # noqa: E401
log, until, show = sys.argv[1], re.compile(sys.argv[2]), re.compile(sys.argv[3])
lim = float(sys.argv[4]) if len(sys.argv) > 4 else 500.0
t0 = time.time()
while True:
    try:
        txt = open(log, encoding="utf-8", errors="replace").read()
    except OSError:
        txt = ""
    k = txt.rfind("BGRUN START")
    txt = txt[k:] if k >= 0 else txt
    if until.search(txt) or time.time() - t0 > lim:
        break
    time.sleep(5)
for ln in txt.splitlines():
    if show.search(ln):
        print(ln[:900])
print("WAITED %.0f s, now %s" % (time.time() - t0, time.strftime("%H:%M:%S")))
