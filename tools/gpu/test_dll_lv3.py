"""test_dll_lv3.py - LabVIEW-handle entries with the donor's FIXED SINGLE-PRECISION types (2026-09-08 10:0x, Saleh datatypes.h +
COM round-trip): X Array I32[2nb] x_in,y_in | Y Array I32[nb] pos in/out | Image U8 2-D | X Output SGL 2-D [nb][9] = x,y,z each
as 3 exact SGL integers (hi, mid=frac*2^24, lo) | Y/Z Output unused | cluster array as dumped from LabVIEW (56-byte DBL elements) |
Bead Is Good U8[nb] in/out | Error Message | Test Array SGL[cross] win_rs.  Both cluster strides and both routes are tested."""
import ctypes as C, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_dll as T
from fixture import read_cal, read_reference, read_image, CAL
import ref_numpy as r

lib = T.lib; win_rs, win_h, cals = r.load_inputs(); cal = read_cal(); rows = read_reference()["frames"]; nb = len(cals); cross = 120
N = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--n=")), 40))
_keep = []


def raw_handle(header_ints, payload):
    """handle whose data starts right after the int32 header (4-byte alignment: SGL/I32/U8/CSG arrays)"""
    hdr = np.array(header_ints, np.int32).tobytes(); buf = C.create_string_buffer(hdr + payload, len(hdr) + len(payload) + 8)
    p = C.cast(buf, C.c_void_p); pp = C.pointer(p); _keep.extend([buf, p, pp]); return pp, C.addressof(buf) + len(hdr)


def f1(a):
    a = np.ascontiguousarray(a, np.float32); return raw_handle([a.size], a.tobytes())


def f2(a):
    a = np.ascontiguousarray(a, np.float32); return raw_handle([a.shape[0], a.shape[1]], a.tobytes())


def c2f(a):
    inter = np.stack([a.real, a.imag], -1).astype(np.float32); return raw_handle([a.shape[0], a.shape[1]], inter.tobytes())


def i1(a):
    a = np.ascontiguousarray(a, np.int32); return raw_handle([a.size], a.tobytes())


def b1(a):
    a = np.ascontiguousarray(a, np.uint8); return raw_handle([a.size], a.tobytes())


def u2(a):
    a = np.ascontiguousarray(a, np.uint8); return raw_handle([1, a.shape[0], a.shape[1]], a.tobytes())      # 3-D {pages=1, rows, cols}


def read_f(addr, n):
    return np.frombuffer((C.c_char * (4 * n)).from_address(addr), dtype=np.float32).copy()


def read_i(addr, n):
    return np.frombuffer((C.c_char * (4 * n)).from_address(addr), dtype=np.int32).copy()


def read_b(addr, n):
    return np.frombuffer((C.c_char * n).from_address(addr), dtype=np.uint8).copy()


def cal_handle_dbl():
    """array of clusters exactly as LabVIEW hands it (dump 2026-09-08): {I32 forget; pad; DBL zstep; H cosband DBL 1-D; H ampl DBL 2-D;
    H cork CDB 2-D; H real DBL 2-D; I32 nslices; pad} = 56 bytes, header {I32 n; pad}"""
    stride = 56; buf = C.create_string_buffer(8 + nb * stride + 8); C.memmove(buf, np.array([nb, 0], np.int32).tobytes(), 8)
    for b, c in enumerate(cals):
        base = C.addressof(buf) + 8 + b * stride
        C.memmove(base, np.array([int(c["forget_radius"]), 0], np.int32).tobytes(), 8); C.memmove(base + 8, np.array([float(c["z_step"])], np.float64).tobytes(), 8)
        for k, (pp, _) in enumerate((T.arr_handle(np.real(c["cosband"]), "d1"), T.arr_handle(c["ampl"], "d2"), T.arr_handle(c["cork"], "c2"), T.arr_handle(c["real"], "d2"))):
            C.memmove(base + 16 + 8 * k, C.cast(C.pointer(C.cast(pp, C.c_void_p)), C.POINTER(C.c_uint64)), 8)
        C.memmove(base + 48, np.array([int(c["n_slices"]), 0], np.int32).tobytes(), 8)
    p = C.cast(buf, C.c_void_p); pp = C.pointer(p); _keep.extend([buf, p, pp]); return pp


