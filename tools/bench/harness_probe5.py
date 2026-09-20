import os, sys, json
import numpy as np, pythoncom
from win32com.client import VARIANT
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "gpu")); sys.path.insert(0, HERE)
import gscript as g, ref_numpy as r
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
reg = json.load(open(os.path.join(HERE, "subvi_harnesses.json"))); h = reg["Tracking-prep I of r"]; path = h["path"]
win_rs, win_h, cals = r.load_inputs(); cb = cals[0]["cosband"]
vi = g.op(path); lab = h["controls"]["cosine bandpass"]
tests = {
 "VARIANT R8 2D pairs": VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [[float(x), 0.0] for x in cb]),
 "VARIANT R8 1D": VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [float(x) for x in cb]),
 "tuple of tuples": tuple((float(x), 0.0) for x in cb),
 "VARIANT R4 1D": VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R4, [float(x) for x in cb]),
 "VARIANT VARIANT 1D": VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, [float(x) for x in cb]),
 "np float64 array": np.asarray(cb, dtype=np.float64),
 "np complex array": np.asarray(cb, dtype=complex),
}
for name, val in tests.items():
    try:
        vi.SetControlValue(lab, val); back = vi.GetControlValue(lab); a = np.array(back, dtype=object)
        print(f"{name}: readback type {type(back).__name__} shape {a.shape} first {str(back)[:60]}", flush=True)
    except Exception as e:
        print(f"{name}: FAILED {str(e)[:120]}", flush=True)
# also: what does the radial-profile control give when read back (a DBL array) vs the cosband control default?
print("radial ctrl readback:", str(vi.GetControlValue(h["controls"]["radial intensity profile"]))[:80], flush=True)
