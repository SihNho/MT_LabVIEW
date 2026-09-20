"""probe_autonics_configure.py - READ-ONLY, NO HARDWARE: front-panel objects and saved defaults of scratch copies of the
Autonics driver's Configure.vi and Close.vi (what a rotor session needs before SetCommand can talk).
  py tools/bgrun.py --max-min 5 --log tools/bench/probe_autonics_configure.log -- py -u tools/bench/probe_autonics_configure.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

D = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor"


def main():
    g._lv = None
    for name in ("Configure.vi", "Close.vi"):
        src = os.path.join(D, name); s = os.path.join(g.CLAUDEDEV, f"SCRATCH_autonics_{name.replace('.vi', '')}_{os.getpid()}.vi")
        shutil.copyfile(src, s); time.sleep(0.3)
        try:
            labels = g.fp_labels(s)
            print(f"{name}: panel {labels}", flush=True)
            vi = g.op(s)
            for _i, lab, ind in labels:
                if lab:
                    try:
                        print(f"   {lab!r:28s} {'IND' if ind else 'CTL'} = {vi.GetControlValue(lab)!r}", flush=True)
                    except Exception as e:
                        print(f"   {lab!r:28s} EXC {str(e)[:80]}", flush=True)
            for di in range(len(g.report_all(s, "Diagram"))):
                print(f"   diagram {di}: {[(r['uid'], r['label']) for r in g.node_labels(s, di)]}", flush=True)
        finally:
            os.remove(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
