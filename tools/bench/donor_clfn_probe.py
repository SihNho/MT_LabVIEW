"""find Call Library Function Nodes in the Saleh-lab GPU demo VIs (copies in claudeDev\SPEC) and list their terminals."""
import os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\GPU Track Algo (Saleh Lab)\GPU Tracking Demo_Fixed discretization error in lateral tracking\GPU Tracking\TrackBatchOfImagesWithGPU.vi"
DST = os.path.join(g.CLAUDEDEV, "SPEC", "DONOR_TrackBatchOfImagesWithGPU.vi")
if os.path.exists(DST): os.remove(DST)
shutil.copyfile(SRC, DST)
for cls in ("CallLibrary", "CallLibraryNode", "Node", "SubVI", "ControlTerminal", "Constant"):
    try:
        objs = g.report(DST, cls); print(cls, len(objs), [(o["uid"], tuple(o["pos"])) for o in objs][:12], flush=True)
    except Exception as e:
        print(cls, "ERR", str(e)[:100], flush=True)
print("fp:", g.fp_labels(DST), flush=True)
print("ExecState", g.exec_state(DST), flush=True)
try:
    print("node_info:", g.node_info(DST), flush=True)
except Exception as e:
    print("node_info ERR", str(e)[:100], flush=True)
