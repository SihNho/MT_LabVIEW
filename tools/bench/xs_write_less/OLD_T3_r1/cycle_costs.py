# ---
# labview: none
# hardware: none
# ---
"""Per cycle of a runner log: its cost (the CYCLE line's $, which already includes the assignment rounds) and how
its assignment rounds ended (PURPOSE_MET / HANDBACK per round), then a RESULT line.

Calls tools/debate_loop.py (cycle_lines, _cost_of) for the per-cycle lines and the cost; only the ASSIGN end-line
outcome is parsed here. A cycle number logged twice (runner restart) has its CYCLE costs summed and its rounds listed
in log order.
Run: py tools/bench/xs_write_less/OLD_T3_r1/cycle_costs.py [runner_log]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from debate_loop import cycle_lines, _cost_of  # noqa: E402

LOG = os.path.join(ROOT, "tools", "bench", "xs_write_less", "inputs", "cycle_runner.log")
NUM = re.compile(r"^(?:CYCLE (\d+) \||ASSIGN \|[^|]*\| cycle (\d+) round)")
END = re.compile(r"^ASSIGN \|[^|]*\| cycle \d+ round (\d+) \| end .*?\| (PURPOSE_MET|HANDBACK)\b")


def main():
    log = sys.argv[1] if len(sys.argv) > 1 else LOG
    with open(log, encoding="utf-8", errors="replace") as f:
        nums = sorted({int(m.group(1) or m.group(2)) for m in map(NUM.match, f) if m})
    rows, unparsed = [], 0
    for n in nums:
        ls = cycle_lines(log, [n], limit=10 ** 6)
        priced = sum(1 for ln in ls if re.match(r"^CYCLE \d+ \|.*\| \$[0-9.]+ \|", ln))
        rounds = []
        for ln in ls:
            if ln.startswith("ASSIGN |") and "| end " in ln:
                m = END.match(ln)
                if m:
                    rounds.append("r%s %s" % m.groups())
                else:
                    unparsed += 1
        rows.append((n, _cost_of(ls) if priced else None, rounds))
        cost = "$%.4f" % rows[-1][1] if priced else "?"
        print("cycle %3d  %10s  %s" % (n, cost, ", ".join(rounds) if rounds else "no assignment rounds"))
    with_r = [r for r in rows if r[2]]
    print("RESULT " + json.dumps({
        "log": os.path.relpath(log, ROOT).replace("\\", "/"), "cycles": len(rows),
        "total_usd": round(sum(r[1] or 0.0 for r in rows), 4), "cycles_unpriced": sum(r[1] is None for r in rows),
        "cycles_with_rounds": len(with_r),
        "rounds_purpose_met": sum(x.endswith("PURPOSE_MET") for r in with_r for x in r[2]),
        "rounds_handback": sum(x.endswith("HANDBACK") for r in with_r for x in r[2]),
        "cycles_last_round_purpose_met": sum(r[2][-1].endswith("PURPOSE_MET") for r in with_r),
        "unparsed_assign_end_lines": unparsed}))


if __name__ == "__main__":
    main()
