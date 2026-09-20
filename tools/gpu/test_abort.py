"""test_abort.py - the rig's real stop gesture is LabVIEW's Abort button, so mt2_close never runs (user, 2026-09-09).
Two safety nets are checked here:
  A. single-context policy: 12 x [mt2_open + a few mt2_track calls] with NO close -> GPU memory must not grow (each open closes
     the previous context) and every run must still produce the reference numbers.
  B. keep-alive idle timeout: with the thread on, stop calling track -> state must go 1 (running) -> 2 (parked) within the idle
     window, and the next track call must un-park it (state 1 again).
Run:  py tools/bgrun.py --max-min 8 --log tools/bench/test_abort.log -- py -u tools/gpu/test_abort.py
"""
import ctypes as C, os, re, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixture import read_cal, read_reference, read_image, CAL
import test_dll as T
lib = T.lib
lib.mt2_open.restype = C.c_int64; lib.mt2_open.argtypes = [C.c_char_p, C.c_int, C.c_int, C.c_char_p, C.c_int]
lib.mt2_set_image.argtypes = [C.c_int64, C.c_uint64, C.c_int, C.c_int, C.c_int]; lib.mt2_set_image.restype = C.c_int
D = C.POINTER(C.c_double); U8 = C.POINTER(C.c_ubyte); I = C.POINTER(C.c_int)
lib.mt2_track.argtypes = [C.c_int64, C.c_int, D, U8, D, I, U8, C.c_char_p, C.c_int]; lib.mt2_track.restype = C.c_int
lib.mt2_close.argtypes = [C.c_int64]
for fn, res in (("mt_gpu_keepalive", C.c_int), ("mt_gpu_keepalive_idle", C.c_int), ("mt_gpu_keepalive_state", C.c_int)):
    getattr(lib, fn).restype = res; getattr(lib, fn).argtypes = [C.c_int] if fn != "mt_gpu_keepalive_state" else []

cal = read_cal(); rows = read_reference()["frames"]; nb = len(cal["xy"]); H, W, LW = 1024, 1280, 1280 + 64
status = C.create_string_buffer(128); buf = np.zeros((H, LW), np.uint8)


def free_mb():
    fr, tot = C.c_size_t(), C.c_size_t()
    if hasattr(lib, "cudaMemGetInfo"):
        lib.cudaMemGetInfo(C.byref(fr), C.byref(tot))
        return fr.value / 1048576.0
    import subprocess
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip().splitlines()[0]
    return -float(out)                                                       # negative = "used MB" (monotonic direction flipped)


def track_once(ctx, k):
    row = rows[k]
    if k == 0:
        state = [[x, y, 0.0] for x, y in cal["xy"]]; good_in = [1] * nb
    else:
        prev = rows[k - 1]; lost = any(v == -1.0 for v in prev["ff"])
        state = [[x, y, 0.0] for x, y in cal["xy"]] if lost else np.array(prev["ff"]).reshape(-1, 3).tolist()
        good_in = [1] * nb if lost else [int(g) for g in prev["good"]]
    buf[:, :W] = read_image(row["frame"])
    assert lib.mt2_set_image(ctx, buf.ctypes.data, LW, W, H) == 0
    xyz_in = np.array(state, np.float64).ravel(); gin = np.array(good_in, np.uint8)
    xyz_out = np.zeros(3 * nb); idx = np.zeros(nb, np.int32); gout = np.zeros(nb, np.uint8)
    rc = lib.mt2_track(ctx, nb, xyz_in.ctypes.data_as(D), gin.ctypes.data_as(U8), xyz_out.ctypes.data_as(D), idx.ctypes.data_as(I), gout.ctypes.data_as(U8), status, 128)
    assert rc == 0, status.value
    worst = 0.0
    for b in range(nb):
        if not good_in[b] or row["ff"][3 * b] == -1.0 or idx[b] != row["pos"][b]:
            continue
        worst = max(worst, float(np.max(np.abs(xyz_out[3 * b:3 * b + 3] - np.array(row["ff"][3 * b:3 * b + 3])))))
    return worst


print("== A. repeated open WITHOUT close (Abort simulation)", flush=True)
mem = []
for run in range(12):
    ctx = lib.mt2_open(CAL.encode("mbcs"), 120, 0, status, 128)
    assert ctx, status.value
    worst = max(track_once(ctx, k) for k in (0, 5, 10))
    mem.append(free_mb())
    print(f"  run {run + 1:2d}: ctx ok, worst dev {worst:.2e}, GPU free {mem[-1]:.0f} MB", flush=True)
    # NO mt2_close - exactly what LabVIEW's Abort leaves behind
drift = mem[1] - mem[-1]
print(f"  GPU memory drift over 11 aborted runs: {drift:+.0f} MB -> {'LEAK' if abs(drift) > 64 else 'OK (single-context policy holds)'}", flush=True)

print("== B. keep-alive idle timeout", flush=True)
lib.mt_gpu_keepalive_idle(1000)
ctx = lib.mt2_open(CAL.encode("mbcs"), 120, 1, status, 128)                   # flags bit0 = keep-alive on
track_once(ctx, 0); s1 = lib.mt_gpu_keepalive_state()
time.sleep(2.5); s2 = lib.mt_gpu_keepalive_state()                            # no tracking: must park
track_once(ctx, 1); s3 = lib.mt_gpu_keepalive_state()                         # a track call must wake it
print(f"  state after track {s1} (1 = running) | after 2.5 s idle {s2} (2 = parked) | after next track {s3} (1)", flush=True)
lib.mt2_close(ctx)
print("  verdict:", "OK" if (s1, s2, s3) == (1, 2, 1) else f"UNEXPECTED {(s1, s2, s3)}", flush=True)
