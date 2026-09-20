"""run_gpu2.py - drive HARNESS_gpu2.vi (our GPU interface: one CLFN mt2_track_simple per frame on the raw IMAQ pixel pointer)
over the fixture frames like run_timing.py: chained state from the LabVIEW reference, outputs compared with the reference
(x,y,z per bead, pos-in-cal index, good flags), COM Run time per frame + the DLL-internal time from the status string.
  py tools/bgrun.py --max-min 30 --log tools/bench/run_gpu2.log -- py -u tools/bench/run_gpu2.py [--n=200] [--every=1] [--flags=0]
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g
from fixture import read_cal, read_reference, DATA, CAL
g._lv = None; g._run.__defaults__ = (6.0, 120.0)
LOADER = os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi"); H = os.path.join(g.CLAUDEDEV, "HARNESS_gpu2.vi")
LAB = json.load(open(os.path.join(HERE, "harness_gpu2_labels.json"))); O = LAB["outputs"]
# controls: IMAQ entries are name -> label, CLFN entries are label -> terminal index; normalise to name -> label
C = {k: (v if isinstance(v, str) else k) for k, v in LAB["controls"].items()}
W, HGT, STATUS_LEN = 1280, 1024, 256


def arg(name, default):
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), None)
    return type(default)(v) if v is not None else default


def out_label(prefix):
    """indicator label for CLFN output `prefix` ('xyz_out' -> 'xyz_out 2' when the control took the bare name)"""
    cands = [k for k in O if k == prefix or k.startswith(prefix + " ")]
    return sorted(cands, key=len)[-1] if cands else None


def main():
    N = arg("n", 200); EVERY = arg("every", 1); FLAGS = arg("flags", 0)
    rows = read_reference()["frames"]
    ld = g.op(LOADER); ld.SetControlValue("file (use dialog)", os.path.join(DATA, "cal002")); g._run(ld)
    nb = int(ld.GetControlValue("# of beads")); xyz0 = list(ld.GetControlValue("x,y,(blankz) array")); print("beads", nb, flush=True)
    vi = g.op(H)
    vi.SetControlValue(C["Image Name"], "timing_gpu2"); vi.SetControlValue(C["cal_path"], CAL)
    vi.SetControlValue(C["width"], W); vi.SetControlValue(C["height"], HGT); vi.SetControlValue(C["nb"], nb)
    vi.SetControlValue(C["status_len"], STATUS_LEN); vi.SetControlValue(C["flags"], FLAGS)
    o_xyz, o_idx, o_good, o_status, o_err = out_label("xyz_out"), out_label("idx_out"), out_label("good_out"), out_label("status"), O.get("error out")
    print("outputs:", o_xyz, o_idx, o_good, o_status, o_err, flush=True)

    def run_frame(frame, state, good_in, pos_in):
        vi.SetControlValue(C["File Path"], os.path.join(DATA, f"img{frame:05d}.tif"))
        vi.SetControlValue(C["xyz_in"], [float(v) for v in state]); vi.SetControlValue(C["good_in"], [1 if v else 0 for v in good_in])
        vi.SetControlValue(C["xyz_out"], [0.0] * (3 * nb)); vi.SetControlValue(C["idx_out"], [0] * nb); vi.SetControlValue(C["good_out"], [0] * nb)
        vi.SetControlValue(C["status"], " " * STATUS_LEN)
        t0 = time.perf_counter(); g._run(vi); dt = time.perf_counter() - t0
        xyz = [float(v) for v in vi.GetControlValue(o_xyz)]; idx = [int(v) for v in vi.GetControlValue(o_idx)]; good = [int(v) for v in vi.GetControlValue(o_good)]
        st = str(vi.GetControlValue(o_status)).rstrip(" \x00"); err = vi.GetControlValue(o_err) if o_err else None
        return dt, xyz, idx, good, st, err

    # HARNESS_base (IMAQ Create + ReadFile only) interleaved, as in run_timing.py: kernel = gpu2 - base
    BL = json.load(open(os.path.join(HERE, "harness_base_labels.json")))["controls"]; vb = g.op(os.path.join(g.CLAUDEDEV, "HARNESS_base.vi"))
    vb.SetControlValue(BL["Image Name"], "timing_base2")

    def run_base(frame):
        vb.SetControlValue(BL["File Path"], os.path.join(DATA, f"img{frame:05d}.tif")); t0 = time.perf_counter(); g._run(vb); return time.perf_counter() - t0

    # warm-up
    dt, xyz, idx, good, st, err = run_frame(rows[0]["frame"], xyz0, [True] * nb, [0] * nb); run_base(rows[0]["frame"])
    print(f"warm-up: {1e3*dt:.1f} ms | status {st!r} | error {err} | xyz[:3] {xyz[:3]} idx {idx} good {good}", flush=True)
    times = []; base_times = []; dll_ms = []; phase = {}; worst = np.zeros(3); flips = 0; n_done = 0; good_mismatch = 0; bad_frames = []
    for i in range(0, len(rows), EVERY):
        if n_done >= N:
            break
        row = rows[i]
        if i == 0:
            state, good_in = xyz0, [True] * nb
        else:
            prev = rows[i - 1]; lost = any(v == -1.0 for v in prev["ff"])
            state, good_in = (xyz0, [True] * nb) if lost else (prev["ff"], prev["good"])
        if n_done % 2 == 0:
            base_times.append(run_base(row["frame"])); dt, xyz, idx, good, st, err = run_frame(row["frame"], state, good_in, [0] * nb)
        else:
            dt, xyz, idx, good, st, err = run_frame(row["frame"], state, good_in, [0] * nb); base_times.append(run_base(row["frame"]))
        times.append(dt)
        if "t=" in st:
            dll_ms.append(float(st.split("t=")[1].split()[0]))
            for key in ("u=", "k=", "e=", "ka="):
                if key in st:
                    phase.setdefault(key, []).append(float(st.split(key)[1].split()[0]))
        for b in range(nb):
            if not good_in[b] or row["ff"][3 * b] == -1.0:
                continue
            dev = np.abs(np.array(xyz[3 * b:3 * b + 3]) - np.array(row["ff"][3 * b:3 * b + 3]))
            if idx[b] != row["pos"][b]:
                flips += 1; bad_frames.append((row["frame"], b, "flip", idx[b], row["pos"][b], [round(v, 4) for v in dev])); continue
            if dev.max() > 1e-4:
                bad_frames.append((row["frame"], b, "dev", [round(v, 4) for v in dev], "good_in", int(bool(good_in[b])), "ref_good", int(bool(row["good"][b])), "ours_good", good[b]))
            worst = np.maximum(worst, dev)
            if bool(good[b]) != bool(row["good"][b]):
                good_mismatch += 1
        n_done += 1
        if n_done <= 3 or n_done % 50 == 0:
            print(f"frame {row['frame']}: {1e3*np.median(times):.2f} ms median | DLL {np.median(dll_ms) if dll_ms else float('nan'):.2f} ms | worst |dx| {worst[0]:.2e} |dy| {worst[1]:.2e} |dz| {worst[2]:.2e} | flips {flips} | status {st!r}", flush=True)
    print("SUMMARY frames", n_done)
    print(f"  HARNESS_gpu2: median {1e3*np.median(times):.2f} ms  mean {1e3*np.mean(times):.2f} ms  sd {1e3*np.std(times):.2f} ms", flush=True)
    print(f"  HARNESS_base: median {1e3*np.median(base_times):.2f} ms  ->  KERNEL (gpu2 - base) {1e3*(np.median(times) - np.median(base_times)):.2f} ms/frame", flush=True)
    for bf in bad_frames[:40]:
        print("  BAD", bf, flush=True)
    if dll_ms:
        print(f"  DLL-internal: median {np.median(dll_ms):.2f} ms  phases " + " ".join(f"{k}{np.median(v):.2f}" for k, v in phase.items()), flush=True)
    print(f"  functional vs LabVIEW reference: worst |dx| {worst[0]:.2e} px |dy| {worst[1]:.2e} px |dz| {worst[2]:.2e} um; index flips {flips}; good-flag mismatches {good_mismatch}", flush=True)
    json.dump({"frames": n_done, "median_ms": 1e3 * float(np.median(times)), "mean_ms": 1e3 * float(np.mean(times)), "dll_median_ms": float(np.median(dll_ms)) if dll_ms else None,
               "base_median_ms": 1e3 * float(np.median(base_times)), "kernel_ms": 1e3 * float(np.median(times) - np.median(base_times)),
               "worst": worst.tolist(), "flips": flips, "good_mismatch": good_mismatch, "bad_frames": [str(b) for b in bad_frames], "times": times, "base_times": base_times, "flags": FLAGS},
              open(os.path.join(HERE, "run_gpu2_results.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
