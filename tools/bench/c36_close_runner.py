r"""c36_close_runner.py - ONE runner, ONE notification, for cycle 36's closing material work.

Chained (CLAUDE.md section 3 "one LabVIEW batch = one runner = one notification"):
  STEP 1  re-run tools/bench/selftest_bgrun_final_line.py (the bgrun + wait_logs repair self-test),
          after its own cp949 crash was fixed. Its 8 gates are the acceptance for both repairs.
  STEP 2  T1, the DISCRIMINATING TEST the hypothesis review asked for
          (archive/peer/2026-09-18-c36-bgrun-finalline-selftest.md section 4): kill the RUNNER
          process itself from outside (taskkill /F, no /T) and see whether a terminal line appears.
          The reviewer predicts NO - `try/finally` does not run on TerminateProcess - which would
          mean the repair closes the internal-exception class but NOT the class that produced the
          three real END-less logs. This step is a MEASUREMENT, not a gate: it prints OBSERVED
          lines and never FAILs, because which repair follows from it is a judgement call.
  STEP 3  py tools/doc_ingest.py --cycle 36, through its OWN nested bgrun so its output lands in a
          log name tools/logclass.py registers as machinery (a document quoted verbatim carries
          `FAIL` and `rc=` text that would otherwise be scanned as this runner's failure).

No LabVIEW, no .vi, no motor, no camera. Nothing under user.lib is touched.

PRIOR ART: tools/bench/selftest_bgrun_fail_scan.py (bgrun's inner-failure regex only, no terminal-line
assertion), tools/bench/repair_c36_selftest.log (this cycle's census of the four END-less logs),
tools/wait_logs.py (the waiter, repaired here). No runner with these three steps exists.

PREDICTION CONTRACT:
  S1  the self-test prints "=== selftest_bgrun_final_line: 8 pass, 0 fail ===" and exits 0
  S2  (measurement, no gate) the externally killed runner's log ends at BGRUN START
  S3  doc_ingest --cycle 36 ends BGRUN END rc=0 and writes an archive/ingest/*.md newer than the run
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
INGEST_DIR = os.path.join(PROJECT, "archive", "ingest")
FAILS = 0


def safe(s):
    s = str(s).replace("rc=", "rc<eq>")
    return s.encode("ascii", errors="replace").decode("ascii")


def say(s):
    print(safe(s), flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def step1():
    global FAILS
    say("== STEP 1: selftest_bgrun_final_line ==")
    p = subprocess.run([sys.executable, "-u", os.path.join(HERE, "selftest_bgrun_final_line.py")],
                       cwd=PROJECT, capture_output=True)
    out = (p.stdout or b"").decode("utf-8", errors="replace")
    err = (p.stderr or b"").decode("utf-8", errors="replace")
    for ln in out.splitlines():
        say("   " + ln)
    if err.strip():
        say("   stderr: " + err.strip()[:400])
    m = re.search(r"=== selftest_bgrun_final_line: (\d+) pass, (\d+) fail ===", out)
    ok = bool(m) and m.group(2) == "0" and p.returncode == 0
    say("   S1 GATE %s  (exit %d, summary %s)" % ("PASS" if ok else "FAIL",
                                                  p.returncode, m.group(0) if m else "<none>"))
    if not ok:
        FAILS += 1


def step2():
    say("== STEP 2: T1 external kill of the RUNNER process (measurement, not a gate) ==")
    tmp = tempfile.mkdtemp(prefix="extkill_")
    logp = os.path.join(tmp, "probe_extkill.log")
    child_pids = []
    try:
        r = subprocess.Popen([sys.executable, os.path.join(PROJECT, "tools", "bgrun.py"),
                              "--max-min", "60", "--log", logp, "--",
                              sys.executable, "-c", "import time;print('a',flush=True);time.sleep(600)"],
                             cwd=PROJECT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5.0)
        q = subprocess.run(["wmic", "process", "where", "ParentProcessId=%d" % r.pid,
                            "get", "ProcessId"], capture_output=True, text=True, errors="replace")
        child_pids = re.findall(r"\b(\d{2,})\b", q.stdout or "")
        k = subprocess.run(["taskkill", "/F", "/PID", str(r.pid)],
                           capture_output=True, text=True, errors="replace")
        time.sleep(2.0)
        with open(logp, "r", encoding="utf-8", errors="replace") as f:
            ls = [x.rstrip("\n") for x in f if x.strip()]
        terminal = [x for x in ls if x.startswith("BGRUN END") or x.startswith("BGRUN TIMEOUT")]
        say("   OBSERVED taskkill on runner pid %d -> exit %d" % (r.pid, k.returncode))
        say("   OBSERVED log lines=%d last=%r" % (len(ls), ls[-1][:120] if ls else "<empty>"))
        say("   OBSERVED terminal line present: %s" % bool(terminal))
        say("   OBSERVED reviewer's prediction was 'no terminal line'; match=%s" % (not terminal))
    finally:
        for pid in child_pids:
            subprocess.run(["taskkill", "/F", "/T", "/PID", pid],
                           capture_output=True, text=True, errors="replace")
        say("   CLEANUP orphan child pids terminated: %s" % (child_pids or "none found"))
        shutil.rmtree(tmp, ignore_errors=True)


def step3():
    global FAILS
    say("== STEP 3: doc_ingest --cycle 36 (nested bgrun, machinery-classified log) ==")
    before = {}
    for n in os.listdir(INGEST_DIR):
        p = os.path.join(INGEST_DIR, n)
        before[n] = (md5(p), os.path.getmtime(p))
    # An ingest archive is named by DATE, and today's file already holds cycle 34's pass. Copy it
    # aside FIRST so an overwrite cannot destroy it (rule 4: nothing is deleted, only moved); the
    # copy is removed again if the original turns out untouched.
    today = time.strftime("%Y-%m-%d")
    guard_src = os.path.join(INGEST_DIR, "%s-ingest-%s.md" % (today, today))
    guard_cpy = os.path.join(INGEST_DIR, "%s-ingest-%s-cycle34.md" % (today, today))
    guarded = os.path.exists(guard_src) and not os.path.exists(guard_cpy)
    if guarded:
        shutil.copy2(guard_src, guard_cpy)
        say("   guarded existing %s -> %s" % (os.path.basename(guard_src), os.path.basename(guard_cpy)))
    logp = os.path.join(PROJECT, "tools", "bench", "doc_ingest_c36.log")
    p = subprocess.run([sys.executable, os.path.join(PROJECT, "tools", "bgrun.py"),
                        "--material", "--max-min", "18", "--log", logp, "--",
                        sys.executable, "-u", os.path.join(PROJECT, "tools", "doc_ingest.py"),
                        "--cycle", "36"],
                       cwd=PROJECT, capture_output=True)
    with open(logp, "r", encoding="utf-8", errors="replace") as f:
        ls = [x.rstrip("\n") for x in f if x.strip()]
    say("   inner runner exit %d | log last: %s" % (p.returncode, ls[-1][:140] if ls else "<empty>"))
    changed = []
    for n in sorted(os.listdir(INGEST_DIR)):
        fp = os.path.join(INGEST_DIR, n)
        if n not in before or before[n][0] != md5(fp):
            changed.append(n)
    if guarded and os.path.exists(guard_cpy) and md5(guard_src) == md5(guard_cpy):
        os.remove(guard_cpy)                       # original untouched -> the guard copy is clutter
        say("   guard copy removed (original unchanged)")
        changed = [c for c in changed if c != os.path.basename(guard_cpy)]
    say("   ingest archives new/changed: %s" % (changed or "NONE"))
    ok = p.returncode == 0 and bool(changed)
    say("   S3 GATE %s" % ("PASS" if ok else "FAIL"))
    if not ok:
        FAILS += 1
    for n in changed:
        say("   --- head of %s ---" % n)
        with open(os.path.join(INGEST_DIR, n), "r", encoding="utf-8", errors="replace") as f:
            body = f.read()
        for ln in body.splitlines()[:12]:
            say("      " + ln[:160])


if __name__ == "__main__":
    step1()
    step2()
    step3()
    say("=== c36_close_runner: %d gate failure(s) ===" % FAILS)
    sys.exit(1 if FAILS else 0)
