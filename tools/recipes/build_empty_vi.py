"""build_empty_vi.py - EMPTY_v0.vi: an empty, runnable top-level VI to author the stage-2 VI in (docs/stage2-plan.md,
toolkit gap 'empty VI'). Copy HARNESS_copy0.vi (probe_harness_base.log: 3 subVIs, 3 controls, 6 wires, 2 orphan
constants), delete every SubVI (+Remove Bad Wires), every ControlTerminal and every Constant; require ExecState 1,
an empty panel and a 0-node diagram; run it once over COM (returns immediately); save.
  py tools/bgrun.py --max-min 6 --log tools/bench/build_empty_vi.log -- py -u tools/recipes/build_empty_vi.py [name]
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "HARNESS_copy0.vi")
OP = os.path.join(g.CLAUDEDEV, (sys.argv[1] if len(sys.argv) > 1 else "EMPTY_v0") + ".vi")
g._run.__defaults__ = (6.0, 60.0)


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP); time.sleep(0.3); g.report_all(OP, "SubVI"); g.open_panel(OP); time.sleep(0.8)
    print(f"start: ExecState {g.exec_state(OP)}", flush=True)
    for cls in ("SubVI", "ControlTerminal", "Constant"):
        n = len(g.report_all(OP, cls))
        for i in range(n - 1, -1, -1):
            try:
                g.delete_object(OP, cls, i, verify=False)
            except Exception as e:
                print(f"   delete {cls}[{i}]: {str(e)[:80]}", flush=True)
        g.remove_bad_wires_scripted(OP)
        print(f"   after deleting {n} {cls}: {[(c, len(g.report_all(OP, c))) for c in ('SubVI', 'ControlTerminal', 'Constant', 'Wire', 'Node')]} ExecState {g.exec_state(OP)}", flush=True)
    es = g.exec_state(OP); panel = g.fp_labels(OP); nodes = g.report_all(OP, "Node")
    print(f"   final: ExecState {es}, panel {panel}, nodes {len(nodes)}", flush=True)
    ok = es == 1 and not [l for _i, l, _ind in panel if l] and not nodes
    if ok:
        t0 = time.time(); g._run(g.op(OP)); print(f"   run: {time.time() - t0:.2f} s", flush=True)
        g.save(OP)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print("\nVERDICT: " + ("EMPTY VI built, runs, saved" if ok else "NOT empty/runnable - not saved"), flush=True)
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main())
