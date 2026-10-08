# ---
# labview: read
# hardware: none
# ---
r"""diag_c147_b1_3_runold - card 147-b1-3 step 2: run ONE stagekit self-test against the PRE-EDIT stagekit
(git HEAD:tools/stagekit.py, md5 9a3fceaf6beead4c37f142a8808a66de) WITHOUT touching the working-tree tools/stagekit.py.

How: the HEAD source is read with `git show` into memory (md5 checked, refuse on mismatch), executed as module
'stagekit' with __file__ = <root>/tools/stagekit.py (so its HERE/ROOT/BENCH and sys.path inserts are the real ones),
and open() of <root>/tools/stagekit.py is redirected to that same HEAD source (selftest_stagekit case F reads the file,
selftest_stagekit.py:151). Then the self-test runs via runpy as __main__. Nothing opens COM or starts LabVIEW.
No scratch copy on disk (the source stays in memory), so there is no scratch dir to delete.
Prior art: no existing old-vs-new stagekit runner in tools/bench; 147-b1-2 compared before/after by log pairs.
Prediction: the same PASS/FAIL counts as the run against the new stagekit 06b8d844.
Usage: py -u tools/bench/diag_c147_b1_3_runold.py tools/bench/<selftest>.py
"""
import builtins
import hashlib
import io
import os
import runpy
import subprocess
import sys
import types

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
TOOLS = os.path.join(ROOT, "tools")
REAL = os.path.join(TOOLS, "stagekit.py")
WANT = "9a3fceaf6beead4c37f142a8808a66de"

raw = subprocess.check_output(["git", "-C", ROOT, "show", "HEAD:tools/stagekit.py"])
md5 = hashlib.md5(raw).hexdigest()
print("OLD-STAGEKIT md5 {0} (want {1})".format(md5, WANT), flush=True)
if md5 != WANT:
    print("REFUSE: HEAD stagekit md5 mismatch", flush=True)
    sys.exit(2)
SRC = raw.decode("utf-8")

_real_open = builtins.open
_key = os.path.normcase(os.path.abspath(REAL))


def _open(file, mode="r", *a, **kw):
    if isinstance(file, str) and os.path.normcase(os.path.abspath(file)) == _key and "r" in mode and "b" not in mode:
        print("OPEN-REDIRECT tools/stagekit.py -> HEAD source", flush=True)
        return io.StringIO(SRC)
    return _real_open(file, mode, *a, **kw)


builtins.open = _open
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
mod = types.ModuleType("stagekit")
mod.__file__ = REAL
sys.modules["stagekit"] = mod
exec(compile(SRC, REAL, "exec"), mod.__dict__)
target = os.path.abspath(sys.argv[1])
sys.argv = [target]
runpy.run_path(target, run_name="__main__")
