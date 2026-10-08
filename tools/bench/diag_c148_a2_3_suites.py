# ---
# labview: none
# hardware: none
# evidence: tools/bench/selftest_t3_regress.py:24
# ---
r"""diag_c148_a2_3_suites - card 148-a2-3 step 2: plain selftest_t3_regress + the four suites that timed out at 240 s in 148-a1-1
(selftest_c134_1_a4, selftest_c134_2_regress, selftest_c_e3_suite, selftest_f2_suite), each compared with the PRE-FIX code.

WHAT EXISTED (reused, not rebuilt): selftest_c_e3_suite.py / selftest_f2_suite.py already run their children in the working tree
AND in a clean `git worktree add --detach <tmp> HEAD` and class each failure NEW or PRE-EXISTING; selftest_t3_regress.py has a
`--root <tree>` option for exactly this. HEAD = cycle 147's commit = the pre-cycle-148 bytes of every edited module (stage_prerun
61d6f590, guard_cycle c080fb7a, guard_write 391a8324, guard_assign b9dc09bb - checked below). Because every child is a SUBPROCESS
loading files from its own tree, a HEAD worktree is the only way the children themselves are pre-fix (diag_c148_a1_2_facts.md:22).
This script only reruns those existing tests; it edits nothing in the project (the worktree lives in %TEMP% and is removed).

LANES (run concurrently, each serial inside): NOW = t3_regress, c134_1_a4, c134_2_regress, c_e3_suite, f2_suite in the working
tree; HEAD = t3_regress --root <wt>, c134_1_a4, c134_2_regress from the HEAD worktree (e3/f2 make their own HEAD worktree).
900 s cap per script (brief: --max-min 15 each). No child RESULT line is echoed raw (bgrun would judge the log by it).

PREDICTION: t3_regress now = 7/3 failing exactly {c133_1_fsroutes, rebase_uidreuse_c143_4, stage_prerun_c106e}; for t3_regress,
c134_1_a4 and c134_2_regress the failing-child set NOW == the set at HEAD; c_e3_suite and f2_suite report 0 NEW failures.
Gates: one per script ("no NEW difference from pre-fix"). A NEW difference is reported, never fixed.
"""
import concurrent.futures as cf
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P   # noqa: E402

CAP = 900
PRE = {"tools/stage_prerun.py": "61d6f590", "tools/hooks/guard_cycle.py": "c080fb7a",
       "tools/hooks/guard_write.py": "391a8324", "tools/hooks/guard_assign.py": "b9dc09bb"}
NOW_LANE = [("t3_regress", ["selftest_t3_regress.py"]), ("c134_1_a4", ["selftest_c134_1_a4.py"]),
            ("c134_2_regress", ["selftest_c134_2_regress.py"]), ("c_e3_suite", ["selftest_c_e3_suite.py"]),
            ("f2_suite", ["selftest_f2_suite.py"])]


def run(tree, name, argv):
    env = dict(os.environ)
    for k in ("CARD_ID", "CARD_LABVIEW", "BGRUN_LOG"):
        env.pop(k, None)
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-u", os.path.join(tree, "tools", "bench", argv[0])] + argv[1:], cwd=tree, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=CAP)
        out, rc = (r.stdout or "") + (r.stderr or ""), r.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = str(e.stdout or ""), "TIMEOUT"
    res = P.parse_result_line(out)
    return {"name": name, "tree": "HEAD" if tree != ROOT else "NOW", "rc": rc, "sec": round(time.time() - t0),
            "gates": None if res is None else "%s %s/%s" % (res.get("status"), (res.get("gates") or {}).get("pass"),
                                                             (res.get("gates") or {}).get("fail")), "out": out}


def failing_children(name, out):
    if name == "t3_regress":
        return sorted(m.group(1) for m in re.finditer(r"^REGRESS (\S+(?: selftest)?) \| rc (\S+) \| (.*?) \| fails", out, re.M)
                      if not (m.group(2) == "0" and m.group(3).startswith("PASS")))
    if name.startswith("c134"):
        return sorted(m.group(1) for m in re.finditer(r"^  FAIL  (.+?) rc=", out, re.M))
    return sorted(m.group(1) for m in re.finditer(r"^  (?:NEW-FAIL|FAIL \(new test\))\s+(\S+)", out, re.M))


def lane(tree, items):
    return [run(tree, n, a) for n, a in items]


def main():
    wt = tempfile.mkdtemp(prefix="c148a23head_")
    subprocess.run(["git", "worktree", "add", "--detach", wt, "HEAD"], cwd=ROOT, capture_output=True, timeout=300)
    for rel, want in PRE.items():
        got = hashlib.md5(open(os.path.join(wt, rel), "rb").read()).hexdigest()[:8]
        print("  FACT  HEAD worktree %s md5 %s (%s)" % (rel, got, "pre-fix" if got == want else "NOT the pre-fix bytes " + want),
              flush=True)
    head_items = [("t3_regress", ["selftest_t3_regress.py", "--root", wt])] + NOW_LANE[1:3]
    try:
        with cf.ThreadPoolExecutor(2) as ex:
            fn, fh = ex.submit(lane, ROOT, NOW_LANE), ex.submit(lane, wt, head_items)
            now, head = fn.result(), fh.result()
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", wt], cwd=ROOT, capture_output=True, timeout=300)
        shutil.rmtree(wt, ignore_errors=True)
    hmap = {h["name"]: h for h in head}
    ok, bad = 0, []
    for r in now + head:
        print("  RUN  %-5s %-15s rc=%s %ss result=%s" % (r["tree"], r["name"], r["rc"], r["sec"], r["gates"]), flush=True)
        for ln in r["out"].splitlines():
            if ln.startswith(("REGRESS ", "  FAIL  ", "  NEW-FAIL", "  PRE-EXISTING", "  FAIL (new")) or re.match(r"^\d+ self-tests:", ln):
                print("     | " + ln.strip()[:260], flush=True)
    for r in now:
        fc = failing_children(r["name"], r["out"])
        if r["name"] in hmap:
            hc = failing_children(r["name"], hmap[r["name"]]["out"])
            same = fc == hc and r["rc"] != "TIMEOUT" and hmap[r["name"]]["rc"] != "TIMEOUT"
            print("  CMP  %s failing now %s | at HEAD %s -> %s" % (r["name"], fc, hc, "SAME" if same else "DIFFERENT"), flush=True)
        else:
            same = not fc and r["rc"] != "TIMEOUT"
            print("  CMP  %s NEW failures %s -> %s" % (r["name"], fc, "none" if same else "NEW"), flush=True)
        if same:
            ok += 1
        else:
            bad.append(r["name"])
    print(P.result_line(P.make_result(ok, len(bad), ("new difference from pre-fix: " + ", ".join(bad)) if bad else None)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
