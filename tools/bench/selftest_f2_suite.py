# ---
# labview: none
# hardware: none
# ---
"""card chat-F2: the existing offline self-tests run in the WORKING TREE and in a clean HEAD worktree (%TEMP%, removed at
the end), each failure classed NEW (passes at HEAD, fails now) or PRE-EXISTING. Copied from selftest_c_e3_suite.py
(card chat-E3, the same comparison) with the list widened to what card chat-F2 touched: stagexec's own offline
self-test (`tools/stagexec.py selftest`, protocol.OFFLINE_SELFTESTS), the stagekit/stagexec self-tests listed in
OFFLINE_SELFTESTS or declared `labview: none`, the doc_lint self-test, and the chat-E3 hook/launch-gate pattern.
Read-declared tests outside OFFLINE_SELFTESTS (selftest_stagekit.py, selftest_hygiene_run.py) are NOT run here.
OFFLINE: no LabVIEW, no peer. PREDICTION: 0 NEW failures.
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
                 r"launch_gate|leg_guard|prerun_diag|protocol|report_gate|s5|stage_prerun|stagexec|stoprecord|x10_chat|"
                 r"case_frame_c124|fs_c126|census_predict|doc_lint_d1|op_hygiene)\w*\.py$")
EXTRA = [("stagexec.py selftest", [os.path.join("tools", "stagexec.py"), "selftest"])]


def run(tree, item):
    name, argv = item
    env = dict(os.environ)
    for k in ("CARD_ID", "CARD_LABVIEW", "BGRUN_LOG"):
        env.pop(k, None)
    try:
        r = subprocess.run([sys.executable, "-u"] + argv, cwd=tree, env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=600)
        out = (r.stdout or "") + (r.stderr or "")
        res = P.parse_result_line(out)
        failed = r.returncode != 0 or (res is not None and P.result_failed(res))
        tail = (res or {}).get("first_fail") or (out.strip().splitlines() or [""])[-1]
        return name, (not failed), str(tail)[:160]
    except subprocess.TimeoutExpired:
        return name, False, "TIMEOUT 600 s"


items = [(n, [os.path.join("tools", "bench", n)]) for n in sorted(os.listdir(HERE)) if PAT.search(n)] + EXTRA
names = [n for n, _a in items]
head = tempfile.mkdtemp(prefix="f2head_")
subprocess.run(["git", "worktree", "add", "--detach", head, "HEAD"], cwd=ROOT, capture_output=True)
try:
    with cf.ThreadPoolExecutor(6) as ex:
        now = dict((n, (ok, t)) for n, ok, t in ex.map(lambda it: run(ROOT, it), items))
        old = dict((n, (ok, t)) for n, ok, t in ex.map(lambda it: run(head, it) if os.path.exists(
            os.path.join(head, it[1][0])) else (it[0], None, "absent at HEAD"), items))
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
