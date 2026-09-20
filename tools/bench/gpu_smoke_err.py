import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g
from fixture import read_cal, read_reference, DATA, CAL
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
OP = os.path.join(g.CLAUDEDEV, "HARNESS_gpu.vi"); lab = json.load(open(os.path.join(HERE, "harness_gpu_labels.json"))); C = lab["controls"]
xy0 = read_cal()["xy"]; row = read_reference()["frames"][0]; nb = len(xy0)
ld = g.op(os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")); ld.SetControlValue("file (use dialog)", CAL); g._run(ld)
vi = g.op(OP); vi.SetControlValue(C["Image Name"], "gpu"); vi.SetControlValue(C["File Path"], os.path.join(DATA, f"img{row['frame']:05d}.tif"))
vi.SetControlValue(C["xy int in"], [int(round(v)) for x, y in xy0 for v in (x, y)]); vi.SetControlValue(C["x,y,z array"], tuple((0.0,) * 9 for _ in xy0))
vi.SetControlValue(C["Bead is good? array in"], [True] * nb); vi.SetControlValue(C["pos in cal image in"], [0] * nb); vi.SetControlValue(C["Error Message"], CAL + " " * 8)
g._run(vi)
for name in ("error out", "Error Message 2", "X Output 2", "Y Array 2", "Bead Is Good Array 2", "X Array 4", "Threads 2", "Cross Size 2"):
    try:
        print(name, "=", repr(vi.GetControlValue(name))[:300], flush=True)
    except Exception as e:
        print(name, "EXC", str(e)[:100], flush=True)
