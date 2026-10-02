r"""prep_c141_p1_q1 - card 141-P1 read-only fact query (no LabVIEW): p4_eq_seq in v16, the bed graph's Equal? nodes,
which of them v16 deletes, and their labels in main_vi_node_labels.json. Prediction: p4_eq_seq has a $work donor #10171,
p4_do_10171 deletes it; >= 1 other Equal? node in the bed graph survives v16."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stage_prerun as SPR  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
v = json.load(open(os.path.join(B, "plan_ring_p4_v16.json"), encoding="utf-8"))
A = v["actions"]
for k, a in enumerate(A, 1):
    if a["id"] in ("p4_eq_seq", "p4_do_10171") or (a.get("op") == "create" and a.get("donor")):
        print("ACT", k, json.dumps(a, default=str)[:1200])
print("TOP", list(v.keys()), v["base"])
gr = json.load(open(os.path.join(B, "graph_ring_p3b2b_20261002_133824.json"), encoding="utf-8"))
print("GRAPH keys", list(gr.keys()))
for k in gr:
    if isinstance(gr[k], list) and gr[k]:
        print("GRAPH list", k, len(gr[k]), json.dumps(gr[k][0], default=str)[:400])
labels = SPR.prim_donor_labels()
deleted = set(int(a["uid"]) for a in A if a.get("op") == "delete_object" and a.get("uid") is not None)
print("DELETED by v16", sorted(deleted))
eq = sorted(u for u, l in labels.items() if l == "Equal?")
print("LABEL Equal? uids", eq)
nodes = {}
for r in gr.get("terminals", []):
    nodes.setdefault(int(r["owner_uid"]), []).append(r)
for u in eq:
    rows = nodes.get(u)
    print("EQ", u, "in_graph", rows is not None, "deleted", u in deleted,
          [(r.get("term_name"), r.get("term_type") or r.get("type"), r.get("wire_uid"), r.get("frame_diagram"), r.get("owner_class")) for r in rows or []])
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
