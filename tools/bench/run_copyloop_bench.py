"""run_copyloop_bench.py - STEADY-STATE cost of IMAQ Copy A->B (1280x1024 U8): N = 1024 copies inside ONE Run.

HARNESS_copyloop (Create A -> ReadFile -> Create B -> Copy A->B once, then a For loop with N = Y Resolution (1024)
doing Copy A->B each iteration) vs HARNESS_copyloop0 (identical, the in-loop Copy deleted: the loop still runs 1024
empty iterations). per-copy steady-state = (median(copyloop) - median(copyloop0)) / 1024. HARNESS_copy1 / copy0 are
re-timed in the same session so the cold (first, allocating) copy cost comes from the same run. Method as
run_copy_bench: one COM Run per frame from Python, files pre-read, panels closed, A-B-A-B order, two passes.
Output tools/bench/copyloop_bench.json.
  py tools/bgrun.py --max-min 20 --log tools/bench/run_copyloop_bench.log -- py -u tools/bench/run_copyloop_bench.py
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
LL = json.load(open(os.path.join(HERE, "harness_copyloop_labels.json"), encoding="utf-8"))["labels"]
H = {"copy0": os.path.join(g.CLAUDEDEV, "HARNESS_copy0.vi"), "copy1": os.path.join(g.CLAUDEDEV, "HARNESS_copy1.vi"),
     "copyloop0": os.path.join(g.CLAUDEDEV, "HARNESS_copyloop0.vi"), "copyloop": os.path.join(g.CLAUDEDEV, "HARNESS_copyloop.vi"),
     # linearity check (peer): the same harness with N = X Resolution (1280); cells run only when the VIs exist
     "copyloopX0": os.path.join(g.CLAUDEDEV, "HARNESS_copyloopX0.vi"), "copyloopX": os.path.join(g.CLAUDEDEV, "HARNESS_copyloopX.vi")}
N_LOOP = 1024            # = Y Resolution of the fixture frames (the loop's N)
N_LOOPX = 1280           # = X Resolution (the X variant's N)
HAVE_X = os.path.exists(H["copyloopX"]) and os.path.exists(H["copyloopX0"])
N, WARM = 60, 5          # timed / warm Runs per cell (a loop Run is ~1024 copies, ~0.4 s)
g._run.__defaults__ = (6.0, 60.0)


def cell(name, frames):
    vi = g.op(H[name])
    lab = LL if name.startswith("copyloop") else LC
    vi.SetControlValue(lab["Image Name"], f"{name}A")
    vi.SetControlValue(lab["Image Name B"], f"{name}B")
    times = []
    for i, fp in enumerate(frames):
        vi.SetControlValue(lab["File Path"], fp)
        t0 = time.perf_counter(); g._run(vi); dt = time.perf_counter() - t0
        if i >= WARM:
            times.append(dt * 1000.0)
        if (i + 1) % 20 == 0:
            print(f"   {name}: run {i + 1}/{len(frames)}", flush=True)     # progress for the stall detector
    med = statistics.median(times); p90 = sorted(times)[int(0.9 * len(times)) - 1]
    print(f"   {name:9s}: median {med:.2f} ms  p90 {p90:.2f} ms  (n={len(times)})", flush=True)
    return {"median_ms": round(med, 3), "p90_ms": round(p90, 3), "n": len(times)}


def main():
    g._lv = None
    for p in H.values():
        if not os.path.exists(p):
            continue
        try:
            g.close_panel(p)
        except Exception:
            pass
    names = ("copy0", "copy1", "copyloop0", "copyloop") + (("copyloopX0", "copyloopX") if HAVE_X else ())
    print(f"cells: {names}", flush=True)
    frames = sorted(glob.glob(os.path.join(fixture.DATA, "img*.tif")))[:N + WARM]
    vi0 = g.op(H["copy0"]); vi0.SetControlValue(LC["Image Name"], "warmA"); vi0.SetControlValue(LC["Image Name B"], "warmB")
    for fp in frames:
        vi0.SetControlValue(LC["File Path"], fp); g._run(vi0)
    print(f"warm-up: {len(frames)} frames pre-read", flush=True)
    res = {}
    for pas in (1, 2):
        for name in names:
            res[f"pass{pas}/{name}"] = cell(name, frames)
    out = {"results": res, "n_loop": N_LOOP, "n_loopX": N_LOOPX if HAVE_X else None}
    for pas in (1, 2):
        cold = res[f"pass{pas}/copy1"]["median_ms"] - res[f"pass{pas}/copy0"]["median_ms"]
        loop = res[f"pass{pas}/copyloop"]["median_ms"] - res[f"pass{pas}/copyloop0"]["median_ms"]
        empty = res[f"pass{pas}/copyloop0"]["median_ms"] - res[f"pass{pas}/copy1"]["median_ms"]
        out[f"pass{pas}"] = {"cold copy ms": round(cold, 3), "steady copy ms": round(loop / N_LOOP, 4),
                             "loop total ms": round(loop, 2), "empty loop overhead ms": round(empty, 3)}
        print(f"pass {pas}: cold Copy {cold:.2f} ms | steady-state Copy {loop / N_LOOP:.4f} ms "
              f"({loop:.1f} ms / {N_LOOP}) | empty 1024-iteration loop {empty:.2f} ms", flush=True)
        if HAVE_X:
            loopx = res[f"pass{pas}/copyloopX"]["median_ms"] - res[f"pass{pas}/copyloopX0"]["median_ms"]
            dT = res[f"pass{pas}/copyloopX"]["median_ms"] - res[f"pass{pas}/copyloop"]["median_ms"]
            per, perx = loop / N_LOOP, loopx / N_LOOPX
            # peer (copyloop-linearity-plan): the per-copy SLOPE agreement is the criterion; the +-1 ms figure on
            # T1280-T1024 is only a secondary, empirical prediction (independent 5 % slope errors allow ~3 ms).
            lin_ok = abs(perx - per) <= 0.05 * per
            sec_ok = abs(dT - 256 * per) <= 1.0
            out[f"pass{pas}"].update({"steady copy ms (N=1280)": round(perx, 4), "T1280-T1024 ms": round(dT, 2),
                                      "linearity (slopes within 5 %)": "PASS" if lin_ok else "FAIL",
                                      "secondary (dT within 1 ms)": "PASS" if sec_ok else "MISS"})
            print(f"pass {pas}: N=1280 steady-state Copy {perx:.4f} ms ({loopx:.1f} ms / {N_LOOPX}) | T1280-T1024 {dT:.2f} ms "
                  f"(predicted {256 * per:.2f}) | linearity {'PASS' if lin_ok else 'FAIL'} | secondary {'PASS' if sec_ok else 'MISS'}", flush=True)
    with open(os.path.join(HERE, "copyloop_bench.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