def decode(v9):
    return [float(v9[3 * k]) + float(v9[3 * k + 1]) / 16777216.0 + float(v9[3 * k + 2]) / 16777216.0 ** 2 for k in range(3)]


def call(f, img, xy_int, good_in, hcal, textin):
    hx, ax = i1(np.array(xy_int, np.int32).ravel()); hy, ay = i1(np.zeros(nb, np.int32)); himg, _ = u2(img)
    hxo, axo = f2(np.zeros((nb, 9), np.float32)); hyo, _ = f2(np.zeros((0, 0))); hzo, _ = f2(np.zeros((0, 0)))
    hbs, abs_ = b1(np.array(good_in, np.uint8)); htest, _ = f1(win_rs); text = C.create_string_buffer(textin.encode("mbcs"), 256)
    t0 = time.perf_counter(); rc = f(0, 0, 0, 0, 0, hx, hy, cross, 10, himg, hxo, hyo, hzo, hcal, hbs, text, htest); dt = time.perf_counter() - t0
    raw = read_f(axo, 9 * nb); out = np.array([decode(raw[9 * b:9 * b + 9]) for b in range(nb)]).ravel()
    return rc, text.value, dt, out, read_i(ay, nb), read_b(abs_, nb)


row = rows[0]; img = read_image(row["frame"]).astype(np.uint8); xy_int = [[r.lv_round(x), r.lv_round(y)] for x, y in cal["xy"]]
empty = T.handle(T.Arr1D, [0], 0)[0]
for name, hc, textin, tag in (("GPUTracking_lv", cal_handle_dbl(), " " * 64, "cluster 56-byte DBL"),
                              ("GPUTracking_file", C.c_void_p(0), CAL + " " * 8, "file"), ("GPUTracking_auto", cal_handle_dbl(), " " * 64, "auto/cluster"),
                              ("GPUTracking_auto", empty, CAL + " " * 8, "auto/file")):
    f = getattr(lib, name); f.restype = C.c_int
    rc, txt, dt, out, pos, good = call(f, img, xy_int, [1] * nb, hc, textin)
    print(f"{name} ({tag}): rc {rc} text {txt!r} {1e3 * dt:.1f} ms; x,y,z {out[:6].round(6)} pos {pos} good {good}; "
          f"max|diff| vs LabVIEW frame {row['frame']}: {np.max(np.abs(out - np.array(row['ff']))):.2e}", flush=True)
# state-chained sweep, cluster route (stride 48 = the lab loader's cluster)
f = lib.GPUTracking_lv; f.restype = C.c_int; hcal = cal_handle_dbl(); worst = np.zeros(3); flips = 0; t_sum = 0.0; n_done = 0
for k in range(0, len(rows), max(1, len(rows) // N)):
    row = rows[k]
    if k == 0:
        state = cal["xy"]; good_in = [1] * nb
    else:
        prev = rows[k - 1]; lost = any(v == -1.0 for v in prev["ff"])
        state = cal["xy"] if lost else np.array(prev["ff"]).reshape(-1, 3)[:, :2]; good_in = [1] * nb if lost else [int(g) for g in prev["good"]]
    xy_int = [[r.lv_round(x), r.lv_round(y)] for x, y in state]
    rc, txt, dt, out, pos, good = call(f, read_image(row["frame"]).astype(np.uint8), xy_int, good_in, hcal, " " * 64); t_sum += dt
    assert rc == 0, txt
    for b in range(nb):
        if not good_in[b] or row["ff"][3 * b] == -1.0:
            continue
        if pos[b] != row["pos"][b]:
            flips += 1; continue
        worst = np.maximum(worst, np.abs(out[3 * b:3 * b + 3] - np.array(row["ff"][3 * b:3 * b + 3])))
    n_done += 1
print(f"sweep {n_done} frames (cluster route): worst |dx| {worst[0]:.2e} px |dy| {worst[1]:.2e} px |dz| {worst[2]:.2e} um vs LabVIEW; "
      f"index flips {flips}; {1e3 * t_sum / n_done:.2f} ms/frame", flush=True)
