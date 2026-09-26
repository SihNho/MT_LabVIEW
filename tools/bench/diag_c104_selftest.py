"""card 104-2: stagexec selftest on the PATCHED file, then the same selftest with ONLY the card-104-2 owners line reverted to
the old code (in memory, never on disk). Prediction: patched = all gates PASS incl. T43/T43b; reverted = T43 FAILS.
No LabVIEW. Found before writing: stagexec.py already has `selftest` (T01..T42); this only adds the old-code contrast."""
import json
import os
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
SX = os.path.join(TOOLS, "stagexec.py")
NEW = 'be.addr.owners = bound_owners(prev.get("owners"), self.bind) or be.addr.owners   # card 104-2: sim -> real'
OLD = 'be.addr.owners = prev.get("owners") or be.addr.owners'


def child(mode):
    sys.path.insert(0, TOOLS)
    src = open(SX, encoding="utf-8").read()
    assert src.count(NEW) == 1, "patched line not found exactly once"
    if mode == "old":
        src = src.replace(NEW, OLD)
    m = types.ModuleType("stagexec")
    m.__file__ = SX
    sys.modules["stagexec"] = m
    exec(compile(src, SX, "exec"), m.__dict__)
    return m.selftest()


def run(mode):
    p = subprocess.run([sys.executable, "-u", __file__, "--child", mode], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=900)
    out = p.stdout + p.stderr
    lines = out.splitlines()
    gl = [x for x in lines if x.startswith("=== GATES")]
    t43 = [x for x in lines if "T43" in x and ("PASS" in x[:8] or "FAIL" in x[:8])]
    return p.returncode, (gl[-1] if gl else "no GATES line"), t43, lines


if __name__ == "__main__":
    if "--child" in sys.argv:
        sys.exit(child(sys.argv[sys.argv.index("--child") + 1]))
    rc_n, g_n, t_n, ln = run("new")
    print("PATCHED  rc {0}  {1}".format(rc_n, g_n))
    for x in t_n:
        print("  " + x[:400])
    for x in ln:
        if x.lstrip().startswith("FAIL"):
            print("  PATCHED FAIL LINE: " + x[:400])
    rc_o, g_o, t_o, _l = run("old")
    print("REVERTED rc {0}  {1}".format(rc_o, g_o))
    for x in t_o:
        print("  " + x[:400])
    ok1 = rc_n == 0 and any("T43 " in x and x.lstrip().startswith("PASS") for x in t_n)
    ok2 = any("T43 " in x and x.lstrip().startswith("FAIL") for x in t_o)
    n = int(ok1) + int(ok2)
    first = None if ok1 else "patched selftest not all PASS: " + g_n
    first = first or (None if ok2 else "T43 did not fail on the reverted (old) owners line")
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if n == 2 else "FAIL",
                                  "gates": {"pass": n, "fail": 2 - n}, "first_fail": first, "artefacts": []}))
    sys.exit(0 if n == 2 else 1)
