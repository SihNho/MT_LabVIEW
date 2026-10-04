# ---
# labview: none
# hardware: none
# ---
"""card chat-E3: run the existing hook / launch-gate / stage self-tests in the WORKING TREE and in a clean HEAD worktree
(%TEMP%, removed at the end) and compare, so a failure is classed NEW (passes at HEAD, fails now) or PRE-EXISTING.
OFFLINE: every listed self-test is a hook/stage_prerun/stop_record/protocol test (no LabVIEW, no peer).
PREDICTION: 0 NEW failures.
"""
import concurrent.futures as cf
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P   # noqa: E402

PAT = re.compile(r"selftest_(?:bgrun|c103d_hooks|c110_launchgate|c111c_launchunit|c121_3_gatefp|c133_1_gatefp|c134_1_dry|"
                 r"card_clock|census_hookin|chat_p[123]|cycle_runner\w*|dry_c130_5|guard_(?:agent|bash|cycle|peer)|"
                 r"launch_gate|leg_guard|prerun_diag|protocol|report_gate|s5|stage_prerun|stagexec|stoprecord|x10_chat)\w*\.py$")


def run(tree, name):
    env = dict(os.environ)
    for k in ("CARD_ID", "CARD_LABVIEW", "BGRUN_LOG"):
        env.pop(k, None)
    try:
        r = subprocess.run([sys.executable, "-u", os.path.join("tools", "bench", name)], cwd=tree, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        out = (r.stdout or "") + (r.stderr or "")
        res = P.parse_result_line(out)
        failed = r.returncode != 0 or (res is not None and P.result_failed(res))
        tail = (res or {}).get("first_fail") or (out.strip().splitlines() or [""])[-1]
        return name, (not failed), str(tail)[:160]
    except subprocess.TimeoutExpired:
        return name, False, "TIMEOUT 300 s"


names = sorted(n for n in os.listdir(HERE) if PAT.search(n))
head = tempfile.mkdtemp(prefix="e3head_")
subprocess.run(["git", "worktree", "add", "--detach", head, "HEAD"], cwd=ROOT, capture_output=True)
try:
    with cf.ThreadPoolExecutor(6) as ex:
        now = dict((n, (ok, t)) for n, ok, t in ex.map(lambda n: run(ROOT, n), names))
        old = dict((n, (ok, t)) for n, ok, t in ex.map(lambda n: run(head, n) if os.path.exists(
            os.path.join(head, "tools", "bench", n)) else (n, None, "absent at HEAD"), names))
finally:
    subprocess.run(["git", "worktree", "remove", "--force", head], cwd=ROOT, capture_output=True)
    shutil.rmtree(head, ignore_errors=True)

new = []
for n in names:
    ok, t = now[n]
    hok, ht = old[n]
    cls = "PASS" if ok else ("NEW-FAIL" if hok else ("PRE-EXISTING" if hok is False else "FAIL (new test)"))
    if cls != "PASS":
        print("  %-14s %s | now: %s | HEAD: %s" % (cls, n, t, ht), flush=True)
    if cls in ("NEW-FAIL", "FAIL (new test)"):
        new.append(n)
print("%d self-tests: %d pass now, %d NEW failures, %d pre-existing" % (
    len(names), sum(1 for n in names if now[n][0]), len(new),
    sum(1 for n in names if not now[n][0] and old[n][0] is False)), flush=True)
print(P.result_line(P.make_result(len(names) - len(new), len(new), new[0] if new else None)), flush=True)
