# ---
# labview: none
# hardware: none
# ---
"""Read-only: guard_assign.card_outside on the 162 scratch card with two next.json versions (cycle 162, pass item 0)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import guard_assign as ga


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


card = load("tools/bench/cards/task_162-a1-1.json")
cfg = ga.load_config()
for rel in ("tools/bench/next_c161_r3.json", "tools/bench/next.json"):
    print("%s -> %r" % (rel, ga.card_outside(card, load(rel), cfg)))
