"""list every node terminal of HARNESS_seq (in memory, unsaved) with wire uid and Is Broken? via OpNetInfo."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
T = os.path.join(g.CLAUDEDEV, "HARNESS_seq.vi")
print("ExecState", g.exec_state(T), "wires", g.count(T, "Wire"), "nodes", g.count(T, "Node"), flush=True)
vi = g.op(g.OP_NET_INFO)
vi.SetControlValue("vi path", T); vi.SetControlValue("Class Name", "Diagram"); vi.SetControlValue("index", 0)
vi.SetControlValue("error in (no error)", (False, 0, "")); vi.SetControlValue("error in", (True, 1, "x")); vi.SetControlValue("Class Name 3", ""); vi.SetControlValue("Class Name 2", "")
for n in range(6):
    vi.SetControlValue("index 2", n); rows = []
    for t in range(20):
        vi.SetControlValue("index 3", t)
        try:
            g._run(vi)
        except RuntimeError:
            break
        name = vi.GetControlValue("Name"); w = int(vi.GetControlValue("UID 2")); br = bool(vi.GetControlValue("Is Broken?"))
        if name == "" and w == 0 and t > 15: break
        if w or br: rows.append((t, name.replace("\n", " ")[:24], w, "BROKEN" if br else ""))
    print(f"node {n} uid {int(vi.GetControlValue('UID'))}: {rows}", flush=True)
