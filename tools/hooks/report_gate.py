"""Stop + UserPromptSubmit hook: the interactive chat MUST report every runner event to the user.

Why (user, 2026-09-23: "30분 간격으로 진행상황 보고하는거, 그리고 사이클 종료시마다 보고하는 걸 안하고있네.
훅으로 안걸려있음? 그러면 훅으로 넣어야함"): the runner ended a cycle at 02:38 and the chat said nothing until
the user asked at 03:19. A rule that lives in memory faded; this one lives in code.

Mechanism
  * The runner log (newest tools/bench/cycle_runner_main_*.log) carries one `CYCLE n | ...` line per finished
    cycle and a `RUNNER STOP | ...` line at the end. `tools/bench/report_ack.json` records which of those
    lines the chat has already reported (by their md5).
  * As a Stop hook: if any CYCLE/RUNNER STOP line is unacknowledged, the turn may NOT end -> exit 2 with the
    reason, which the harness feeds back to Claude. Claude reports, then runs `--ack`.
  * As a UserPromptSubmit hook: prints the unreported lines as context so the reply leads with them.
  * `--ack` marks everything currently in the log as reported. `--status` prints the state.
  * Runner-spawned cells (BENCH_CELL / CYCLE_SESSION set) are exempt - they are not the chat.
  * Every report demand also lists the OPEN items of tools/bench/decisions_pending.json (decisions-pending/1),
    because a cycle-end report must name the user decisions the work is waiting on (session protocol v1, 2026-09-24).
The 30-minute heartbeat itself is a session cron (CronCreate) - a hook cannot wake a session, it can only
refuse to let one fall silent once it is awake.
"""
import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BENCH = os.path.join(ROOT, "tools", "bench")
ACK = os.path.join(BENCH, "report_ack.json")
EVENT_RE = re.compile(r"^(CYCLE\s+\d+\s*\||RUNNER STOP\s*\||BGRUN (END|TIMEOUT))")


def newest_runner_log():
    logs = glob.glob(os.path.join(BENCH, "cycle_runner_main_*.log"))
    if not logs:
        return None
    return max(logs, key=os.path.getmtime)


def events():
    log = newest_runner_log()
    if not log:
        return log, []
    out = []
    with open(log, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if EVENT_RE.match(line):
                out.append((hashlib.md5(line.encode("utf-8")).hexdigest(), line))
    return log, out


def load_ack():
    try:
        with open(ACK, encoding="utf-8") as f:
            return set(json.load(f).get("reported", []))
    except Exception:
        return set()


def unreported():
    log, ev = events()
    seen = load_ack()
    return log, [(h, l) for h, l in ev if h not in seen]


def decisions_block(path=None):
    """The OPEN user decisions (tools/bench/decisions_pending.json, schema decisions-pending/1) that every cycle-end
    report must list (session protocol v1 wiring, 2026-09-24 - user: "사용자 결정도 이렇게 구현하여 적용"). Empty
    string when there are none or the file is unreadable (a broken list must not wedge the chat)."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import protocol
        items = protocol.open_decisions(path or protocol.DECISIONS)
    except Exception:      # noqa: BLE001
        return ""
    if not items:
        return ""
    rows = ["  %s (asked %s by %s%s): %s  options: %s%s" % (
        it["id"], it["asked"], it["by"],
        ("; blocks " + ",".join(it["blocks"])) if it.get("blocks") else "",
        it["question"], " | ".join(it.get("options") or []),
        ("  recommended: " + it["recommendation"]) if it.get("recommendation") else "") for it in items]
    return ("\nOPEN USER DECISIONS — the report MUST list each of these (tools/bench/decisions_pending.json):\n"
            + "\n".join(rows) + "\n")


def ack():
    log, ev = events()
    with open(ACK, "w", encoding="utf-8") as f:
        json.dump({"log": log, "reported": [h for h, _ in ev]}, f, indent=1)
    print("report_gate: acknowledged %d event(s) from %s" % (len(ev), log))


def main():
    if "--ack" in sys.argv:
        ack()
        return 0
    if os.environ.get("BENCH_CELL") or os.environ.get("CYCLE_SESSION"):
        return 0
    log, un = unreported()
    if "--status" in sys.argv:
        print("log=%s unreported=%d" % (log, len(un)))
        for _, l in un:
            print("  " + l[:200])
        sys.stdout.write(decisions_block())
        return 0
    if not un:
        return 0
    text = "\n".join("  " + l[:300] for _, l in un)
    msg = ("[hook report_gate] %d UNREPORTED RUNNER EVENT(S) in %s — report them to the user FIRST "
           "(cycle number, exit code, cost, what the cycle delivered, what NEXT says), then run "
           "`py tools/hooks/report_gate.py --ack`. The turn cannot end until then.\n%s"
           % (len(un), os.path.basename(log or "?"), text))
    msg += decisions_block()
    # Stop hook: exit 2 blocks the stop and feeds stderr back to Claude. UserPromptSubmit: stdout is context.
    try:
        payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except Exception:
        payload = {}
    if payload.get("hook_event_name") == "Stop":
        if payload.get("stop_hook_active"):
            return 0  # do not loop forever
        sys.stderr.write(msg + "\n")
        return 2
    sys.stdout.write(msg + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
