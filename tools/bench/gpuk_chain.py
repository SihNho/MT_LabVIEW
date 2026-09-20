"""gpuk_chain.py - verify the DROP-IN GPU kernel numerically, in the same harness family as the CPU rows:
  1. fresh LabVIEW, deploy the current DLL, and point the DLL's calibration fallback at the fixture (mt_track_cal.txt beside it,
     since GPU_kernel_v1's `cal path` control is empty by default)
  2. build HARNESS_gpuk (build_harness_variant --name=gpuk: HARNESS_loadcal + IMAQ Create/ReadFile + windows + GPU_kernel_v1)
  3. run_timing.py --harness=base --harness=par --harness=gpuk : identical harnesses, so the three rows are directly comparable
     and every output is checked against the LabVIEW reference.
  py tools/bgrun.py --max-min 50 --log tools/bench/gpuk_chain.log -- py -u tools/bench/gpuk_chain.py [n]
"""
import os, shutil, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "gpu"))
from fixture import CAL  # noqa: E402
N = sys.argv[1] if len(sys.argv) > 1 else "200"
DEBUG = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug"


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
open(os.path.join(DEBUG, "mt_track_cal.txt"), "w").write(CAL)               # the DLL's calibration fallback for the empty control
print("deployed", os.path.getsize(SRC), "bytes; cal fallback ->", CAL, flush=True)
rc = run(["-u", os.path.join(TOOLS, "recipes", "build_harness_variant.py"), "--name=gpuk"], 1200, "build_harness_gpuk")
if rc == 0:
    run(["-u", os.path.join(TOOLS, "bench", "run_timing.py"), f"--n={N}", "--harness=base", "--harness=par", "--harness=gpuk"], 2400, "run_timing")
else:
    print("harness build failed - timing skipped", flush=True)
