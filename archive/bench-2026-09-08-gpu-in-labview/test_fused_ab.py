"""test_fused_ab.py - A/B of the fused single-launch kernel vs the classic ~25-call path, through the LabVIEW-handle entry
(GPUTracking_lv, cluster route), N chained fixture frames: |fused - classic| and both vs the LabVIEW reference, plus
DLL-internal times (t=..., e=GPU event ms)."""
import ctypes as C, os, re, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0], "--n=1"]
import test_dll_lv3 as T
from fixture import read_image
lib = T.lib; f = lib.GPUTracking_lv; f.restype = C.c_int; lib.mt_gpu_set_fused.restype = C.c_int
N = int(os.environ.get("N", "40")); hcal = T.cal_handle_dbl(); rows = T.rows; nb = T.nb


def run_mode(fused):
    lib.mt_gpu_set_fused(int(fused)); outs = []; ts = []; es = []; poss = []; goods = []
    for k in range(0, len(rows), max(1, len(rows) // N)):
        row = rows[k]
        if k == 0:
            state = T.cal["xy"]; good_in = [1] * nb
        else:
            prev = rows[k - 1]; lost = any(v == -1.0 for v in prev["ff"])
            state = T.cal["xy"] if lost else np.array(prev["ff"]).reshape(-1, 3)[:, :2]; good_in = [1] * nb if lost else [int(g) for g in prev["good"]]
        xy_int = [[T.r.lv_round(x), T.r.lv_round(y)] for x, y in state]
        rc, txt, dt, out, pos, good = T.call(f, read_image(row["frame"]).astype(np.uint8), xy_int, good_in, hcal, " " * 64)
        assert rc == 0, txt
        m = re.search(rb"t=([\d.]+).*e=([\d.]+)", txt); ts.append(float(m.group(1))); es.append(float(m.group(2)))
        outs.append((k, out, good_in)); poss.append(pos); goods.append(good)
    return outs, poss, goods, np.array(ts), np.array(es)


o1, p1, g1, t1, e1 = run_mode(1); o0, p0, g0, t0, e0 = run_mode(0)
worst_ab = 0.0; worst_lv = np.zeros(3); flips = 0; n = 0
for (k, a, gin), (_, b, _), pa, pb, ga, gb in zip(o1, o0, p1, p0, g1, g0):
    row = rows[k]
    for bd in range(nb):
        if not gin[bd] or row["ff"][3 * bd] == -1.0:
            continue
        worst_ab = max(worst_ab, float(np.max(np.abs(a[3 * bd:3 * bd + 3] - b[3 * bd:3 * bd + 3]))))
        if pa[bd] != pb[bd] or ga[bd] != gb[bd]:
            flips += 1
        if pa[bd] == row["pos"][bd]:
            worst_lv = np.maximum(worst_lv, np.abs(a[3 * bd:3 * bd + 3] - np.array(row["ff"][3 * bd:3 * bd + 3])))
    n += 1
print(f"A/B over {n} frames: worst |fused - classic| {worst_ab:.2e} (x,y px / z um); index/good mismatches {flips}", flush=True)
print(f"fused vs LabVIEW: worst |dx| {worst_lv[0]:.2e} px |dy| {worst_lv[1]:.2e} px |dz| {worst_lv[2]:.2e} um", flush=True)
print(f"DLL-internal median: fused {np.median(t1[1:]):.2f} ms (GPU event {np.median(e1[1:]):.2f}) | classic {np.median(t0[1:]):.2f} ms (GPU event {np.median(e0[1:]):.2f})", flush=True)
