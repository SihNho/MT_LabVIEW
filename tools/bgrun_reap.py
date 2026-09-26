r"""bgrun_reap.py - the END line a KILLED bgrun cannot write for itself (card 92-4 / 91-2; retrospective-cycle90
`device-failed`, threshold 1: `tools/bench/diag_c90_t0stamp_scratch.log` ended at START after an outside tree kill).

bgrun's try/finally (2026-09-18) covers every exit path THE RUNNER ITSELF takes. It cannot cover a `taskkill /T /F`
aimed at it from outside (a session cleaning up, a deadline on an OUTER bgrun, a user reclaiming the machine): the
process is gone before any `finally` runs, and the log stays at START - which every waiter in the fleet reads as
"still running" (wait_logs.py, audit_cycle A2, a material session holding its turn). So the record is closed by the
NEXT process that looks, from a fact the dead runner left behind:

    BGRUN START <stamp> limit <m> min: <cmd>      (unchanged; jev.py:222 / jev_gaterow_q.py:57 / protocol.py:63
    BGRUN PID <n>                                  parse that exact shape, so the pid is the NEXT line, not a field)

`reap()` walks the bench's `*.log` files (newest 14 days), takes each file's LAST run segment, and when that segment
has a `BGRUN PID` line, NO terminal line (END / TIMEOUT / KILLED) and the pid is NOT in `tasklist`, appends

    BGRUN KILLED (external) pid=<n> marked <stamp> by <who>: no END/TIMEOUT and the runner process is gone

Never touches a live pid (a reused pid reads as live - the safe direction; that log stays open and is listed by
audit A2 as unfinished, exactly as today). Never touches a segment without a `BGRUN PID` line (logs from before this
change stay as they were). Never rewrites anything: one appended line, once (a KILLED line is itself terminal).
Callers: `tools/bgrun.py` at every start (`BGRUN REAP ...` line only when something was marked), and
`tools/cycle_runner.py`'s cycle-end hook (`BGRUN-REAP |` runner-log line). `audit_cycle` A2 lists KILLED logs as
ended-but-flagged. Self-test: tools/bench/selftest_bgrun_reap.py.

PRIOR ART checked: tools/bgrun.py `_write_final` (own-process paths only), tools/wait_logs.py (reads, never writes),
tools/audit_cycle.py A2 (reports, never closes), tools/lv_stallcheck.ps1 (LabVIEW liveness, not bgrun's).
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import time

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT, "tools"))
BENCH = os.path.join(PROJECT, "tools", "bench")

TERMINAL = ("BGRUN END", "BGRUN TIMEOUT", "BGRUN KILLED")
PID_RE = re.compile(r"^BGRUN PID (\d+)\b", re.M)
KILLED_RE = re.compile(r"^BGRUN KILLED \(external\) pid=(\d+)", re.M)
MAX_AGE_DAYS = 14


def live_pids():
    """Set of running pids from ONE tasklist call; None when tasklist itself failed (then nothing is reaped)."""
    try:
        r = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True,
                           errors="replace", timeout=60)
    except Exception:  # noqa: BLE001
        return None
    if r.returncode != 0:
        return None
    pids = set(int(x) for x in re.findall(r'^"[^"]*","(\d+)"', r.stdout or "", re.M))
    return pids if pids else None


def classify(text):
    """(state, pid) of the LAST run segment: 'none' (no START), 'ended' (terminal line present),
    'undecidable' (no BGRUN PID line - pre-92-4 log), 'open' (pid known, no terminal line)."""
    if "BGRUN START" not in text:
        return "none", None
    seg = text.rsplit("BGRUN START", 1)[-1]
    if any(ln.startswith(TERMINAL) for ln in seg.splitlines()):
        return "ended", None
    m = PID_RE.search(seg)
    if not m:
        return "undecidable", None
    return "open", int(m.group(1))


def _tail_is_terminal(path, nbytes=4096):
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - nbytes))
            tail = f.read().decode("utf-8", errors="replace")
    except OSError:
        return True   # unreadable: leave it alone
    lines = [ln for ln in tail.splitlines() if ln.strip()]
    return bool(lines) and lines[-1].startswith(TERMINAL)


def killed_line(pid, who):
    return ("BGRUN KILLED (external) pid=%d marked %s by %s: no END/TIMEOUT and the runner process is gone\n"
            % (pid, time.strftime("%Y-%m-%d %H:%M:%S"), who))


def reap(bench=BENCH, exclude=(), who="bgrun_reap", max_age_days=MAX_AGE_DAYS, dry_run=False, pids=None):
    """Mark every dead-runner log under `bench`. Returns {"marked": [(path, pid)], "open_live": [(path, pid)],
    "undecidable": [path], "scanned": n, "pids": "ok"|"unavailable"}. `exclude` = paths never touched (a caller's
    own log). With `dry_run` nothing is written."""
    out = {"marked": [], "open_live": [], "undecidable": [], "scanned": 0, "pids": "ok"}
    excl = set(os.path.normcase(os.path.abspath(p)) for p in exclude)
    cutoff = time.time() - max_age_days * 86400
    candidates = []
    for p in glob.glob(os.path.join(bench, "*.log")):
        try:
            if os.path.getmtime(p) < cutoff:
                continue
        except OSError:
            continue
        if os.path.normcase(os.path.abspath(p)) in excl:
            continue
        out["scanned"] += 1
        if _tail_is_terminal(p):
            continue
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError:
            continue
        state, pid = classify(text)
        if state == "undecidable":
            out["undecidable"].append(p)
        elif state == "open":
            candidates.append((p, pid))
    if not candidates:
        return out
    if pids is None:
        pids = live_pids()
    if pids is None:                       # tasklist failed: nobody's liveness is known, touch nothing
        out["pids"] = "unavailable"
        out["open_live"] = candidates
        return out
    for p, pid in candidates:
        if pid in pids:
            out["open_live"].append((p, pid))
            continue
        if not dry_run:
            try:
                with open(p, "a", encoding="utf-8") as f:
                    f.write(killed_line(pid, who))
            except OSError:
                continue
        out["marked"].append((p, pid))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bench", default=BENCH)
    ap.add_argument("--dry-run", action="store_true", help="list what would be marked; write nothing")
    ap.add_argument("--max-age-days", type=float, default=MAX_AGE_DAYS)
    ap.add_argument("--who", default="bgrun_reap.py")
    a = ap.parse_args()
    r = reap(bench=a.bench, who=a.who, max_age_days=a.max_age_days, dry_run=a.dry_run,
             exclude=[os.environ.get("BGRUN_LOG", "")] if os.environ.get("BGRUN_LOG") else ())
    for p, pid in r["marked"]:
        print("%s %s pid=%d" % ("WOULD MARK" if a.dry_run else "MARKED", os.path.basename(p), pid))
    for p, pid in r["open_live"]:
        print("LIVE       %s pid=%d" % (os.path.basename(p), pid))
    for p in r["undecidable"]:
        print("NO-PID     %s (pre-92-4 START, cannot decide)" % os.path.basename(p))
    print("scanned=%d marked=%d live=%d undecidable=%d pids=%s"
          % (r["scanned"], len(r["marked"]), len(r["open_live"]), len(r["undecidable"]), r["pids"]))
    try:
        import protocol
        print(protocol.result_line(protocol.make_result(len(r["marked"]), 0, None)), flush=True)
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
