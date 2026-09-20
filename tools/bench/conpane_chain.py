"""conpane_chain.py - restart LabVIEW, then build OpConPane_v0 and read TRACK_kernel_v1's connector pane.
  py tools/bgrun.py --max-min 20 --log tools/bench/build_opconpane.log -- py -u tools/bench/conpane_chain.py
"""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
for tag, args, to in (("lv_restart", [os.path.join(TOOLS, "lv_restart.py")], 400),
                      ("build_conpane", ["-u", os.path.join(TOOLS, "recipes", "build_opconpane.py")], 900)):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=to, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{tag} rc {rc}", flush=True)
