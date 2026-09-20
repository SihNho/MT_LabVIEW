"""probe_setcommand2.py - READ-ONLY: panel wiring of a scratch copy of SetCommand.vi (which panel object sits on which
wire: Pos_degree, '*(type *) &x', read buffer, Baseline Startpoint, Numeric, Ring) + the case structure's tunnels
(tunnels() over all LoopTunnels is for loops; the case's own terminals come from node_terms on diagram 0).
  py tools/bgrun.py --max-min 10 --log tools/bench/probe_setcommand2.log -- py -u tools/bench/probe_setcommand2.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor\SetCommand.vi"
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_setcommand2_{os.getpid()}.vi")
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    shutil.copyfile(SRC, S); time.sleep(0.3)
    try:
        for r in g.panel_wiring(S):
            print(f"  panel {r['label']!r:28s} indicator={r['indicator']} uid {r['uid']} is_source={r['is_source']} wire {r['wire']}", flush=True)
        nu, rows = g.node_terms_uid(S, 0, 0)
        print(f"diagram 0 node 0 uid {nu} (the case structure): {[(r['i'], r['name'], r['is_source'], r['wire']) for r in rows]}", flush=True)
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        os.remove(S)
    return 0


if __name__ == "__main__":
    sys.exit(main())
