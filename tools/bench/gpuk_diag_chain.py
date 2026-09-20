"""gpuk_diag_chain.py - the drop-in GPU kernel costs 11.31 ms/frame in HARNESS_gpuk while the same DLL measures ~1.6 ms
internally (HARNESS_gpu2: 1.14 ms in LabVIEW).  Split the difference: run the gpuk harness with MT_GPU_LOG set, so the DLL
appends its own per-frame timing (total, upload, kernel, GPU events) to a file even though the subVI passes status_len 0.

  DLL time ~1.6 ms  -> the ~9.7 ms is LabVIEW-side inside GPU_kernel_v1 (IMAQ nodes / data copies / subVI overhead)
  DLL time ~11 ms   -> the DLL itself is slow in this context (image source, clocks, per-frame reallocation)
  py tools/bgrun.py --max-min 30 --log tools/bench/gpuk_diag.log -- py -u tools/bench/gpuk_diag_chain.py [n]
"""
import os, shutil, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "gpu"))
from fixture import CAL  # noqa: E402
N = sys.argv[1] if len(sys.argv) > 1 else "60"
DEBUG = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug"
import time as _t
# a unique file per run: the previous LabVIEW keeps its log handle open until it exits, so a fixed name cannot be deleted
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"mt_gpu_frames_{_t.strftime('%H%M%S')}.txt")
os.environ["MT_GPU_LOG"] = LOG                                              # LabVIEW inherits this from lv_restart's parent


def run(args, timeout, tag):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=timeout, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{tag} rc {rc}", flush=True); return rc


run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
SRC = os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll")
for name in ("mt_track.dll", "GPU Tracking.dll"):
    shutil.copyfile(SRC, os.path.join(DEBUG, name))
open(os.path.join(DEBUG, "mt_track_cal.txt"), "w").write(CAL)
print("deployed", os.path.getsize(SRC), "bytes; MT_GPU_LOG ->", LOG, flush=True)
run(["-u", os.path.join(TOOLS, "bench", "run_timing.py"), f"--n={N}", "--harness=base", "--harness=par", "--harness=gpuk"], 2400, "run_timing")
if os.path.exists(LOG):
    rows = [l.split() for l in open(LOG).read().split("\n") if l.strip()]
    vals = [[float(x) for x in r] for r in rows if len(r) == 4]
    if vals:
        import statistics as st
        med = [st.median([v[i] for v in vals]) for i in range(4)]
        print(f"DLL per-frame (n={len(vals)}): total {med[0]:.2f} ms | upload {med[1]:.2f} | kernel {med[2]:.2f} | events {med[3]:.2f}", flush=True)
        print("  first 5:", vals[:5], flush=True)
else:
    print("no DLL log written - MT_GPU_LOG did not reach the LabVIEW process", flush=True)
