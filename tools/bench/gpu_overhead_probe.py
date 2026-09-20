"""gpu_overhead_probe.py - where does TRACK_kernel_v1's extra ~1 ms on the GPU backend come from?

INDEX row 18 measured, over three repeats each: backend 0 track 2.84 vs par 2.87 ms/frame (no cost at all), backend 1
track 3.04 vs gpuk 1.98 (+1.06). A cost that appears ONLY on the GPU path cannot be the Case Structure, which is identical
in both frames. Two candidate explanations, and one cheap experiment that separates them.

  H1  MEASUREMENT ARTEFACT. run_timing drives base -> par -> gpuk -> track for every frame, so on backend 1 the GPU is
      called TWICE per frame and `track` is always the SECOND caller, right after `gpuk`. The extra millisecond would then
      belong to being second (GPU still finishing, staging buffer just used, driver queue non-empty), not to TRACK.
  H2  REAL COST inside TRACK's GPU frame. Then it stays when TRACK is the only GPU caller in the pass.

Cells, each a fresh LabVIEW with the frame files pre-cached and the DLL's own per-frame log on:
  A  base + gpuk            (GPU called once per frame, by gpuk)
  B  base + track           (GPU called once per frame, by track)      <- H1 predicts B == A, H2 predicts B == A + 1 ms
  C  base + gpuk + track    (the row-18 condition, both callers)       <- reproduces +1 ms if H1 holds
The DLL log additionally splits each call into total/upload/kernel, so if a real cost exists we learn whether it is inside
the DLL or on the LabVIEW side of the CLFN.

TRACK's saved default is set to index = 1 (GPU frame) once at the start, in its own session, followed by a restart, because
a VI-Server touch of a subVI inflates its call by ~9 ms (docs/NAMES.md).
  py tools/bgrun.py --max-min 40 --log tools/bench/gpu_overhead_probe.log -- py -u tools/bench/gpu_overhead_probe.py [n]
"""
import json, os, shutil, statistics as st, subprocess, sys, time
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS); HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS); sys.path.insert(0, os.path.join(TOOLS, "gpu"))
from fixture import CAL, read_reference, DATA  # noqa: E402
N = sys.argv[1] if len(sys.argv) > 1 else "200"
DEBUG = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug"
RESULTS = os.path.join(HERE, "run_timing_results.json")
CELLS = [("A gpuk alone", ["base", "gpuk"]),
         ("B track alone", ["base", "track"]),
         ("C both", ["base", "gpuk", "track"])]


def run(args, timeout, tag):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=timeout, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"   {tag} rc {rc}", flush=True); return rc


def warm(n):
    rows = read_reference()["frames"][:int(n)]
    t0 = time.time(); total = 0
    for r in rows:
        try:
            with open(os.path.join(DATA, f"img{r['frame']:05d}.tif"), "rb") as f:
                while True:
                    b = f.read(1 << 20)
                    if not b:
                        break
                    total += len(b)
        except OSError:
            break
    print(f"   warmed {total / 1e6:.0f} MB in {time.time() - t0:.1f} s", flush=True)


def deploy():
    for name in ("mt_track.dll", "GPU Tracking.dll"):
        shutil.copyfile(os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll"), os.path.join(DEBUG, name))
    open(os.path.join(DEBUG, "mt_track_cal.txt"), "w").write(CAL)


# --- TRACK's backend -> GPU, in its own session, then a restart -------------------------------------------------
run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart (configure)")
run(["-c", "import sys,os; sys.path.insert(0, r'%s'); import gscript as g; "
     "T=os.path.join(g.CLAUDEDEV,'TRACK_kernel_v1.vi'); "
     "print('   configured index=1, saved', g.make_default(T, {'index': 1}), 'bytes', flush=True)" % TOOLS], 300, "configure")

rows = []
for tag, harnesses in CELLS:
    print(f"\n######## {tag}: {harnesses}", flush=True)
    log = os.path.join(HERE, f"mt_gpu_frames_probe_{tag.split()[0]}.txt")
    os.environ["MT_GPU_LOG"] = log                       # BEFORE the restart, or LabVIEW never inherits it
    run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
    deploy(); warm(N)
    run(["-u", os.path.join(TOOLS, "bench", "run_timing.py"), f"--n={N}"] + [f"--harness={h}" for h in harnesses],
        2400, "run_timing")
    row = {"cell": tag, "harnesses": harnesses}
    if os.path.exists(RESULTS):
        d = json.load(open(RESULTS))
        row["frames"] = d.get("frames")
        row["median_ms"] = {k: round(v[0], 2) for k, v in d["stats_ms"].items()}
        row["sd_ms"] = {k: round(v[2], 2) for k, v in d["stats_ms"].items()}
        row["kernel_ms"] = {k: round(v, 2) for k, v in d["kernel_ms"].items()}
        row["worst_dev"] = d["worst_dev"]
    if os.path.exists(log):
        vals = [[float(x) for x in l.split()] for l in open(log).read().split("\n") if len(l.split()) == 4]
        if vals:
            row["dll_calls"] = len(vals)
            row["dll_median"] = [round(st.median([v[i] for v in vals]), 3) for i in range(4)]
    m = row.get("median_ms", {})
    if m and m.get("base", 0) > min([v for k, v in m.items() if k != "base"] or [9e9]):
        row["SUSPECT"] = "base slower than a kernel harness - contention, non-result"
        print("   !! SUSPECT: base slower than a kernel row; this cell is a non-result", flush=True)
    print("   " + json.dumps(row, ensure_ascii=False), flush=True)
    rows.append(row)
    json.dump(rows, open(os.path.join(HERE, "gpu_overhead_probe_results.json"), "w"), indent=1)

print("\n######## VERDICT", flush=True)
for r in rows:
    k = r.get("kernel_ms", {})
    print(f"  {r['cell']:>14}: kernel ms {k} | DLL calls {r.get('dll_calls')} median {r.get('dll_median')}", flush=True)
a = next((r for r in rows if r["cell"].startswith("A")), {}).get("kernel_ms", {}).get("gpuk")
b = next((r for r in rows if r["cell"].startswith("B")), {}).get("kernel_ms", {}).get("track")
if a and b:
    d = b - a
    print(f"\n  track alone {b:.2f} - gpuk alone {a:.2f} = {d:+.2f} ms/frame", flush=True)
    print("  -> H1 (being the SECOND GPU caller in the pass) explains row 18; the case structure is free on the GPU path too"
          if abs(d) < 0.4 else
          "  -> H2: the cost is real and belongs to TRACK's GPU frame; compare the DLL medians to place it", flush=True)
