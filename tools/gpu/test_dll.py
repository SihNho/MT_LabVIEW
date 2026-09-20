"""test_dll.py - exercise mt_track.dll from Python: (a) the plain mt_gpu_* API and (b) the LabVIEW-handle entry point
GPUTracking_lv with handles laid out exactly as LabVIEW 64-bit passes them; compare with the NumPy reference and the
LabVIEW reference on fixture frames.   py tools/gpu/test_dll.py [--n=20]
"""
import ctypes as C
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ref_numpy as r  # noqa: E402
from fixture import read_cal, read_image, read_reference  # noqa: E402

DLL = os.path.join(HERE, "cuda", "mt_track.dll")
os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin")
lib = C.CDLL(DLL)
lib.mt_gpu_last_error.restype = C.c_char_p
D = C.POINTER(C.c_double); I = C.POINTER(C.c_int)


# ---------------------------------------------------------------- LabVIEW 64-bit handle layouts (pack 8) ----------
class Arr1D(C.Structure):
    _fields_ = [("n", C.c_int32), ("pad", C.c_int32), ("d", C.c_double * 1)]


class ArrI32(C.Structure):
    _fields_ = [("n", C.c_int32), ("d", C.c_int32 * 1)]


class ArrU8(C.Structure):
    _fields_ = [("n", C.c_int32), ("d", C.c_uint8 * 1)]


class Arr2U8(C.Structure):
    _fields_ = [("rows", C.c_int32), ("cols", C.c_int32), ("d", C.c_uint8 * 1)]


class Arr2D(C.Structure):
    _fields_ = [("rows", C.c_int32), ("cols", C.c_int32), ("d", C.c_double * 1)]


class Cal(C.Structure):
    _fields_ = [("forget", C.c_int32), ("zstep", C.c_float), ("cosband", C.c_void_p), ("ampl", C.c_void_p), ("cork", C.c_void_p),
                ("real", C.c_void_p), ("nslices", C.c_int32), ("pad", C.c_int32)]


_keep = []


def handle(struct_cls, header, payload_bytes):
    """allocate {header ints..., data} and return a pointer-to-pointer (LabVIEW handle) plus a numpy view of the data."""
    hsize = getattr(struct_cls, "d").offset                     # data offset = where LabVIEW's pack(8) layout puts it
    buf = C.create_string_buffer(hsize + payload_bytes)
    C.memmove(buf, bytes(np.array(header, dtype=np.int32).tobytes()) + b"\0" * (hsize - 4 * len(header)), hsize)
    p = C.cast(buf, C.c_void_p); pp = C.pointer(p); _keep.extend([buf, p, pp])
    return pp, C.addressof(buf) + hsize


def arr_handle(a, kind):
    a = np.ascontiguousarray(a)
    if kind == "d1":
        pp, addr = handle(Arr1D, [a.size], 8 * a.size); C.memmove(addr, a.astype(np.float64).tobytes(), 8 * a.size)
        return pp, (addr, np.float64, a.size)
    if kind == "i1":
        pp, addr = handle(ArrI32, [a.size], 4 * a.size); C.memmove(addr, a.astype(np.int32).tobytes(), 4 * a.size)
        return pp, (addr, np.int32, a.size)
    if kind == "b1":
        pp, addr = handle(ArrU8, [a.size], a.size); C.memmove(addr, a.astype(np.uint8).tobytes(), a.size)
        return pp, (addr, np.uint8, a.size)
    if kind == "u2":
        pp, addr = handle(Arr2U8, [a.shape[0], a.shape[1]], a.size); C.memmove(addr, a.astype(np.uint8).tobytes(), a.size)
        return pp, (addr, np.uint8, a.size)
    if kind == "d2":
        pp, addr = handle(Arr2D, [a.shape[0], a.shape[1]], 8 * a.size); C.memmove(addr, a.astype(np.float64).tobytes(), 8 * a.size)
        return pp, (addr, np.float64, a.size)
    if kind == "c2":
        inter = np.stack([a.real, a.imag], -1).astype(np.float64)
        pp, addr = handle(Arr2D, [a.shape[0], a.shape[1]], 16 * a.size); C.memmove(addr, inter.tobytes(), 16 * a.size)
        return pp, (addr, np.float64, 2 * a.size)
    raise ValueError(kind)


def read_back(view):
    addr, dt, n = view
    return np.frombuffer((C.c_char * (np.dtype(dt).itemsize * n)).from_address(addr), dtype=dt).copy()


def cal_handle(cals):
    nb = len(cals); hsize = 8
    buf = C.create_string_buffer(hsize + nb * C.sizeof(Cal)); C.memmove(buf, np.array([nb, 0], dtype=np.int32).tobytes(), 8)
    for b, c in enumerate(cals):
        cell = Cal.from_address(C.addressof(buf) + hsize + b * C.sizeof(Cal))
        cell.forget = int(c["forget_radius"]); cell.zstep = float(c["z_step"]); cell.nslices = int(c["n_slices"])
        for name, kind in (("cosband", "d1"), ("ampl", "d2"), ("cork", "c2"), ("real", "d2")):
            pp, _ = arr_handle(np.real(c["cosband"]) if name == "cosband" else c[name], kind)
            setattr(cell, name, C.cast(pp, C.c_void_p))
    p = C.cast(buf, C.c_void_p); pp = C.pointer(p); _keep.extend([buf, p, pp]); return pp


