"""motor_gate2_live.py - THE LIVE test of the reworked gate, USER PRESENT AT THE RIG AND USER-ORDERED
(2026-09-18 15:2x, rig 조립/assembled, LabVIEW not running, COM3/COM4 free). Every motion below is one of the
steps the user listed; this file sends nothing else.

PRIOR ART CHECKED: tools/bench/p2_pi_softlimit_test2.ps1 (same PI sequence, measured 14:5x - MOV 1 40 => ERR 7,
no motion), tools/bench/p2_asi_set_limits.ps1 (the SL/SU values now in tools/bench/motor_limits.json),
tools/bench/selftest_motor_gate2.py (the same contract with NO port). Nothing here re-implements a transmit: every
command goes through `py tools/motor_gate.py`, which is the only route guard_bash.py leaves open.

PREDICTION CONTRACT (the run FAILS if any gate differs):
  L1  --session start                      code 0; PI TMN 0 / TMX 39, ASI SL -3.8475/-4.7744 SU 0.1525/-0.7744
                                           read back within 0.001; tools/bench/motor_session.json written
  L2  pi "MOV 1 5" --execute               moves; 'RESULT: reached 5'
  L3  pi "MOV 1 40" --execute              the GATE ALLOWS it (no numeric envelope left) and the CONTROLLER
                                           refuses: 'ERR? right after send = 7', POS still 5, no HALT SENT
  L4  pi "MOV 1 0" --execute               back to 0
  L5  asi "M X=-16475" --execute           +0.2 mm, moves, X = -16475 +-5
  L6  asi "M X=-18475" --execute           back, X = -18475 +-5
  L7  asi "HOME X" --execute               REFUSED BY THE GATE, code 3, no port opened for it
  L8  --session end                        code 0; PI TMX 52, ASI SL/SU +-500; the session file is deleted
  L9  --session start                      code 0 again - THE LIMITS ARE LEFT IN FORCE (the user wants them on)
  L10 no command outside this list reached a port (the gate's own log lines for this run are counted)

  MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/motor_gate2_live.log -- py -u tools/bench/motor_gate2_live.py
"""
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GATE = os.path.join(ROOT, "tools", "motor_gate.py")
SESSION = os.path.join(ROOT, "tools", "bench", "motor_session.json")
GATELOG = os.path.join(ROOT, "tools", "bench", "motor_gate.log")
gates = []


def asc(s):
    return str(s).encode("ascii", "replace").decode("ascii")


