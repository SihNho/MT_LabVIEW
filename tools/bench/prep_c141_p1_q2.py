r"""prep_c141_p1_q2 - card 141-P1 read-only fact query (no LabVIEW): for each surviving bed Equal? node (q1: #3812 #10019
#22284 #22731 #29111) the source of its x and y inputs (owner class, owner label, terminal name) from the bed graph and
main_vi_node_labels.json - type evidence for 'I32 x/y preferred'. Prediction: every input has exactly one source."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stage_prerun as SPR  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
gr = json.load(open(os.path.join(B, "graph_ring_p3b2b_20261002_133824.json"), encoding="utf-8"))
labels = SPR.prim_donor_labels()
objs = dict((int(o["uid"]), o) for o in gr["objs"])
by_w = {}
for r in gr["terminals"]:
    if r.get("wire_uid"):
        by_w.setdefault(int(r["wire_uid"]), []).append(r)
ok = True
for u in (3812, 10019, 22284, 22731, 29111):
    o = objs.get(u, {})
    print("EQ", u, "owner", o.get("owner"), "class", o.get("class"))
    for r in gr["terminals"]:
        if int(r["owner_uid"]) != u:
            continue
        w = int(r.get("wire_uid") or 0)
        others = [x for x in by_w.get(w, []) if int(x["owner_uid"]) != u]
        srcs = [x for x in others if x["is_source"]] if not r["is_source"] else []
        if not r["is_source"] and len(srcs) != 1:
            ok = False
        for x in (srcs if not r["is_source"] else others):
            ou = int(x["owner_uid"])
            print("   {0:8s} w{1} {2} #{3} {4} label={5!r} term={6!r}".format(r["term_name"], w, "<-" if not r["is_source"] else "->", ou,
                  x["owner_class"], labels.get(ou), x["term_name"]))
print(protocol.result_line(protocol.make_result(1 if ok else 0, 0 if ok else 1, None if ok else "one source per input", [])))
