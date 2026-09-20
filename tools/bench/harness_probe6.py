"""quad-fit and fit-to-cal harnesses with DBL inputs: LabVIEW vs NumPy."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "gpu")); sys.path.insert(0, HERE)
import gscript as g, ref_numpy as r, subvi_harness as sh
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
reg = json.load(open(os.path.join(HERE, "subvi_harnesses.json")))
hq = reg["tracking- quadratic fit to phase nghbrd"]
for ph in ([0.1, 0.05, 0.0, -0.05, -0.1], [0.0335, -0.0332, -0.0966, -0.1617, -0.2252], [0.21, 0.13, 0.02, -0.07, -0.20], [0.3, 0.1, 0.05, -0.02, -0.1]):
    o = sh.run(hq, {"neighborhood phases": ph, "index of best-fit cal image slice": 29}, ["bead z pos as a cal image index"])
    print(f"quad: phases {ph} -> LV {float(o['bead z pos as a cal image index']):.8f}  np {r.quad_fit_phase(ph, 29):.8f}", flush=True)
hf = reg["Tracking-fit prepped I of r to cal"]
win_rs, win_h, cals = r.load_inputs(); c = cals[0]
prep = c["real"][29] * 0.8 + 0.3
o = sh.run(hf, {"prepped I(r)": [float(v) for v in prep], "Real portion of hilbert/bandpass filtered r-shifted claibration image": [[float(v) for v in row] for row in c["real"]]},
           ["Index of closest cal image slice"])
print("fit-to-cal: LV", o["Index of closest cal image slice"], "np", r.fit_prep_to_cal(prep, c["real"]), flush=True)
