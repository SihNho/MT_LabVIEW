# ---
# labview: none
# hardware: none
# evidence: tools/bench/graph_ring_p5s02d_20261010_154830.json
# ---
r"""diag_c166_a1_6_probe - card 166-a1-6 (OFFLINE, read-only): print the terminal rows that hold uid 23501 / 23481 / 23042 as term or owner
in the stored step-4 base (graph_ring_p5s02c) and adopted (graph_ring_p5s02d) graphs, and the row keys, so the row-level identity of the
reuse detector is chosen on data. PREDICTION: base has rows owned by 23501 (LoopTunnel) and 23042 (Comparison); adopted holds 23501 and 23481
as term uids of #12170. Writes nothing.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c166_a1_6_probe.log -- py -u tools/bench/diag_c166_a1_6_probe.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol  # noqa: E402

B = os.path.dirname(os.path.abspath(__file__))
n = 0
for f in ("graph_ring_p5s02c_20261010_131658.json", "graph_ring_p5s02d_20261010_154830.json"):
    g = json.load(open(os.path.join(B, f), encoding="utf-8"))
    print("FILE", f, "keys", sorted(g), "row keys", sorted(g["terminals"][0]), "obj keys", sorted(g["objs"][0]))
    for u in (23501, 23481, 23042, 12170):
        rows = [r for r in g["terminals"] if int(r.get("term_uid") or 0) == u or int(r.get("owner_uid") or 0) == u]
        print("  uid", u, "obj", [o for o in g["objs"] if int(o["uid"]) == u], "rows", len(rows))
        for r in rows[:6]:
            print("    ", dict((k, r.get(k)) for k in ("term_uid", "owner_uid", "owner_class", "term_class", "term_name", "frame_diagram", "wire_uid")))
    n += 1
print(protocol.result_line(protocol.make_result(n, 0, None, [])), flush=True)
