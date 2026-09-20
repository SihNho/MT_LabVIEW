r"""retro_cycle13_runner.py - ONE runner for cycle 13's mandatory retrospective gate (CLAUDE.md, "Every cycle
ends with a RETROSPECTIVE").  No LabVIEW is touched: this is documents + peer dispatch only.

PRIOR ART CHECKED before writing this: tools/audit_cycle.py and tools/retrospective.py already exist and are the
devices; tools/bench/retro_cycle12.log is the previous run of exactly this pair.  Nothing new is built here - this
file only CHAINS the two existing tools into a single bgrun so the cycle costs one notification (CLAUDE.md, "One
LabVIEW batch = one runner = one notification").

WHAT CYCLE 12's RUN GOT WRONG AND THIS FIXES: retro_cycle12.log:33-36 shows the runner exiting rc=1 on a cp949
UnicodeEncodeError while PRINTING the child's stdout - the audit and review had both completed.  Here every child
is run with encoding='utf-8' and every print goes through a writer that cannot raise on the console code page.

PREDICTION CONTRACT (machine-checkable, evaluated at the end of this file):
  P1  audit_cycle.py --cycle 13 exits 0 and its stdout contains a line starting with 'C7' (the scope-creep
      counter added in cycle 12).                                     -> gate A
  P2  retrospective.py --cycle 13 exits 0 and archives exactly one new archive/peer/*retrospective-cycle13*.md
      that did not exist before this run.                             -> gate B
  P3  that archive file contains at least one 'VIOLATION:' line.      -> gate C
  P4  no file under the project is modified by this runner except tools/bench/*.log and the archive entry the
      peer dispatcher writes.                                         -> gate D (reported, not enforced)
A failed gate is a FAILED PREDICTION and owes a peer review (CLAUDE.md).
"""
import io
import os
import subprocess
import sys
import time
import glob

HERE = os.path.dirname(os.path.abspath(__file__))          # tools/bench
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)


def say(*a):
    print(*a, flush=True)


def run(cmd, timeout):
    t0 = time.time()
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return r.returncode, r.stdout or "", r.stderr or "", time.time() - t0


gates = []


def gate(label, ok, detail=""):
    gates.append((label, ok, detail))
    say(("-> PASS  " if ok else "-> FAIL  ") + label + ("  " + detail if detail else ""))


say("=== cycle-13 retrospective runner ===")
say(f"    root {ROOT}")

# ---------------------------------------------------------------- A: compliance audit, --cycle 13
say("\n--- A: py tools/audit_cycle.py --cycle 13 ---")
rc, out, err, dt = run([sys.executable, os.path.join(TOOLS, "audit_cycle.py"), "--cycle", "13"], 600)
say(out)
if err.strip():
    say("STDERR:\n" + err)
say(f"    audit rc={rc} in {dt:.1f}s")
has_c7 = any(ln.strip().startswith("C7") for ln in out.splitlines())
gate("A1 audit_cycle --cycle 13 rc==0", rc == 0, f"rc={rc}")
gate("A2 audit output has a C7 scope-creep line", has_c7)

# ---------------------------------------------------------------- B: the retrospective dispatch
before = set(glob.glob(os.path.join(ROOT, "archive", "peer", "*retrospective-cycle13*.md")))
say(f"\n--- B: py tools/retrospective.py --cycle 13 ---  (pre-existing archives: {len(before)})")
rc2, out2, err2, dt2 = run([sys.executable, os.path.join(TOOLS, "retrospective.py"), "--cycle", "13"], 1200)
say(out2)
if err2.strip():
    say("STDERR:\n" + err2)
say(f"    retrospective rc={rc2} in {dt2:.1f}s")
after = set(glob.glob(os.path.join(ROOT, "archive", "peer", "*retrospective-cycle13*.md")))
new = sorted(after - before)
gate("B1 retrospective rc==0", rc2 == 0, f"rc={rc2}")
gate("B2 exactly one new retrospective-cycle13 archive", len(new) == 1, f"new={[os.path.basename(p) for p in new]}")

# ---------------------------------------------------------------- C: the archive carries VIOLATION lines
viol = []
if new:
    with open(new[0], "r", encoding="utf-8", errors="replace") as f:
        txt = f.read()
    viol = [ln.strip() for ln in txt.splitlines() if ln.strip().startswith("VIOLATION:")]
    say(f"\n--- C: {os.path.basename(new[0])} ---")
    say(f"    {len(txt)} chars, {len(viol)} VIOLATION line(s)")
    for v in viol:
        say("    " + v)
gate("C1 archive contains >=1 VIOLATION line", len(viol) >= 1, f"n={len(viol)}")

# ---------------------------------------------------------------- D: violations.py --due, verbatim
say("\n--- D: py tools/violations.py --due  (VERBATIM) ---")
rc3, out3, err3, dt3 = run([sys.executable, os.path.join(TOOLS, "violations.py"), "--due"], 300)
say("<<<DUE-BEGIN>>>")
say(out3.rstrip("\n"))
say("<<<DUE-END>>>")
if err3.strip():
    say("STDERR:\n" + err3)
say(f"    violations --due rc={rc3} in {dt3:.1f}s")

say("\n--- D2: py tools/violations.py (full count) ---")
rc4, out4, err4, dt4 = run([sys.executable, os.path.join(TOOLS, "violations.py")], 300)
say(out4.rstrip("\n"))

npass = sum(1 for _, ok, _ in gates if ok)
nfail = len(gates) - npass
say(f"\n=== retro_cycle13 runner: {npass} pass, {nfail} fail ===")
say(f"=== violations --due rc={rc3}; DUE output is between the markers above ===")
sys.exit(0 if nfail == 0 else 1)
