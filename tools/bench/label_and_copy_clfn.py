"""label the donor's Call Library Function Node (inside its loop) with OpSetLabel, then copy_into a fresh VI and check that a
CallLibrary object arrived.  py tools/bgrun.py --max-min 15 --log tools/bench/label_copy_clfn.log -- py -u tools/bench/label_and_copy_clfn.py"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\GPU Track Algo (Saleh Lab)\GPU Tracking Demo_Fixed discretization error in lateral tracking\GPU Tracking\TrackBatchOfImagesWithGPU.vi"
DONOR = os.path.join(g.CLAUDEDEV, "DONOR_clfn.vi"); TARGET = os.path.join(g.CLAUDEDEV, "GPU_clfn_target.vi")
for p in (DONOR, TARGET):
    if os.path.exists(p): os.remove(p)
shutil.copyfile(SRC, DONOR); shutil.copyfile(os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi"), TARGET)
g.report(DONOR, "SubVI"); g.open_panel(DONOR); time.sleep(1.0)
clfn = g.report(DONOR, "CallLibrary")[0]["uid"]; nd = g.count(DONOR, "Diagram"); print("CLFN uid", clfn, "diagrams", nd, flush=True)
found = None
for d in range(nd):
    nodes, nets = g.net_map(DONOR, d, max_nodes=40, max_terms=3)
    uids = [v[0] for v in nodes.values()]
    if clfn in uids:
        found = (d, uids.index(clfn)); print(f"CLFN is Nodes[{found[1]}] of diagram {d}; terminals of that node (first 3): {nodes[found[1]][2]}", flush=True); break
    print(f"diagram {d}: {len(uids)} nodes", flush=True)
if not found:
    print("STOP: CLFN not found in any diagram", flush=True); sys.exit(2)
uid = g.set_node_label(DONOR, found[0], found[1], "CLFN_DONOR"); print("set_node_label -> UID", uid, flush=True)
print("donor saved (labelled):", g.save(DONOR, allow_broken=True), flush=True)
g.close_panel(DONOR); time.sleep(1.0)
try:
    added = g.copy_into(DONOR, "CLFN_DONOR", TARGET); print("copy_into added:", added, flush=True)
except Exception as e:
    print("copy_into failed:", str(e)[:200], flush=True); sys.exit(3)
g.report(TARGET, "SubVI")
print("target CallLibrary:", g.report(TARGET, "CallLibrary"), "nodes", g.count(TARGET, "Node"), "ExecState", g.exec_state(TARGET), flush=True)
nodes, nets = g.net_map(TARGET, 0, max_nodes=6, max_terms=40)
for n, (u, _, terms) in nodes.items():
    print(f"  node {n} uid {u}: {[(t, nm) for t, nm, w in terms]}", flush=True)
