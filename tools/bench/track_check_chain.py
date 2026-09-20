"""track_check_chain.py - FUNCTIONAL check of TRACK_kernel_v1 (backend-selectable kernel) in the harness family.

  1. MT_GPU_LOG set, fresh LabVIEW, DLL + calibration fallback deployed (as gpuk_chain.py)
  2. build HARNESS_track (build_harness_variant --name=track: same harness as par/gpuk, kernel = TRACK_kernel_v1)
  3. for backend in (0, 1): set TRACK_kernel_v1's non-pane control `index` to the backend, make it the DEFAULT
     (ActiveX VirtualInstrument.MakeCurValsDefault - probed here; a failure is printed, not hidden), save, then
     run_timing --harness=base --harness=par --harness=track on N frames and read run_timing_results.json
Predictions:
  backend 0 -> DLL log does NOT grow, track outputs == par outputs (worst dev 0 vs the LabVIEW reference, like par)
  backend 1 -> DLL log grows by N lines, track worst dev == the GPU level (z ~3e-6 um), kernel time ~ gpuk
Either way the frame identity ('0, Default' = CPU) is settled by the log, not assumed.
  py tools/bgrun.py --max-min 45 --log tools/bench/track_check.log -- py -u tools/bench/track_check_chain.py [n]
"""
import json, os, shutil, subprocess, sys, time
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS); HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS); sys.path.insert(0, os.path.join(TOOLS, "gpu"))
from fixture import CAL  # noqa: E402
N = sys.argv[1] if len(sys.argv) > 1 else "50"
DEBUG = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug"
LOG = os.path.join(HERE, f"mt_gpu_frames_track_{time.strftime('%H%M%S')}.txt")
RESULTS = os.path.join(HERE, "run_timing_results.json")
os.environ["MT_GPU_LOG"] = LOG                                              # inherited by LabVIEW through lv_restart


def run(args, timeout, tag):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=timeout, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"   {tag} rc {rc}", flush=True); return rc


def log_lines():
    return len([l for l in open(LOG).read().split("\n") if len(l.split()) == 4]) if os.path.exists(LOG) else 0


run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
SRC = os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll")
for name in ("mt_track.dll", "GPU Tracking.dll"):
    shutil.copyfile(SRC, os.path.join(DEBUG, name))
open(os.path.join(DEBUG, "mt_track_cal.txt"), "w").write(CAL)
print("deployed", os.path.getsize(SRC), "bytes; cal fallback ->", CAL, "; MT_GPU_LOG ->", LOG, flush=True)
if run(["-u", os.path.join(TOOLS, "recipes", "build_harness_variant.py"), "--name=track"], 1200, "build_harness_track") != 0:
    print("harness build failed - stop", flush=True); sys.exit(3)

import gscript as g  # noqa: E402  (one COM client at a time: run_timing runs as a subprocess AFTER this client's calls)
TRACK = os.path.join(g.CLAUDEDEV, "TRACK_kernel_v1.vi")
rows = []
for backend in (0, 1):
    print(f"\n===== backend = {backend}", flush=True)
    g._lv = None
    vi = g.lv().GetVIReference(TRACK, "", False, 0)
    vi.SetControlValue("index", backend)
    try:
        g._invoke(vi, "MakeCurValsDefault")
        print("   MakeCurValsDefault: OK", flush=True)
    except Exception as e:
        print(f"   MakeCurValsDefault: FAILED {str(e)[:160]}", flush=True)
    print("   index now", vi.GetControlValue("index"), "| saved", g.save(TRACK), "bytes", flush=True)
    del vi; g._lv = None
    l0 = log_lines()
    run(["-u", os.path.join(TOOLS, "bench", "run_timing.py"), f"--n={N}", "--harness=base", "--harness=par", "--harness=track"], 2400, "run_timing")
    l1 = log_lines()
    row = {"backend": backend, "dll_log_lines_added": l1 - l0}
    if os.path.exists(RESULTS):
        d = json.load(open(RESULTS)); row["frames"] = d.get("frames")
        row["stats_ms"] = {k: round(v[0], 2) for k, v in d["stats_ms"].items()}
        row["kernel_ms"] = {k: round(v, 2) for k, v in d["kernel_ms"].items()}; row["worst_dev"] = d["worst_dev"]
    print("   ", json.dumps(row, ensure_ascii=False), flush=True)
    rows.append(row)
print("\n===== SUMMARY", flush=True)
for r in rows:
    print(f"  backend {r['backend']}: DLL log +{r['dll_log_lines_added']} lines | kernel ms {r.get('kernel_ms')} | worst dev {r.get('worst_dev')}", flush=True)
json.dump(rows, open(os.path.join(HERE, "track_check_results.json"), "w"), indent=1)
