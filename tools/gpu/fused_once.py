import ctypes as C, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_dll as T
from fixture import read_cal, read_reference, read_image
import ref_numpy as r
lib = T.lib; win_rs, win_h, cals = r.load_inputs(); cal = read_cal(); rows = read_reference()["frames"]; nb = len(cals); cross = 120
D = C.POINTER(C.c_double); I = C.POINTER(C.c_int)
lib.mt_gpu_set_fused(int(os.environ.get("FUSED", "1")))
h = C.c_void_p(); rc = lib.mt_gpu_init(cross, int(cals[0]["n_slices"]), nb, win_rs.ctypes.data_as(D), win_h.ctypes.data_as(D), C.byref(h)); assert rc == 0, lib.mt_gpu_last_error()
for b, c in enumerate(cals):
    L = c["real"].shape[1]
    rc = lib.mt_gpu_set_bead(h, b, int(c["forget_radius"]), C.c_double(float(c["z_step"])), np.ascontiguousarray(np.real(c["cosband"])).ctypes.data_as(D), None,
                             np.ascontiguousarray(c["real"]).ctypes.data_as(D), np.ascontiguousarray(c["ampl"]).ctypes.data_as(D),
                             np.ascontiguousarray(c["cork"].real).ctypes.data_as(D), np.ascontiguousarray(c["cork"].imag).ctypes.data_as(D), L)
    assert rc == 0, lib.mt_gpu_last_error()
img = read_image(rows[0]["frame"]).astype(np.uint8); xi = np.array([r.lv_round(x) for x, y in cal["xy"]], np.int32); yi = np.array([r.lv_round(y) for x, y in cal["xy"]], np.int32)
gi = np.ones(nb, np.int32); xo = np.zeros(nb); yo = np.zeros(nb); zo = np.zeros(nb); io = np.zeros(nb, np.int32); go = np.zeros(nb, np.int32)
rc = lib.mt_gpu_track_any(h, img.ctypes.data_as(C.POINTER(C.c_ubyte)), img.shape[0], img.shape[1], nb, xi.ctypes.data_as(I), yi.ctypes.data_as(I), gi.ctypes.data_as(I),
                          xo.ctypes.data_as(D), yo.ctypes.data_as(D), zo.ctypes.data_as(D), io.ctypes.data_as(I), go.ctypes.data_as(I))
print("rc", rc, lib.mt_gpu_last_error() if rc else "", "x,y,z", np.c_[xo, yo, zo][:2].round(6).tolist(), "idx", io.tolist(), "good", go.tolist(), "ref", np.array(rows[0]["ff"][:6]).round(6).tolist())
