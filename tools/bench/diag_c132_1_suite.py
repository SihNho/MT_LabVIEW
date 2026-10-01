r"""diag_c132_1_suite - card 132-1 (PD275(e)): run the full stage_prerun self-test set + this card's X10 / name-gate self-tests,
each in its own child process (offline, COM never opened by any of them - protocol.OFFLINE_SELFTESTS / c125_1), and print one
line per suite with its RESULT gate counts. PASS = every suite's RESULT status PASS. Prior art: each suite's own bgrun line.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c132_1_suite.log -- py -u tools/bench/diag_c132_1_suite.py"""
import glob, os, subprocess, sys                                                    # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                # noqa: E402
SUITES = sorted(os.path.basename(p) for p in glob.glob(os.path.join(B, "selftest_stage_prerun_*.py"))
                if not p.endswith("_mktrace.py")) + ["selftest_x10_c130_1.py", "selftest_x10_c132_1.py", "selftest_namegate_c132_1.py"]
res = []
for name in SUITES:
    try:
        p = subprocess.run([sys.executable, "-u", os.path.join(B, name)], cwd=ROOT, capture_output=True, text=True, timeout=500)
        out, rc = p.stdout, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT"
    rl = P.all_result_lines(out)
    r = rl[-1] if rl else {}
    g = r.get("gates") or {}
    ok = rc == 0 and r.get("status") == "PASS"
    res.append((name, ok))
    print("{0}  SUITE {1}: rc {2} status {3} gates {4}/{5} first_fail {6}".format(
        "PASS" if ok else "FAIL", name, rc, r.get("status"), g.get("pass"), g.get("fail"), str(r.get("first_fail"))[:300]), flush=True)
npass, nfail = sum(1 for _n, c in res if c), sum(1 for _n, c in res if not c)
print(P.result_line(P.make_result(npass, nfail, next((n for n, c in res if not c), None))), flush=True)
sys.stdout.flush()
os._exit(1 if nfail else 0)
