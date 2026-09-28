r"""finish_orphan_cycle.py - run the runner's END-OF-CYCLE hooks for a cycle whose runner process died while its
judgement session (claude -p) kept going (2026-09-28 09:12: every background task of the chat session, the runner and
the supervisor included, was killed at once with exit 127; cycle 116's judgement session survived, orphaned).

Waits for --pid to exit, then does exactly what cycle_runner.main does after a session: land_retrospective,
git_commit_cycle, motor_limits_hook("end"), labview_close_hook, bgrun_reap_hook, and writes a `CYCLE n | ... | exit ?`
line + a note to --log so report_gate / the chat see the cycle end. It starts no new cycle.
    py -u tools/finish_orphan_cycle.py --pid 10376 --cycle 116 --log tools/bench/cycle_runner_main_20260928a.log
"""
import argparse, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import cycle_runner as CR                                                   # noqa: E402


def alive(pid):
    out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/NH"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout
    return str(pid) in out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pid", type=int, required=True)
    ap.add_argument("--cycle", type=int, required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--started", default="?")
    x = ap.parse_args()
    bench = os.path.join(ROOT, "tools", "bench")
    log = x.log if os.path.isabs(x.log) else os.path.join(ROOT, x.log)
    status_path = os.path.join(ROOT, "STATUS.md")
    a = argparse.Namespace(dry_run=False, dry_cmd=None, no_motor_hooks=False, no_labview_close=False)
    CR.log_line(log, "ORPHAN-FINISH | %s | cycle %d | runner process died 09:12; waiting for judgement pid %d"
                % (time.strftime("%Y-%m-%d %H:%M:%S"), x.cycle, x.pid))
    while alive(x.pid):
        time.sleep(30)
    end = time.strftime("%Y-%m-%d %H:%M:%S")
    CR.land_retrospective(bench, log)
    CR.git_commit_cycle(x.cycle, log)
    ok_end, why_end = CR.motor_limits_hook("end", x.cycle, a, bench, log, CR.read(status_path))
    ok_lv, why_lv = CR.labview_close_hook(x.cycle, a, bench, log, CR.read(status_path))
    CR.bgrun_reap_hook(x.cycle, bench, log)
    line = ("CYCLE %d | %s | %s | exit ? (orphaned: runner died, finished by finish_orphan_cycle.py) | $? | "
            "motor-end %s, labview-close %s" % (x.cycle, x.started, end, "OK" if ok_end else why_end,
                                                "OK" if ok_lv else why_lv))
    CR.log_line(log, line)
    # the runner numbers its next cycle from THIS cumulative log (last_cycle_number), not from the per-run log;
    # without it a relaunch reused the orphan's number (2026-09-28 10:32)
    CR.log_line(os.path.join(bench, "cycle_runner.log"), line)
    CR.log_line(log, "RUNNER STOP | %s | orphan cycle %d finished by finish_orphan_cycle.py (runner process had died)"
                % (end, x.cycle))
    return 0 if (ok_end and ok_lv) else 1


if __name__ == "__main__":
    sys.exit(main())
