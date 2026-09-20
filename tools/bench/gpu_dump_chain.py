import os, shutil, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
DLL_SRC = os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll"); DLL_DST = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug\GPU Tracking.dll"
def run(args, timeout, tag):
    r = subprocess.run(args, timeout=timeout, cwd=ROOT); print(f"{tag} rc {r.returncode}", flush=True); return r.returncode
run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
shutil.copyfile(DLL_SRC, DLL_DST); print("deployed", os.path.getsize(DLL_DST), flush=True)
run([sys.executable, "-u", os.path.join(TOOLS, "bench", "gpu_smoke_err.py")], 300, "smoke_err")
run([sys.executable, "-u", os.path.join(TOOLS, "gpu", "decode_dump.py")], 60, "decode")
