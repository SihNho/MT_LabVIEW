"""run_copy_bench.py - per-frame cost of a reference-safe IMAQ Copy (1280x1024 U8) on the fixture.

HARNESS_copy0 (two IMAQ Creates + ReadFile) vs HARNESS_copy1 (+ IMAQ Copy A->B); same method as run_display_bench:
one COM Run per frame from Python, files pre-read, 10 warm + 200 timed, two passes (copy0, copy1, copy0, copy1),
panels closed. cost(Copy) = median(copy1) - median(copy0). Also re-times HARNESS_disp0 / disp1 in the same session so
the ImageToArray comparison is from the same run. Output tools/bench/copy_bench.json.
  py tools/bgrun.py --max-min 15 --log tools/bench/run_copy_bench.log -- py -u tools/bench/run_copy_bench.py
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

LC = json.load(open(os.path.join(HERE, "harness_copy_labels.json"), encoding="utf-8"))["labels"]
LD = json.load(open(os.path.join(HERE, "harness_display_labels.json"), encoding="utf-8"))["labels"]
H = {"copy0": os.path.join(g.CLAUDEDEV, "HARNESS_copy0.vi"), "copy1": os.path.join(g.CLAUDEDEV, "HARNESS_copy1.vi"),
     "disp0": os.path.join(g.CLAUDEDEV, "HARNESS_disp0.vi"), "disp1": os.path.join(g.CLAUDEDEV, "HARNESS_disp1.vi")}
N, WARM = 200, 10
g._run.__defaults__ = (6.0, 60.0)


def cell(name, frames):
    vi = g.op(H[name])
    lab = LC if name.startswith("copy") else LD
    vi.SetControlValue(lab["Image Name"], f"{name}A")
    if "Image Name B" in lab and name.startswith("copy"):
        vi.SetControlValue(lab["Image Name B"], f"{name}B")
    times = []
    for i, fp in enumerate(frames):
        vi.SetControlValue(lab["File Path"], fp)
        t0 = time.perf_counter(); g._run(vi); dt = time.perf_counter() - t0
        if i >= WARM:
            times.append(dt * 1000.0)
    med = statistics.median(times); p90 = sorted(times)[int(0.9 * len(times)) - 1]
    print(f"   {name:6s}: median {med:.2f} ms  p90 {p90:.2f} ms  (n={len(times)})", flush=True)
    return {"median_ms": round(med, 3), "p90_ms": round(p90, 3), "n": len(times)}


def main():
    g._lv = None
    for p in H.values():
        try:
            g.close_panel(p)
        except Exception:
            pass
    frames = sorted(glob.glob(os.path.join(fixture.DATA, "img*.tif")))[:N + WARM]
    vi0 = g.op(H["disp0"]); vi0.SetControlValue(LD["Image Name"], "warm")
    for fp in frames:
        vi0.SetControlValue(LD["File Path"], fp); g._run(vi0)
    print(f"warm-up: {len(frames)} frames pre-read", flush=True)
    res = {}
    for pas in (1, 2):
        for name in ("copy0", "copy1", "disp0", "disp1"):
            res[f"pass{pas}/{name}"] = cell(name, frames)
    out = {"results": res}
    for pas in (1, 2):
        c = res[f"pass{pas}/copy1"]["median_ms"] - res[f"pass{pas}/copy0"]["median_ms"]
        a = res[f"pass{pas}/disp1"]["median_ms"] - res[f"pass{pas}/disp0"]["median_ms"]
        b = res[f"pass{pas}/copy0"]["median_ms"] - res[f"pass{pas}/disp0"]["median_ms"]
        out[f"pass{pas}"] = {"IMAQ Copy ms": round(c, 3), "ImageToArray ms": round(a, 3), "second IMAQ Create ms": round(b, 3)}
        print(f"pass {pas}: IMAQ Copy {c:.2f} ms | ImageToArray {a:.2f} ms | a second IMAQ Create {b:.2f} ms", flush=True)
    with open(os.path.join(HERE, "copy_bench.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
