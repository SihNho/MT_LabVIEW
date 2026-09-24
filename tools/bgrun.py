"""bgrun.py — the ONLY allowed way to run a LabVIEW-touching command in the background.

    py tools/bgrun.py --max-min 15 --log tools/bench/xyz.log -- py -u tools/recipes/foo.py --arg

Runs the command as a child (own process group, no console window), streams its stdout/stderr
line-by-line into --log (unbuffered, so a monitor sees progress), and KILLS THE WHOLE TREE when
--max-min elapses. Always ends by writing one of
    BGRUN END rc=<n> after <s>s
    BGRUN TIMEOUT killed after <s>s (limit <m> min)
to the log and stdout — so silence can never mean "still running" for longer than the limit.
"Always" has had a MECHANISM only since 2026-09-18: the `try/finally` at the bottom of this file plus
`_write_final`, which covers the exit paths the three explicit `out(...)` calls do not (see `_STATE`).
The PreToolUse guard (tools/hooks/guard_bash.py) refuses a backgrounded LabVIEW command that does
not go through this runner (user, 2026-09-05: a hung discovery job sat 3 h 48 min unnoticed).
"""
import argparse
import os
import re
import subprocess
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # peer answers carry non-cp949 chars (crash 2026-09-06)
except Exception:
    pass
import threading
import time

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT, "tools"))
import logclass  # noqa: E402  - ONE definition of "is this log the machinery watching the build?"
import protocol  # noqa: E402  - C6: the script's own RESULT line is the verdict (docs/session-protocol.md)


DETACHED_PROCESS = 0x00000008
CREATE_BREAKAWAY_FROM_JOB = 0x01000000
DETACH_ENV = "BGRUN_DETACHED"

# THE MECHANISM BEHIND THE DOCSTRING'S "ALWAYS" (repair, 2026-09-18, cycle 36; 5th occurrence of the
# OPEN-54 class). Until now the guarantee at the top of this file - "Always ends by writing BGRUN END /
# BGRUN TIMEOUT" - had NO mechanism: the file contained no try/finally and no atexit, so every exit path
# that was not one of the three explicit `out(...)` calls left a log whose last line was START. Four such
# logs are on disk (diag_fstunnelterm_v2_panelcost, p2_open_copy, prose_cycle25, wait_runner_exit), and a
# START-only log is read by every waiter in the fleet - wait_logs.py, audit_cycle's in-flight test, a
# material session holding its turn open - as "still running", forever. The failing paths are ordinary:
# a command whose executable does not exist (Popen raises FileNotFoundError), an unwritable log path, a
# KeyboardInterrupt, any exception in this runner's own code.
# `_STATE["final"]` is set by the three terminal `out(...)` lines; `_STATE["delegated"]` marks the ONE
# path that must NOT get a terminal line here - a successful `--detach`, where the detached copy owns the
# log and writing END in the parent would tell a waiter the job finished the moment it started.
_STATE = {"log": None, "final": False, "delegated": False}


def _write_final(line):
    """Append the terminal line on a path main() never reached; never raise doing it.

    Non-fatal by construction: a finalizer that itself throws re-creates the very hole it closes.
    The stdout echo is skipped in the DETACHED copy, whose stdout IS this same log file.
    """
    _STATE["final"] = True
    logp = _STATE.get("log")
    if logp:
        try:
            with open(logp, "a", encoding="utf-8", errors="replace") as f:
                f.write(line)
                f.flush()
        except Exception:
            pass
    if os.environ.get(DETACH_ENV) != "1":
        try:
            sys.stdout.write(line)
            sys.stdout.flush()
        except Exception:
            pass


