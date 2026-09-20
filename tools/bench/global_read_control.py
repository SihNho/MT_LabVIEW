"""global_read_control.py - POSITIVE CONTROL for the READ direction of a global-variable node.

Every global access site measured in the main VI so far reads Is Source? = FALSE (WRITE). Before that is written
into docs/main-vi-state.md the op must be shown to say TRUE on a READ global. Construction: drop `Global motor
pos.vi` onto a scratch copy of OpFPLabels_v0 with drop_subvi (LabVIEW places a global VI as a Global node, read
mode by default); walk the diagram to find the node by its 'Trans position' terminal (the global's first field is
what a fresh node shows); run gscript.node_terms on it.
    prediction: exactly one named terminal, Is Source? = TRUE (READ), wire 0 (nothing wired), src_err 0.
If the drop makes a SubVI node instead (terminals named after a connector pane), that is reported and the control
is INCONCLUSIVE - not a pass.
Scratch unique per run, deleted; nothing saved.
  py tools/bgrun.py --max-min 8 --log tools/bench/global_read_control.log -- py -u tools/bench/global_read_control.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

GLOBAL = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\four-fold tracking\Global motor pos.vi"
SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_globalread_{os.getpid()}.vi")
for _old in [p for p in os.listdir(g.CLAUDEDEV) if p.startswith("SCRATCH_globalread")]:
    try:
        os.remove(os.path.join(g.CLAUDEDEV, _old))
    except OSError:
        pass
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    shutil.copyfile(SRC, S)
    g.open_panel(S)
    time.sleep(0.8)
    n0 = len(g.report_all(S, "Node"))
    try:
        r = g.drop_subvi(S, GLOBAL, 0, (300, 700))
        print(f"drop_subvi -> {r}", flush=True)
    except Exception as e:
        print(f"drop_subvi EXC {str(e)[:200]}", flush=True)
    n1 = len(g.report_all(S, "Node"))
    print(f"Node count {n0} -> {n1}; SubVI {len(g.report_all(S, 'SubVI'))}; ExecState {g.exec_state(S)}", flush=True)
    nodes, _ = g.net_map(S, 0, max_nodes=60, max_terms=24)
    hit = None
    for n, (uid, _l, terms) in nodes.items():
        names = [t for _ti, t, _w in terms if t]
        if any("position" in t for t in names):
            hit = (n, uid, names)
    print(f"global node by terminal name: {hit}", flush=True)
    verdict = "INCONCLUSIVE"
    if hit:
        rows = g.node_terms(S, 0, hit[0])
        data = [r for r in rows if r["name"]]
        for r in rows[:4]:
            print(f"   {r}", flush=True)
        if len(data) == 1 and not data[0]["src_err"]:
            verdict = "PASS: READ global -> Is Source? TRUE" if data[0]["is_source"] else "FAIL: READ global reads Is Source? FALSE"
        else:
            verdict = f"INCONCLUSIVE: {len(data)} named terminals / src_err {[r['src_err'] for r in data]}"
    print(f"VERDICT (positive control): {verdict}", flush=True)
    try:
        g.close_panel(S)
        time.sleep(0.3)
        os.remove(S)
        print("scratch deleted", flush=True)
    except Exception as e:
        print("cleanup:", str(e)[:80], flush=True)
    return 0 if verdict.startswith("PASS") else 3


if __name__ == "__main__":
    sys.exit(main())
