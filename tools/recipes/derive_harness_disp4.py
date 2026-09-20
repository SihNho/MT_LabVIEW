"""derive_harness_disp4.py - HARNESS_disp4.vi = disp3 with the Picture indicator removed (Draw output unwired).

Peer (archive/peer/2026-09-14-display-bench-results.md): the +Draw cost must be split into picture CONSTRUCTION
(Draw Flattened Pixmap's own work) and the Picture INDICATOR write/paint. disp4 keeps the whole chain but deletes
the 'new picture' indicator terminal (+ Remove Bad Wires): a subVI still executes with an unwired output.
Copy on disk -> open_panel -> delete the ControlTerminal whose label is 'new picture' -> RBW -> ExecState 1 -> save
-> close_panel (the runner needs the panels CLOSED at start: run 1 of the bench measured 'closed' with panels the
build had left open).
  py tools/bgrun.py --max-min 6 --log tools/bench/derive_harness_disp4.log -- py -u tools/recipes/derive_harness_disp4.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "HARNESS_disp3.vi")
DST = os.path.join(g.CLAUDEDEV, "HARNESS_disp4.vi")
g._run.__defaults__ = (6.0, 60.0)


def main():
    g._lv = None
    try:
        g.close_panel(DST); time.sleep(0.2)
    except Exception:
        pass
    if os.path.exists(DST):
        os.remove(DST)
    shutil.copyfile(SRC, DST); g.report_all(DST, "SubVI"); g.open_panel(DST); time.sleep(0.8)
    labs = g.fp_labels(DST)
    print("panel objects:", labs, flush=True)
    idx = next((i for i, lab, is_ind in labs if lab == "new picture"), None)
    if idx is None:
        print("STOP: no 'new picture' indicator", flush=True); return 2
    cts = g.report_all(DST, "ControlTerminal")
    print(f"ControlTerminals {len(cts)}; panel index of 'new picture' = {idx}", flush=True)
    # ControlTerminal Traverse order is not guaranteed == panel order: delete the one whose removal drops the wire
    # count by exactly 1 and leaves the two controls' wires (verified by fp_labels afterwards).
    w0 = len(g.report_all(DST, "Wire"))
    done = False
    for i in range(len(cts) - 1, -1, -1):
        before = [o["uid"] for o in g.report_all(DST, "ControlTerminal")]
        try:
            g.delete_object(DST, "ControlTerminal", i, verify=False)
        except Exception as e:
            print(f"   delete ControlTerminal[{i}] EXC {str(e)[:80]}", flush=True); continue
        g.remove_bad_wires_scripted(DST)
        labs2 = [lab for _i, lab, _ in g.fp_labels(DST)]
        if "new picture" not in labs2 and "File Path" in labs2 and "Image Name" in labs2:
            done = True; break
        print(f"   ControlTerminal[{i}] was not 'new picture' (labels now {labs2}) - REVERTING by rebuilding from disp3", flush=True)
        g.revert(DST); time.sleep(0.5)
    es = g.exec_state(DST); w1 = len(g.report_all(DST, "Wire"))
    print(f"done={done} Wire {w0} -> {w1} ExecState {es} labels {[lab for _i, lab, _ in g.fp_labels(DST)]}", flush=True)
    if not (done and es == 1):
        print("VERDICT: FAILED - not saved", flush=True); return 3
    g.set_auto_error_handling(DST, False); g.save(DST)
    for p in (SRC, DST) + tuple(os.path.join(g.CLAUDEDEV, f"HARNESS_disp{k}.vi") for k in range(3)):
        try:
            g.close_panel(p)
        except Exception:
            pass
    print("VERDICT: HARNESS_disp4 saved; all display harness panels closed", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