def relaunch_detached(logp):
    """Re-exec THIS runner so it survives its caller's exit (cycle 15 deliverable 1).

    Why: twice on 2026-09-16 a sub-agent backgrounded bgrun and then returned; the child
    (peer.ps1 -> codex) died with it and the log held START with no END. CREATE_NEW_PROCESS_GROUP
    |CREATE_NO_WINDOW (the old flags) does NOT detach: the child keeps the caller's console and,
    more importantly, stays inside whatever Windows JOB OBJECT the agent's shell belongs to, and a
    job with JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE takes every member down when the shell exits.

    So the deadline, the tree-kill and the END/TIMEOUT line all move into a SECOND copy of this
    process that is (a) DETACHED_PROCESS - no inherited console, (b) CREATE_NEW_PROCESS_GROUP - no
    inherited Ctrl+C/Ctrl+Break, (c) CREATE_BREAKAWAY_FROM_JOB where the job permits it, which is
    what actually escapes the kill-on-close. Breakaway raises ACCESS_DENIED when the job forbids
    it, so it is TRIED first and the flags fall back without it. stdin/stdout/stderr go to DEVNULL:
    the detached copy writes only the log, which is where an unattended run is read from anyway.
    """
    env = dict(os.environ, **{DETACH_ENV: "1"})
    argv = [sys.executable, os.path.abspath(__file__)] + sys.argv[1:]
    base = DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    last = None
    # codex, archive/peer/2026-09-17-bgrun-detach-deadline.md section 3: sending the DETACHED COPY's own
    # stderr to DEVNULL loses every failure it can have BEFORE it writes START (bad log path, import
    # error, missing interpreter) - and the caller has already returned 0, so nothing anywhere records
    # it. Its streams therefore go to the LOG, which is the one place an unattended run is read from.
    sink = open(logp, "a", encoding="utf-8", buffering=1)
    for flags, how in ((base | CREATE_BREAKAWAY_FROM_JOB, "breakaway"), (base, "detached")):
        try:
            p = subprocess.Popen(argv, cwd=PROJECT, env=env, creationflags=flags,
                                 stdin=subprocess.DEVNULL, stdout=sink,
                                 stderr=subprocess.STDOUT, close_fds=False)
        except OSError as e:                       # ACCESS_DENIED when the job forbids breakaway
            last = e
            continue
        # `mode=detached` means CREATE_BREAKAWAY_FROM_JOB was REFUSED, i.e. the runner is still inside
        # the caller's job and a kill-on-close job can still take it down - the very failure this flag
        # exists to stop. The mode is on the line so a log can be read for it, never assumed.
        line = f"BGRUN DETACH pid={p.pid} mode={how} log={logp}\n"
        sys.stdout.write(line)
        sys.stdout.flush()
        sink.write(line)
        sink.flush()
        sink.close()
        return 0
    sink.close()
    sys.stderr.write(f"BGRUN DETACH FAILED: {last}\n")
    return 125


JEV_SCRIPT_RE = re.compile(r"(?:^|[\\/])tools[\\/](?:jev\w*|bench[\\/]jev_\w*)\.py$", re.I)


