# ---
# labview: none
# hardware: none
# ---
"""Count OPEN gate false-positive entries per gate class in the xs_write_less input copy of the queue.

Prior art checked: tools/gate_fp.py read_queue (reads the queue; called here, not copied).
"""
import collections
import json
import os
import sys

TOOLS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, TOOLS)
import gate_fp  # noqa: E402

QUEUE = os.path.join(TOOLS, "bench", "xs_write_less", "inputs", "gate_fp_queue.jsonl")

rows = gate_fp.read_queue(QUEUE)
counts = collections.Counter(r.get("gate") for r in rows if r.get("status") == "open")
for gate, n in counts.most_common():
    print("%3d  %s" % (n, gate))
print("RESULT " + json.dumps({"ok": bool(rows), "rows": len(rows), "open": sum(counts.values()), "per_gate": dict(counts)}))
