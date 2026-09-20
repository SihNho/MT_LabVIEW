"""probe_opforloop.py - READ-ONLY: the structure of OpForLoop_v0.vi (nodes, labels, terminals, panel) and the connector
of erdosmiller 'Create While Loop.vi' (dropped on a scratch copy of OpForLoop_v0, terminals read, then deleted) - to
plan OpWhileLoop_v0 as a copy of OpForLoop_v0 with the creator swapped.
  py tools/bgrun.py --max-min 8 --log tools/bench/probe_opforloop.log -- py -u tools/bench/probe_opforloop.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = g.OP_FORLOOP
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_opforloop_{os.getpid()}.vi")
CWL = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\Create While Loop.vi"
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    shutil.copyfile(SRC, S); time.sleep(0.3)
    try:
        print("ExecState", g.exec_state(S), flush=True)
        print("panel:", g.fp_labels(S), flush=True)
        for cls in ("SubVI", "Function", "Property", "Invoke", "Constant", "Diagram"):
            print(f"{cls}: {[(o['uid'], o['class'], o.get('owner')) for o in g.report_all(S, cls)]}", flush=True)
        labels = {r["uid"]: r["label"] for r in g.node_labels(S, 0)}
        for cand in range(40):
            nu, rows = g.node_terms_uid(S, 0, cand)
            if not nu:
                break
            print(f"  node {cand} uid {nu} {labels.get(nu)!r}: {[(r['i'], r['name'], r['is_source'], r['wire']) for r in rows]}", flush=True)
        print("--- panel wiring:", flush=True)
        for r in g.panel_wiring(S):
            print(f"   {r['label']!r:36s} ind={r['indicator']} wire {r['wire']}", flush=True)
        g.open_panel(S); time.sleep(0.5)
        before = g.uids(S, "SubVI")
        g.drop_subvi(S, CWL, 0, (100, 900))
        new = [u for u in g.uids(S, "SubVI") if u not in before]
        labels = {r["uid"]: r["label"] for r in g.node_labels(S, 0)}
        for cand in range(40):
            nu, rows = g.node_terms_uid(S, 0, cand)
            if not nu:
                break
            if nu in new:
                print(f"Create While Loop.vi terminals: {[(r['i'], r['name'], r['is_source']) for r in rows]}", flush=True)
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        os.remove(S)
    return 0


if __name__ == "__main__":
    sys.exit(main())
