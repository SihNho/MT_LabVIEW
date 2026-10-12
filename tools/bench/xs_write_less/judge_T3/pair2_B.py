# ---
# labview: none
# hardware: none
# ---
"""Per cycle of the xs_write_less input copy of the runner log: its cost and how its assignment rounds ended.

Cost = the '$x' field of the 'CYCLE N | ...' line(s) ('?' when no line carries a number, e.g. a killed or orphaned
cycle). Rounds = the 'ASSIGN | ... | cycle N round K | end ...' lines, in log order: PURPOSE_MET or HANDBACK (trigger).

Prior art checked: docs/toolkit-capabilities.md and tools/cycle_runner.py, tools/logclass.py have no parser for these
lines (cycle_runner.last_cycle_number reads only the number); cycle_runner.read is called for the file text.
"""
import collections
import json
import os
import re
import sys

TOOLS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, TOOLS)
import cycle_runner  # noqa: E402

LOG = os.path.join(TOOLS, "bench", "xs_write_less", "inputs", "cycle_runner.log")
CYCLE_RE = re.compile(r"^CYCLE (\d+) \|")
COST_RE = re.compile(r"\| \$([0-9.]+) \|")
ROUND_RE = re.compile(r"^ASSIGN \| [^|]+\| cycle (\d+) round (\d+) \| end [^|]*\|[^|]*\|[^|]*\|[^|]*\| (PURPOSE_MET|HANDBACK[^|]*?) *(\||$)")

costs = collections.OrderedDict()
rounds = collections.defaultdict(list)
for line in cycle_runner.read(LOG).splitlines():
    m = CYCLE_RE.match(line)
    if m:
        n = int(m.group(1))
        c = COST_RE.search(line)
        costs.setdefault(n, None)
        if c:
            costs[n] = (costs[n] or 0.0) + float(c.group(1))
        continue
    m = ROUND_RE.match(line)
    if m:
        rounds[int(m.group(1))].append("r%s %s" % (m.group(2), m.group(3).replace("HANDBACK ", "HANDBACK")))

for n in sorted(set(costs) | set(rounds)):
    cost = costs.get(n)
    print("cycle %3d  %10s  %s" % (n, "?" if cost is None else "$%.4f" % cost, ", ".join(rounds.get(n, [])) or "-"))

ended = [r.split(" ", 1)[1] for n in rounds for r in rounds[n]]
print("RESULT " + json.dumps({
    "ok": bool(costs),
    "cycles": len(set(costs) | set(rounds)),
    "cost_known": sum(1 for c in costs.values() if c is not None),
    "total_usd": round(sum(c for c in costs.values() if c is not None), 4),
    "cycles_with_rounds": len(rounds),
    "rounds": len(ended),
    "purpose_met": sum(1 for e in ended if e == "PURPOSE_MET"),
    "handback": sum(1 for e in ended if e.startswith("HANDBACK")),
}))
