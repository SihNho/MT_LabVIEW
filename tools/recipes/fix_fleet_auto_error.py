"""fix_fleet_auto_error.py - turn AUTOMATIC ERROR HANDLING OFF on fleet ops that still have it (and save them).

Why (2026-09-14 23:1x, archive/peer/2026-09-14-wiresr-test-fail2-imaqcopy-llb-path.md and ...-t8b-...): with automatic
error handling ON, an op that errors raises an UNTITLED modal dialog and opens its own block diagram; the scripted
batch then sits behind it until gscript's watchdog dismisses it, and every VI window reads 'blocked'. The fleet
convention for new ops is set_auto_error_handling(False) - these older ops predate it. Callers already read/raise
`error out` where it matters (drop_subvi does; fp_labels does not read errors at all - noted).

Prediction: for each op, exec_state stays 1 and the file is saved; nothing else changes (Node/Wire counts equal).
  py tools/bgrun.py --max-min 6 --log tools/bench/fix_fleet_auto_error.log -- py -u tools/recipes/fix_fleet_auto_error.py
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

# OpFPLabels_v0 is deliberately NOT here: gscript.fp_labels() uses the out-of-range error dialog as its loop
# terminator and never reads error out (peer ...-t8b-...: disabling the dialog would make it run to max_n with stale
# values). Fix fp_labels to read/stop on the bounds error FIRST, then add the op here.
OPS = ["OpSubVI_v1.vi"]
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    rc = 0
    for name in OPS:
        p = os.path.join(g.CLAUDEDEV, name)
        n0, w0, es0 = g.count(p, "Node"), g.count(p, "Wire"), g.exec_state(p)
        g.open_panel(p); time.sleep(0.5)
        g.set_auto_error_handling(p, False)
        es1 = g.exec_state(p)
        if es1 == 1:
            g.save(p)
        try:
            g.close_panel(p)
        except Exception:
            pass
        n1, w1 = g.count(p, "Node"), g.count(p, "Wire")
        ok = es0 == 1 and es1 == 1 and n0 == n1 and w0 == w1
        print(f"{name}: ExecState {es0}->{es1}, nodes {n0}->{n1}, wires {w0}->{w1} -> {'OK saved' if ok else 'NOT OK (not saved)' if es1 != 1 else 'OK saved (counts differ!)'}", flush=True)
        rc |= 0 if ok else 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
