r"""s2_headcmp - card chat-S2 (offline): the before/after discriminator for the two red self-tests of s2_regress_after.log
(selftest_stage_prerun_c106e.py E1, selftest_stage_prerun_c114.py R4). Each runs twice in a child: once with the git-HEAD copies of
the modules card chat-S2 edited (stage_prerun, stagekit, stagexec, census_predict) preloaded into sys.modules, once as the tree is.
Same shim as tools/bench/prep_c138_1_regress.py:24-31. Both tests are classified offline by guard_peer.script_touches_labview
(v2) and ran without COM in s2_regress_after.log; GATE_SOFT_LOG -> %TEMP%.
PREDICTION CONTRACT: each test's failing gate labels are IDENTICAL with HEAD and with the edited tree (=> not caused by chat-S2).
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                        # noqa: E402

MODS = ("stage_prerun", "stagekit", "stagexec", "census_predict")
TESTS = ("selftest_stage_prerun_c106e.py", "selftest_stage_prerun_c114.py")
HEADDIR = tempfile.mkdtemp(prefix="s2head_")
TRIP = os.path.join(HERE, "c125_1_offline_measure.py")
SHIM = ("import importlib.util, runpy, sys\n"
        "sys.path.insert(0, %r)\n"
        "for m in sys.argv[2].split(',') if sys.argv[2] else []:\n"
        "    sp = importlib.util.spec_from_file_location(m, %r + '/' + m + '.py'); mod = importlib.util.module_from_spec(sp)\n"
        "    sys.modules[m] = mod; sp.loader.exec_module(mod)\n"
        "p = sys.argv[1]; sys.argv = [p] + sys.argv[3:]\n"
        "runpy.run_path(p, run_name='__main__')\n")
FAIL_RE = re.compile(r"^\s*FAIL\s+(\S+)", re.M)


def main():
    for m in MODS:
        src = subprocess.run(["git", "show", "HEAD:tools/%s.py" % m], cwd=ROOT, capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout
        with open(os.path.join(HEADDIR, m + ".py"), "w", encoding="utf-8") as f:
            f.write(src)
    env = dict(os.environ, GATE_SOFT_LOG=os.path.join(tempfile.gettempdir(), "s2_headcmp_soft.jsonl"))
    res = []
    for t in TESTS:
        got = {}
        for tag, head in (("HEAD", ",".join(MODS)), ("TREE", "")):
            p = subprocess.run([sys.executable, "-u", "-c", SHIM % (os.path.join(ROOT, "tools"), HEADDIR.replace("\\", "/")),
                                os.path.join(HERE, t), head], cwd=ROOT, env=env, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=600)
            got[tag] = sorted(set(FAIL_RE.findall(p.stdout or "")))
            r = protocol.parse_result_line(p.stdout or "")
            print("%-36s %s rc=%s gates=%s failing=%s" % (t, tag, p.returncode, (r or {}).get("gates"), got[tag]), flush=True)
        same = got["HEAD"] == got["TREE"]
        res.append((t, same))
        print("  %s  %s failing gates identical with HEAD modules and with the edited tree" % ("PASS" if same else "FAIL", t), flush=True)
    nf = sum(1 for _t, ok in res if not ok)
    print(protocol.result_line(protocol.make_result(len(res) - nf, nf, next((t for t, ok in res if not ok), None))), flush=True)
    return 0 if not nf else 1


if __name__ == "__main__":
    sys.exit(main())
