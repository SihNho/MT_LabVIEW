# ---
# labview: none
# hardware: none
# ---
"""Card 146-a1-1: run every old hook self-test (and the new c146 one when present) and print pass/fail per file.
OFFLINE: no LabVIEW. Prediction: every listed self-test exits 0 with fail 0 (before AND after the hook edits).
Existing tools reused: the selftests themselves; this driver only collects their RESULT lines."""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P  # noqa: E402

TESTS = ["selftest_c_e3", "selftest_guard_peer_budget", "selftest_guard_peer_failre", "selftest_guard_peer_jev",
         "selftest_guard_peer_ladder", "selftest_guard_peer_samerow", "selftest_guard_peer_scan_tmp",
         "selftest_guard_peer_77_measure", "selftest_guard_peer_scrreq_c144", "selftest_guard_peer_c146"]
tag = sys.argv[1] if len(sys.argv) > 1 else "run"
ok_n = bad_n = 0
first = None
for t in TESTS:
    p = os.path.join(HERE, t + ".py")
    if not os.path.exists(p):
        print("SKIP %s (absent)" % t, flush=True)
        continue
    r = subprocess.run([sys.executable, "-u", p], cwd=ROOT, capture_output=True, text=True, timeout=280,
                       encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    lines = [ln for ln in out.splitlines() if ln.startswith("RESULT ")]
    counts = "?"
    if lines:
        try:
            g = json.loads(lines[-1][7:]).get("gates") or {}
            counts = "%s/%s" % (g.get("pass"), g.get("fail"))
        except ValueError:
            pass
    if counts in ("?", "None/None"):
        m = re.findall(r"=== (?:[\w ]+: )?(\d+) pass[,/ ]+(\d+) fail", out)
        counts = ("%s/%s" % m[-1]) if m else "%d/%d(lines)" % (
            len(re.findall(r"^\s*PASS\b", out, re.M)), len(re.findall(r"^\s*FAIL\b", out, re.M)))
    fails = [ln.strip() for ln in out.splitlines() if re.match(r"\s*FAIL\b", ln)]
    good = r.returncode == 0 and not fails
    print("%s %s rc=%d pass/fail=%s %s" % ("OK " if good else "BAD", t, r.returncode, counts,
                                          (" | ".join(fails))[:400]), flush=True)
    if not good:
        print(out[-1500:], flush=True)
    if good:
        ok_n += 1
    else:
        bad_n += 1
        first = first or t
print(P.result_line(P.make_result(ok_n, bad_n, first)), flush=True)
