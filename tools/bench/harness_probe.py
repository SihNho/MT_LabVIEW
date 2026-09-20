import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "gpu")); sys.path.insert(0, HERE)
import gscript as g, ref_numpy as r
from fixture import read_cal, read_image
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
reg = json.load(open(os.path.join(HERE, "subvi_harnesses.json")))
h = reg["tracking-calculate radial profile-openv2"]; path = h["path"]
print("fp:", g.fp_labels(path), flush=True)
nodes, nets = g.net_map(path, 0, max_nodes=3, max_terms=12)
print("nodes:", {n: v[2] for n, v in nodes.items()}, flush=True)
print("wires:", g.count(path, "Wire"), "ExecState", g.exec_state(path), flush=True)
cal = read_cal(); img = read_image(4); x, y = cal["xy"][0]; xi, yi = r.lv_round(x), r.lv_round(y)
sub = r.sub_image(img, xi, yi, 72, "yx")
vi = g.op(path)
vi.SetControlValue("Input Image", [[int(v) for v in row] for row in sub]); vi.SetControlValue("half cross", 60)
vi.SetControlValue("x center", 72.4); vi.SetControlValue("y center", 71.7)
print("readback half cross", vi.GetControlValue("half cross"), "image", np.array(vi.GetControlValue("Input Image")).shape, flush=True)
g._run(vi)
for _, l, ind in g.fp_labels(path):
    v = vi.GetControlValue(l); a = np.array(v)
    print(f"  {l!r} ind={ind}: shape {a.shape} {a.ravel()[:4]}", flush=True)
