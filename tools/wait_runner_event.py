r"""wait_runner_event.py - the main chat's report trigger (2026-09-28). Run it BACKGROUNDED from the main chat session;
it exits as soon as the runner log carries an unreported event (report_gate.unreported()), or after --max-min
(the 30-min progress tick), and its exit wakes the chat, which reports and starts the next waiter.

Why: the scheduled task `runner-cycle-report` could not deliver — send_message is refused inside scheduled runs
even with the project allow rule (runs of 2026-09-28 02:24-06:54), and its completion notification never reached
the chat. A background command's exit is the one wake-up this session has been shown to receive.
Reads files only; touches no LabVIEW, motor or runner.
    py -u tools/wait_runner_event.py --max-min 30
"""
import os, sys, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "hooks"))
import report_gate as RG                                                    # noqa: E402

max_min = float(sys.argv[sys.argv.index("--max-min") + 1]) if "--max-min" in sys.argv else 30.0
t0 = time.time()
while True:
    _log, ev = RG.unreported()                   # (log path, [(md5, line), ...])
    if ev:
        print("RUNNER-EVENT %d unreported:" % len(ev))
        for _h, line in ev:
            print("  " + line[:300])
        sys.exit(0)
    if (time.time() - t0) / 60.0 >= max_min:
        log = RG.newest_runner_log()
        tail = open(log, encoding="utf-8", errors="replace").read().splitlines()[-2:] if log else []
        print("TICK %.0f min, no new event. runner log tail:" % max_min)
        for line in tail:
            print("  " + line[:200])
        sys.exit(0)
    time.sleep(30)