def is_jev_command(cmd):
    """True when the script this command runs (its FIRST `.py` token) is a Jev script. Never the log name."""
    script = next((t for t in cmd if t.lower().endswith(".py")), None)
    return bool(script and JEV_SCRIPT_RE.search(script.strip("\"'")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-min", type=float, required=True, help="hard deadline in minutes")
    ap.add_argument("--log", required=True, help="log file (appended)")
    ap.add_argument("--detach", action="store_true",
                    help="return immediately; the runner re-execs itself detached from this caller "
                         "so the caller's exit cannot kill the child. Deadline/END line unchanged.")
    ap.add_argument("--material", action="store_true",
                    help="declare this a MATERIAL-session run (tools/hooks/guard_bash.py MARKER_RE). "
                         "Purely a declaration - it changes nothing here. It exists because the older "
                         "`MATERIAL=1 py ...` env prefix cannot be permitted under `claude -p`: an allow "
                         "rule never matches past an assignment of a non-known-safe variable, so the "
                         "prefixed command matches no rule and is auto-denied. As a flag it lands inside "
                         "the existing Bash(py tools/*) rule. See guard_bash.py MARKER_RE for the measurement.")
    ap.add_argument("cmd", nargs=argparse.REMAINDER, help="-- then the command")
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd:
        ap.error("no command after --")
    logp = os.path.join(PROJECT, a.log) if not os.path.isabs(a.log) else a.log
    os.makedirs(os.path.dirname(logp), exist_ok=True)
    _STATE["log"] = logp
    if a.detach and os.environ.get(DETACH_ENV) != "1":
        rc = relaunch_detached(logp)
        # Only a SUCCESSFUL detach delegates the terminal line to the detached copy. A FAILED one
        # (rc=125, breakaway and plain detach both refused) leaves nobody to write it, so it falls
        # through to the finalizer like any other failure.
        _STATE["delegated"] = (rc == 0)
        return rc
    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0)
    t0 = time.time()
    with open(logp, "a", encoding="utf-8") as log:
        # In the DETACHED copy sys.stdout IS this same log file (relaunch_detached points it there so a
        # pre-START crash still leaves a trace), so echoing would double every line.
        echo = os.environ.get(DETACH_ENV) != "1"

        def out(line):
            log.write(line); log.flush()
            if line.startswith("BGRUN END") or line.startswith("BGRUN TIMEOUT"):
                _STATE["final"] = True     # the finalizer must not append a SECOND terminal line
            if echo:
                # NON-FATAL ECHO (repair, 2026-09-18). The echo is a convenience; the log is the record.
                # sys.stdout here can be a cp949 console (the reconfigure at import is itself in a try),
                # so one non-cp949 character in a child's output used to raise UnicodeEncodeError out of
                # the pump thread or out of main - killing the runner between START and END.
                try:
                    sys.stdout.write(line); sys.stdout.flush()
                except Exception:
                    pass
        out(f"BGRUN START {time.strftime('%Y-%m-%d %H:%M:%S')} limit {a.max_min} min: {' '.join(cmd)}\n")
        # BGRUN_LOG - the ONE line that makes audit_cycle's own-log exemption reachable (STATUS OPEN 42;
        # archive/peer/2026-09-18-c20-audit-a1-motorgate-{codex,opus}.md, both ANSWERED, `device-failed`
        # threshold 1). `audit_cycle.py:242` has read `os.environ.get("BGRUN_LOG","")` since it was written, to
        # list - rather than FAIL - the log of the runner the audit is itself running inside (that log cannot
        # carry its END line yet). Nothing ever set it: a child inherits the parent's environment, and this
        # Popen passed no `env=`, so `in_flight` at `:247` was unreachable code and every audit run under bgrun
        # reported its own in-flight log as an unfinished run - which cost cycle 35 a $2.9750 review.
        # ABSOLUTE path on purpose; the audit compares basenames, and an absolute value is also usable by any
        # other child that wants to name the log it is writing into.
        child_env = dict(os.environ, BGRUN_LOG=logp)
        p = subprocess.Popen(cmd, cwd=PROJECT, env=child_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="replace", bufsize=1, creationflags=flags)
        done = threading.Event()

        # A RUNNER MUST NOT REPORT SUCCESS OVER AN INNER FAILURE (device for the `unreported-fact` slug,
        # 2026-09-16). `probe_relocate_route_run2.log:25`: the outer PowerShell wrapper ended rc=0 while the probe
        # it wrapped printed `probe exit=1`, so a failed batch looked like a passed one - and everything measured
        # through such a runner is void without anyone noticing. A wrapper script that forgets to propagate is the
        # normal case, not the exception, so the detection lives HERE rather than in each scratch runner.
        # NARROWED 2026-09-16 (STATUS OPEN 6): the summary-line alternative used to be `=== .*?\bfail(?:ed|ure)?\b`,
        # which matched the WORD, so a passing summary - "=== OpOwnerChain_v1 build: 20 pass, 0 fail ===" - was
        # reported as an inner failure and every passing recipe ended rc=1. It now requires a NON-ZERO count
        # immediately before `fail`. The other two alternatives are unchanged.
        # A REVIEWER'S PROSE IS NOT A BUILD'S OUTPUT (STATUS OPEN 8, fixed 2026-09-16). `retro_cycle11.log:102`
        # ended `BGRUN END rc=1 (inner failure)` because the peer's own answer QUOTED the regex bug of OPEN 6:
        # "...was recorded by `bgrun` as `rc=1` because '0 fail' matched the failure regex". The scan read the
        # reviewer's sentence as the run's result. `tools/logclass.py` has solved exactly this class of error for
        # guard_peer and audit_cycle since 2026-09-16 ("evidence about a cycle, never the thing under test") and
        # its docstring already says review logs "must not be scanned for failure strings"; bgrun was the one
        # scanner that never got the exclusion. The OUTCOME line still decides: a review dispatch that genuinely
        # exits non-zero is still reported by `p.wait()`, which this does not touch.
        # DEVICE FOR `device-failed` ROUND 5 (docs/violation-decisions.md, 2026-09-17 03:38). The previous scan knew
        # exactly three shapes - `rc=<n>`/`exit=<n>`, `**FAIL**`, and the `=== N fail ===` summary - and the fleet's
        # OTHER gate-printing convention, `  -> FAIL  <gate name>`, was in none of them. So
        # `tools/bench/diag_stop_condterm_panel.log:15-18` printed a failed gate AND a `SUMMARY 3/4 gates pass`
        # line and still ended `BGRUN END rc=0`: a diagnostic whose prediction failed looked like one that passed,
        # which is the same blindness the round-1 device was built to remove. `^\s*(?:->\s*)?FAIL\b` is the form
        # audit_cycle/guard_peer already match, so the three scanners now agree. Review logs stay excluded through
        # logclass.is_review_log (a reviewer quoting "-> FAIL" is evidence, never the thing under test).
        # Self-test: tools/bench/selftest_bgrun_fail_scan.py (the literal line above -> rc=1; a PASS-only log -> rc=0).
        # MOTOR VOCABULARY (cycle 69, device-failed repair of retrospective-cycle68): pi_testmove_20260923e.log:23
        # `RESULT: NOT at target`, :34 `RESULT: REJECTED BY THE CONTROLLER - ERR 216`, :22 `ERR?=216` - and the run
        # ended `BGRUN END rc=0` (:51). The senders now also print `FAIL:`; these alternatives catch the old wording
        # and any chain that drops it. Anchored: `RESULT:` at line start; ERR? only with a NON-ZERO number, so the
        # green logs' `ERR?=0` / `ERR? after SPA = 0` and the ALLOWED line's prose "answers ERR 7" do not match.
        # Self-test: tools/bench/selftest_motor_fail_exit.py. Keep identical to audit_cycle.FAILURE_RE's motor part.
        # JEV COMMANDS ARE EXEMPT FROM THE SCAN (device-failed repair, docs/violation-decisions.md
        # `## device-failed - 2026-09-24 03:53`; the other half of the user's 2026-09-22 "Jev는 면제"). A Jev
        # survey/classifier QUOTES failure lines by construction - its input is other runs' logs - and
        # tools/bench/device_value_a.log:1754 ended rc=1 on such a quote; the survey then mangled its own output
        # ("F-AIL", "rc:1") to get past the scan, hiding real failures from every later reader. SCOPED BY THE
        # COMMAND, NEVER BY THE LOG NAME: the exemption applies only when the SCRIPT this run executes (the first
        # `.py` token of the command) is `tools/jev*.py` or `tools/bench/jev_*.py`. The process's own exit code
        # still decides rc. Self-test: tools/bench/selftest_bgrun_jev_exempt.py.
        # ==== THE BODY SCAN ABOVE IS REMOVED (session protocol v1, C6; user-approved 2026-09-24 "모든 영역에 JSON").
        # The history paragraphs are kept because they say WHY each alternative once existed; none of them runs now.
        # The scan read quoted prose as failures (device_value_a/b, dryrun_l7_r_address, `rc=2` in passing
        # self-tests: cycles 70, 71, 73) and every repair widened or narrowed one regex. The verdict is now the
        # SCRIPT'S OWN: its `RESULT {...}` line(s) (tools/protocol.py) - status != PASS or gates.fail > 0 on ANY of
        # them => rc=1 - and, when it prints none, the exit code alone. stagekit prints RESULT from its gate counts
        # on every exit path; motor_gate.py prints one per call, so a rejected move is still caught.
        # Review logs and Jev commands keep their exemption: a reviewer or a Jev survey may QUOTE a RESULT line.
        read_result = not logclass.is_review_log(logp) and not is_jev_command(cmd)
        results = []

        def pump():
            for line in p.stdout:
                out(line)
                if read_result and line.startswith(protocol.RESULT_PREFIX + "{"):
                    results.append(line)
            done.set()
        threading.Thread(target=pump, daemon=True).start()
        deadline = t0 + a.max_min * 60
        while not done.wait(timeout=2):
            if time.time() > deadline:
                # "killed" USED TO BE UNVERIFIED (codex, archive/peer/2026-09-17-bgrun-detach-deadline.md,
                # its single strongest point): subprocess.run does not raise on a non-zero exit, so the
                # taskkill result was discarded and the TIMEOUT line was written unconditionally -
                # a failed kill and a successful one produced the identical log. Both the kill's own
                # result and an after-the-fact existence check on the PID are now ON THE LINE.
                k = subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)],
                                   capture_output=True, text=True, errors="replace")
                time.sleep(0.5)
                q = subprocess.run(["tasklist", "/FI", f"PID eq {p.pid}", "/NH"],
                                   capture_output=True, text=True, errors="replace")
                alive = str(p.pid) in (q.stdout or "")
                # stdout and stderr SEPARATELY (codex, archive/peer/2026-09-17-bgrun-treekill-orphan.md:
                # `k.stdout or k.stderr` hides a per-process failure whenever ANY process was killed
                # successfully - "mixed success" reads exactly like total success).
                out(f"BGRUN KILL taskkill rc={k.returncode} pid={p.pid} still_listed={alive}\n"
                    f"BGRUN KILL stdout: {(k.stdout or '').strip()[:600]!r}\n"
                    f"BGRUN KILL stderr: {(k.stderr or '').strip()[:600]!r}\n")
                out(f"BGRUN TIMEOUT killed after {time.time() - t0:.0f}s (limit {a.max_min} min)\n")
                return 124
        rc = p.wait()
        done.wait(timeout=5)                   # the pump may still hold the last lines (the RESULT line) at exit
        bad = [d for d in protocol.all_result_lines("".join(results)) if protocol.result_failed(d)]
        if rc == 0 and bad:
            d = bad[0]
            g = d.get("gates") or {}
            out(f"BGRUN END rc=1 after {time.time() - t0:.0f}s (RESULT: status={d.get('status')} "
                f"gates {g.get('pass')}/{g.get('fail')} first_fail={str(d.get('first_fail'))[:160]}; "
                f"the process itself said 0)\n")
            return 1
        out(f"BGRUN END rc={rc} after {time.time() - t0:.0f}s\n")
        return rc


if __name__ == "__main__":
    # try/finally, NOT atexit: atexit handlers do not run on os._exit or on a hard kill, and they run
    # AFTER interpreter shutdown has begun (open() and sys.stdout can already be unusable). A finally
    # block here covers every path this process can take by itself; the deadline/tree-kill path is the
    # one that covers the child. Self-test: tools/bench/selftest_bgrun_final_line.py (4 exit paths).
    _t_start = time.time()
    _rc = 125
    try:
        _rc = main()
    except SystemExit as e:                       # argparse's ap.error(): usually before the log is known
        _rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    except BaseException:                         # KeyboardInterrupt included - it is an exit path too
        import traceback
        _tb = traceback.format_exc(limit=4).strip().replace("\n", " | ")[-400:]
        _write_final("BGRUN END rc=125 after %.0fs (runner exception: %s)\n"
                     % (time.time() - _t_start, _tb))
        _rc = 125
    finally:
        if not _STATE["final"] and not _STATE["delegated"]:
            _write_final("BGRUN END rc=%s after %.0fs (runner exited with no terminal line)\n"
                         % (_rc, time.time() - _t_start))
    sys.exit(_rc)
