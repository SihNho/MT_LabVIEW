"""READ-ONLY diagnostic (RECOVERY_LOCKED): is OpForLoop_v1's 'Inputs Indexing?' control wired into Create For Loop's
'Inputs Indexing?' input? (T3 of build_opforloop_v1.log: tunnel created from the control but IndexMode 0.)
  py tools/bgrun.py --max-min 4 --log tools/bench/diag_opforloop_v1.log -- py -u tools/bench/diag_opforloop_v1.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
OP = os.path.join(g.CLAUDEDEV, "OpForLoop_v1.vi")
g._lv = None
labels = {r["uid"]: r["label"] for r in g.node_labels(OP, 0)}
pw = {r["label"]: r for r in g.panel_wiring(OP)}
print("panel:", {k: (v["wire"], v["indicator"]) for k, v in pw.items()}, flush=True)
for n in range(60):
    u, rows = g.node_terms_uid(OP, 0, n)
    if not u: break
    if labels.get(u) == "Create For Loop.vi":
        print("Create For Loop terminals:", [(r["name"], "S" if r["is_source"] else "s", r["wire"]) for r in rows], flush=True)
