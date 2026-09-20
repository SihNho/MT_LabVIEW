"""track_time_chain.py - discriminating test for the TRACK row's extra ~9 ms/frame (track_check.log, 2026-09-10).

Hypothesis H1': track_check_chain touched TRACK_kernel_v1 through VI Server (GetVIReference + SetControlValue) before timing,
which loads the subVI's FRONT PANEL data space; a loaded panel makes every call refresh its controls (the IMAQ image display
among them) - HARNESS_par's kernel was never touched. Prediction if H1' holds: with a fresh LabVIEW and NO VI Server access to
TRACK_kernel_v1, track kernel ms ~ par kernel ms (+ < 0.3 ms for the extra subVI layer). If the ~9 ms stays, the cost is
structural (case tunnels copying the calibration arrays - H3).
  py tools/bgrun.py --max-min 30 --log tools/bench/track_time.log -- py -u tools/bench/track_time_chain.py [n]
"""
import os, shutil, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "gpu"))
from fixture import CAL  # noqa: E402
N = sys.argv[1] if len(sys.argv) > 1 else "50"
DEBUG = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug"


def run(args, timeout, tag):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=timeout, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"   {tag} rc {rc}", flush=True); return rc


run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
for name in ("mt_track.dll", "GPU Tracking.dll"):
    shutil.copyfile(os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll"), os.path.join(DEBUG, name))
open(os.path.join(DEBUG, "mt_track_cal.txt"), "w").write(CAL)
run(["-u", os.path.join(TOOLS, "bench", "run_timing.py"), f"--n={N}", "--harness=base", "--harness=par", "--harness=track"], 2400, "run_timing")
