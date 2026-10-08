# ---
# labview: read
# hardware: none
# ---
r"""diag_c147_c3_1_run - card 147-c3-1: run tools/bench/selftest_stagekit.py on the working-tree stagekit (md5 06b8d844)
WITH COM BLOCKED and WITHOUT any case-J routing, so the leak counter shows whether the patched test is self-sufficient.

Prior art: tools/bench/diag_c147_b1_4_run.py (its COM block is copied here; its case-J routing of g.create_local_read
cannot be switched off, which is why this smallest driver exists - brief_147-c3-1.md step 2). No edit of any tool.
COM BLOCK: win32com Dispatch / dynamic.Dispatch / gencache.EnsureDispatch; gscript lv, _invoke, _run, open_panel,
create_local_read, create_local_write, _recover_poison; subprocess run/Popen/call/check_output naming LabVIEW.exe
-> raise + count.
Prediction: selftest_stagekit rc 0, 51 pass / 0 fail, COM leaks 0.
Usage: py -u tools/bench/diag_c147_c3_1_run.py
"""
import hashlib
import json
import os
import re
import runpy
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
TOOLS = os.path.join(ROOT, "tools")
TARGET = os.path.join(TOOLS, "bench", "selftest_stagekit.py")
WANT = "06b8d844284deacab535a9ee442d4964"
LEAKS = []
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "bench"))
import protocol                                                                    # noqa: E402


def blocked(name):
    def _stub(*a, **k):
        LEAKS.append(name)
        print("COM-LEAK BLOCKED {0} (call #{1})".format(name, len(LEAKS)), flush=True)
        raise RuntimeError("COM blocked by diag_c147_c3_1_run: " + name)
    return _stub


import win32com.client as wc                                                       # noqa: E402
from win32com.client import dynamic, gencache                                      # noqa: E402
wc.Dispatch = blocked("win32com.client.Dispatch")
dynamic.Dispatch = blocked("win32com.client.dynamic.Dispatch")
gencache.EnsureDispatch = blocked("win32com.client.gencache.EnsureDispatch")
_LVRE = re.compile(r"LabVIEW\.exe|Name LabVIEW", re.I)
for _n in ("run", "Popen", "call", "check_output"):
    _orig = getattr(subprocess, _n)

    def _wrap(*a, _orig=_orig, _n=_n, **k):
        argv = a[0] if a else k.get("args", "")
        if _LVRE.search(" ".join(argv) if isinstance(argv, (list, tuple)) else str(argv)):
            return blocked("subprocess." + _n + " LabVIEW")()
        return _orig(*a, **k)
    setattr(subprocess, _n, _wrap)

md5 = hashlib.md5(open(os.path.join(TOOLS, "stagekit.py"), "rb").read()).hexdigest()
print("STAGEKIT md5 {0} (want {1})".format(md5, WANT), flush=True)
if md5 != WANT:
    print("REFUSE: stagekit md5 mismatch", flush=True)
    sys.exit(2)
import gscript as g                                                                # noqa: E402
for _n in ("lv", "_invoke", "_run", "open_panel", "create_local_read", "create_local_write", "_recover_poison"):
    if hasattr(g, _n):
        setattr(g, _n, blocked("gscript." + _n))
import stagekit                                                                    # noqa: E402,F401

checks = []
T = runpy.run_path(TARGET, run_name="selftest_under_diag")
_chk = T["check"]


def _rec(label, ok, detail=""):
    checks.append([label, bool(ok)])
    return _chk(label, ok, detail)


T["main"].__globals__["check"] = _rec
rc = T["main"]()
npass = sum(1 for _l, ok in checks if ok)
nfail = len(checks) - npass
out = os.path.join(TOOLS, "bench", "diag_c147_c3_1_selftest_stagekit.json")
json.dump({"stagekit_md5": md5, "rc": rc, "pass": npass, "fail": nfail,
           "failing": [l for l, ok in checks if not ok], "checks": checks, "com_leaks": LEAKS},
          open(out, "w", encoding="utf-8"), indent=1)
print("DIAG rc {0} checks {1} pass / {2} fail; COM leaks {3}".format(rc, npass, nfail, len(LEAKS)), flush=True)
ok = (not LEAKS) and nfail == 0 and npass == 51
first = None if ok else "leaks {0} fail {1} pass {2}".format(len(LEAKS), nfail, npass)
print(protocol.result_line(protocol.make_result(1 if ok else 0, 0 if ok else 1, first,
                                                [{"path": os.path.relpath(out, ROOT),
                                                  "md5": hashlib.md5(open(out, "rb").read()).hexdigest()}])), flush=True)
sys.exit(0)
