r"""selftest_bgrun_reap.py - card 92-4: does a bgrun killed FROM OUTSIDE get its terminal line, and does nothing
else change?

PRIOR ART: selftest_bgrun_final_line.py (the runner's OWN exit paths, 4 cases), selftest_bgrun_fail_scan.py,
selftest_bgrun_jev_exempt.py (re-runs the other two + motor_fail_exit against BGRUN_UNDER_TEST). None of them kills
the runner from outside; that is the hole retrospective-cycle90 named (`diag_c90_t0stamp_scratch.log:17`).

PREDICTION CONTRACT (each gate FAILs loudly if the observation differs):
  R1  installed bgrun writes `BGRUN PID <own pid>` on the line after START; START itself still parses
      (logclass.last_bgrun_command == the command; protocol.BGRUN_START_RE matches)
  R2  a bgrun on a 60 s sleep child, `taskkill /T /F` on the RUNNER pid from outside -> runner gone, log has
      START + PID and NO END/TIMEOUT (the hole, reproduced)
  R3  bgrun_reap.reap(bench=tmp) -> that log gets exactly one `BGRUN KILLED (external) pid=<n>` line, last line
  R4  reap again -> nothing marked, still exactly one KILLED line (idempotent)
  R5  LIVE negative: a bgrun still running its sleep child is NOT marked (listed as open_live); it then ends by
      itself with `BGRUN END rc=0` and carries no KILLED line
  R6  a finished log (START/PID/END) is untouched
  R7  a pre-92-4 log (START, no PID line) is untouched and listed as undecidable
  R8  REAP AT BGRUN START: a dead-pid fixture in the REAL bench (tools/bench/selftest_bgrun_reap_fixture_killed.log)
      is marked by an ordinary bgrun run, which writes `BGRUN REAP marked KILLED: <fixture>`; fixture deleted after
  R9  audit_cycle.a2_state: "" / ended / killed / unfinished on four bodies
  R10 cycle_runner.bgrun_reap_hook(n, bench=tmp, runner_log) marks a dead-pid log and writes one `BGRUN-REAP |` line
  X1..X7 the existing self-tests still pass, each run as a subprocess against the installed bgrun:
      selftest_bgrun_final_line, selftest_bgrun_fail_scan, selftest_bgrun_jev_exempt, selftest_cycle_runner,
      selftest_audit_c7, selftest_audit_c4c_split, selftest_audit_cost_window
Only processes THIS test started are ever killed (card rule 2).
"""
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
TOOLS = os.path.join(PROJECT, "tools")
sys.path.insert(0, TOOLS)
import bgrun_reap  # noqa: E402
import logclass  # noqa: E402
import protocol  # noqa: E402

BGRUN = os.path.join(TOOLS, "bgrun.py")
PASS, FAIL, FIRST = 0, 0, None


def safe(s):
    return str(s).encode("ascii", errors="replace").decode("ascii")


def gate(name, ok, detail=""):
    global PASS, FAIL, FIRST
    if ok:
        PASS += 1
    else:
        FAIL += 1
        FIRST = FIRST or name
    print("  -> %s %s  %s" % ("PASS" if ok else "FAIL", name, safe(detail)), flush=True)


