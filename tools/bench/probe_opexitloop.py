"""probe_opexitloop.py - READ-ONLY: structure of OpExitLoop_v0.vi (nodes, terminals, panel wiring) and the connector of
erdosmiller 'Exit While Loop.vi' / 'Exit Loop.vi' (dropped on a scratch copy, read, deleted) - to plan the stop-button
wiring of a scripted While loop (Stop Condition by control name).
  py tools/bgrun.py --max-min 8 --log tools/bench/probe_opexitloop.log -- py -u tools/bench/probe_opexitloop.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpExitLoop_v0.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_opexitloop_{os.getpid()}.vi")
LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
g._run.__defaults__ = (6.0, 120.0)


def dump(path, tag):
    labels = {r["uid"]: r["label"] for r in g.node_labels(path, 0)}
    for cand in range(40):
        nu, rows = g.node_terms_uid(path, 0, cand)
        if not nu:
            break
        print(f"  {tag} node {cand} uid {nu} {labels.get(nu)!r}: {[(r['i'], r['name'], r['is_source'], r['wire']) for r in rows]}", flush=True)


def main():
    g._lv = None
    shutil.copyfile(SRC, S); time.sleep(0.3)
    try:
        print("panel:", g.fp_labels(S), flush=True)
        for r in g.panel_wiring(S):
            print(f"   {r['label']!r:32s} ind={r['indicator']} wire {r['wire']}", flush=True)
        dump(S, "exitloop")
        g.open_panel(S); time.sleep(0.5)
        for name in ("Exit While Loop.vi", "Exit Loop.vi"):
            before = g.uids(S, "SubVI"); g.drop_subvi(S, os.path.join(LIB, name), 0, (100, 900))
            new = [u for u in g.uids(S, "SubVI") if u not in before]
            for cand in range(60):
                nu, rows = g.node_terms_uid(S, 0, cand)
                if not nu:
                    break
                if nu in new:
                    print(f"{name} terminals: {[(r['i'], r['name'], r['is_source']) for r in rows]}", flush=True)
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        os.remove(S)
    return 0


if __name__ == "__main__":
    sys.exit(main())
