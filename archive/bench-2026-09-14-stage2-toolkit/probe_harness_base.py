"""probe_harness_base.py - READ-ONLY: what HARNESS_base.vi (a small runnable VI) contains - object census, node labels,
panel objects - to plan the 'empty VI' recipe (delete everything, keep it runnable) for the stage-2 top level.
  py tools/bgrun.py --max-min 5 --log tools/bench/probe_harness_base.log -- py -u tools/bench/probe_harness_base.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

for name in ("HARNESS_base.vi", "HARNESS_copy0.vi"):
    p = os.path.join(g.CLAUDEDEV, name)
    print(f"--- {name}: ExecState {g.exec_state(p)}", flush=True)
    for cls in ("Diagram", "SubVI", "Function", "Property", "Invoke", "Constant", "ControlTerminal", "Wire", "ForLoop", "WhileLoop", "CaseStructure"):
        rows = g.report_all(p, cls)
        print(f"   {cls}: {len(rows)} {[(o['uid'], o['class']) for o in rows][:12]}", flush=True)
    print(f"   labels: {[(r['uid'], r['label']) for r in g.node_labels(p, 0)]}", flush=True)
    print(f"   panel: {g.fp_labels(p)}", flush=True)
