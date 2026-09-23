"""wait_log - touches no LabVIEW: poll a bgrun log for its END/TIMEOUT line for at most 25 s, print the state."""
import sys
import time

p = sys.argv[1]
t0 = time.time()
while time.time() - t0 < 25:
    try:
        txt = open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        txt = ""
    txt = "BGRUN START" + txt.rsplit("BGRUN START", 1)[-1] if "BGRUN START" in txt else txt   # the last run only
    if "BGRUN END" in txt or "BGRUN TIMEOUT" in txt:
        print("ENDED:", [l for l in txt.splitlines() if l.startswith("BGRUN")][-1])
        sys.exit(0)
    time.sleep(3)
print("RUNNING; last line:", (txt.splitlines() or [""])[-1][:160])
