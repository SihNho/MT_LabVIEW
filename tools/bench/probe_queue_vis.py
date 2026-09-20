"""probe_queue_vis.py - READ-ONLY: connectors of erdosmiller 'Create Obtain Queue.vi', 'Create Enqueue Element.vi',
'Create Dequeue Element.vi', 'Create Release Queue.vi', 'Create Bundle by Name.vi', 'Create Unbundle by Name.vi',
'Create Build Array.vi' (each dropped on a scratch copy of OpForLoop_v0, terminals read, scratch deleted) - to plan the
queue / cluster ops of stage 2 (docs/stage2-plan.md gaps 3-4).
  py tools/bgrun.py --max-min 8 --log tools/bench/probe_queue_vis.log -- py -u tools/bench/probe_queue_vis.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

S = os.path.join(g.CLAUDEDEV, f"SCRATCH_queuevis_{os.getpid()}.vi")
LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
NAMES = ["Create Obtain Queue.vi", "Create Enqueue Element.vi", "Create Dequeue Element.vi", "Create Release Queue.vi",
         "Create Bundle by Name.vi", "Create Unbundle by Name.vi", "Create Build Array.vi", "Create Constant.vi", "Create Equal.vi"]
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    shutil.copyfile(g.OP_FORLOOP, S); time.sleep(0.3); g.report_all(S, "SubVI"); g.open_panel(S); time.sleep(0.5)
    try:
        y = 900
        for name in NAMES:
            before = g.uids(S, "SubVI"); g.drop_subvi(S, os.path.join(LIB, name), 0, (100, y)); y += 150
            new = [u for u in g.uids(S, "SubVI") if u not in before]
            for cand in range(80):
                nu, rows = g.node_terms_uid(S, 0, cand)
                if not nu:
                    break
                if nu in new:
                    print(f"{name}: {[(r['i'], r['name'], r['is_source']) for r in rows if r['name']]}", flush=True)
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        os.remove(S)
    return 0


if __name__ == "__main__":
    sys.exit(main())
