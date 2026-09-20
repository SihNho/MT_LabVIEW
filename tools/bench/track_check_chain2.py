"""track_check_chain2.py - FUNCTIONAL + timing check of TRACK_kernel_v1 with the backend chosen by its saved DEFAULT.

Per backend (0 = CPU frame, 1 = GPU frame):
  a. configure session: SetControlValue(TRACK, 'index', backend) -> OpMakeDefault_v0 (VI method 3F3) -> save
  b. fresh LabVIEW (the configure touch loads the panel and inflates the call by ~9 ms - docs/NAMES.md timing protocol),
     DLL + cal fallback deployed, MT_GPU_LOG set
  c. run_timing --harness=base --harness=par --harness=gpuk --harness=track, N frames; DLL log line count before/after
Predictions: backend 0 -> log +0, track dev 0, track kernel ~ par; backend 1 -> log +N, track dev at the GPU level (z ~3e-6),
track kernel ~ gpuk. HARNESS_track must already exist (track_check_chain.py built it).
  py tools/bgrun.py --max-min 45 --log tools/bench/track_check2.log -- py -u tools/bench/track_check_chain2.py [n]
"""
import json, os, shutil, subprocess, sys, time
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS); HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS); sys.path.insert(0, os.path.join(TOOLS, "gpu"))
from fixture import CAL  # noqa: E402
N = sys.argv[1] if len(sys.argv) > 1 else "50"
DEBUG = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug"
LOG = os.path.join(HERE, f"mt_gpu_frames_track2_{time.strftime('%H%M%S')}.txt")
RESULTS = os.path.join(HERE, "run_timing_results.json")
os.environ["MT_GPU_LOG"] = LOG


def run(args, timeout, tag):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=timeout, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"   {tag} rc {tag and rc}", flush=True); return rc


def log_lines():
    return len([l for l in open(LOG).read().split("\n") if len(l.split()) == 4]) if os.path.exists(LOG) else 0


def configure(backend):
    """One short COM session: value -> default -> save. Runs in a subprocess so its COM client is gone before the restart."""
    code = ("import sys,os; sys.path.insert(0, r'%s'); import gscript as g; T=os.path.join(g.CLAUDEDEV,'TRACK_kernel_v1.vi'); "
            "vi=g.lv().GetVIReference(T,'',False,0); vi.SetControlValue('index',%d); "
            "o=g.op(os.path.join(g.CLAUDEDEV,'OpMakeDefault_v0.vi')); o.SetControlValue('vi path',T); g._run(o); "
            "print('   configured: index', vi.GetControlValue('index'), 'saved', g.save(T), 'bytes', flush=True)" % (TOOLS, backend))
    return run(["-c", code], 300, f"configure backend={backend}")


rows = []
for backend in (0, 1):
    print(f"\n===== backend = {backend}", flush=True)
    run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart (configure session)")
    configure(backend)
    run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart (timing session)")
    for name in ("mt_track.dll", "GPU Tracking.dll"):
        shutil.copyfile(os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll"), os.path.join(DEBUG, name))
    open(os.path.join(DEBUG, "mt_track_cal.txt"), "w").write(CAL)
    l0 = log_lines()
    run(["-u", os.path.join(TOOLS, "bench", "run_timing.py"), f"--n={N}", "--harness=base", "--harness=par", "--harness=gpuk", "--harness=track"], 2400, "run_timing")
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
json.dump(rows, open(os.path.join(HERE, "track_check2_results.json"), "w"), indent=1)
