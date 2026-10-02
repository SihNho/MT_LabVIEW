"""usage_stop_watch.py - stop the cycle runner when WEEKLY usage reaches a threshold (user, 2026-10-02:
"주간 사용량 90퍼센트 되면 사이클 진행 멈춰줘").

Every --every-min minutes it makes one tiny `claude -p` call (haiku) with stream-json output and reads the
`rate_limit_event` -> rate_limit_info.unifiedWindows.seven_day.utilization (0..1, the same number the app's
"Weekly - all models" card shows). At >= --threshold it writes a graceful STOP line at the top of STATUS.md
(the runner finishes the cycle in progress, closes LabVIEW, releases motor limits, then exits; runner_supervisor
sees a real stop and does not relaunch) and exits. A probe that cannot read the number is logged and retried;
it never writes STOP on a missing number.

  py tools/bgrun.py --max-min 4320 --log tools/bench/usage_stop_watch.log -- py -u tools/usage_stop_watch.py
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = os.path.join(ROOT, "STATUS.md")
STOP_RE = re.compile(r"^STOP\b", re.M)


def weekly_utilization():
    """Fraction 0..1, or None when the probe could not read it."""
    cmd = ["claude", "-p", "Reply with the single word OK", "--model", "claude-haiku-4-5-20251001",
           "--output-format", "stream-json", "--verbose"]
    try:
        out = subprocess.run(cmd, cwd=tempfile.gettempdir(), capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=180, shell=(os.name == "nt")).stdout
    except (subprocess.TimeoutExpired, OSError) as e:
        print("PROBE ERROR %s" % e, flush=True)
        return None
    for line in out.splitlines():
        if '"rate_limit_event"' not in line:
            continue
        try:
            info = json.loads(line).get("rate_limit_info") or {}
            return float(info["unifiedWindows"]["seven_day"]["utilization"])
        except (ValueError, KeyError, TypeError):
            continue
    print("PROBE NO rate_limit_event in %d lines" % len(out.splitlines()), flush=True)
    return None


def write_stop(util, threshold):
    with open(STATUS, encoding="utf-8") as f:
        text = f.read()
    if STOP_RE.search(text):
        return "STOP already present"
    line = ("STOP - USAGE WATCH %s: weekly all-models usage %.0f %% >= %.0f %% (user 2026-10-02: \"주간 사용량 "
            "90퍼센트 되면 사이클 진행 멈춰줘\"). Graceful: the cycle in progress finishes, then the runner exits and the "
            "supervisor does not relaunch. Restart only when the user says so (after the weekly reset).\n"
            % (time.strftime("%Y-%m-%d %H:%M"), util * 100, threshold * 100))
    lines = text.splitlines(keepends=True)
    # insert right after the YAML frontmatter (--- ... ---), else at the top
    at = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                at = i + 1
                break
    lines.insert(at, line)
    tmp = STATUS + ".usagewatch.tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write("".join(lines))
    os.replace(tmp, STATUS)
    return "STOP written at line %d" % (at + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.90)
    ap.add_argument("--every-min", type=float, default=10.0)
    ap.add_argument("--once", action="store_true", help="probe once, print, never write STOP")
    a = ap.parse_args()
    while True:
        u = weekly_utilization()
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if u is None:
            print("WATCH | %s | weekly ? (probe failed) | retry in %.0f min" % (stamp, a.every_min), flush=True)
        else:
            print("WATCH | %s | weekly %.0f %% | threshold %.0f %%" % (stamp, u * 100, a.threshold * 100), flush=True)
            if a.once:
                return 0
            if u >= a.threshold:
                print("TRIGGER | %s | %s" % (stamp, write_stop(u, a.threshold)), flush=True)
                return 0
        if a.once:
            return 1
        time.sleep(a.every_min * 60)


if __name__ == "__main__":
    sys.exit(main())
