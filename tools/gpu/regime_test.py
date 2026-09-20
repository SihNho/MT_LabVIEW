import ctypes as C, time, numpy as np, sys, re, subprocess, csv, collections, os
sys.argv = ["x", "--n=1"]
import test_dll_lv3 as T
from fixture import read_image
lib = T.lib; f = lib.GPUTracking_lv; f.restype = C.c_int
img = read_image(T.rows[0]["frame"]).astype(np.uint8); xy_int = [[T.r.lv_round(x), T.r.lv_round(y)] for x, y in T.cal["xy"]]; hcal = T.cal_handle_dbl()
Q = "timestamp,pstate,clocks.sm,clocks.mem,pcie.link.gen.current,pcie.link.width.current,utilization.gpu,utilization.memory,power.draw"
def regime(label, gap, ka, secs=8):
    CSV = r"C:/Users/KimLab/AppData/Local/Temp/claude/nvsmi_%s.csv" % label.replace(" ", "_")
    lib.mt_gpu_keepalive(ka); time.sleep(0.5)
    smi = subprocess.Popen([r"C:\Windows\System32\nvidia-smi.exe", "--query-gpu=" + Q, "--format=csv", "-lms", "200"], stdout=open(CSV, "w"))
    ts = []; us = []; es = []; t_end = time.time() + secs
    while time.time() < t_end:
        rc, txt, dt, out, pos, good = T.call(f, img, xy_int, [1] * T.nb, hcal, " " * 64); assert rc == 0, txt
        m = re.search(rb"t=([\d.]+) u=([\d.]+) k=([\d.]+) e=([\d.]+)", txt); ts.append(float(m.group(1))); us.append(float(m.group(2))); es.append(float(m.group(4)))
        if gap: time.sleep(gap)
    smi.kill(); time.sleep(0.3); n = len(ts)
    rows = [r for r in csv.reader(open(CSV)) if len(r) >= 9][1:]
    c = collections.Counter((r[1].strip(), r[2].strip(), r[3].strip(), "gen" + r[4].strip(), "x" + r[5].strip()) for r in rows)
    print(f"{label:28s} calls {n:4d}: t {np.median(ts[n//2:]):.2f} u {np.median(us[n//2:]):.2f} e {np.median(es[n//2:]):.2f} ms | {c.most_common(2)}", flush=True)
    lib.mt_gpu_keepalive(0)
regime("tight loop", 0.0, 0)
regime("15 ms gaps", 0.015, 0)
regime("15 ms gaps + keepalive", 0.015, 1)
regime("5 ms gaps", 0.005, 0)
regime("2 ms gaps", 0.002, 0)
