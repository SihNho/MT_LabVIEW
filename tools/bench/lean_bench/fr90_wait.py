r"""fr90_wait - wait up to N seconds (<= 28) for "BGRUN END" in a bgrun log, then print the log's last lines. Reads only.
    py tools/bench/lean_bench/fr90_wait.py <log> [secs] [lines]"""
import sys, time                                                                          # noqa: E401
p, secs, n = sys.argv[1], min(float(sys.argv[2]) if len(sys.argv) > 2 else 25, 28), int(sys.argv[3]) if len(sys.argv) > 3 else 6
t0 = time.time()


def text():
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


while time.time() - t0 < secs and "BGRUN END" not in text():
    time.sleep(2)
print("\n".join(text().splitlines()[-n:]))
print("WAIT %s after %.0fs" % ("ENDED" if "BGRUN END" in text() else "still running", time.time() - t0))
