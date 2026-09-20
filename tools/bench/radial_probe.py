"""radial_probe.py - radial-profile harness: LabVIEW vs NumPy with SGL emulation on/off, 3 beads, frame 4."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "gpu")); sys.path.insert(0, HERE)
import gscript as g, ref_numpy as r, subvi_harness as sh
from fixture import read_cal, read_image
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
reg = json.load(open(os.path.join(HERE, "subvi_harnesses.json"))); h = reg["tracking-calculate radial profile-openv2"]
win_rs, win_h, cals = r.load_inputs(); img = read_image(4); cal = read_cal()
np.set_printoptions(precision=9, linewidth=200)
for b in (0, 1, 3):
    x, y = cal["xy"][b]; xi, yi = r.lv_round(x), r.lv_round(y)
    res = r.track_bead(img, xi, yi, 120, win_rs, win_h, cals[b], r.Params())
    sub = r.sub_image(img, xi, yi, 72, "yx"); sx = res["x"] - xi; sy = res["y"] - yi
    o = sh.run(h, {"Input Image": [[int(v) for v in row] for row in sub], "half cross": 60, "x center": float(72 + sx), "y center": float(72 + sy)}, ["radial intensity profile"])
    lv = np.array(o["radial intensity profile"])
    for sgl in (True, False):
        mine = r.radial_profile(sub, 72 + sx, 72 + sy, 60, sgl)
        d = np.abs(lv - mine); print(f"bead {b} sgl={sgl}: max|diff| {d.max():.3e} at {d.argmax()}; n(diff>1e-9) {(d > 1e-9).sum()}", flush=True)
    print("   LV[40:44]", lv[40:44], "\n   sgl [40:44]", r.radial_profile(sub, 72 + sx, 72 + sy, 60, True)[40:44], flush=True)
    # what does LV do with float32 for the whole thing? emulate sum-in-float32 of products rounded to float32
    np.savez(os.path.join(HERE, f"radial_probe_b{b}.npz"), lv=lv, sub=sub, xc=72 + sx, yc=72 + sy)
