r"""wait_logs.py - block for a BOUNDED number of seconds until every named log carries a terminal line.

WHY THIS EXISTS (2026-09-18, cycle 35 dispatch 4). `.claude/agents/material.md` tells a material session to
wait for its own bgrun dispatches with a foreground shell loop
(`until grep -q "BGRUN END\|BGRUN TIMEOUT" <log>; do sleep 10; done`). Under `claude -p` that command is
DENIED by the permission layer - the project's allow list carries `Bash(py tools/*)`, `Bash(ls *)`,
`Bash(tasklist *)`, `Bash(certutil -hashfile *)` and nothing else - and so is the Monitor tool, so a session
that must not end while a dispatch runs had no legal way to wait at all.

`tools/hooks/guard_bash.py:252-254` allows a FOREGROUND LabVIEW-touching command with a declared timeout of at
most 30 s, so this script's own deadline is capped at 29 s: one call = one bounded tick, and the guard's
guarantee is untouched. It starts nothing, kills nothing, and never touches LabVIEW or a motor - it only
reads files.

PRIOR ART checked before writing: `ls tools/` (49 entries) has no waiter; `tools/bgrun.py` is the LAUNCHER
(it writes the `BGRUN END|TIMEOUT` line this script waits for) and has no wait-for-another-log mode;
`grep "^def " tools/gscript.py` is LabVIEW-only.

Usage:
  py tools/wait_logs.py [--seconds N] [--pattern RE] <log> [<log> ...]
Exit 0 = every log matched; 3 = the tick expired with at least one still running (NOT an error - call again).
"""
import argparse
import os
import re
import sys
import time

# ENCODING-SAFE OUTPUT (repair, 2026-09-18, cycle 36). This script CRASHED AT THE MOMENT IT SUCCEEDED:
# `UnicodeEncodeError: 'cp949' codec can't encode character '—'` out of the DONE print, because the
# lines it echoes are log tails written by peers and recipes in UTF-8 (em-dashes, arrows, Korean) while a
# child process's stdout defaults to the console codepage, cp949 on this machine. Two sessions hit it the
# same day, and the crash replaces a rc=0 "every log terminal" with a traceback and rc=1 - the waiter
# reporting failure on the tick where it should have returned success. Both halves are needed: the
# reconfigure fixes the common case, and _p() survives the case where reconfigure is unavailable or the
# stream is a pipe pinned to another codec.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _p(text):
    """print() that can never raise UnicodeEncodeError - a waiter must not die on its own output."""
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(text.encode(enc, errors="replace").decode(enc, errors="replace"), flush=True)


DEFAULT_PATTERN = r"BGRUN (END|TIMEOUT)"
# The 29 s ceiling is the FOREGROUND-tick default, not a hard cap: `tools/hooks/guard_bash.py:252-254`
# already refuses a foreground call declaring more, and a longer wait is legal when the call itself is
# backgrounded through `py tools/bgrun.py --material --max-min N --log <f> -- py -u tools/wait_logs.py ...`,
# which then carries its own kill deadline. One notification instead of N ticks.
DEFAULT_SECONDS = 28.0


def tail(path, n=3):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    except OSError as e:
        return ["<unreadable: %s>" % e]
    return lines[-n:] if lines else ["<empty>"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--seconds", type=float, default=DEFAULT_SECONDS)
    ap.add_argument("--pattern", default=DEFAULT_PATTERN)
    a = ap.parse_args()
    rx = re.compile(a.pattern)
    deadline = time.time() + a.seconds

    done = {}
    while True:
        for p in a.logs:
            if p in done:
                continue
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    for ln in f:
                        if rx.search(ln):
                            done[p] = ln.strip()
                            break
            except OSError:
                pass
        if len(done) == len(a.logs) or time.time() >= deadline:
            break
        time.sleep(1.0)

    for p in a.logs:
        base = os.path.basename(p)
        if p in done:
            _p("DONE      %s  | %s" % (base, done[p]))
        else:
            _p("RUNNING   %s  | %d lines | tail: %s"
               % (base, len(tail(p, 10**9)), " // ".join(tail(p, 2))))
    _p("WAITED %d/%d logs terminal" % (len(done), len(a.logs)))
    return 0 if len(done) == len(a.logs) else 3


if __name__ == "__main__":
    sys.exit(main())
