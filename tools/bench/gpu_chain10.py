import os, shutil, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
DLL_SRC = os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll"); DLL_DST = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug\GPU Tracking.dll"
def run(args, timeout, tag):
    r = subprocess.run(args, timeout=timeout, cwd=ROOT); print(f"{tag} rc {r.returncode}", flush=True); return r.returncode
os.environ["MT_GPU_KEEPALIVE"] = os.environ.get("MT_GPU_KEEPALIVE", "0"); print("MT_GPU_KEEPALIVE", os.environ["MT_GPU_KEEPALIVE"], flush=True)   # inherited by the LabVIEW process
run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
shutil.copyfile(DLL_SRC, DLL_DST); print("deployed", os.path.getsize(DLL_DST), flush=True)
sys.exit(run([sys.executable, "-u", os.path.join(TOOLS, "bench", "run_timing.py"), "--n=200", "--harness=base", "--harness=gpu"], 2400, "run_timing gpu"))
