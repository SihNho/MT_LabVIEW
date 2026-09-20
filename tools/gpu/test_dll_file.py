"""test_dll_file.py - the file-route entry (GPUTracking_file / _auto with an EMPTY cluster array): cal path in the text buffer."""
import ctypes as C, sys, time, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_dll as T
from fixture import read_cal, read_reference, read_image, CAL
import ref_numpy as r
lib = T.lib; win_rs, win_h, cals = r.load_inputs(); cal = read_cal(); rows = read_reference()["frames"]; nb = len(cals); cross = 120
row = rows[0]; img = read_image(row["frame"]).astype(np.uint8)
xyz = np.array([[x, y, 0.0] for x, y in cal["xy"]]).reshape(-1)
hx, vxo = T.arr_handle(xyz.copy(), "d1"); hy, vyo = T.arr_handle(np.zeros(nb, np.int32), "i1"); himg, _ = T.arr_handle(img, "u2")
hxo = C.c_void_p(0); hyo, _ = T.arr_handle(win_h, "d1"); hzo, vzo = T.arr_handle(np.ones(nb, np.uint8), "b1")
hbs, _ = T.arr_handle(np.ones(nb, np.uint8), "b1"); htest, _ = T.arr_handle(win_rs, "d1")
empty = T.handle(T.Arr1D, [0], 0)[0]                       # empty cluster array handle {n=0}
for name, hcal in (("GPUTracking_file", C.c_void_p(0)), ("GPUTracking_auto", empty)):
    f = getattr(lib, name); f.restype = C.c_int
    text = C.create_string_buffer(CAL.encode("mbcs") + b" " * 8, 256)
    C.memmove(vxo[0], xyz.tobytes(), 8 * xyz.size)
    t0 = time.perf_counter(); rc = f(0, 0, 0, 0, 0, hx, hy, cross, 10, himg, hxo, hyo, hzo, hcal, hbs, text, htest); dt = time.perf_counter() - t0
    out = T.read_back(vxo); pos = T.read_back(vyo); good = T.read_back(vzo)
    print(f"{name}: rc {rc} text {text.value!r} {1e3 * dt:.1f} ms (incl. cal load); x,y,z {out[:6].round(6)} pos {pos} good {good}")
    print(f"    reference frame {row['frame']}: {np.array(row['ff'][:6]).round(6)} pos {row['pos']} good {row['good']}; max|diff| {np.max(np.abs(out - np.array(row['ff']))):.2e}")
    C.memmove(vxo[0], xyz.tobytes(), 8 * xyz.size); text = C.create_string_buffer(CAL.encode("mbcs") + b" " * 8, 256)
    t0 = time.perf_counter(); rc = f(0, 0, 0, 0, 0, hx, hy, cross, 10, himg, hxo, hyo, hzo, hcal, hbs, text, htest)
    print(f"    second call (cached) {1e3 * (time.perf_counter() - t0):.1f} ms rc {rc} {text.value!r}")
