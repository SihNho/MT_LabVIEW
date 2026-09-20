"""test_mt2.py - the v2 interface from Python: mt2_open(cal) -> mt2_set_image(strided buffer like an IMAQ image: line width
= width + 64) -> mt2_track over N chained fixture frames vs the LabVIEW reference; DLL-internal timings from the status."""
import ctypes as C, os, re, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixture import read_cal, read_reference, read_image, CAL
import ref_numpy as r
import test_dll as T                                              # same DLL search-path setup (cudart/cufft) as the other tests
lib = T.lib
lib.mt2_open.restype = C.c_int64; lib.mt2_open.argtypes = [C.c_char_p, C.c_int, C.c_int, C.c_char_p, C.c_int]
lib.mt2_set_image.argtypes = [C.c_int64, C.c_uint64, C.c_int, C.c_int, C.c_int]; lib.mt2_set_image.restype = C.c_int
D = C.POINTER(C.c_double); U8 = C.POINTER(C.c_ubyte); I = C.POINTER(C.c_int)
lib.mt2_track.argtypes = [C.c_int64, C.c_int, D, U8, D, I, U8, C.c_char_p, C.c_int]; lib.mt2_track.restype = C.c_int
lib.mt2_close.argtypes = [C.c_int64]
N = int(os.environ.get("N", "40")); KA = int(os.environ.get("KA", "0"))
cal = read_cal(); rows = read_reference()["frames"]; nb = len(cal["xy"]); cross = 120
status = C.create_string_buffer(128)
ctx = lib.mt2_open(CAL.encode("mbcs"), cross, KA, status, 128); print("mt2_open ->", ctx != 0, status.value)
assert ctx
H, W = 1024, 1280; LW = W + 64
buf = np.zeros((H, LW), np.uint8)                                  # strided host buffer standing in for the IMAQ image
worst = np.zeros(3); flips = 0; ts = []; n_done = 0
for k in range(0, len(rows), max(1, len(rows) // N)):
    row = rows[k]
    if k == 0:
        state = [[x, y, 0.0] for x, y in cal["xy"]]; good_in = [1] * nb
    else:
        prev = rows[k - 1]; lost = any(v == -1.0 for v in prev["ff"])
        state = [[x, y, 0.0] for x, y in cal["xy"]] if lost else np.array(prev["ff"]).reshape(-1, 3).tolist(); good_in = [1] * nb if lost else [int(g) for g in prev["good"]]
    img = read_image(row["frame"]); buf[:, :W] = img
    assert lib.mt2_set_image(ctx, buf.ctypes.data, LW, W, H) == 0
    xyz_in = np.array(state, np.float64).ravel(); gin = np.array(good_in, np.uint8); xyz_out = np.zeros(3 * nb); idx = np.zeros(nb, np.int32); gout = np.zeros(nb, np.uint8)
    t0 = time.perf_counter(); rc = lib.mt2_track(ctx, nb, xyz_in.ctypes.data_as(D), gin.ctypes.data_as(U8), xyz_out.ctypes.data_as(D), idx.ctypes.data_as(I), gout.ctypes.data_as(U8), status, 128); dt = time.perf_counter() - t0
    assert rc == 0, status.value
    m = re.search(rb"t=([\d.]+)", status.value); ts.append(float(m.group(1)))
    for b in range(nb):
        if not good_in[b] or row["ff"][3 * b] == -1.0:
            continue
        if idx[b] != row["pos"][b]:
            flips += 1; continue
        worst = np.maximum(worst, np.abs(xyz_out[3 * b:3 * b + 3] - np.array(row["ff"][3 * b:3 * b + 3])))
    n_done += 1
print(f"mt2 over {n_done} frames: worst |dx| {worst[0]:.2e} px |dy| {worst[1]:.2e} px |dz| {worst[2]:.2e} um vs LabVIEW; flips {flips}; "
      f"DLL-internal median {np.median(ts[1:]):.2f} ms; last status {status.value!r}; wall {1e3*dt:.2f} ms")
lib.mt2_close(ctx)
