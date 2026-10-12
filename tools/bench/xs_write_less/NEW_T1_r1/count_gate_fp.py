# ---
# labview: none
# hardware: none
# ---
"""count_gate_fp.py - number of OPEN gate-fp queue entries per gate class, then a RESULT line.

Gate class: `checker:<tool>` for a checker gate, else the hook name (`guard_peer.undisposed`, `guard_assign:x` ->
`guard_peer`, `guard_assign`). Reads the queue with gate_fp.read_queue (no second parser).
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, TOOLS)
import gate_fp  # noqa: E402

QUEUE = os.path.join(HERE, "..", "inputs", "gate_fp_queue.jsonl")


def gate_class(gate):
    parts = (gate or "?").split(":")
    if parts[0] == "checker" and len(parts) > 1:
        return "checker:" + parts[1]
    return parts[0].split(".")[0]


assert gate_class("checker:stagekit:PB") == "checker:stagekit"
assert gate_class("guard_peer.undisposed") == "guard_peer"
assert gate_class("guard_assign:c-outside-purpose") == "guard_assign"
assert gate_class("guard_bash") == "guard_bash"
assert gate_class(None) == "?"

# read_queue returns [] for a missing file; say so instead of printing zero counts.
if not os.path.isfile(QUEUE):
    print('RESULT ' + json.dumps({"ok": False, "why": "missing " + QUEUE}))
    sys.exit(1)

counts = Counter(gate_class(r.get("gate")) for r in gate_fp.read_queue(QUEUE) if r.get("status") == "open")
for cls, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
    print("%3d  %s" % (n, cls))
print("RESULT " + json.dumps({"ok": True, "open": sum(counts.values()), "by_class": dict(counts)}))
