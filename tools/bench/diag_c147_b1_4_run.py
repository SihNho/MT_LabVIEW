# ---
# labview: read
# hardware: none
# ---
r"""diag_c147_b1_4_run - card 147-b1-4: run ONE stagekit self-test on the PRE-EDIT (git HEAD, md5 9a3fceaf) or the NEW
(working tree, md5 06b8d844) tools/stagekit.py WITH COM BLOCKED, and write the per-check results to a JSON file.

Prior art: tools/bench/diag_c147_b1_3_runold.py (HEAD source in memory + open() redirect) - reused here verbatim in
spirit; it had no COM block, which is what this driver adds. No edit of stagekit, gscript or any self-test.

COM BLOCK (installed BEFORE stagekit is loaded, so every later importer sees it):
  win32com.client.Dispatch / dynamic.Dispatch / gencache.EnsureDispatch -> raise + count;
  gscript.lv, _invoke, _run, open_panel, create_local_read, create_local_write, _recover_poison -> raise + count;
  subprocess.run/Popen/call/check_output whose argv names LabVIEW.exe or 'Name LabVIEW' -> raise + count.
CASE J ONLY (selftest_stagekit.py:314-350): stagekit.py:794 calls g.create_local_read(work, panel_index); the test
stubs the OLD creator K.mod('diag_s3b_l0_localname_v2').create_local(t, label, panel_index) (:322-330). While the
caller stack contains case_j_local_read_index, the g.create_local_read stub routes to THAT test stub (label taken from
the test's own panel_wiring stub at panel_index) and adds is_source=[True] (stagekit.py:797 demands it; the test stub
returns {'err': None} only). Counted as J-ROUTED, not as a leak.
Prediction: NEW and OLD give identical per-check results; COM leaks 0 in both; selftest_stagekit 49 pass / 0 fail with
the J routing (the 147-b1-3 NEW run was 47/2 only because J reached COM).
Usage: py -u tools/bench/diag_c147_b1_4_run.py old|new tools/bench/<selftest>.py
"""
import builtins
import hashlib
import io
import json
import os
import re
import runpy
import subprocess
import sys
import types

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
TOOLS = os.path.join(ROOT, "tools")
REAL = os.path.join(TOOLS, "stagekit.py")
WANT = {"old": "9a3fceaf6beead4c37f142a8808a66de", "new": "06b8d844284deacab535a9ee442d4964"}
MODE, TARGET = sys.argv[1], os.path.abspath(sys.argv[2])
LEAKS, JROUTED = [], []
sys.path.insert(0, TOOLS)
import protocol                                                                    # noqa: E402


def blocked(name):
    def _stub(*a, **k):
        LEAKS.append(name)
        print("COM-LEAK BLOCKED {0} (call #{1})".format(name, len(LEAKS)), flush=True)
        raise RuntimeError("COM blocked by diag_c147_b1_4_run: " + name)
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

# ---- load stagekit (old = HEAD source in memory, new = working tree), md5 checked
if MODE == "old":
    raw = subprocess.check_output(["git", "-C", ROOT, "show", "HEAD:tools/stagekit.py"])
else:
    raw = open(REAL, "rb").read()
md5 = hashlib.md5(raw).hexdigest()
print("STAGEKIT mode {0} md5 {1} (want {2})".format(MODE, md5, WANT[MODE]), flush=True)
if md5 != WANT[MODE]:
    print("REFUSE: stagekit md5 mismatch", flush=True)
    sys.exit(2)
SRC = raw.decode("utf-8")
if MODE == "old":
    _real_open, _key = builtins.open, os.path.normcase(os.path.abspath(REAL))

    def _open(file, mode="r", *a, **kw):
        if isinstance(file, str) and os.path.normcase(os.path.abspath(file)) == _key and "r" in mode and "b" not in mode:
            print("OPEN-REDIRECT tools/stagekit.py -> HEAD source", flush=True)
            return io.StringIO(SRC)
        return _real_open(file, mode, *a, **kw)
    builtins.open = _open
import gscript as g                                                                # noqa: E402
for _n in ("lv", "_invoke", "_run", "open_panel", "create_local_write", "_recover_poison"):
    if hasattr(g, _n):
        setattr(g, _n, blocked("gscript." + _n))
_cl_block = blocked("gscript.create_local_read")
K = types.ModuleType("stagekit")
K.__file__ = REAL
sys.modules["stagekit"] = K


def _create_local_read(target, panel_index, *a, **k):
    f = sys._getframe(1)
    while f is not None and f.f_code.co_name != "case_j_local_read_index":
        f = f.f_back
    if f is None:
        return _cl_block(target, panel_index, *a, **k)
    label = K.g.panel_wiring(target)[panel_index]["label"]           # the TEST's panel_wiring stub (:328)
    r = dict(K.mod("diag_s3b_l0_localname_v2").create_local(target, label, panel_index))  # the TEST's creator stub
    r.setdefault("is_source", [True])
    JROUTED.append((label, panel_index))
    print("J-ROUTED g.create_local_read({0!r}, {1}) -> test stub, label {2!r}".format(target, panel_index, label), flush=True)
    return r


g.create_local_read = _create_local_read
exec(compile(SRC, REAL, "exec"), K.__dict__)

# ---- run the self-test, recording every check
checks, rc = [], None
if os.path.basename(TARGET) == "selftest_stagekit.py":
    T = runpy.run_path(TARGET, run_name="selftest_under_diag")
    _chk = T["check"]

    def _rec(label, ok, detail=""):
        checks.append([label, bool(ok)])
        return _chk(label, ok, detail)
    T["main"].__globals__["check"] = _rec
    rc = T["main"]()
else:
    buf, _so = io.StringIO(), sys.stdout

    class _Tee(object):
        def write(self, s):
            buf.write(s)
            return _so.write(s)

        def flush(self):
            _so.flush()
    sys.stdout = _Tee()
    sys.argv = [TARGET]
    try:
        runpy.run_path(TARGET, run_name="__main__")
        rc = 0
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    finally:
        sys.stdout = _so
    for line in buf.getvalue().splitlines():
        m = re.match(r"GATE (PASS|FAIL) \| (.*?) \|", line)
        if m:
            checks.append([m.group(2), m.group(1) == "PASS"])
npass = sum(1 for _l, ok in checks if ok)
nfail = len(checks) - npass
out = os.path.join(ROOT, "tools", "bench", "diag_c147_b1_4_{0}_{1}.json".format(
    MODE, os.path.splitext(os.path.basename(TARGET))[0]))
json.dump({"mode": MODE, "stagekit_md5": md5, "target": os.path.relpath(TARGET, ROOT), "rc": rc, "pass": npass,
           "fail": nfail, "failing": [l for l, ok in checks if not ok], "checks": checks, "com_leaks": LEAKS,
           "j_routed": JROUTED}, open(out, "w", encoding="utf-8"), indent=1)
print("DIAG mode {0} rc {1} checks {2} pass / {3} fail; COM leaks {4}; J-routed {5}".format(
    MODE, rc, npass, nfail, len(LEAKS), len(JROUTED)), flush=True)
first = None if not LEAKS else "COM leak " + LEAKS[0]
print(protocol.result_line(protocol.make_result(1 if not LEAKS else 0, 1 if LEAKS else 0, first,
                                                [{"path": os.path.relpath(out, ROOT),
                                                  "md5": hashlib.md5(open(out, "rb").read()).hexdigest()}])), flush=True)
sys.exit(0)
