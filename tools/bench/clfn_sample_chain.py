import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
def run(args, timeout, tag):
    r = subprocess.run(args, timeout=timeout, cwd=ROOT); print(f"{tag} rc {r.returncode}", flush=True); return r.returncode
run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
run([sys.executable, "-u", os.path.join(TOOLS, "bench", "clfn_sample.py")], 600, "clfn sample")
