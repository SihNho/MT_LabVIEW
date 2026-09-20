"""Block until a bgrun log's LAST line is its final BGRUN END/TIMEOUT line, then print the tail.

Why this exists (cycle 47, 2026-09-19): five retrospectives (cycles 37, 38, 44, 45, 46) were killed by
session exit before `bgrun` could write its final line, and each one blocked the NEXT cycle's build at
`guard_cycle.py`'s stale-retrospective branch. CLAUDE.md OPEN 54(b) says the launching session must hold
its turn open until the child lands; a `claude -p` session does that by keeping a tool call in flight.

This is not a new process device (user, 2026-09-18 08:53) - it is a 40-line wait, the mechanical form of a
rule that already exists. It touches no LabVIEW, opens no reference and changes nothing.

    py tools/bgrun.py --max-min 25 --log tools/bench/wait_retro.log -- \
        py -u tools/bench/wait_bgrun_end.py tools/bench/retro.log 1400

Exit 0 = the final line arrived. Exit 1 = the deadline passed without it (report as a NON-RESULT, never
as "the retrospective failed" - CLAUDE.md, a value returned beside an error has measured nothing).
"""
import re
import sys
import time

FINAL = re.compile(r"^BGRUN (END|TIMEOUT)")


def last_line(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    except OSError:
        return ""
    return lines[-1] if lines else ""


def tail(path, n):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    except OSError:
        return []
    return lines[-n:]


def main():
    log = sys.argv[1]
    deadline_s = float(sys.argv[2]) if len(sys.argv) > 2 else 1400.0
    poll_s = float(sys.argv[3]) if len(sys.argv) > 3 else 15.0
    started = time.time()
    while time.time() - started < deadline_s:
        if FINAL.match(last_line(log)):
            print("WAIT OK after %.0fs" % (time.time() - started))
            for ln in tail(log, 6):
                print(ln)
            return 0
        time.sleep(poll_s)
    print("WAIT GAVE UP after %.0fs - NON-RESULT, not a failure of the child" % deadline_s)
    for ln in tail(log, 6):
        print(ln)
    return 1


if __name__ == "__main__":
    sys.exit(main())
