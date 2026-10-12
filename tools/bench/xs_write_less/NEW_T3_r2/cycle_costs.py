# ---
# labview: none
# hardware: none
# ---
"""Per cycle of tools/bench/xs_write_less/inputs/cycle_runner.log: the runner's cost (the CYCLE line's $) and how
each assignment round ended (PURPOSE_MET / HANDBACK, from the ASSIGN ... end lines). Ends with a RESULT {...} line.

Line formats come from tools/bench/livebench/lb_collect.py (CYCLE_RE, ASSIGN_END_RE), imported, not copied.
lb_collect.runner_section() does this walk too but reads <wt>/tools/bench/cycle_runner.log only, so it cannot be
pointed at the inputs/ copy; this script walks the lines itself with the same regexes.
"""
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
LOG = os.path.join(REPO, "tools", "bench", "xs_write_less", "inputs", "cycle_runner.log")
sys.path.insert(0, os.path.join(REPO, "tools", "bench", "livebench"))
from lb_collect import ASSIGN_END_RE, CYCLE_RE  # noqa: E402

# Any CYCLE line, including the ones CYCLE_RE skips (usage-limit retries, KILLED, orphaned 'exit ?'), so such a
# cycle is still listed, with an unknown cost, instead of vanishing.
ANY_CYCLE_RE = re.compile(r"^CYCLE (\d+) \|")


def parse(lines):
    """-> {cycle: {"usd": float|None, "rounds": [(round, outcome), ...]}}; the last priced CYCLE line wins."""
    cycles = {}
    for ln in lines:
        m = CYCLE_RE.match(ln)
        if m:
            c = cycles.setdefault(int(m.group(1)), {"usd": None, "rounds": []})
            c["usd"] = None if m.group(5) == "?" else float(m.group(5)[1:])
            continue
        m = ANY_CYCLE_RE.match(ln)
        if m:
            cycles.setdefault(int(m.group(1)), {"usd": None, "rounds": []})
            continue
        m = ASSIGN_END_RE.match(ln)
        if m:
            c = cycles.setdefault(int(m.group(2)), {"usd": None, "rounds": []})
            c["rounds"].append((int(m.group(3)), m.group(8)))
    return cycles


def selfcheck():
    sample = [
        "CYCLE 62 | 2026-09-22 10:00:20 | 2026-09-22 10:03:43 | usage-limit attempt 1, non-result; sleeping",
        "CYCLE 62 | 2026-09-22 10:18:45 | 2026-09-22 11:26:40 | exit 0 | $30.0875 | text",
        "CYCLE 141 | 2026-10-02 21:56:06 | 2026-10-03 00:11:05 | exit ? (orphaned) | $? | motor-end OK",
        "ASSIGN | 2026-10-07 20:22:37 | cycle 144 round 1 | end exit 0 | $13.0819 | 28 min | 4 card(s) | "
        "HANDBACK (session) | detail",
        "ASSIGN | 2026-10-07 21:13:45 | cycle 144 round 2 | end exit 0 | $15.0886 | 47 min | 3 card(s) | "
        "PURPOSE_MET | all 6 pass item(s) met with evidence",
        "ASSIGN | 2026-10-07 20:27:08 | cycle 144 round 2 | start claude-sonnet-5-5/high, caps 180 min | x.json",
    ]
    got = parse(sample)
    assert got[62] == {"usd": 30.0875, "rounds": []}, got[62]
    assert got[141] == {"usd": None, "rounds": []}, got[141]
    assert got[144] == {"usd": None, "rounds": [(1, "HANDBACK"), (2, "PURPOSE_MET")]}, got[144]
    assert parse([]) == {}


def main():
    selfcheck()
    if not os.path.isfile(LOG):
        print("RESULT " + json.dumps({"ok": False, "error": "missing " + LOG}))
        return 1
    with open(LOG, encoding="utf-8", errors="replace") as f:
        cycles = parse(f.read().splitlines())

    for n in sorted(cycles):
        c = cycles[n]
        cost = "$?" if c["usd"] is None else "$%.4f" % c["usd"]
        if c["rounds"]:
            ended = "ended %s (rounds: %s)" % (c["rounds"][-1][1], ", ".join("r%d %s" % r for r in c["rounds"]))
        else:
            ended = "no assignment rounds"
        print("cycle %3d  %9s  %s" % (n, cost, ended))

    with_rounds = [c for c in cycles.values() if c["rounds"]]
    all_rounds = [o for c in with_rounds for _, o in c["rounds"]]
    print("RESULT " + json.dumps({
        "ok": True,
        "cycles": len(cycles),
        "total_usd": round(sum(c["usd"] for c in cycles.values() if c["usd"] is not None), 4),
        "unpriced_cycles": sorted(n for n, c in cycles.items() if c["usd"] is None),
        "cycles_with_rounds": len(with_rounds),
        "cycles_ended_purpose_met": sum(c["rounds"][-1][1] == "PURPOSE_MET" for c in with_rounds),
        "cycles_ended_handback": sum(c["rounds"][-1][1] == "HANDBACK" for c in with_rounds),
        "rounds_purpose_met": all_rounds.count("PURPOSE_MET"),
        "rounds_handback": all_rounds.count("HANDBACK"),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
