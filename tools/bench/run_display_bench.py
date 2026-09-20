"""run_display_bench.py - display-path cost on the fixture: HARNESS_disp0..3, one Run per frame timed from Python.

Conditions (peer review archive/peer/2026-09-14-display-path-harness-plan.md): 'closed' = front panel not open
(construction cost of ImageToArray / Flatten / Draw); 'open' = front panel opened via COM (representative: the user
runs with the panel visible; asynchronous panel updates may still coalesce - stated). Frames alternate through the
fixture (img00004.tif ...) so the image changes every run. Per harness: warm-up 10, then N=200 runs, per-run seconds
via perf_counter; report median and p90; stage cost = median(dispk) - median(disp0) within the same condition.
Fixture asserted once: 1280x1024, mode L (8-bit), via PIL. Output tools/bench/display_bench.json + printed table.
  py tools/bgrun.py --max-min 25 --log tools/bench/run_display_bench.log -- py -u tools/bench/run_display_bench.py
"""
import glob
import json
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g  # noqa: E402
import fixture  # noqa: E402

LAB = json.load(open(os.path.join(HERE, "harness_display_labels.json"), encoding="utf-8"))["labels"]
H = {k: os.path.join(g.CLAUDEDEV, f"HARNESS_disp{k}.vi") for k in range(5)}     # disp4 = disp3 without the Picture indicator
H = {k: p for k, p in H.items() if os.path.exists(p)}
N, WARM = 200, 10
g._run.__defaults__ = (6.0, 60.0)


def main():
    g._lv = None
    frames = sorted(glob.glob(os.path.join(fixture.DATA, "img*.tif")))[:N + WARM]
    from PIL import Image
    im = Image.open(frames[0])
    assert im.size == (1280, 1024) and im.mode == "L", (im.size, im.mode)
    print(f"fixture: {len(frames)} frames, {im.size} {im.mode}", flush=True)
    # Run 1 (13:22): the FIRST cell (closed/disp0) read 15.5 ms median / 28 ms p90 while every later cell that
    # re-read the same files sat at ~7 ms - the OS file cache was cold for the first pass. Pre-read every frame
    # once through disp0 before any timed cell, and time two full passes so a cold first cell would show as pass 1 != pass 2.
    vi0 = g.op(H[0]); vi0.SetControlValue(LAB["Image Name"], "warm")
    t0 = time.perf_counter()
    for fp in frames:
        vi0.SetControlValue(LAB["File Path"], fp); g._run(vi0)
    print(f"warm-up: {len(frames)} frames pre-read through disp0 in {time.perf_counter() - t0:.1f} s", flush=True)
    results = {}
    for cond in ("closed", "open", "closed2"):
        for k in sorted(H):
            vi = g.op(H[k])
            if cond == "open":
                g.open_panel(H[k]); time.sleep(0.8)
            vi.SetControlValue(LAB["Image Name"], f"disp{k}")
            times = []
            for i, fp in enumerate(frames):
                vi.SetControlValue(LAB["File Path"], fp)
                t0 = time.perf_counter(); g._run(vi); dt = time.perf_counter() - t0
                if i >= WARM:
                    times.append(dt * 1000.0)
            med = statistics.median(times); p90 = sorted(times)[int(0.9 * len(times)) - 1]
            results[f"{cond}/disp{k}"] = {"median_ms": round(med, 3), "p90_ms": round(p90, 3), "n": len(times)}
            print(f"   {cond:6s} disp{k}: median {med:.2f} ms  p90 {p90:.2f} ms  (n={len(times)})", flush=True)
            if cond == "open":
                try:
                    g.close_panel(H[k])
                except Exception:
                    pass
    print("\nstage cost = median(dispk) - median(disp0), same condition:", flush=True)
    table = {}
    for cond in ("closed", "open", "closed2"):
        base = results[f"{cond}/disp0"]["median_ms"]
        for k, name in ((1, "ImageToArray"), (2, "+ Flatten Pixmap"), (3, "+ Draw Flattened Pixmap -> Picture"),
                        (4, "+ Draw Flattened Pixmap, NO indicator")):
            if k not in H:
                continue
            d = results[f"{cond}/disp{k}"]["median_ms"] - base
            table[f"{cond}/{name}"] = round(d, 3)
            print(f"   {cond:6s} {name:36s} cumulative {d:6.2f} ms", flush=True)
    with open(os.path.join(HERE, "display_bench.json"), "w", encoding="utf-8") as f:
        json.dump({"results": results, "stage_cumulative_ms": table, "frames": len(frames), "N": N, "warm": WARM,
                   "note": "one Run per frame timed from Python; base = disp0 (Create+ReadFile); 'open' = panel opened via COM"},
                  f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
