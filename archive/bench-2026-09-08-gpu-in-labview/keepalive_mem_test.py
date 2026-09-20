import ctypes as C, time, numpy as np, sys, re, subprocess, csv, collections
sys.argv = ["x", "--n=1"]
import test_dll_lv3 as T
from fixture import read_image
lib = T.lib; f = lib.GPUTracking_lv; f.restype = C.c_int
img = read_image(T.rows[0]["frame"]).astype(np.uint8); xy_int = [[T.r.lv_round(x), T.r.lv_round(y)] for x, y in T.cal["xy"]]; hcal = T.cal_handle_dbl()
Q = "timestamp,pstate,clocks.sm,clocks.mem,utilization.memory,power.draw"
def regime(label, ka, iters, period, mb, secs=8):
    CSV = r"C:/Users/KimLab/AppData/Local/Temp/claude/nvsmi_keepmem.csv"
    if ka: lib.mt_gpu_keepalive_tune(iters, period, mb)
    lib.mt_gpu_keepalive(ka); time.sleep(1.0)
    smi = subprocess.Popen([r"C:\Windows\System32\nvidia-smi.exe", "--query-gpu=" + Q, "--format=csv", "-lms", "200"], stdout=open(CSV, "w"))
    ts = []; us = []; es = []; t_end = time.time() + secs
    while time.time() < t_end:
        rc, txt, dt, out, pos, good = T.call(f, img, xy_int, [1] * T.nb, hcal, " " * 64); assert rc == 0, txt
        m = re.search(rb"t=([\d.]+) u=([\d.]+) k=([\d.]+) e=([\d.]+)", txt); ts.append(float(m.group(1))); us.append(float(m.group(2))); es.append(float(m.group(4))); time.sleep(0.015)
    smi.kill(); time.sleep(0.3); n = len(ts); lib.mt_gpu_keepalive(0)
    rows = [r for r in csv.reader(open(CSV)) if len(r) >= 6][1:]
    c = collections.Counter((r[1].strip(), r[3].strip()) for r in rows); pw = [float(r[5].replace("W", "")) for r in rows if r[5].strip().replace(".", "").replace("W", "").strip().isdigit()]
    print(f"{label:34s}: t {np.median(ts[n//2:]):.2f} u {np.median(us[n//2:]):.2f} e {np.median(es[n//2:]):.2f} ms | {c.most_common(2)} | power {np.mean(pw):.0f} W", flush=True)
regime("15 ms gaps, no keep-alive", 0, 0, 0, 0)
regime("keep-alive 8 MB copy / 1 ms", 1, 2000, 1, 8)
regime("keep-alive 64 MB copy / 1 ms", 1, 2000, 1, 64)
regime("keep-alive 128 MB copy / 0 ms", 1, 2000, 0, 128)
