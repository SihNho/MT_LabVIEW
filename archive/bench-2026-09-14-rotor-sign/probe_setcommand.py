"""probe_setcommand.py - READ-ONLY look at a scratch COPY of the Autonics driver SetCommand.vi (the rotor read path
parses UNSIGNED: docs/rotor-sign-diagnosis.md). Prints every diagram's nodes with labels (node_labels) and terminals
(node_terms), the object census, and the front panel - to plan the signed-read copy. Scratch deleted; the
instr.lib original is never touched.
  py tools/bgrun.py --max-min 10 --log tools/bench/probe_setcommand.log -- py -u tools/bench/probe_setcommand.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor\SetCommand.vi"
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_setcommand_{os.getpid()}.vi")
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    if not os.path.exists(SRC):
        print(f"STOP: {SRC} not found", flush=True); return 2
    shutil.copyfile(SRC, S); time.sleep(0.3)
    try:
        print("ExecState", g.exec_state(S), flush=True)
        for cls in ("Diagram", "Constant", "Function", "SubVI", "Property", "Invoke", "CaseStructure", "Sequence", "ControlTerminal"):
            rows = g.report_all(S, cls)
            print(f"{cls}: {len(rows)} -> {[(o['uid'], o['class'], o.get('owner')) for o in rows][:30]}", flush=True)
        ndia = len(g.report_all(S, "Diagram"))
        for di in range(ndia):
            labels = {r["uid"]: r["label"] for r in g.node_labels(S, di)}
            print(f"--- diagram {di}: {len(labels)} nodes", flush=True)
            for cand in range(40):
                nu, rows = g.node_terms_uid(S, di, cand)
                if not nu:
                    break
                print(f"  node {cand} uid {nu} {labels.get(nu)!r}: {[(r['i'], r['name'], r['is_source'], r['wire']) for r in rows]}", flush=True)
        print("panel:", g.fp_labels(S), flush=True)
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        os.remove(S)
    return 0


if __name__ == "__main__":
    sys.exit(main())
