"""run_timing.py - LabVIEW-side timing of the sequential (four-fold) kernel vs the CPU-parallel (PARALLEL_kernel_v3 clean,
P=4) kernel on the fixture: HARNESS_base (no kernel) / HARNESS_seq / HARNESS_par are run on the same frames with the
same inputs, interleaved; kernel time = harness time - base time (COM Run + IMAQ ReadFile + windows cancel out).
Outputs are also checked against the LabVIEW reference (functional verification of the cleaned v3).
  py tools/bgrun.py --max-min 40 --log tools/bench/run_timing.log -- py -u tools/bench/run_timing.py [--n=200] [--every=1]
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g
from fixture import read_cal, read_reference, DATA, CAL
g._lv = None; g._run.__defaults__ = (6.0, 120.0)
LOADER = os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")
NAMES = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--harness=")] or ["base", "seq", "par"]
H = {k: os.path.join(g.CLAUDEDEV, f"HARNESS_{k}.vi") for k in NAMES}
LAB = {k: json.load(open(os.path.join(HERE, f"harness_{k}_labels.json"))) for k in NAMES}
OUT_KEY = {k: "x,y,z array out" for k in NAMES if LAB[k]["outputs"]}


# the GPU harness carries the calibration-file path in its C-string parameter (the DLL loads the .cal itself and
# overwrites the buffer with the status); the other harnesses get a blank 64-char buffer
ERRMSG = lambda k: (CAL + " " * 8) if k == "gpu" else " " * 64


def lv_round(v):
    return int(np.rint(v))                                           # round-half-even = LabVIEW's DBL -> I32 coercion


def setc(k, vi, name, value):
    lab = LAB[k]["controls"].get(name)
    if not lab:
        return
    if name == "x,y,z array" and LAB[k].get("gpu_encoding") == "xint+sgl9":
        # GPU harness (donor CLFN, SGL types): integer x,y in -> 'X Array 3' (I32[2nb]); outputs land in the SGL [nb][9] 'X Output'
        nb = len(value) // 3
        vi.SetControlValue(LAB[k]["controls"]["xy int in"], [lv_round(value[3 * b + j]) for b in range(nb) for j in (0, 1)])
        vi.SetControlValue(lab, tuple((0.0,) * 9 for _ in range(nb)))
        return
    vi.SetControlValue(lab, value)


def flat(k, v):
    if LAB[k].get("gpu_encoding") == "xint+sgl9":                    # decode hi + mid 2^-24 + lo 2^-48 per x, y, z
        return [float(row[3 * j]) + float(row[3 * j + 1]) / 16777216.0 + float(row[3 * j + 2]) / 16777216.0 ** 2 for row in v for j in range(3)]
    return [float(x) for row in v for x in (row if isinstance(row, (tuple, list)) else (row,))]


def arg(name, default):
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), None)
    return type(default)(v) if v is not None else default


def main():
    N = arg("n", 200); EVERY = arg("every", 1)
    rows = read_reference()["frames"]; xy0 = read_cal()["xy"]
    ld = g.op(LOADER); ld.SetControlValue("file (use dialog)", os.path.join(DATA, "cal002")); g._run(ld)
    nb = int(ld.GetControlValue("# of beads")); xyz0 = list(ld.GetControlValue("x,y,(blankz) array"))
    vis = {k: g.op(p) for k, p in H.items()}
    for k, vi in vis.items():
        setc(k, vi, "Image Name", f"timing_{k}"); setc(k, vi, "# of bead 4 packs", nb // 4); setc(k, vi, "4 pack remainder", nb % 4)
        setc(k, vi, "Optional Rectangle", [0, 0, 1280, 1024])            # GPU harness: whole-image rectangle for ImageToArray
    times = {k: [] for k in H}; worst = {k: 0.0 for k in OUT_KEY}; n_done = 0; dll_ms = []; phase = {}
    # warm-up
    for k, vi in vis.items():
        setc(k, vi, "File Path", os.path.join(DATA, f"img{rows[0]['frame']:05d}.tif")); setc(k, vi, "x,y,z array", xyz0)
        setc(k, vi, "Bead is good? array in", [True] * nb); setc(k, vi, "pos in cal image in", [0] * nb); setc(k, vi, "Error Message", ERRMSG(k)); g._run(vi)
    for i in range(0, len(rows), EVERY):
        if n_done >= N:
            break
        row = rows[i]
        if i == 0:
            state = (xyz0, [True] * nb, [0] * nb)
        else:
            prev = rows[i - 1]; lost = any(v == -1.0 for v in prev["ff"])
            state = (xyz0, [True] * nb, prev["pos"]) if lost else (prev["ff"], prev["good"], prev["pos"])
        for k in (NAMES if n_done % 2 == 0 else NAMES[::-1]):     # alternate order
            vi = vis[k]
            setc(k, vi, "File Path", os.path.join(DATA, f"img{row['frame']:05d}.tif"))
            setc(k, vi, "x,y,z array", state[0]); setc(k, vi, "Bead is good? array in", state[1]); setc(k, vi, "pos in cal image in", state[2])
            setc(k, vi, "Error Message", ERRMSG(k))
            t0 = time.perf_counter(); g._run(vi); dt = time.perf_counter() - t0; times[k].append(dt)
            if LAB[k].get("gpu_encoding"):                                  # the DLL appends its internal time: 'No_Errors t=1.234'
                msg = str(vi.GetControlValue(LAB[k]["outputs"]["Error Message out"]))
                if "t=" in msg:
                    dll_ms.append(float(msg.split("t=")[1].split()[0]))
                    for key in ("u=", "k=", "d=", "e=", "ui="):
                        if key in msg:
                            phase.setdefault(key, []).append(float(msg.split(key)[1].split()[0]))
            if k in OUT_KEY:
                out = flat(k, vi.GetControlValue(LAB[k]["outputs"][OUT_KEY[k]]))
                worst[k] = max(worst[k], max(abs(a - b) for a, b in zip(out, row["ff"])))
        n_done += 1
        if n_done <= 3 or n_done % 50 == 0:
            m = {k: 1e3 * np.median(v) for k, v in times.items()}
            print(f"frame {row['frame']}: median ms " + " ".join(f"{k} {v:.1f}" for k, v in m.items()) + " | worst dev " + " ".join(f"{k} {v:.2e}" for k, v in worst.items()), flush=True)
    stats = {k: (1e3 * float(np.median(v)), 1e3 * float(np.mean(v)), 1e3 * float(np.std(v))) for k, v in times.items()}
    print("SUMMARY frames", n_done)
    if dll_ms:
        print(f"  DLL-internal (from the status string): median {np.median(dll_ms):.2f} ms  mean {np.mean(dll_ms):.2f} ms  n {len(dll_ms)}", flush=True)
        print("  DLL phases (median ms): " + " ".join(f"{k}{np.median(v):.2f}" for k, v in phase.items()), flush=True)
    for k, (med, mean, sd) in stats.items():
        print(f"  {k}: median {med:.2f} ms  mean {mean:.2f} ms  sd {sd:.2f} ms", flush=True)
    base = stats["base"][0] if "base" in stats else 0.0
    kern = {k: stats[k][0] - base for k in stats if k != "base"}
    print("  KERNEL (median - base) ms/frame: " + ", ".join(f"{k} {v:.2f}" for k, v in kern.items()), flush=True)
    print("  functional: worst |dev| vs LabVIEW reference: " + ", ".join(f"{k} {v:.2e}" for k, v in worst.items()), flush=True)
    json.dump({"frames": n_done, "stats_ms": stats, "kernel_ms": kern, "worst_dev": worst, "times": {k: v for k, v in times.items()}},
              open(os.path.join(HERE, "run_timing_results.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
