"""test_dll_lv2.py - the LabVIEW-handle entries with the DONOR's fixed parameter types (2026-09-08 09:5x):
X Array I32[] unused | Y Array I32[nb] pos in/out | Array of Images U8 2-D | X Output DBL 2-D [nb][3] x,y,z in/out |
Y/Z Output DBL 2-D unused | Array Cal Cluster | Bead Is Good Array U8[nb] in/out | Error Message C string | Test Array DBL[cross] win_rs.
Runs GPUTracking_lv (cluster route), GPUTracking_file and GPUTracking_auto (both routes) on fixture frame 4 and a state-chained
sweep of N frames through the cluster route, against the LabVIEW reference.  No LabVIEW needed."""
import ctypes as C, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_dll as T
from fixture import read_cal, read_reference, read_image, CAL
import ref_numpy as r

lib = T.lib; win_rs, win_h, cals = r.load_inputs(); cal = read_cal(); rows = read_reference()["frames"]; nb = len(cals); cross = 120
N = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--n=")), 40))


def handles(img, xyz2d, good):
    hx, _ = T.arr_handle(np.zeros(nb, np.int32), "i1"); hy, vy = T.arr_handle(np.zeros(nb, np.int32), "i1"); himg, _ = T.arr_handle(img, "u2")
    hxo, vxo = T.arr_handle(np.asarray(xyz2d, np.float64), "d2"); hyo, _ = T.arr_handle(np.zeros((0, 0)), "d2"); hzo, _ = T.arr_handle(np.zeros((0, 0)), "d2")
    hbs, vbs = T.arr_handle(np.asarray(good, np.uint8), "b1"); htest, _ = T.arr_handle(win_rs, "d1")
    return hx, hy, himg, hxo, hyo, hzo, hbs, htest, vxo, vy, vbs


row = rows[0]; img = read_image(row["frame"]).astype(np.uint8); xyz2d = [[x, y, 0.0] for x, y in cal["xy"]]
hcal = T.cal_handle(cals); empty = T.handle(T.Arr1D, [0], 0)[0]
for name, hc, textin in (("GPUTracking_lv", hcal, " " * 64), ("GPUTracking_file", C.c_void_p(0), CAL + " " * 8),
                         ("GPUTracking_auto", hcal, " " * 64), ("GPUTracking_auto", empty, CAL + " " * 8)):
    f = getattr(lib, name); f.restype = C.c_int
    hx, hy, himg, hxo, hyo, hzo, hbs, htest, vxo, vy, vbs = handles(img, xyz2d, [1] * nb)
    text = C.create_string_buffer(textin.encode("mbcs"), 256)
    t0 = time.perf_counter(); rc = f(0, 0, 0, 0, 0, hx, hy, cross, 10, himg, hxo, hyo, hzo, hc, hbs, text, htest); dt = time.perf_counter() - t0
    out = T.read_back(vxo); pos = T.read_back(vy); good = T.read_back(vbs)
    print(f"{name} ({'cluster' if hc is hcal else 'file'}): rc {rc} text {text.value!r} {1e3 * dt:.1f} ms; x,y,z {out[:6].round(6)} pos {pos} good {good}; "
          f"max|diff| vs LabVIEW frame {row['frame']}: {np.max(np.abs(out - np.array(row['ff']))):.2e}", flush=True)
# state-chained sweep through the cluster route (as the timing harness will run it)
f = lib.GPUTracking_lv; f.restype = C.c_int; worst = np.zeros(3); flips = 0; t_sum = 0.0; n_done = 0
for k in range(0, len(rows), max(1, len(rows) // N)):
    row = rows[k]
    if k == 0:
        state = [[x, y, 0.0] for x, y in cal["xy"]]; good_in = [1] * nb
    else:
        prev = rows[k - 1]; lost = any(v == -1.0 for v in prev["ff"])
        state = [[x, y, 0.0] for x, y in cal["xy"]] if lost else np.array(prev["ff"]).reshape(-1, 3).tolist(); good_in = [1] * nb if lost else [int(g) for g in prev["good"]]
    img = read_image(row["frame"]).astype(np.uint8)
    hx, hy, himg, hxo, hyo, hzo, hbs, htest, vxo, vy, vbs = handles(img, state, good_in); text = C.create_string_buffer(b" " * 64, 256)
    t0 = time.perf_counter(); rc = f(0, 0, 0, 0, 0, hx, hy, cross, 10, himg, hxo, hyo, hzo, hcal, hbs, text, htest); t_sum += time.perf_counter() - t0
    assert rc == 0, text.value
    out = T.read_back(vxo); pos = T.read_back(vy)
    for b in range(nb):
        if not good_in[b] or row["ff"][3 * b] == -1.0:
            continue
        if pos[b] != row["pos"][b]:
            flips += 1; continue
        worst = np.maximum(worst, np.abs(out[3 * b:3 * b + 3] - np.array(row["ff"][3 * b:3 * b + 3])))
    n_done += 1
print(f"sweep {n_done} frames (cluster route): worst |dx| {worst[0]:.2e} px |dy| {worst[1]:.2e} px |dz| {worst[2]:.2e} um vs LabVIEW; index flips {flips}; "
      f"{1e3 * t_sum / n_done:.2f} ms/frame", flush=True)
