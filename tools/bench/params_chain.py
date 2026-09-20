import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
r = subprocess.run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], timeout=400, cwd=ROOT); print("lv_restart rc", r.returncode, flush=True)
r = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "recipes", "build_opclfnparams.py")], timeout=720, cwd=ROOT); print("build_opclfnparams rc", r.returncode, flush=True)
