import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)


def run(args, timeout, tag):
    r = subprocess.run(args, timeout=timeout, cwd=ROOT); print(f"{tag} rc {r.returncode}", flush=True); return r.returncode


run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
if run([sys.executable, "-u", os.path.join(TOOLS, "bench", "fix_gpu_harness3.py")], 900, "fix3"):
    sys.exit(1)
run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
if run([sys.executable, "-u", os.path.join(TOOLS, "bench", "gpu_smoke_file.py")], 600, "smoke"):
    sys.exit(2)
run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
sys.exit(run([sys.executable, "-u", os.path.join(TOOLS, "bench", "run_timing.py"), "--n=200", "--harness=base", "--harness=gpu"], 2400, "run_timing gpu"))
