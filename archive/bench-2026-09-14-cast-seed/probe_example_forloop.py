"""probe_example_forloop.py - READ-ONLY look at a scratch copy of NI's example
'VI Scripting with Structures - For Loop.vi': every node of diagram 0 with its label and terminals (node_labels +
node_terms), the object census (Constant / Function / Property / Invoke), and the front-panel objects. Purpose: locate
the ForLoop class-specifier constant and the New VI Object node whose output is ForLoop-typed (the cast seed).
Scratch deleted afterwards; the original example is never touched.
  py tools/bgrun.py --max-min 10 --log tools/bench/probe_example_forloop.log -- py -u tools/bench/probe_example_forloop.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EX = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:\Program Files\National Instruments\LabVIEW 2026\examples\Application Control\VI Scripting\Structures\VI Scripting with Structures - For Loop.vi"
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_ex_forloop_{os.getpid()}.vi")
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    shutil.copyfile(EX, S); time.sleep(0.3)
    try:
        print("ExecState", g.exec_state(S), flush=True)
        for cls in ("Constant", "Function", "Property", "Invoke", "SubVI", "ForLoop", "Diagram", "ControlTerminal"):
            rows = g.report_all(S, cls)
            print(f"{cls}: {len(rows)} -> {[(o['uid'], o['class'], o.get('owner')) for o in rows][:20]}", flush=True)
        labels = {r["uid"]: r["label"] for r in g.node_labels(S, 0)}
        print(f"node labels diagram 0: {labels}", flush=True)
        for cand in range(40):
            nu, rows = g.node_terms_uid(S, 0, cand)
            if not nu:
                break
            print(f"  node {cand} uid {nu} {labels.get(nu)!r}: {[(r['i'], r['name'], r['is_source'], r['wire']) for r in rows]}", flush=True)
        print("panel:", g.fp_labels(S), flush=True)
        ndia = len(g.report_all(S, "Diagram"))
        for di in range(1, min(ndia, 6)):
            print(f"diagram {di} labels: {[(r['uid'], r['label']) for r in g.node_labels(S, di)]}", flush=True)
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        os.remove(S)
    return 0


if __name__ == "__main__":
    sys.exit(main())
