"""gpu2_chain.py - fresh LabVIEW (a client was killed mid-edit) -> build HARNESS_gpu2 (guarded) -> if saved, run_gpu2 (N frames)."""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
N = sys.argv[1] if len(sys.argv) > 1 else "200"


def run(args, timeout, tag):
    try:
        rc = subprocess.run(args, timeout=timeout, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{tag} rc {rc}", flush=True); return rc


run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
import shutil
SRC = os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll")
for DST in (r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug\mt_track.dll",          # our interface (no space in the name!)
            r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug\GPU Tracking.dll"):     # the Saleh-node harness (HARNESS_gpu)
    shutil.copyfile(SRC, DST); print("deployed", os.path.getsize(DST), "bytes ->", DST, flush=True)
rc = 0 if "--skip-build" in sys.argv else run([sys.executable, "-u", os.path.join(TOOLS, "recipes", "build_harness_gpu2.py")], 1500, "build_harness_gpu2")
if rc == 0:
    run([sys.executable, "-u", os.path.join(TOOLS, "bench", "run_gpu2.py"), f"--n={N}"], 1500, "run_gpu2")
else:
    print("build failed - run skipped", flush=True)
