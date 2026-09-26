import json, glob, os, struct, sys
import numpy as np
B = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench"
ls = sorted(glob.glob(os.path.join(B, "t0_legs", "c94_step4v2_2026*")))
print(ls[-3:])
d = [x for x in ls if not x.endswith("_dry")][-1]
print(os.listdir(d))
j = json.load(open(glob.glob(os.path.join(d, "leg4_A_p15_a1", "leg.json"))[0]))
rd = j["facts"]["run_dir"]; print(rd, j["facts"]["tra"])
f = [x for x in os.listdir(rd) if x.lower().startswith("tra")][0] if os.path.isdir(rd) else None
print(f)
if f:
    b = open(os.path.join(rd, f), "rb").read(); k = b.find(b"not in z!)") + 10
    print(b[:k][-600:])
    r, c = struct.unpack("<ii", b[k:k + 8]); a = np.frombuffer(b[k + 8:], dtype="<f8").reshape(r, c)
    print(r, c, a[:5, :4]); dt = np.diff(a[:, 0]); print("dt median", np.median(dt), np.percentile(dt, 95), a[-1, 0] - a[0, 0])
