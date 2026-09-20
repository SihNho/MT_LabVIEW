"""track_chain.py - restart LabVIEW, then build TRACK_kernel_v1 (tools/recipes/build_track_kernel_v1.py).
  py tools/bgrun.py --max-min 25 --log tools/bench/build_track_kernel_v1.log -- py -u tools/bench/track_chain.py
"""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
for tag, args, to in (("lv_restart", [os.path.join(TOOLS, "lv_restart.py")], 400),
                      ("build_track", ["-u", os.path.join(TOOLS, "recipes", "build_track_kernel_v1.py")], 1200)):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=to, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{tag} rc {rc}", flush=True)
