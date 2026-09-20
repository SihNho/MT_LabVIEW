"""strip the donor VI copy to its Call Library Function Node and see what Create Control/Indicator make on its terminals
(the CLFN parameters are probably 'Adapt to Type' handles -> the wrapper could wire our own DBL arrays)."""
import os, shutil, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\GPU Track Algo (Saleh Lab)\GPU Tracking Demo_Fixed discretization error in lateral tracking\GPU Tracking\TrackBatchOfImagesWithGPU.vi"
DST = os.path.join(g.CLAUDEDEV, "GPU_kernel_probe.vi")
if os.path.exists(DST): os.remove(DST)
shutil.copyfile(SRC, DST); g.report(DST, "SubVI"); g.open_panel(DST); time.sleep(1.0)
clfn = g.report(DST, "CallLibrary")[0]["uid"]; print("CLFN uid", clfn, flush=True)
# delete every other node
while True:
    nodes = g.report(DST, "Node"); others = [i for i, o in enumerate(nodes) if o["uid"] != clfn]
    if not others: break
    try:
        g.delete_object(DST, "Node", others[0])
    except RuntimeError as e:                      # a structure takes its contents with it
        if "expected 1 object gone" not in str(e): raise
g.remove_bad_wires_scripted(DST)
while g.count(DST, "ControlTerminal"):
    g.delete_object(DST, "ControlTerminal", 0)
g.remove_bad_wires_scripted(DST)
print("stripped: nodes", g.count(DST, "Node"), "controls", g.count(DST, "ControlTerminal"), "wires", g.count(DST, "Wire"), "ExecState", g.exec_state(DST), flush=True)
nodes, nets = g.net_map(DST, 0, max_nodes=2, max_terms=40)
print("CLFN terminals:", [(t, nm) for t, nm, w in nodes[0][2]], flush=True)
vi = g.op(DST)
for t, nm, w in nodes[0][2]:
    fp0 = {l for _, l, _ in g.fp_labels(DST)}
    new, label = g.create_control(DST, 0, t)
    if not new:
        new = g.create_indicator(DST, 0, t); labs = [l for _, l, _ in g.fp_labels(DST) if l not in fp0]; label = labs[-1] if labs else None; kind = "IND"
    else:
        kind = "CTRL"
    try:
        v = vi.GetControlValue(label) if label else None; desc = f"{type(v).__name__} {np.array(v, dtype=object).shape if hasattr(v, '__len__') and not isinstance(v, str) else v}"
    except Exception as e:
        desc = "read ERR " + str(e)[:60]
    print(f"  t{t} {nm!r}: {kind} label={label!r} value={desc} wires={g.count(DST, 'Wire')} ExecState={g.exec_state(DST)}", flush=True)
print("saved", g.save(DST, allow_broken=True) if g.exec_state(DST) != 1 else g.save(DST), flush=True)
