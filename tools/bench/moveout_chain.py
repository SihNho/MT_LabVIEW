import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = subprocess.run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], timeout=400); print("lv_restart rc", r.returncode, flush=True)
r = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "recipes", "build_opmoveout.py")], timeout=800); print("build rc", r.returncode, flush=True)
if r.returncode != 0: sys.exit(r.returncode)
r = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "bench", "extract_clfn.py")], timeout=1000); print("extract rc", r.returncode, flush=True)
sys.exit(r.returncode)
