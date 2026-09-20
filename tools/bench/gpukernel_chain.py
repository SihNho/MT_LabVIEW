"""gpukernel_chain.py - fresh LabVIEW -> deploy the current DLL -> build GPU_kernel_v1.vi (drop-in GPU backend)."""
import os, shutil, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)


def run(args, timeout, tag):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=timeout, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{tag} rc {rc}", flush=True); return rc


run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
SRC = os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll")
for DST in (r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug\mt_track.dll",
            r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug\GPU Tracking.dll"):
    shutil.copyfile(SRC, DST)
print("deployed", os.path.getsize(SRC), "bytes", flush=True)
run(["-u", os.path.join(TOOLS, "recipes", "build_gpu_kernel.py")], 1500, "build_gpu_kernel")
