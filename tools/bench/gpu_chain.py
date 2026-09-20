import os, shutil, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
def run(args, timeout, tag):
    r = subprocess.run(args, timeout=timeout, cwd=ROOT); print(f"{tag} rc {r.returncode}", flush=True); return r.returncode
run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
shutil.copyfile(os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll"), r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug\GPU Tracking.dll"); print("DLL deployed", flush=True)
if run([sys.executable, "-u", os.path.join(TOOLS, "gpu", "test_dll.py"), "--n=5"], 600, "ctypes test"): sys.exit(1)
if run([sys.executable, "-u", os.path.join(TOOLS, "bench", "gpu_base_smoke.py")], 400, "smoke"): sys.exit(2)
if run([sys.executable, "-u", os.path.join(TOOLS, "recipes", "build_harness_gpu.py")], 1200, "build gpu harness"): sys.exit(3)
run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
sys.exit(run([sys.executable, "-u", os.path.join(TOOLS, "bench", "run_timing.py"), "--n=200", "--harness=base", "--harness=gpu"], 2400, "run_timing gpu"))
