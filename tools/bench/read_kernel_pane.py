"""read_kernel_pane.py - front-panel labels (tabbing order, control vs indicator) of PARALLEL_kernel_v3.vi, the pane that the
GPU backend subVI must inherit.  Headless read only; the VI is never modified."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
K = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi")
rows = g.fp_labels(K)
out = [{"index": i, "label": lab, "indicator": bool(ind)} for i, lab, ind in rows]
for r in out:
    print(f"  {r['index']:2d} {'IND' if r['indicator'] else 'CTL'} {r['label']!r}", flush=True)
json.dump(out, open(os.path.join(HERE, "kernel_pane.json"), "w"), indent=1)
print("nodes", g.count(K, "Node"), "wires", g.count(K, "Wire"), "ExecState", g.exec_state(K), flush=True)
