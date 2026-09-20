import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g
from fixture import read_cal, read_reference, DATA, CAL
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
OP = os.path.join(g.CLAUDEDEV, "HARNESS_gpu.vi"); lab = json.load(open(os.path.join(HERE, "harness_gpu_labels.json"))); C = lab["controls"]
xy0 = read_cal()["xy"]; row = read_reference()["frames"][0]; nb = len(xy0)
ld = g.op(os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")); ld.SetControlValue("file (use dialog)", CAL); g._run(ld)
vi = g.op(OP); vi.SetControlValue(C["Image Name"], "gpu"); p = os.path.join(DATA, f"img{row['frame']:05d}.tif"); print("image file exists", os.path.exists(p), p, flush=True)
vi.SetControlValue(C["File Path"], p)
vi.SetControlValue(C["xy int in"], [int(round(v)) for x, y in xy0 for v in (x, y)]); vi.SetControlValue(C["x,y,z array"], tuple((0.0,) * 9 for _ in xy0))
vi.SetControlValue(C["Bead is good? array in"], [True] * nb); vi.SetControlValue(C["pos in cal image in"], [0] * nb)
for rect in ([0, 0, 1280, 1024], [0, 0, 1279, 1023], [0, 0, 1024, 1280], [0, 0, 100, 100], [10, 10, 110, 110], [1, 1, 1279, 1023]):
    vi.SetControlValue(C["Optional Rectangle"], rect); print("rect set ->", vi.GetControlValue(C["Optional Rectangle"]), flush=True)
    vi.SetControlValue(C["Error Message"], " " * 64); g._run(vi)
    print(f"  rect {rect}: msg {vi.GetControlValue(lab['outputs']['Error Message out'])!r} | error out {vi.GetControlValue('error out')}", flush=True)
print("File Path readback:", repr(vi.GetControlValue(C["File Path"])), "Image Name:", repr(vi.GetControlValue(C["Image Name"])), flush=True)
