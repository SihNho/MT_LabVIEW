"""track_bench.py - the TIMING benchmark for TRACK_kernel_v1 (backend-selectable kernel), quiet-machine repeats.

Why: the 2026-09-10 functional check (INDEX row 17) proved both backends run, but its timing rows were noisy (base sd 19-26 ms)
because the machine was busy, so the headline numbers still came from INDEX rows 15-16. This measures the selectable kernel
against the bare kernels in IDENTICAL harnesses, with the protocol the earlier run taught us:

  * the backend is the SAVED DEFAULT of TRACK_kernel_v1's `index` control, set once per backend in its own short COM session
    (gscript.make_default, VI method 3F3), because SetControlValue on a loaded subVI does not reach its call
  * LabVIEW is RESTARTED after that configure session and before every timing repeat, because a VI-Server touch loads the
    subVI's front-panel data space and adds ~9 ms/frame to its call (docs/NAMES.md, timing protocol)
  * base / par / gpuk / track are interleaved inside one run_timing pass, so the four rows share the same frames and the same
    COM + IMAQ overhead; kernel time = median(harness) - median(base)
  * every output is checked against the LabVIEW reference; the DLL logs its own per-frame time (MT_GPU_LOG)
  * nvidia-smi clocks are recorded before and after each repeat (the GPU P-state was the cause of an earlier 3.7x artefact)

Prediction contract: track(index 0) ~ par + case overhead (< 0.5 ms), track(index 1) ~ gpuk + the same overhead;
track(0) deviation 0.00 vs the reference, track(1) deviation ~2.7e-6 um in z.
  py tools/bgrun.py --max-min 55 --log tools/bench/track_bench.log -- py -u tools/bench/track_bench.py [repeats] [n]
"""
import json, os, shutil, statistics as st, subprocess, sys, time
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS); HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS); sys.path.insert(0, os.path.join(TOOLS, "gpu"))
from fixture import CAL  # noqa: E402
REPEATS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
N = sys.argv[2] if len(sys.argv) > 2 else "200"
DEBUG = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Debug"
RESULTS = os.path.join(HERE, "run_timing_results.json")
HARNESSES = ["base", "par", "gpuk", "track"]


def run(args, timeout, tag):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=timeout, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"   {tag} rc {rc}", flush=True); return rc


def clocks(tag):
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=clocks.sm,clocks.mem,pstate,temperature.gpu",
                              "--format=csv,noheader"], capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as e:
        out = f"(nvidia-smi failed: {e})"
    print(f"   clocks {tag}: {out}", flush=True); return out


def configure(backend):
    """One short COM session: index -> default -> save. A subprocess, so its client is gone before the restart."""
    code = ("import sys,os; sys.path.insert(0, r'%s'); import gscript as g; "
            "T=os.path.join(g.CLAUDEDEV,'TRACK_kernel_v1.vi'); "
            "print('   configured: saved', g.make_default(T, {'index': %d}), 'bytes', flush=True)" % (TOOLS, backend))
    return run(["-c", code], 300, f"configure index={backend}")


def deploy(log):
    # NOTE 2026-09-10: LabVIEW inherits MT_GPU_LOG from THIS process at ITS start, so the variable must already be set when
    # lv_restart runs. The first bench run called deploy() after the restart and every dll_ms came back None. Callers now set
    # the variable before restarting; this assignment is kept only so a direct deploy() call is still self-contained.
    os.environ["MT_GPU_LOG"] = log
    for name in ("mt_track.dll", "GPU Tracking.dll"):
        shutil.copyfile(os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll"), os.path.join(DEBUG, name))
    open(os.path.join(DEBUG, "mt_track_cal.txt"), "w").write(CAL)


def warm_cache(n):
    """Pull every frame this run will read into the OS file cache FIRST.

    Root cause of the 2026-09-10 18:4x non-result: the fixture lives on G:, a Storage Space backed by a 4 TB spinning HDD,
    and run_timing feeds the SAME file to all four harnesses with `base` always first. base therefore pays the physical read
    and the other three hit the cache. When the disk is contended that inversion is enormous: base median 26.68 ms against
    par 10.83, i.e. a NEGATIVE kernel time. With 64 GB of RAM the whole 200-frame set is ~260 MB, so warming it makes all
    four harnesses read from RAM, which is the condition the archived rows 15-16 were implicitly measured under."""
    from fixture import read_reference, DATA
    rows = read_reference()["frames"][:int(n)]
    total = 0; t0 = time.time()
    for r in rows:
        p = os.path.join(DATA, f"img{r['frame']:05d}.tif")
        try:
            with open(p, "rb") as f:
                while True:
                    b = f.read(1 << 20)
                    if not b:
                        break
                    total += len(b)
        except OSError as e:
            print(f"   warm: {e}", flush=True); break
    print(f"   warmed {len(rows)} frames, {total / 1e6:.0f} MB in {time.time() - t0:.1f} s", flush=True)


def quiet_check():
    """Name the known measurement contaminants if they are up, so a noisy repeat is explainable from the log alone."""
    try:
        out = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=30).stdout.lower()
    except Exception:
        return
    busy = [n for n in ("hwmonitor", "ollama", "chrome", "msedge") if n in out]
    print(f"   contaminants up: {busy if busy else 'none'}", flush=True)


