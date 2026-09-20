"""asi_xy_check.py <X|Y> - the user's 2026-09-17 ASI envelope check: offsets -0.4, -2, +0.4, +2, 0 mm from the
ANCHOR on one axis, each sent through tools/motor_gate.py --execute. PREDICTION: +-0.4 and 0 move and are read
back within 5 units; +-2 are REFUSED (exit 3) and the position does not change. Every motion goes through the gate;
this file opens no port itself."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
axis = sys.argv[1].upper()
assert axis in ("X", "Y")
with open(os.path.join(ROOT, "tools", "bench", "motor_anchor.json"), encoding="utf-8-sig") as f:
    anchor = json.load(f)["asi"]
base = round(anchor["%s_mm" % axis.lower()] * 10000)
bad = 0
for off_mm, expect in ((-0.4, 0), (-2.0, 3), (0.4, 0), (2.0, 3), (0.0, 0)):
    cmd = "M %s=%d" % (axis, base + round(off_mm * 10000))
    print("=== offset %+.1f mm -> %s (expect exit %d)" % (off_mm, cmd, expect), flush=True)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "motor_gate.py"), "--device", "asi",
                        "--command", cmd, "--execute"], capture_output=True, text=True, timeout=150)
    print((r.stdout + r.stderr).strip(), flush=True)
    print("    exit %d %s" % (r.returncode, "OK" if r.returncode == expect else "UNEXPECTED"), flush=True)
    if r.returncode != expect:
        bad += 1
        if expect == 3:
            print("STOP: a move that should have been refused was not", flush=True)
            break
print("SUMMARY axis %s: %d unexpected" % (axis, bad))
sys.exit(1 if bad else 0)