def gate(label, ok, detail=""):
    gates.append((bool(ok), label, asc(detail)))
    print(asc("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail[:160])), flush=True)


def run(argv, label):
    print("\n=== %s :: py tools/motor_gate.py %s" % (label, " ".join(argv)), flush=True)
    p = subprocess.run([sys.executable, GATE] + argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=150)
    out = p.stdout.decode("utf-8", "replace")
    for line in out.strip().splitlines():
        print("   | " + asc(line), flush=True)
    print("   exit code=%d" % p.returncode, flush=True)
    return p.returncode, out


def num(pattern, text, default=None):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else default


def main():
    t0 = time.time()
    log_before = os.path.getsize(GATELOG) if os.path.exists(GATELOG) else 0

    # L1 -------------------------------------------------------------- session start
    code, out = run(["--session", "start"], "L1 session start")
    sess = json.load(open(SESSION, encoding="utf-8")) if os.path.exists(SESSION) else None
    pi_rb = (sess or {}).get("limits_readback", {}).get("pi", {})
    asi_rb = (sess or {}).get("limits_readback", {}).get("asi", {})
    gate("L1 session start, limits verified by readback",
         code == 0 and sess is not None and abs(pi_rb.get("TMX", -1) - 39.0) <= 0.001
         and abs(pi_rb.get("TMN", -1) - 0.0) <= 0.001
         and abs(asi_rb.get("SL", {}).get("X", 0) + 3.8475) <= 0.001
         and abs(asi_rb.get("SU", {}).get("Y", 0) + 0.7744) <= 0.001,
         "PI %s  ASI %s" % (json.dumps(pi_rb, sort_keys=True), json.dumps(asi_rb, sort_keys=True)))
    if code != 0:
        print("ABORT: the session hook did not verify the controller limits - no move is attempted", flush=True)
        return summarize(t0, log_before)

    # L2 -------------------------------------------------------------- PI 0 -> 5
    code, out = run(["--device", "pi", "--command", "MOV 1 5", "--execute"], "L2 PI MOV 1 5")
    pos = num(r"after:\s+POS\?=1=([-+0-9.eE]+)", out)
    gate("L2 PI moved to 5", code == 0 and pos is not None and abs(pos - 5.0) < 0.01, "POS after = %s" % pos)

    # L3 -------------------------------------------------------------- PI 40: the CONTROLLER must refuse
    code, out = run(["--device", "pi", "--command", "MOV 1 40", "--execute"], "L3 PI MOV 1 40 (controller refuses)")
    err = re.search(r"ERR\? right after send = (\S+)", out)
    pos40 = num(r"after:\s+POS\?=1=([-+0-9.eE]+)", out)
    gate("L3 gate ALLOWED, controller answered ERR 7, axis did not move",
         "ALLOWED (pi)" in out and err is not None and err.group(1) == "7"
         and pos40 is not None and abs(pos40 - 5.0) < 0.01 and "HALT SENT" not in out,
         "ERR=%s POS after=%s (was 5)" % (err.group(1) if err else None, pos40))

    # L4 -------------------------------------------------------------- PI back to 0
    code, out = run(["--device", "pi", "--command", "MOV 1 0", "--execute"], "L4 PI MOV 1 0")
    pos0 = num(r"after:\s+POS\?=1=([-+0-9.eE]+)", out)
    gate("L4 PI back at 0", code == 0 and pos0 is not None and abs(pos0) < 0.01, "POS after = %s" % pos0)

    # L5/L6 ------------------------------------------------------------ ASI +0.2 mm and back
    code, out = run(["--device", "asi", "--command", "M X=-16475", "--execute"], "L5 ASI M X=-16475 (+0.2 mm)")
    x5 = num(r"after:\s+X=([-+0-9.eE]+)", out)
    gate("L5 ASI X reached -16475", code == 0 and x5 is not None and abs(x5 + 16475) <= 5, "X after = %s" % x5)

    code, out = run(["--device", "asi", "--command", "M X=-18475", "--execute"], "L6 ASI M X=-18475 (back)")
    x6 = num(r"after:\s+X=([-+0-9.eE]+)", out)
    gate("L6 ASI X back at -18475", code == 0 and x6 is not None and abs(x6 + 18475) <= 5, "X after = %s" % x6)

    # L7 -------------------------------------------------------------- HOME must be refused BY THE GATE
    code, out = run(["--device", "asi", "--command", "HOME X", "--execute"], "L7 ASI HOME X (must be refused)")
    gate("L7 gate refused HOME X", code == 3 and "REFUSED" in out and "SENT:" not in out,
         (out.strip().splitlines() or [""])[-1][:150])

    # L8 -------------------------------------------------------------- release
    code, out = run(["--session", "end"], "L8 session end (release)")
    tmx = num(r"LIMITS TMN=[-+0-9.eE]+ TMX=([-+0-9.eE]+)", out)
    aslx = num(r"LIMITS SL X=([-+0-9.eE]+)", out)
    gate("L8 released: PI TMX 52, ASI SL -500, session file deleted",
         code == 0 and tmx is not None and abs(tmx - 52.0) <= 0.001 and aslx is not None
         and abs(aslx + 500) <= 0.001 and not os.path.exists(SESSION),
         "TMX=%s ASI SL X=%s file=%s" % (tmx, aslx, os.path.exists(SESSION)))

    # L9 -------------------------------------------------------------- re-arm: the user wants the limits ON
    code, out = run(["--session", "start"], "L9 session start again (LEAVE THE LIMITS SET)")
    sess = json.load(open(SESSION, encoding="utf-8")) if os.path.exists(SESSION) else None
    pi_rb = (sess or {}).get("limits_readback", {}).get("pi", {})
    asi_rb = (sess or {}).get("limits_readback", {}).get("asi", {})
    gate("L9 limits left IN FORCE at the end",
         code == 0 and sess is not None and abs(pi_rb.get("TMX", -1) - 39.0) <= 0.001
         and abs(asi_rb.get("SL", {}).get("X", 0) + 3.8475) <= 0.001,
         "PI %s  ASI %s" % (json.dumps(pi_rb, sort_keys=True), json.dumps(asi_rb, sort_keys=True)))
    return summarize(t0, log_before)


def summarize(t0, log_before):
    sent = []
    if os.path.exists(GATELOG):
        with open(GATELOG, encoding="utf-8") as f:
            f.seek(log_before)
            sent = [ln.strip() for ln in f if "\tSENT\t" in ln]
    print("\nGATE LOG lines written by this run (transmits only):", flush=True)
    for ln in sent:
        print("   | " + asc(ln[:180]), flush=True)
    gate("L10 exactly five transmits reached a port (2 PI moves + 1 refused-by-controller + 2 ASI moves)",
         len(sent) == 5, "%d SENT lines" % len(sent))
    bad = [g for g in gates if not g[0]]
    print("\n%d/%d GATES PASS, %d FAIL, %.0fs" % (len(gates) - len(bad), len(gates), len(bad), time.time() - t0),
          flush=True)
    for g in bad:
        print(asc("  FAILING: %s | %s" % (g[1], g[2])), flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
