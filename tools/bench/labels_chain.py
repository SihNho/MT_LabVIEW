import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
def run(args, timeout, tag):
    r = subprocess.run(args, timeout=timeout, cwd=ROOT); print(f"{tag} rc {r.returncode}", flush=True); return r.returncode
run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
run([sys.executable, "-u", os.path.join(TOOLS, "bench", "clfn_lib_labels.py")], 400, "clfn labels")      # ONE COM client at a time (two at once crashed LabVIEW, 2026-09-09)
run([sys.executable, "-u", os.path.join(TOOLS, "bench", "imaq_ptr_labels.py")], 300, "imaq labels")
