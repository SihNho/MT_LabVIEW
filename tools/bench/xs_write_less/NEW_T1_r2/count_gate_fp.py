# ---
# labview: none
# hardware: none
# ---
"""count_gate_fp.py - number of OPEN gate false-positive entries per gate class, from the xs_write_less input copy.

Gate class = the entry's `gate` field as logged by tools/gate_fp.py (e.g. guard_bash, checker:stage_prerun:X5).
Reads the queue with gate_fp.read_queue (no second parser). Ends with a RESULT {...} line.
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


def open_per_gate(rows):
    """Counter {gate: number of rows with status 'open'}; a missing gate counts under '(none)'."""
    return collections.Counter(r.get("gate") or "(none)" for r in rows if r.get("status") == "open")


assert open_per_gate([]) == {}
assert open_per_gate([{"gate": "guard_bash", "status": "open"}, {"gate": "guard_bash", "status": "drained"},
                      {"status": "open"}]) == {"guard_bash": 1, "(none)": 1}

if not os.path.isfile(QUEUE):   # read_queue returns [] for a missing file; say so instead of printing zero
    print("RESULT " + json.dumps({"ok": False, "error": "missing " + os.path.normpath(QUEUE)}))
    sys.exit(1)

rows = gate_fp.read_queue(QUEUE)
counts = open_per_gate(rows)
for gate, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
    print("%4d  %s" % (n, gate))
print("RESULT " + json.dumps({"ok": True, "rows": len(rows), "open": sum(counts.values()), "classes": len(counts),
                              "per_gate": dict(counts)}))
