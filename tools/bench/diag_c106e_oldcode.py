"""diag_c106e_oldcode - card 106-5 negative control: the SAME inputs as selftest_stage_prerun_c106e L1/L2 and M1 through
HEAD:tools/stage_prerun.py (git show into %TEMP%), to show the new cases fail on the old code. Offline, no LabVIEW.
PREDICTION (run 2): old `py -V<NL>py -u <stage>` NOT found, old unquoted `wc -l x<NL>py -u <stage>` found; old M1 (690.0 MB) ok True (margin 0 against MEMSTOP 700); old find_graph has no
plan_graphs parameter (TypeError).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c106e_oldcode.log -- py -u tools/bench/diag_c106e_oldcode.py"""
import importlib.util
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P   # noqa: E402

src = subprocess.run(["git", "show", "HEAD:tools/stage_prerun.py"], cwd=ROOT, capture_output=True).stdout
td = tempfile.mkdtemp(prefix="c106e_old_")
path = os.path.join(td, "stage_prerun_head.py")
open(path, "wb").write(src)
spec = importlib.util.spec_from_file_location("stage_prerun_head", path)
OLD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(OLD)
OLD.ROOT, OLD.BENCH = ROOT, os.path.join(ROOT, "tools", "bench")
stage = os.path.normpath(os.path.join(ROOT, "tools", "recipes", "stage_d1_disp.py"))
g = []
# run 1 (07:32) predicted a miss on `wc -l x<NL>py -u <stage>` and was WRONG: shlex(posix=False) reads the newline as
# whitespace, the `py` token is still found. Run 2: the old miss needs line 1 to end in a python token without a script,
# whose flag-skip then takes line 2's `py` as the "script" (i = j + 1 skips it).
l1 = OLD.launched_py('py -V\npy -u tools/recipes/stage_d1_disp.py --stop-after 40')
g.append(("O1 old launched_py misses the stage after `py -V<NL>`", stage not in l1, l1))
l1u = OLD.launched_py('wc -l x\npy -u tools/recipes/stage_d1_disp.py --stop-after 40')
g.append(("O1u old launched_py FINDS the unquoted `wc -l x<NL>py -u <stage>` (run 1's observation)", stage in l1u, l1u))
# review archive/peer/2026-09-27-c106e-oldcode-o1.md s4 (a): the backslash-quote shape of c103d-hooks-before s1 is FOUND by
# HEAD too (non-POSIX shlex: quotes inside a word are literal) - it is not a negative for launched_py
l1a = OLD.launched_py('wc -l \\"x\npy -u tools/recipes/stage_d1_disp.py\n\\"')
g.append(("O1a old launched_py FINDS the backslash-quote `wc -l \\\"x<NL>py -u <stage><NL>\\\"`", stage in l1a, l1a))
rec = [{"path": os.path.join(ROOT, "fixture.log"), "mtime": 0, "stop_after": None, "from_step": None,
        "rows": [{"tag": "read", "k": 0, "mb": 600.0}, {"tag": "op", "k": 1, "mb": 690.0}]}]
m = OLD.mem_margin(os.path.join(ROOT, "tools", "recipes", "stage_d1_disp.py"), records=rec) if hasattr(OLD, "mem_margin") else None
g.append(("O2 old X10 passes 690.0 MB (or has no X10)", m is None or m["ok"] is True, m))
try:
    OLD.find_graph("0" * 32, [])
    fg = "accepted"
except TypeError as e:
    fg = "TypeError " + str(e)
g.append(("O3 old find_graph takes no plan graphs", fg.startswith("TypeError"), fg))
for lab, ok, d in g:
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(d)[:300]), flush=True)
n = sum(1 for x in g if x[1])
print(P.result_line(P.make_result(n, len(g) - n, next((x[0] for x in g if not x[1]), None))), flush=True)
sys.stdout.flush()
os._exit(0 if n == len(g) else 1)
