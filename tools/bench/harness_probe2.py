import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "gpu")); sys.path.insert(0, HERE)
import gscript as g, ref_numpy as r, subvi_harness as sh
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
reg = json.load(open(os.path.join(HERE, "subvi_harnesses.json"))); h = reg["Tracking-prep I of r"]; path = h["path"]
win_rs, win_h, cals = r.load_inputs(); c = cals[0]
rad = list(np.arange(60, dtype=float))
vi = g.op(path)
print("labels:", g.fp_labels(path), flush=True)
lab = lambda k: h["controls"].get(k) or h["indicators"].get(k)
for k, v in (("radial intensity profile", [float(x) for x in rad]), ("cosine bandpass", [float(x) for x in c["cosband"]]), ("forget radius", 23), ("halfcross", 60)):
    try:
        vi.SetControlValue(lab(k), v); print("set", k, "->", np.array(vi.GetControlValue(lab(k))).shape, flush=True)
    except Exception as e:
        print("set", k, "FAILED", str(e)[:150], flush=True)
try:
    vi.SetControlValue(lab("cosine bandpass"), [[float(x), 0.0] for x in c["cosband"]]); print("set cosband as (re,im) pairs ->", np.array(vi.GetControlValue(lab("cosine bandpass"))).shape, flush=True)
except Exception as e:
    print("complex set FAILED", str(e)[:150], flush=True)
g._run(vi)
for _, l, ind in g.fp_labels(path):
    a = np.array(vi.GetControlValue(l)); print(f"  {l[:30]!r} ind={ind}: shape {a.shape} {a.ravel()[:3]}", flush=True)
