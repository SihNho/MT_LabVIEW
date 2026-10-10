# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_159-e1-1.md
# ---
"""Card 159-e1-1 probe (read-only): data shapes of the 94ffff94 graph, the P5-1 graph and the p5s02a sim end, for the CEN2 end-pair key.
PREDICTION: prints keys; sink and source rows of a wire share frame_diagram (count of wires where they differ printed)."""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402


def jl(p):
    return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))


g = jl("tools/bench/graph_ring_p5s02a_20261010_032547.json")
P = jl("tools/bench/plan_ring_p5s02a.json")
print("graph keys", list(g.keys()))
print("term row", g["terminals"][0])
print("obj", g["objs"][0])
print("owners", type(g.get("owners")), list((g.get("owners") or {}).items())[:2])
print("base", P["finalized"]["base"], "step0", P["finalized"]["step_files"][0], "end", P["finalized"]["step_files"][-1])
s = jl(P["finalized"]["step_files"][-1]["path"])["state"]
print("state keys", list(s.keys()))
print("sim row", s["terminals"][0])
for name, rows in (("real", g["terminals"]), ("sim", s["terminals"])):
    by = collections.defaultdict(set)
    dup = collections.Counter(r["term_uid"] for r in rows)
    for r in rows:
        if r.get("wire_uid"):
            by[r["wire_uid"]].add(r.get("frame_diagram"))
    print(name, "rows", len(rows), "dup term uids", sum(1 for v in dup.values() if v > 1), "wires", len(by),
          "multi-frame wires", sum(1 for v in by.values() if len(v) > 1), [(w, sorted(map(str, v))) for w, v in by.items() if len(v) > 1][:5])
b = jl(P["finalized"]["base"]["path"])
for name, rows in (("base", b["terminals"]), ("sim", s["terminals"]), ("real", g["terminals"])):
    print(name, "rows of term 3453 / 5704:", [r for r in rows if r["term_uid"] in (3453, 5704)])
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
