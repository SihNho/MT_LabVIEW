"""gpu_smoke_file.py - HARNESS_gpu.vi with the file-route DLL: inspect (wires/ExecState), then one fixture frame vs reference.
The cal path travels in the 'Error Message' string control (>= 60 chars; the DLL overwrites it with the status)."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g
from fixture import read_cal, read_reference, DATA, CAL
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
OP = os.path.join(g.CLAUDEDEV, "HARNESS_gpu.vi")
print("file", os.path.getsize(OP), time.ctime(os.path.getmtime(OP)), flush=True)
print("wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), "Invokes", g.count(OP, "Invoke"), flush=True)
lab = json.load(open(os.path.join(HERE, "harness_gpu_labels.json"))); C = lab["controls"]
xy0 = read_cal()["xy"]; rows = read_reference()["frames"]; nb = len(xy0)
ld = g.op(os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")); ld.SetControlValue("file (use dialog)", CAL); g._run(ld)
print("loader beads", ld.GetControlValue("# of beads"), flush=True)
vi = g.op(OP)
if "Optional Rectangle" in C:
    vi.SetControlValue(C["Optional Rectangle"], [0, 0, 1280, 1024])
vi.SetControlValue(C["Image Name"], "gpu")
for k in (0, 1):
    row = rows[k]
    vi.SetControlValue(C["File Path"], os.path.join(DATA, f"img{row['frame']:05d}.tif"))
    vi.SetControlValue(C["xy int in"], [int(round(v)) for x, y in xy0 for v in (x, y)]); vi.SetControlValue(C["x,y,z array"], tuple((0.0,) * 9 for _ in xy0)); vi.SetControlValue(C["Bead is good? array in"], [True] * nb)
    vi.SetControlValue(C["pos in cal image in"], [0] * nb); vi.SetControlValue(C["Error Message"], CAL + " " * 8)
    t0 = time.time(); g._run(vi); dt = time.time() - t0
    out = [float(row[3 * j]) + float(row[3 * j + 1]) / 16777216.0 + float(row[3 * j + 2]) / 16777216.0 ** 2 for row in vi.GetControlValue(lab["outputs"]["x,y,z array out"]) for j in range(3)]; msg = vi.GetControlValue(lab["outputs"]["Error Message out"])
    print(f"frame {row['frame']}: run {dt * 1e3:.0f} ms; msg {msg!r}; out {[round(v, 6) for v in out[:6]]}; ref {[round(v, 6) for v in row['ff'][:6]]}; "
          f"max|diff| {max(abs(a - b) for a, b in zip(out, row['ff'])):.2e}", flush=True)
    print("   pos", list(vi.GetControlValue(lab["outputs"]["pos in cal image out"])), "good", list(vi.GetControlValue(lab["outputs"]["Bead is good? array out"])), flush=True)
