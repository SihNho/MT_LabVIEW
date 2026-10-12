# ---
# labview: none
# hardware: none
# ---
"""Per cycle of inputs/cycle_runner.log: its cost and the outcome of each assignment round (PURPOSE_MET / HANDBACK).

Cost = debate_loop._cost_of over that cycle's CYCLE lines (called, not copied): a cycle number logged more than once
(re-run, restart) sums its priced lines; a line with no `$` (killed, usage limit) adds nothing.
Usage: py cycle_costs.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LOG = os.path.join(HERE, "..", "inputs", "cycle_runner.log")
sys.path.insert(0, TOOLS)
from debate_loop import _cost_of  # noqa: E402

CYCLE_RX = re.compile(r"^CYCLE (\d+) \|")
ROUND_END_RX = re.compile(r"^ASSIGN \|[^|]*\| cycle (\d+) round (\d+) \| end [^|]*\|[^|]*\|[^|]*\|[^|]*\| (PURPOSE_MET|HANDBACK)\b")


def parse(lines):
    """{cycle: {"lines": [CYCLE lines], "rounds": [(round, outcome), ...]}} in log order."""
    cycles = {}
    for ln in lines:
        m = CYCLE_RX.match(ln)
        if m:
            cycles.setdefault(int(m.group(1)), {"lines": [], "rounds": []})["lines"].append(ln)
            continue
        m = ROUND_END_RX.match(ln)
        if m:
            cycles.setdefault(int(m.group(1)), {"lines": [], "rounds": []})["rounds"].append((int(m.group(2)), m.group(3)))
    return cycles


def selfcheck():
    sample = [
        "CYCLE 9 | a | b | KILLED by the user's order | non-result, void | x",
        "CYCLE 9 | a | b | exit 0 | $1.5000 | x",
        "CYCLE 9 | a | b | exit 0 | $2.2500 | x",
        "ASSIGN | t | cycle 9 round 1 | start claude/high | f.json",
        "ASSIGN | t | cycle 9 round 1 | end exit 0 | $1.0 | 2 min | 0 card(s) | HANDBACK (session) | why",
        "ASSIGN | t | cycle 9 round 2 | end exit 0 | $1.0 | 2 min | 1 card(s) | PURPOSE_MET | ok",
    ]
    c = parse(sample)
    assert list(c) == [9], c
    assert abs(_cost_of(c[9]["lines"]) - 3.75) < 1e-9, c
    assert c[9]["rounds"] == [(1, "HANDBACK"), (2, "PURPOSE_MET")], c
    assert parse([]) == {}


def main():
    selfcheck()
    with open(LOG, encoding="utf-8", errors="replace") as f:
        cycles = parse(f.read().splitlines())
    total, n_met, n_hb = 0.0, 0, 0
    for n in sorted(cycles):
        cost = _cost_of(cycles[n]["lines"])
        rounds = cycles[n]["rounds"]
        total += cost
        n_met += sum(1 for _, o in rounds if o == "PURPOSE_MET")
        n_hb += sum(1 for _, o in rounds if o == "HANDBACK")
        shown = " ".join("r%d=%s" % r for r in rounds) or "-"
        print("cycle %4d  $%8.4f  rounds: %s" % (n, cost, shown))
    print("RESULT " + json.dumps({"ok": True, "cycles": len(cycles), "total_usd": round(total, 4),
                                  "rounds": n_met + n_hb, "purpose_met": n_met, "handback": n_hb}))


if __name__ == "__main__":
    main()
