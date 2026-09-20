"""quad_probe.py - designed inputs for the quadratic-fit harness to identify LabVIEW's formula."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "gpu")); sys.path.insert(0, HERE)
import gscript as g, subvi_harness as sh
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
hq = json.load(open(os.path.join(HERE, "subvi_harnesses.json")))["tracking- quadratic fit to phase nghbrd"]
o = np.arange(5) - 2.0
cases = {
 "lin c=0.3": 0.05 * (o - 0.3),
 "lin c=-1.2": 0.05 * (o + 1.2),
 "lin steep c=0.3": 0.5 * (o - 0.3),
 "quad in o": 0.05 * (o - 0.3) + 0.01 * o ** 2,
 "quad in o 2": 0.1 * (o - 0.7) - 0.03 * o ** 2,
 "lin + bump at o=-2": 0.05 * (o - 0.3) + np.array([0.02, 0, 0, 0, 0]),
 "lin + bump at o=0": 0.05 * (o - 0.3) + np.array([0, 0, 0.02, 0, 0]),
 "lin + bump at o=+2": 0.05 * (o - 0.3) + np.array([0, 0, 0, 0, 0.02]),
 "lin + bump at o=+1": 0.05 * (o - 0.3) + np.array([0, 0, 0, 0.02, 0]),
 "phase of exact offset quadratic": None,
}
# offset = a phase^2 + b phase + c  ->  phases solving for offsets o: pick a=2,b=10,c=0.3 -> phase = root
a_, b_, c_ = 2.0, 10.0, 0.3
cases["phase of exact offset quadratic"] = np.array([(-b_ + np.sqrt(b_ * b_ - 4 * a_ * (c_ - oi))) / (2 * a_) for oi in o])
out = {}
for name, ph in cases.items():
    r = sh.run(hq, {"neighborhood phases": [float(v) for v in ph], "index of best-fit cal image slice": 29}, ["bead z pos as a cal image index"])
    z = float(r["bead z pos as a cal image index"]); out[name] = {"phases": [float(v) for v in ph], "lv": z}
    print(f"{name:34s} phases {np.array2string(ph, precision=5)} -> LV {z:.10f}", flush=True)
json.dump(out, open(os.path.join(HERE, "quad_probe.json"), "w"), indent=1)