rows = []
for backend in (0, 1):
    print(f"\n######## backend (saved default of `index`) = {backend}", flush=True)
    run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart (configure)")
    configure(backend)
    for rep in range(1, REPEATS + 1):
        print(f"\n===== backend {backend}, repeat {rep}/{REPEATS}", flush=True)
        log = os.path.join(HERE, f"mt_gpu_frames_bench_b{backend}_r{rep}.txt")
        os.environ["MT_GPU_LOG"] = log                      # BEFORE the restart, or LabVIEW never sees it
        run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart (timing)")
        deploy(log)
        warm_cache(N)
        quiet_check()
        before = clocks("before")
        run(["-u", os.path.join(TOOLS, "bench", "run_timing.py"), f"--n={N}"] + [f"--harness={h}" for h in HARNESSES],
            2400, "run_timing")
        after = clocks("after")
        row = {"backend": backend, "repeat": rep, "clocks_before": before, "clocks_after": after}
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
                row["dll_ms"] = [round(st.median([v[i] for v in vals]), 2) for i in range(4)]
                row["dll_frames"] = len(vals)
        m = row.get("median_ms", {})
        if m and m.get("base", 0) > min(m.get("par", 9e9), m.get("gpuk", 9e9), m.get("track", 9e9)):
            row["SUSPECT"] = "base slower than a kernel harness - disk or CPU contention, treat as a NON-RESULT"
            print(f"   !! SUSPECT: base {m.get('base')} ms is slower than a kernel row; this repeat is a non-result", flush=True)
        print("   " + json.dumps(row, ensure_ascii=False)[:460], flush=True)
        rows.append(row)
        json.dump(rows, open(os.path.join(HERE, "track_bench_results.json"), "w"), indent=1)

print("\n######## SUMMARY (kernel ms/frame = median(harness) - median(base))", flush=True)
print(f"{'backend':>7} {'rep':>4} | {'base':>7} {'par':>7} {'gpuk':>7} {'track':>7} | {'K par':>7} {'K gpuk':>7} {'K track':>7} | {'sd base':>8} | dev track", flush=True)
for r in rows:
    m = r.get("median_ms", {}); k = r.get("kernel_ms", {}); s = r.get("sd_ms", {}); d = r.get("worst_dev", {})
    print(f"{r['backend']:>7} {r['repeat']:>4} | {m.get('base','?'):>7} {m.get('par','?'):>7} {m.get('gpuk','?'):>7} {m.get('track','?'):>7} | "
          f"{k.get('par','?'):>7} {k.get('gpuk','?'):>7} {k.get('track','?'):>7} | {s.get('base','?'):>8} | {d.get('track','?')}", flush=True)
for backend in (0, 1):
    sel = [r for r in rows if r["backend"] == backend and "kernel_ms" in r]
    if sel:
        for key in ("par", "gpuk", "track"):
            vals = [r["kernel_ms"][key] for r in sel if key in r["kernel_ms"]]
            if vals:
                print(f"  backend {backend} {key:>5}: median of repeats {st.median(vals):.2f} ms/frame  (runs {vals})", flush=True)
print("\nDLL internal (total/upload/kernel/x) medians per repeat:", [r.get("dll_ms") for r in rows], flush=True)
