"""gpuk_repeat.py - the drop-in GPU kernel measured three times, because two runs of the same comparison disagreed:
run A (quiet machine, sd 0.2-0.7 ms) gave gpuk 11.31 ms/frame, runs B and C gave 3.22 and 2.22 while the DLL's own log said
1.65-1.77 ms every time.  Something outside the DLL varies; the prime suspect is the GPU power state (the memory clock drops at a
low duty cycle - docs/gpu-backend.md), so each repeat records nvidia-smi clocks before and after.

Each repeat: base + par + gpuk, 200 chained frames, outputs checked against the LabVIEW reference, DLL per-frame log on.
  py tools/bgrun.py --max-min 60 --log tools/bench/gpuk_repeat.log -- py -u tools/bench/gpuk_repeat.py [repeats] [n]
"""
import json, os, re, shutil, subprocess, sys, time
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "gpu"))
from fixture import CAL  # noqa: E402
REPEATS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
N = sys.argv[2] if len(sys.argv) > 2 else "200"
DEBUG = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug"
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "run_timing_results.json")


def clocks(tag):
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=clocks.sm,clocks.mem,pstate,utilization.gpu,temperature.gpu",
                              "--format=csv,noheader"], capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as e:
        out = f"(nvidia-smi failed: {e})"
    print(f"   clocks {tag}: {out}", flush=True); return out


def run(args, timeout, tag):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=timeout, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"   {tag} rc {rc}", flush=True); return rc


rows = []
for rep in range(1, REPEATS + 1):
    print(f"\n===== repeat {rep}/{REPEATS}", flush=True)
    log = os.path.join(HERE, f"mt_gpu_frames_rep{rep}_{time.strftime('%H%M%S')}.txt")
    os.environ["MT_GPU_LOG"] = log
    run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
    for name in ("mt_track.dll", "GPU Tracking.dll"):
        shutil.copyfile(os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll"), os.path.join(DEBUG, name))
    open(os.path.join(DEBUG, "mt_track_cal.txt"), "w").write(CAL)
    before = clocks("before")
    run(["-u", os.path.join(TOOLS, "bench", "run_timing.py"), f"--n={N}", "--harness=base", "--harness=par", "--harness=gpuk"], 2400, "run_timing")
    after = clocks("after")
    row = {"repeat": rep, "clocks_before": before, "clocks_after": after}
    if os.path.exists(RESULTS):
        d = json.load(open(RESULTS)); row["stats_ms"] = {k: round(v[0], 2) for k, v in d["stats_ms"].items()}
        row["kernel_ms"] = {k: round(v, 2) for k, v in d["kernel_ms"].items()}; row["worst_dev"] = d["worst_dev"]
    if os.path.exists(log):
        vals = [[float(x) for x in l.split()] for l in open(log).read().split("\n") if len(l.split()) == 4]
        if vals:
            import statistics as st
            row["dll_ms"] = [round(st.median([v[i] for v in vals]), 2) for i in range(4)]; row["dll_frames"] = len(vals)
    print("   ", json.dumps(row, ensure_ascii=False)[:400], flush=True)
    rows.append(row)
print("\n===== SUMMARY of repeats", flush=True)
for r in rows:
    k = r.get("kernel_ms", {}); s = r.get("stats_ms", {})
    print(f"  rep {r['repeat']}: base {s.get('base')} par {s.get('par')} gpuk {s.get('gpuk')} | KERNEL par {k.get('par')} gpuk {k.get('gpuk')}"
          f" | DLL {r.get('dll_ms')} | clocks before {r['clocks_before']}", flush=True)
json.dump(rows, open(os.path.join(HERE, "gpuk_repeat_results.json"), "w"), indent=1)
