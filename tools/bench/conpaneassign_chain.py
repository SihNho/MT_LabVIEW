"""conpaneassign_chain.py - restart LabVIEW, then build and test OpConPaneAssign_v0.
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opconpaneassign.log -- py -u tools/bench/conpaneassign_chain.py
"""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
for tag, args, to in (("lv_restart", [os.path.join(TOOLS, "lv_restart.py")], 400),
                      ("build_assign", ["-u", os.path.join(TOOLS, "recipes", "build_opconpaneassign.py")] + sys.argv[1:], 1200)):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=to, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{tag} rc {rc}", flush=True)
