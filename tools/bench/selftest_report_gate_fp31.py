"""Self-test for gate-fp fp-31 (card 139-2): report_gate.py reads unacked events from every runner log written since
the last ack (not only the newest), and --ack keeps the union of reported hashes.

Prior art checked: tools/hooks/report_gate.py (the code under test; REPORT_GATE_BENCH env for another bench),
tools/wait_runner_event.py (imports report_gate.unreported(), signature unchanged). No earlier fp-31 self-test exists.

Prediction contract (all on temp dirs; the real report_ack.json is never written):
  C1 missed event appended to an OLDER-named log after the ack            -> flagged
  C2 after ack() nothing is flagged in any log                             -> 0 unreported
  C3 a log older than both the ack log and the ack file, with a new line   -> never read, not flagged
  C4 no ack file                                                           -> every log read
  C5 ack names a log that no longer exists                                 -> every log read
  C6 ack() keeps a previous hash that is in no current log; 'log' = newest -> union, no hash lost
  C7 old log written after the ack but the acked log written even later    -> still flagged (ack-file mtime floor)
  C8 the same event line in two logs                                       -> counted once
  L1 live bench (read-only): new unreported count >= old newest-log-only count, no exception
"""
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import report_gate as R   # noqa: E402
import protocol as P      # noqa: E402

REAL_BENCH, REAL_ACK = R.BENCH, R.ACK
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def h(line):
    return hashlib.md5(line.encode("utf-8")).hexdigest()


class Bench:
    def __init__(self):
        self.d = tempfile.mkdtemp(prefix="rg_fp31_")
        R.BENCH = self.d
        R.ACK = os.path.join(self.d, "report_ack.json")
        self.t = time.time() - 10000

    def write(self, name, lines, append=False, mtime=None):
        p = os.path.join(self.d, "cycle_runner_main_%s.log" % name)
        with open(p, "a" if append else "w", encoding="utf-8") as f:
            for ln in lines:
                f.write(ln + "\n")
        self.t += 100
        os.utime(p, (mtime or self.t, mtime or self.t))
        return p

    def ack(self):
        assert os.path.dirname(R.ACK) == self.d and REAL_ACK != R.ACK
        R.ack()
        self.t += 100
        os.utime(R.ACK, (self.t, self.t))

    def un(self):
        return [l for _, l in R.unreported()[1]]

    def close(self):
        R.BENCH, R.ACK = REAL_BENCH, REAL_ACK
        shutil.rmtree(self.d, ignore_errors=True)


# C1 + C2
b = Bench()
b.write("a", ["CYCLE 133 | rc=0", "HEARTBEAT | c133"])
b.write("b", ["CYCLE 134x | rc=0".replace("x", ""), "BGRUN END rc=0 after 1s"])
b.ack()
check("C2a acked flagged nowhere", b.un() == [], str(b.un()))
b.write("a", ["CYCLE 135 | rc=0", "RUNNER STOP | budget"], append=True)
u = b.un()
check("C1 missed event in old log flagged", u == ["CYCLE 135 | rc=0", "RUNNER STOP | budget"], str(u))
b.ack()
check("C2b after ack nothing flagged", b.un() == [], str(b.un()))
b.close()

# C3
b = Bench()
old = b.write("old", ["CYCLE 100 | rc=0"])
b.write("cur", ["CYCLE 101 | rc=0"])
b.ack()
with open(old, "a", encoding="utf-8") as f:
    f.write("CYCLE 999 | rc=0\n")
os.utime(old, (b.t - 5000, b.t - 5000))
check("C3 older log never read", b.un() == [] and old not in R.logs_to_read(), str(b.un()))
b.close()

# C4
b = Bench()
b.write("x", ["CYCLE 1 | rc=0"])
b.write("y", ["CYCLE 2 | rc=0"])
check("C4 no ack -> every log", b.un() == ["CYCLE 1 | rc=0", "CYCLE 2 | rc=0"], str(b.un()))
b.close()

