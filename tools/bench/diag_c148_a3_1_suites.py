# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c148_a2_3_facts.md:17
# ---
r"""diag_c148_a3_1_suites - card 148-a3-1 steps 0-2: retry of diag_c148_a2_3_suites.py (which crashed at :81 because the
`git worktree add` at :79 ran with rc/stderr discarded). Every subprocess here is checked (rc + stderr printed) and the
script STOPS at the first failed setup step.

WHAT EXISTED (reused): the four suites themselves - selftest_c134_1_a4.py / selftest_c134_2_regress.py (ROOT = their own
file's tree, so a copy in another tree runs that tree's children) and selftest_c_e3_suite.py / selftest_f2_suite.py (they
already compare the working tree with their own clean HEAD worktree, created unchecked at :46 / :53 and removed in finally).
STEP 0: LabVIEW process count (tasklist), git worktree list. STEP 1: remove the stale worktrees Temp/e3head_r96iqm4t and
Temp/f2head_1n3cihvt (git worktree remove --force, rc checked), git worktree prune, delete EMPTY Temp/c148a23head_* dirs.
STEP 2: pre-fix tree = `git worktree add --detach %TEMP%\c148a31_* HEAD` (HEAD 07202624 = cycle 147's commit), md5 of every
cycle-148-edited module there vs the HEAD blob vs disk. Lanes NOW (main tree) and PRE (that worktree) run concurrently, each
serial: c134_1_a4, c134_2_regress, c_e3_suite, f2_suite, cap 1500 s each (brief: >= 15 min). Worktrees made by the e3/f2
suites (e3head_*/f2head_*) and my own are removed at the very end (never mid-run: the other lane may be using one).
Child RESULT lines are never echoed raw (bgrun would judge this log by them).
GREEN per suite = NOW rc 0 with RESULT PASS, OR no child failing NOW that does not fail PRE (NEW = NOW-failing minus
PRE-failing, or a TIMEOUT). Children failing only PRE are listed, not counted.
PREDICTION: 4/4 green; c_e3/f2 report 0 NEW; c134_1/c134_2 failing sets NOW == PRE.
    py tools/bgrun.py --material --max-min 80 --log tools/bench/diag_c148_a3_1_suites.log -- py -u tools/bench/diag_c148_a3_1_suites.py
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

CAP = 1500
TEMP = tempfile.gettempdir()
STALE = ["e3head_r96iqm4t", "f2head_1n3cihvt"]
EDITED = ["tools/stage_prerun.py", "tools/hooks/guard_cycle.py", "tools/hooks/guard_write.py", "tools/hooks/guard_assign.py",
          "tools/bench/selftest_assign_flow.py", "tools/bench/selftest_c147_b1_2.py", "tools/bench/selftest_chat_p1.py",
          "tools/bench/selftest_chat_p2.py", "tools/bench/selftest_guard_cycle_offline.py",
          "tools/bench/selftest_guard_cycle_rerun.py", "tools/bench/selftest_guard_session.py",
          "tools/bench/selftest_guard_session_pairing.py"]
SUITES = ["selftest_c134_1_a4.py", "selftest_c134_2_regress.py", "selftest_c_e3_suite.py", "selftest_f2_suite.py"]


class Stop(Exception):
    pass


def sh(argv, what, timeout=300, ok_rc=(0,), binary=False):
    r = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout)
    err = r.stderr.decode("utf-8", "replace").strip()
    print("  STEP  %s rc=%s%s" % (what, r.returncode, (" stderr=%r" % err[:400]) if err else ""), flush=True)
    if r.returncode not in ok_rc:
        raise Stop("%s rc %s: %s" % (what, r.returncode, err[:200]))
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def labview_count():
    out = sh(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe", "/NH"], "tasklist LabVIEW.exe", timeout=20)
    n = sum(1 for ln in out.splitlines() if ln.lower().startswith("labview.exe"))
    print("  FACT  LabVIEW processes: %d" % n, flush=True)
    return n


def worktrees(tag):
    out = sh(["git", "worktree", "list", "--porcelain"], "git worktree list (%s)" % tag)
    paths = [ln[9:].strip() for ln in out.splitlines() if ln.startswith("worktree ")]
    for p in paths:
        print("  WT    %s: %s" % (tag, p), flush=True)
    return paths


def mine(p):
    b = os.path.basename(p.replace("/", os.sep).rstrip(os.sep))
    in_temp = os.path.normcase(os.path.dirname(os.path.abspath(p))) == os.path.normcase(os.path.abspath(TEMP))
    return in_temp and re.match(r"^(e3head_|f2head_|c148a31_)", b) is not None


def run(tree, name):
    env = dict(os.environ)
    for k in ("CARD_ID", "CARD_LABVIEW", "BGRUN_LOG"):
        env.pop(k, None)
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-u", os.path.join(tree, "tools", "bench", name)], cwd=tree, env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=CAP)
        out, rc = (r.stdout or "") + (r.stderr or ""), r.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else str(e.stdout or "")), "TIMEOUT"
    res = P.parse_result_line(out)
    return {"name": name, "lane": "NOW" if tree == ROOT else "PRE", "rc": rc, "sec": round(time.time() - t0), "res": res,
            "out": out}


def failing(r):
    if r["name"].startswith("selftest_c134"):
        return set(m.group(1) for m in re.finditer(r"^  FAIL  (.+?) rc=", r["out"], re.M))
    return set(m.group(2) for m in re.finditer(r"^  (NEW-FAIL|PRE-EXISTING|FAIL \(new test\))\s+(\S+) \| now:", r["out"], re.M))


def summary(r):
    res = r["res"] or {}
    g = res.get("gates") or {}
    return "%s %s/%s" % (res.get("status"), g.get("pass"), g.get("fail")) if res else "no RESULT line"


def main():
    wt, made = None, False
    ok, bad = 0, []
    try:
        n0 = labview_count()
        if n0:
            raise Stop("LabVIEW running before the card (%d)" % n0)
        before = worktrees("before")
        for s in STALE:
            p = os.path.join(TEMP, s)
            if any(os.path.normcase(os.path.abspath(x)) == os.path.normcase(p) for x in before):
                sh(["git", "worktree", "remove", "--force", p], "git worktree remove --force %s" % s)
            else:
                print("  FACT  %s not in the worktree list" % s, flush=True)
            if os.path.isdir(p):
                shutil.rmtree(p)
                print("  STEP  rmtree leftover %s" % p, flush=True)
        sh(["git", "worktree", "prune"], "git worktree prune")
        for d in sorted(x for x in os.listdir(TEMP) if x.startswith("c148a23head_")):
            p = os.path.join(TEMP, d)
            if os.path.isdir(p) and not os.listdir(p):
                os.rmdir(p)
                print("  STEP  removed empty %s" % p, flush=True)
            else:
                print("  FACT  %s NOT empty - left in place" % p, flush=True)
        worktrees("after cleanup")
        head = sh(["git", "rev-parse", "HEAD"], "git rev-parse HEAD").strip()
        print("  FACT  HEAD %s" % head, flush=True)
        wt = tempfile.mkdtemp(prefix="c148a31_")
        sh(["git", "worktree", "add", "--detach", wt, "HEAD"], "git worktree add --detach %s HEAD" % wt, timeout=600)
        made = True
        for rel in EDITED:
            blob = sh(["git", "show", "HEAD:" + rel], "git show HEAD:%s" % rel, binary=True)
            bm = hashlib.md5(blob).hexdigest()[:8]
            crlf = hashlib.md5(blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest()[:8]
            pw = os.path.join(wt, rel)
            wm = hashlib.md5(open(pw, "rb").read()).hexdigest()[:8] if os.path.isfile(pw) else "ABSENT"
            dm = hashlib.md5(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:8]
            print("  PRE   %-48s tree %s | HEAD blob %s (crlf %s) | disk %s -> %s" % (
                rel, wm, bm, crlf, dm, "pre-fix" if wm in (bm, crlf) and wm != dm else "CHECK"), flush=True)
            if wm not in (bm, crlf):
                raise Stop("pre-fix tree %s is not the HEAD blob" % rel)
        for s in SUITES:
            if not os.path.isfile(os.path.join(wt, "tools", "bench", s)):
                raise Stop("suite %s absent in the pre-fix tree" % s)
        with cf.ThreadPoolExecutor(2) as ex:
            fn = ex.submit(lambda: [run(ROOT, s) for s in SUITES])
            fp = ex.submit(lambda: [run(wt, s) for s in SUITES])
            now, pre = fn.result(), fp.result()
        pmap = dict((r["name"], r) for r in pre)
        for r in now + pre:
            print("  RUN   %-4s %-28s rc=%s %5ss result=%s" % (r["lane"], r["name"], r["rc"], r["sec"], summary(r)), flush=True)
            for ln in r["out"].splitlines():
                if ln.startswith(("  FAIL  ", "  SKIP  ", "  NEW-FAIL", "  PRE-EXISTING", "  FAIL (new", "  STOP  ")) or \
                        re.match(r"^\d+ self-tests:", ln):
                    print("     | " + ln.strip()[:300], flush=True)
        for r in now:
            p = pmap[r["name"]]
            fnow, fpre = failing(r), failing(p)
            new = sorted(fnow - fpre)
            to = r["rc"] == "TIMEOUT" or p["rc"] == "TIMEOUT"
            green0 = r["rc"] == 0 and (r["res"] or {}).get("status") == "PASS"
            green = green0 or (not new and not to)
            print("  CMP   %-28s NOW fail %s | PRE fail %s | NEW %s | pre-only %s%s -> %s" % (
                r["name"], sorted(fnow), sorted(fpre), new, sorted(fpre - fnow), " | TIMEOUT" if to else "",
                "GREEN" if green else "NEW DIFFERENCE"), flush=True)
            if green:
                ok += 1
            else:
                bad.append(r["name"])
    except Stop as e:
        print("  STOP  %s" % e, flush=True)
        bad.append("setup: %s" % e)
    finally:
        try:
            for p in worktrees("end, before removal"):
                if mine(p):
                    sh(["git", "worktree", "remove", "--force", p], "git worktree remove --force %s" % os.path.basename(p))
            sh(["git", "worktree", "prune"], "git worktree prune")
            if wt and os.path.isdir(wt):
                shutil.rmtree(wt, ignore_errors=True)
            worktrees("final")
            labview_count()
        except Stop as e:
            print("  STOP  cleanup: %s" % e, flush=True)
            bad.append("cleanup: %s" % e)
    print(P.result_line(P.make_result(ok, len(bad), ("; ".join(bad))[:190] if bad else None)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
