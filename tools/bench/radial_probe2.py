"""radial_probe2.py - synthetic images through the radial-profile harness to expose LabVIEW's exact arithmetic."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "gpu")); sys.path.insert(0, HERE)
import gscript as g, subvi_harness as sh
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
h = json.load(open(os.path.join(HERE, "subvi_harnesses.json")))["tracking-calculate radial profile-openv2"]
n = 144; jj, ii = np.meshgrid(np.arange(n), np.arange(n))
imgs = {"const100": np.full((n, n), 100), "colidx": jj.copy(), "rowidx": ii.copy(), "delta_72_100": (ii == 72) & (jj == 100), "delta_50_60": (ii == 50) & (jj == 60),
        "delta_72_100_v255": ((ii == 72) & (jj == 100)) * 255, "checker": ((ii + jj) % 2) * 200}
out = {}
for cx, cy in ((72.4, 71.7), (72.0, 72.0), (71.55, 72.3)):
    for name, im in imgs.items():
        im = np.asarray(im).astype(int)
        o = sh.run(h, {"Input Image": [[int(v) for v in row] for row in im], "half cross": 60, "x center": float(cx), "y center": float(cy)}, ["radial intensity profile"])
        lv = np.array(o["radial intensity profile"]); out[f"{name}|{cx}|{cy}"] = lv
        print(f"{name} cx={cx} cy={cy}: {np.array2string(lv[:6], precision=9)} ... {np.array2string(lv[-3:], precision=9)}", flush=True)
np.savez(os.path.join(HERE, "radial_probe_synth.npz"), **out); print("saved", flush=True)