# C5
b = Bench()
gone = b.write("gone", ["CYCLE 3 | rc=0"])
with open(R.ACK, "w", encoding="utf-8") as f:
    json.dump({"log": gone, "reported": [h("CYCLE 3 | rc=0")]}, f)
os.remove(gone)
b.write("p", ["CYCLE 4 | rc=0"])
b.write("q", ["CYCLE 5 | rc=0"])
os.utime(R.ACK, (b.t + 100, b.t + 100))   # ack file newest: only the missing-log rule can make p/q readable
check("C5 ack log missing -> every log", b.un() == ["CYCLE 4 | rc=0", "CYCLE 5 | rc=0"], str(b.un()))
b.close()

# C6
b = Bench()
b.write("m", ["CYCLE 6 | rc=0"])
with open(R.ACK, "w", encoding="utf-8") as f:
    json.dump({"log": None, "reported": ["deadbeef" * 4]}, f)
newest = b.write("n", ["CYCLE 7 | rc=0"])
b.ack()
d = json.load(open(R.ACK, encoding="utf-8"))
ok = ("deadbeef" * 4 in d["reported"] and h("CYCLE 6 | rc=0") in d["reported"]
      and h("CYCLE 7 | rc=0") in d["reported"] and d["log"] == newest)
check("C6 ack union, log=newest", ok, json.dumps(d)[:200])
b.close()

# C7
b = Bench()
a = b.write("a", ["CYCLE 8 | rc=0"])
c = b.write("c", ["CYCLE 9 | rc=0"])
b.ack()
b.write("a", ["CYCLE 10 | rc=0"], append=True)   # old log written after the ack ...
b.write("c", ["HEARTBEAT | c10"], append=True)  # ... and the acked log written even later
check("C7 old log after ack still read", b.un() == ["CYCLE 10 | rc=0", "HEARTBEAT | c10"], str(b.un()))
b.close()

# C8
b = Bench()
b.write("d1", ["BGRUN END rc=0 after 5s"])
b.write("d2", ["BGRUN END rc=0 after 5s", "CYCLE 11 | rc=0"])
check("C8 duplicate line counted once", b.un() == ["BGRUN END rc=0 after 5s", "CYCLE 11 | rc=0"], str(b.un()))
b.close()


# L1 live, read-only: the pre-fp-31 logic (newest log only, report_gate.py:38-69 before the change) vs the new one
def old_unreported():
    logs = glob.glob(os.path.join(REAL_BENCH, "cycle_runner_main_*.log"))
    if not logs:
        return []
    log = max(logs, key=os.path.getmtime)
    try:
        seen = set(json.load(open(REAL_ACK, encoding="utf-8")).get("reported", []))
    except Exception:
        seen = set()
    out = []
    with open(log, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if R.EVENT_RE.match(line) and h(line) not in seen:
                out.append(line)
    return out


ack_md5_before = hashlib.md5(open(REAL_ACK, "rb").read()).hexdigest() if os.path.isfile(REAL_ACK) else None
try:
    o = old_unreported()
    log, n = R.unreported()
    R.decisions_block()
    read = [os.path.basename(p) for p in R.logs_to_read()]
    print("LIVE old=%d new=%d logs_read=%s" % (len(o), len(n), read))
    for _, l in n:
        print("  NEW-UNREPORTED " + l[:160])
    ack_md5_after = hashlib.md5(open(REAL_ACK, "rb").read()).hexdigest() if os.path.isfile(REAL_ACK) else None
    check("L1 live new>=old, no error, real ack untouched",
          len(n) >= len(o) and ack_md5_before == ack_md5_after, "old=%d new=%d" % (len(o), len(n)))
except Exception as e:   # noqa: BLE001
    check("L1 live new>=old, no error, real ack untouched", False, repr(e))

npass = sum(1 for _, ok in results if ok)
nfail = len(results) - npass
ff = next((n for n, ok in results if not ok), None)
print(P.result_line(P.make_result(npass, nfail, first_fail=ff)))
sys.exit(0 if nfail == 0 else 1)
