# ---
# labview: none
# hardware: none
# ---
"""count_gate_fp - number of OPEN gate false positives per gate class, read from the bench input copy of the queue.

Gate class = the hook name for a guard (suffixes like `.undisposed` or `:c-outside-purpose` dropped), or
`checker:<tool>` for a checker gate. Reading the queue is gate_fp.read_queue (shared, not re-written here).
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, TOOLS)
import gate_fp  # noqa: E402

QUEUE = os.path.join(HERE, "..", "inputs", "gate_fp_queue.jsonl")


def gate_class(gate):
    parts = (gate or "?").split(".")[0].split(":")
    return ":".join(parts[:2]) if parts[0] == "checker" else parts[0]


rows = gate_fp.read_queue(QUEUE)
open_rows = [r for r in rows if r.get("status") == "open"]
counts = collections.Counter(gate_class(r.get("gate")) for r in open_rows)
for cls, n in counts.most_common():
    print("%-28s %d" % (cls, n))
print("RESULT " + json.dumps({"rows": len(rows), "open": len(open_rows), "per_class": dict(counts.most_common())}))
