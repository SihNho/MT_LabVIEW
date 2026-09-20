"""copy the Saleh-lab CLFN into a fresh VI: label it inside copy_into's prepare hook (the donor is broken and cannot be saved)."""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\GPU Track Algo (Saleh Lab)\GPU Tracking Demo_Fixed discretization error in lateral tracking\GPU Tracking\TrackBatchOfImagesWithGPU.vi"
TARGET = os.path.join(g.CLAUDEDEV, "GPU_clfn_target.vi")
if os.path.exists(TARGET): os.remove(TARGET)
shutil.copyfile(os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi"), TARGET)


def prepare(src):
    g.report(src, "SubVI")
    try:
        g.open_panel(src)
    except Exception as e:
        print("open_panel:", str(e)[:80], flush=True)
    time.sleep(1.0)
    print("prepare: CallLibrary in source:", g.report(src, "CallLibrary"), flush=True)
    print("prepare: set_node_label ->", g.set_node_label(src, 4, 0, "CLFN_DONOR"), flush=True)


added = g.copy_into(SRC, "CLFN_DONOR", TARGET, prepare=prepare); print("copy_into added:", added, flush=True)
g.report(TARGET, "SubVI"); g.open_panel(TARGET); time.sleep(1.0)
print("target CallLibrary:", g.report(TARGET, "CallLibrary"), "nodes", g.count(TARGET, "Node"), "ExecState", g.exec_state(TARGET), flush=True)
nodes, nets = g.net_map(TARGET, 0, max_nodes=4, max_terms=40)
for n, (u, _, terms) in nodes.items():
    print(f"  node {n} uid {u}: {[(t, nm) for t, nm, w in terms]}", flush=True)
