"""READ-ONLY census of OpMoveByLabel_v0.vi (donor for OpMoveByIndex_v0): node labels + terminals with wire uids, panel.
  py tools/bgrun.py --max-min 4 --log tools/bench/diag_opmovebylabel.log -- py -u tools/bench/diag_opmovebylabel.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

OP = g.OP_MOVE_LABEL
g._lv = None
labels = {r["uid"]: r["label"] for r in g.node_labels(OP, 0)}
print("panel:", [(r["label"], r["wire"], r["indicator"]) for r in g.panel_wiring(OP)], flush=True)
for n in range(60):
    u, rows = g.node_terms_uid(OP, 0, n)
    if not u:
        break
    print(f"n{n} uid {u} {labels.get(u)!r}: {[(r['i'], r['name'], 'S' if r['is_source'] else 's', r['wire']) for r in rows]}", flush=True)
print("classes:", {c: len(g.report_all(OP, c)) for c in ("Function", "SubVI", "IndexArray", "Invoke", "Property", "Constant", "Wire")}, flush=True)
