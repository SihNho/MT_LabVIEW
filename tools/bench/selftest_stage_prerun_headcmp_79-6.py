r"""selftest_stage_prerun_headcmp_79-6 - discriminating test from archive/peer/2026-09-25-c79-6-k_launchgate.md s4:
run tools/bench/selftest_launch_gate.py (a) against the WORKING stage_prerun.py (79-6 edit) and (b) against
HEAD:tools/stage_prerun.py (git show, into a %TEMP% tree; the same guard_bash.py copied beside it), and print both
per-case FAIL sets. No LabVIEW, nothing written in the project besides this log.
PREDICTION (claim under attack): both runs 20/8 with the identical failing set {C2,C3,C4,C5,C6,M4,M5,M6}.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_stage_prerun_headcmp_79-6.log -- py -u tools/bench/selftest_stage_prerun_headcmp_79-6.py"""
import os, re, shutil, subprocess, sys                                             # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS, ROOT = os.path.dirname(HERE), os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, TOOLS)
import protocol as P   # noqa: E402
T = os.path.join(os.environ.get("TEMP", "."), "headcmp_79_6_{0}".format(os.getpid()))
os.makedirs(os.path.join(T, "tools", "bench"), exist_ok=True)
os.makedirs(os.path.join(T, "tools", "hooks"), exist_ok=True)
head = subprocess.run(["git", "show", "HEAD:tools/stage_prerun.py"], cwd=ROOT, capture_output=True).stdout
open(os.path.join(T, "tools", "stage_prerun.py"), "wb").write(head)
shutil.copyfile(os.path.join(HERE, "selftest_launch_gate.py"), os.path.join(T, "tools", "bench", "selftest_launch_gate.py"))
shutil.copyfile(os.path.join(TOOLS, "hooks", "guard_bash.py"), os.path.join(T, "tools", "hooks", "guard_bash.py"))
print("HEAD stage_prerun.py bytes", len(head), "COUNTED_BY" in head.decode("utf-8", "replace"), "stageplan_check" in head.decode("utf-8", "replace"))


def run(path, pp):
    env = dict(os.environ, PYTHONPATH=pp)
    p = subprocess.run([sys.executable, "-u", path], cwd=ROOT, capture_output=True, text=True, timeout=200, env=env)
    fails = sorted(set(m.group(1) for m in re.finditer(r"^\s+FAIL\s+([A-Z]\d+b?)\b", p.stdout, re.M)))
    summ = [ln for ln in p.stdout.splitlines() if ln.startswith("=== GATES")]
    print("RUN", path, "rc", p.returncode, summ, "FAILS", fails, ("STDERR " + p.stderr[-300:]) if p.stderr.strip() else "", flush=True)
    return fails, summ


pp = os.pathsep.join([TOOLS, os.path.join(TOOLS, "hooks"), os.path.join(TOOLS, "bench")])
fw, sw = run(os.path.join(HERE, "selftest_launch_gate.py"), pp)
fh, sh = run(os.path.join(T, "tools", "bench", "selftest_launch_gate.py"), pp)
# PIN MOVED by card chat-L2: the 8 were selftest_launch_gate's STALE retry-cap cases (they recorded through
# check_launch(record=True), whose lines were never counted). chat-L2 rebuilt them on bgrun's record_started(), so the
# predicted failing set is now EMPTY (archive/peer/2026-09-25-hyp-lintverify-20260925.md, H3).
want = []
g = [("H1 working-tree failing set == HEAD failing set", fw == fh), ("H2 failing set == the predicted (empty since chat-L2)", fw == want)]
for lab, ok in g:
    print("  {0}  {1}  work {2} head {3}".format("PASS" if ok else "FAIL", lab, fw, fh))
shutil.rmtree(T, ignore_errors=True)
n = sum(1 for _l, o in g if o)
print(P.result_line(P.make_result(n, len(g) - n, next((l for l, o in g if not o), None))))
sys.stdout.flush()
os._exit(0 if n == len(g) else 1)
