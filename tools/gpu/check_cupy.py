"""check_cupy.py - CuPy port vs (a) the NumPy reference and (b) the LabVIEW reference on the fixture, plus timing.
  py tools/gpu/check_cupy.py [--every=10] [--n=100000]
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cuda_env  # noqa: E402,F401  (pip CUDA libs on PATH before cupy)
import cupy as cp  # noqa: E402
import ref_numpy as r  # noqa: E402
import ref_cupy as rc  # noqa: E402
from fixture import read_cal, read_image, read_reference  # noqa: E402


def arg(name, default):
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), None)
    return type(default)(v) if v is not None else default


def main():
    EVERY = arg("every", 10); N = arg("n", 10 ** 9)
    win_rs, win_h, cals = r.load_inputs(); cal = read_cal(); xy0 = cal["xy"]
    rows = read_reference()["frames"]; nb = len(cals); cross = 120
    pack = rc.CalPack(cals, 60)
    worst_np = np.zeros(3); worst_lv = np.zeros(3); n_done = 0; n_idx_diff = 0; t_gpu = 0.0; t_cpu = 0.0
    for k in range(0, len(rows), EVERY):
        if n_done >= N:
            break
        row = rows[k]
        if k == 0:
            state = np.array(xy0); good_in = [True] * nb
        else:
            prev = rows[k - 1]; lost = any(v == -1.0 for v in prev["ff"])
            state = np.array(xy0) if lost else np.array(prev["ff"]).reshape(-1, 3)[:, :2]
            good_in = [True] * nb if lost else prev["good"]
        img = read_image(row["frame"])
        xi = [r.lv_round(state[b][0]) for b in range(nb)]; yi = [r.lv_round(state[b][1]) for b in range(nb)]
        t0 = time.perf_counter(); g = rc.track_beads_gpu(img, xi, yi, cross, win_rs, win_h, pack); cp.cuda.Stream.null.synchronize(); t_gpu += time.perf_counter() - t0
        t0 = time.perf_counter()
        c = [r.track_bead(img, xi[b], yi[b], cross, win_rs, win_h, cals[b]) for b in range(nb)]
        t_cpu += time.perf_counter() - t0
        for b in range(nb):
            if not good_in[b] or row["ff"][3 * b] == -1.0:
                continue
            d_np = np.abs([g["x"][b] - c[b]["x"], g["y"][b] - c[b]["y"], g["z"][b] - c[b]["z"]])
            d_lv = np.abs([g["x"][b] - row["ff"][3 * b], g["y"][b] - row["ff"][3 * b + 1], g["z"][b] - row["ff"][3 * b + 2]])
            if g["index"][b] != c[b]["index"]:
                n_idx_diff += 1; print(f"frame {row['frame']} bead {b}: index gpu {g['index'][b]} numpy {c[b]['index']} (near-tie)", flush=True)
                continue
            worst_np = np.maximum(worst_np, d_np); worst_lv = np.maximum(worst_lv, d_lv)
        n_done += 1
        if n_done <= 2 or n_done % 200 == 0:
            print(f"frame {row['frame']}: gpu-vs-numpy worst {worst_np} | gpu-vs-LabVIEW worst {worst_lv}", flush=True)
    print(f"SUMMARY frames={n_done} gpu-vs-numpy worst |dx| {worst_np[0]:.2e} |dy| {worst_np[1]:.2e} |dz| {worst_np[2]:.2e} um; "
          f"gpu-vs-LabVIEW worst |dx| {worst_lv[0]:.2e} |dy| {worst_lv[1]:.2e} |dz| {worst_lv[2]:.2e} um; index near-tie flips {n_idx_diff}; "
          f"time/frame gpu {1e3 * t_gpu / n_done:.1f} ms (5 beads, unbatched frames, incl. H2D/D2H) numpy {1e3 * t_cpu / n_done:.1f} ms", flush=True)
    # throughput: many beads in one batch (replicate the 5 beads of one frame R times)
    img = read_image(rows[0]["frame"]); xi = [r.lv_round(v) for v in xy0[:, 0]]; yi = [r.lv_round(v) for v in xy0[:, 1]]
    for R in (1, 20, 100):
        pk = rc.CalPack(cals * R, 60)
        rc.track_beads_gpu(img, xi * R, yi * R, cross, win_rs, win_h, pk); cp.cuda.Stream.null.synchronize()
        t0 = time.perf_counter()
        for _ in range(5):
            rc.track_beads_gpu(img, xi * R, yi * R, cross, win_rs, win_h, pk)
        cp.cuda.Stream.null.synchronize(); dt = (time.perf_counter() - t0) / 5
        print(f"batch of {5 * R} beads: {1e3 * dt:.1f} ms -> {1e3 * dt / (5 * R):.3f} ms/bead", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
