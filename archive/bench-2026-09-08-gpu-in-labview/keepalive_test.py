import ctypes as C, time, numpy as np, sys, re, subprocess, csv, collections
sys.argv = ["x", "--n=1"]
import test_dll_lv3 as T
from fixture import read_image
lib = T.lib; f = lib.GPUTracking_lv; f.restype = C.c_int
img = read_image(T.rows[0]["frame"]).astype(np.uint8); xy_int = [[T.r.lv_round(x), T.r.lv_round(y)] for x, y in T.cal["xy"]]; hcal = T.cal_handle_dbl()
CSV = r"C:/Users/KimLab/AppData/Local/Temp/claude/nvsmi_keep.csv"
smi = subprocess.Popen([r"C:\Windows\System32\nvidia-smi.exe", "--query-gpu=timestamp,pstate,clocks.sm,utilization.gpu,power.draw", "--format=csv", "-lms", "250"], stdout=open(CSV, "w"))
marks = []
for label, ka in (("keepalive ON", 1), ("keepalive OFF", 0)):
    T.call(f, img, xy_int, [1] * T.nb, hcal, " " * 64); lib.mt_gpu_keepalive(ka); ts = []; es = []; t0 = time.time(); t_end = t0 + 10
    while time.time() < t_end:
        rc, txt, dt, out, pos, good = T.call(f, img, xy_int, [1] * T.nb, hcal, " " * 64)
        assert rc == 0, txt
        m = re.search(rb"t=([\d.]+) u=([\d.]+) k=([\d.]+) e=([\d.]+)", txt); ts.append(float(m.group(1))); es.append(float(m.group(4))); time.sleep(0.015)
    n = len(ts); marks.append((label, t0, time.time()))
    print(f"{label}: 15 ms gaps, {n} calls: DLL median t {np.median(ts[n//2:]):.2f} ms, GPU event {np.median(es[n//2:]):.2f} ms; status {txt!r}", flush=True)
smi.kill(); time.sleep(0.5)
rows = [r for r in csv.reader(open(CSV)) if len(r) >= 5][1:]; h = len(rows) // 2
for name, part in (("ON half", rows[:h]), ("OFF half", rows[h:])):
    c = collections.Counter((r[1].strip(), r[2].strip()) for r in part); pw = [float(r[4].replace("W", "")) for r in part if r[4].strip().replace(".", "").replace("W", "").strip().isdigit()]
    print(name, "pstate/clock:", c.most_common(3), "| mean power %.1f W" % (sum(pw) / len(pw)) if pw else "")