def lines(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return [ln.rstrip("\n") for ln in f if ln.strip()]


def pid_of(p):
    m = re.search(r"^BGRUN PID (\d+)", "\n".join(lines(p)) if os.path.exists(p) else "", re.M)
    return int(m.group(1)) if m else None


def start_bgrun(logp, minutes, cmd):
    return subprocess.Popen([sys.executable, BGRUN, "--max-min", str(minutes), "--log", logp, "--"] + cmd,
                            cwd=PROJECT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def wait_pid_line(logp, secs=20):
    t0 = time.time()
    while time.time() - t0 < secs:
        if os.path.exists(logp) and pid_of(logp):
            return pid_of(logp)
        time.sleep(0.2)
    return None


def alive(pid):
    q = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/NH"], capture_output=True, text=True, errors="replace")
    return str(pid) in (q.stdout or "")


def killed_count(p):
    return sum(1 for ln in lines(p) if ln.startswith("BGRUN KILLED (external) pid="))


def main():
    tmp = tempfile.mkdtemp(prefix="bgrunreap_")
    fixture = os.path.join(HERE, "selftest_bgrun_reap_fixture_killed.log")
    try:
        # R1 - PID line + START still parses
        l1 = os.path.join(tmp, "r1.log")
        subprocess.run([sys.executable, BGRUN, "--max-min", "1", "--log", l1, "--", sys.executable, "-c", "print('ok')"],
                       cwd=PROJECT, capture_output=True)
        ls = lines(l1)
        i_start = next((i for i, ln in enumerate(ls) if ln.startswith("BGRUN START")), -1)
        pid_ok = i_start >= 0 and i_start + 1 < len(ls) and re.match(r"^BGRUN PID \d+$", ls[i_start + 1]) is not None
        cmd_ok = logclass.last_bgrun_command(l1).startswith(sys.executable) and "-c" in logclass.last_bgrun_command(l1)
        re_ok = protocol.BGRUN_START_RE.search("\n".join(ls)) is not None
        gate("R1 PID line after START, START parses", pid_ok and cmd_ok and re_ok,
             "pid_line=%s cmd=%s re=%s | %s" % (pid_ok, cmd_ok, re_ok, ls[i_start + 1] if pid_ok else ls[:3]))

        # R2 - the hole: outside tree kill
        l2 = os.path.join(tmp, "r2_killed.log")
        p2 = start_bgrun(l2, 5, [sys.executable, "-c", "import time; time.sleep(60)"])
        pid2 = wait_pid_line(l2)
        k = subprocess.run(["taskkill", "/T", "/F", "/PID", str(p2.pid)], capture_output=True, text=True, errors="replace")
        t0 = time.time()
        while alive(p2.pid) and time.time() - t0 < 15:
            time.sleep(0.3)
        p2.wait(timeout=15)
        body2 = lines(l2)
        hole = pid2 == p2.pid and not alive(p2.pid) and not any(
            ln.startswith(("BGRUN END", "BGRUN TIMEOUT", "BGRUN KILLED")) for ln in body2)
        gate("R2 outside kill leaves START+PID, no END", hole,
             "pid line %s == popen %s, taskkill rc=%d, alive=%s, last=%s" % (pid2, p2.pid, k.returncode, alive(p2.pid),
                                                                            body2[-1][:60] if body2 else "<empty>"))

        # R5 setup first (live run must be running while R3 reaps)
        l5 = os.path.join(tmp, "r5_live.log")
        p5 = start_bgrun(l5, 5, [sys.executable, "-c", "import time; time.sleep(8)"])
        pid5 = wait_pid_line(l5)

        # R6/R7 fixtures
        l6 = os.path.join(tmp, "r6_done.log")
        with open(l6, "w", encoding="utf-8") as f:
            f.write("BGRUN START 2026-09-26 00:00:00 limit 5 min: py -u probe.py\nBGRUN PID %d\nx\nBGRUN END rc=0 after 1s\n" % p2.pid)
        l7 = os.path.join(tmp, "r7_old.log")
        with open(l7, "w", encoding="utf-8") as f:
            f.write("BGRUN START 2026-09-18 00:00:00 limit 5 min: py -u probe.py\nstep 3 still working\n")

        # R3 - reap the tmp bench
        r = bgrun_reap.reap(bench=tmp, who="selftest")
        marked = [os.path.basename(p) for p, _ in r["marked"]]
        b2 = lines(l2)
        gate("R3 reaper marks the killed log once, as last line", marked == ["r2_killed.log"] and killed_count(l2) == 1
             and b2[-1].startswith("BGRUN KILLED (external) pid=%d" % p2.pid),
             "marked=%s killed_lines=%d last=%s" % (marked, killed_count(l2), b2[-1][:90] if b2 else ""))
        r2 = bgrun_reap.reap(bench=tmp, who="selftest")
        gate("R4 idempotent", not r2["marked"] and killed_count(l2) == 1, "marked=%s count=%d" % (r2["marked"], killed_count(l2)))
        live_listed = [os.path.basename(p) for p, _ in r["open_live"]]
        gate("R5a live run not marked, listed open_live", "r5_live.log" in live_listed and killed_count(l5) == 0
             and pid5 == p5.pid, "open_live=%s pid=%s/%s" % (live_listed, pid5, p5.pid))
        gate("R6 finished log untouched", killed_count(l6) == 0 and lines(l6)[-1].startswith("BGRUN END"), lines(l6)[-1])
        und = [os.path.basename(p) for p in r["undecidable"]]
        gate("R7 pre-92-4 log undecidable, untouched", und == ["r7_old.log"] and lines(l7)[-1] == "step 3 still working",
             "undecidable=%s last=%s" % (und, lines(l7)[-1]))
        p5.wait(timeout=60)
        b5 = lines(l5)
        gate("R5b live run then ends by itself, no KILLED", b5[-1].startswith("BGRUN END rc=0") and killed_count(l5) == 0,
             b5[-1][:80])

        # R8 - reap at bgrun start, on the REAL bench through a fixture with the dead pid from R2
        with open(fixture, "w", encoding="utf-8") as f:
            f.write("BGRUN START 2026-09-26 00:00:00 limit 5 min: py -u tools/bench/selftest_fixture.py\nBGRUN PID %d\n"
                    "working\n" % p2.pid)
        l8 = os.path.join(tmp, "r8.log")
        subprocess.run([sys.executable, BGRUN, "--max-min", "1", "--log", l8, "--", sys.executable, "-c", "print('ok')"],
                       cwd=PROJECT, capture_output=True)
        b8 = "\n".join(lines(l8))
        fx = lines(fixture)
        fx_ok = killed_count(fixture) == 1 and fx[-1].startswith("BGRUN KILLED (external) pid=%d" % p2.pid)
        said = re.search(r"^BGRUN REAP marked KILLED: .*selftest_bgrun_reap_fixture_killed\.log pid=%d" % p2.pid,
                         b8, re.M) is not None
        ended = b8.rstrip().splitlines()[-1].startswith("BGRUN END rc=0") if b8.strip() else False
        gate("R8 bgrun start reaps the fixture and says so", fx_ok and said and ended,
             "fixture_ok=%s said=%s ended=%s | fixture last=%s" % (fx_ok, said, ended, fx[-1][:70] if fx else ""))
        os.remove(fixture)

        # R9 - audit A2 reading
        import audit_cycle
        a2 = audit_cycle.a2_state
        bodies = {"": "STALL: x\n", "ended": "BGRUN START x\nBGRUN END rc=0\n",
                  "killed": "BGRUN START x\nBGRUN PID 5\nBGRUN KILLED (external) pid=5 marked now by t: gone\n",
                  "unfinished": "BGRUN START x\nBGRUN PID 5\n"}
        got = {k: a2(v) for k, v in bodies.items()}
        gate("R9 audit_cycle.a2_state four states", all(got[k] == k for k in bodies), str(got))

        # R10 - cycle_runner hook
        import cycle_runner
        tb = os.path.join(tmp, "bench10")
        os.makedirs(tb)
        l10 = os.path.join(tb, "diag_x.log")
        with open(l10, "w", encoding="utf-8") as f:
            f.write("BGRUN START 2026-09-26 00:00:00 limit 5 min: py -u x.py\nBGRUN PID %d\n" % p2.pid)
        rl = os.path.join(tb, "runner.log")
        r10 = cycle_runner.bgrun_reap_hook(92, tb, rl)
        rls = lines(rl)
        gate("R10 cycle_runner hook marks + logs one BGRUN-REAP line",
             r10 is not None and len(r10["marked"]) == 1 and killed_count(l10) == 1
             and len([ln for ln in rls if ln.startswith("BGRUN-REAP |")]) == 1 and "diag_x.log" in rls[-1],
             rls[-1][:160] if rls else "<no runner log>")

        # X - existing self-tests, as subprocesses against the installed bgrun
        env = dict(os.environ, BGRUN_UNDER_TEST=BGRUN)
        for tag, name, want in (("X1", "selftest_bgrun_final_line.py", "pass, 0 fail"),
                                ("X2", "selftest_bgrun_fail_scan.py", None),
                                ("X3", "selftest_bgrun_jev_exempt.py", None),
                                ("X4", "selftest_cycle_runner.py", None),
                                ("X5", "selftest_audit_c7.py", None),
                                ("X6", "selftest_audit_c4c_split.py", None),
                                ("X7", "selftest_audit_cost_window.py", None)):
            t0 = time.time()
            w = subprocess.run([sys.executable, "-u", os.path.join(HERE, name)], cwd=PROJECT, capture_output=True,
                               text=True, encoding="utf-8", errors="replace", env=env, timeout=1200)
            so = (w.stdout or "") + (w.stderr or "")
            summ = [ln for ln in so.splitlines() if "===" in ln or ln.startswith("RESULT") or "pass" in ln.lower() and "fail" in ln.lower()]
            gate("%s %s rc 0" % (tag, name), w.returncode == 0,
                 "rc=%d %.0fs | %s" % (w.returncode, time.time() - t0, (summ[-1] if summ else so.strip().splitlines()[-1:])))
    finally:
        if os.path.exists(fixture):
            os.remove(fixture)
        shutil.rmtree(tmp, ignore_errors=True)
    print("=== selftest_bgrun_reap: %d pass, %d fail ===" % (PASS, FAIL), flush=True)
    print(protocol.result_line(protocol.make_result(PASS, FAIL, FIRST)), flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
