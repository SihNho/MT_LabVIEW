"""run_dispI_bench.py - Image Display route vs Picture route, same session, same method as run_display_bench.

Cells: disp0 (loader base), disp3 (ImageToArray -> Flatten -> Draw -> Picture), dispI (ReadFile 'Image Out' -> IMAQ
Image Display terminal). Conditions closed / open / closed2; 210 frames pre-read; 10 warm + 200 timed; one COM Run
per frame from Python. Cost = cell - disp0 within a condition. Output tools/bench/dispI_bench.json.
  py tools/bgrun.py --max-min 20 --log tools/bench/run_dispI_bench.log -- py -u tools/bench/run_dispI_bench.py
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

LD = json.load(open(os.path.join(HERE, "harness_display_labels.json"), encoding="utf-8"))["labels"]
LI = json.load(open(os.path.join(HERE, "harness_dispI_labels.json"), encoding="utf-8"))["labels"]
H = {"disp0": os.path.join(g.CLAUDEDEV, "HARNESS_disp0.vi"), "disp1": os.path.join(g.CLAUDEDEV, "HARNESS_disp1.vi"),
     "disp3": os.path.join(g.CLAUDEDEV, "HARNESS_disp3.vi"), "dispI": os.path.join(g.CLAUDEDEV, "HARNESS_dispI.vi")}
LAB = {"disp0": LD, "disp1": LD, "disp3": LD, "dispI": LI}
N, WARM = 200, 10
g._run.__defaults__ = (6.0, 60.0)


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
    for cond in ("closed", "open", "closed2"):
        for name in ("disp0", "disp1", "disp3", "dispI"):
            vi = g.op(H[name]); lab = LAB[name]
            if cond == "open":
                g.open_panel(H[name]); time.sleep(0.8)
            vi.SetControlValue(lab["Image Name"], name)
            times = []
            for i, fp in enumerate(frames):
                vi.SetControlValue(lab["File Path"], fp)
                t0 = time.perf_counter(); g._run(vi); dt = time.perf_counter() - t0
                if i >= WARM:
                    times.append(dt * 1000.0)
            med = statistics.median(times); p90 = sorted(times)[int(0.9 * len(times)) - 1]
            res[f"{cond}/{name}"] = {"median_ms": round(med, 3), "p90_ms": round(p90, 3)}
            print(f"   {cond:7s} {name}: median {med:.2f} ms  p90 {p90:.2f} ms", flush=True)
            if cond == "open":
                try:
                    g.close_panel(H[name])
                except Exception:
                    pass
    print("\nroute cost (same condition): disp3 - disp0 = Picture route; dispI - disp1 = Image Display terminal (dispI = disp1's chain + the display branch):", flush=True)
    table = {}
    for cond in ("closed", "open", "closed2"):
        b0, b1 = res[f"{cond}/disp0"]["median_ms"], res[f"{cond}/disp1"]["median_ms"]
        for name, base, desc in (("disp3", b0, "Picture route (ImageToArray+Flatten+Draw->Picture)"), ("dispI", b1, "Image Display terminal (branch off Image Out)")):
            d = res[f"{cond}/{name}"]["median_ms"] - base; table[f"{cond}/{name}"] = round(d, 3)
            print(f"   {cond:7s} {desc:52s} {d:6.2f} ms", flush=True)
    json.dump({"results": res, "route_ms": table}, open(os.path.join(HERE, "dispI_bench.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