def main():
    N = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--n=")), 20))
    win_rs, win_h, cals = r.load_inputs(); cal = read_cal(); rows = read_reference()["frames"]; nb = len(cals); cross = 120
    # ---- (a) plain API
    h = C.c_void_p()
    rc = lib.mt_gpu_init(cross, int(cals[0]["n_slices"]), nb, win_rs.ctypes.data_as(D), win_h.ctypes.data_as(D), C.byref(h))
    assert rc == 0, lib.mt_gpu_last_error()
    for b, c in enumerate(cals):
        length = c["real"].shape[1]
        rc = lib.mt_gpu_set_bead(h, b, int(c["forget_radius"]), C.c_double(float(c["z_step"])), np.ascontiguousarray(np.real(c["cosband"])).ctypes.data_as(D), None,
                                 np.ascontiguousarray(c["real"]).ctypes.data_as(D), np.ascontiguousarray(c["ampl"]).ctypes.data_as(D),
                                 np.ascontiguousarray(c["cork"].real).ctypes.data_as(D), np.ascontiguousarray(c["cork"].imag).ctypes.data_as(D), length)
        assert rc == 0, lib.mt_gpu_last_error()
    worst_np = np.zeros(3); worst_lv = np.zeros(3); t_dll = 0.0; n_done = 0; flips = 0
    xo = np.zeros(nb); yo = np.zeros(nb); zo = np.zeros(nb); io = np.zeros(nb, np.int32); go = np.zeros(nb, np.int32)
    for k in range(0, len(rows), max(1, len(rows) // N)):
        row = rows[k]
        if k == 0:
            state = np.array(cal["xy"]); good_in = [True] * nb
        else:
            prev = rows[k - 1]; lost = any(v == -1.0 for v in prev["ff"]); state = np.array(cal["xy"]) if lost else np.array(prev["ff"]).reshape(-1, 3)[:, :2]; good_in = [True] * nb if lost else prev["good"]
        img = read_image(row["frame"]).astype(np.uint8); xi = np.array([r.lv_round(v) for v in state[:, 0]], np.int32); yi = np.array([r.lv_round(v) for v in state[:, 1]], np.int32)
        gi = np.array(good_in, np.int32)
        t0 = time.perf_counter()
        rc = lib.mt_gpu_track(h, img.ctypes.data_as(C.POINTER(C.c_ubyte)), img.shape[0], img.shape[1], nb, xi.ctypes.data_as(I), yi.ctypes.data_as(I), gi.ctypes.data_as(I),
                              xo.ctypes.data_as(D), yo.ctypes.data_as(D), zo.ctypes.data_as(D), io.ctypes.data_as(I), go.ctypes.data_as(I))
        t_dll += time.perf_counter() - t0
        assert rc == 0, lib.mt_gpu_last_error()
        for b in range(nb):
            if not good_in[b] or row["ff"][3 * b] == -1.0:
                continue
            ref = r.track_bead(img, int(xi[b]), int(yi[b]), cross, win_rs, win_h, cals[b])
            if ref["index"] != io[b]:
                flips += 1; continue
            worst_np = np.maximum(worst_np, np.abs([xo[b] - ref["x"], yo[b] - ref["y"], zo[b] - ref["z"]]))
            worst_lv = np.maximum(worst_lv, np.abs([xo[b] - row["ff"][3 * b], yo[b] - row["ff"][3 * b + 1], zo[b] - row["ff"][3 * b + 2]]))
        n_done += 1
    print(f"(a) plain API: {n_done} frames; DLL-vs-NumPy worst |dx| {worst_np[0]:.2e} |dy| {worst_np[1]:.2e} |dz| {worst_np[2]:.2e} um; "
          f"DLL-vs-LabVIEW worst |dx| {worst_lv[0]:.2e} |dy| {worst_lv[1]:.2e} |dz| {worst_lv[2]:.2e} um; index flips {flips}; "
          f"time {1e3 * t_dll / n_done:.2f} ms/frame (5 beads, incl. 1.3 MB image upload)", flush=True)
    lib.mt_gpu_free(h)
    # ---- (b) LabVIEW-handle entry point on frame 4
    row = rows[0]; img = read_image(row["frame"]).astype(np.uint8)
    xyz = np.array([[x, y, 0.0] for x, y in cal["xy"]]).reshape(-1)
    hx, vxo = arr_handle(xyz.copy(), "d1"); hy, vyo = arr_handle(np.zeros(nb, np.int32), "i1"); himg, _ = arr_handle(img, "u2")
    hxo = C.c_void_p(0); hyo, _ = arr_handle(win_h, "d1"); hzo, vzo = arr_handle(np.ones(nb, np.uint8), "b1")
    hcal = cal_handle(cals); hbs, _ = arr_handle(np.ones(nb, np.uint8), "b1"); htest, _ = arr_handle(win_rs, "d1")
    text = C.create_string_buffer(256)
    f = lib.GPUTracking_lv; f.restype = C.c_int
    t0 = time.perf_counter()
    rc = f(0, 0, 0, 0, 0, hx, hy, cross, 10, himg, hxo, hyo, hzo, hcal, hbs, text, htest)
    dt = time.perf_counter() - t0
    out = read_back(vxo); pos = read_back(vyo); good = read_back(vzo)
    print(f"(b) LabVIEW-handle entry: rc {rc} text {text.value!r} {1e3 * dt:.1f} ms; x,y,z {out[:6].round(6)} pos {pos} good {good}")
    print(f"    reference frame {row['frame']}: {np.array(row['ff'][:6]).round(6)} pos {row['pos']} good {row['good']}")
    print(f"    max|diff| vs LabVIEW reference: {np.max(np.abs(out - np.array(row['ff']))):.2e}")
    # second call (cached calibration) timing
    C.memmove(vxo[0], xyz.tobytes(), 8 * xyz.size)
    t0 = time.perf_counter(); rc = f(0, 0, 0, 0, 0, hx, hy, cross, 10, himg, hxo, hyo, hzo, hcal, hbs, text, htest); print(f"    second call {1e3 * (time.perf_counter() - t0):.1f} ms rc {rc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
