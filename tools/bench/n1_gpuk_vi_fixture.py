"""n1_gpuk_vi_fixture.py - N1 at the VI LEVEL: GPU_kernel_v1.vi (inside HARNESS_gpuk.vi) vs the CPU-kernel
reference over the WHOLE 10,043-frame fixture, per bead, per axis. MEASUREMENT ONLY - nothing is fixed, no
kernel is touched, no original is opened (rule 1 / 1a).

WHAT ALREADY EXISTS (checked before writing, CLAUDE.md "before creating any new op/tool/recipe"):
  * tools/bench/gpu_n1_deltas.py  - the SAME comparison at the DLL level (ctypes -> tools/gpu/cuda/mt_track.dll),
                                    full fixture, per bead/axis, 8/8 gates, log gpu_n1_deltas.log 2026-09-17.
                                    It never loads LabVIEW, so it does NOT answer "does GPU_kernel_v1.vi agree".
  * tools/bench/run_timing.py     - drives HARNESS_base/par/gpuk over COM, N frames, and keeps ONE SCALAR
                                    `worst |dev|` over x,y,z together (run_timing.py:91). Cannot separate the
                                    axes, so it cannot be read against 1e-6 px / 1e-4 um. N defaults to 200.
  * tools/bench/gpuk_repeat.py    - three 200-frame repeats of run_timing (gpuk_repeat.log 2026-09-09:
                                    worst |dev| 2.93e-06 in all three, KERNEL gpuk 2.65/2.88/3.19 ms).
  * tools/bench/gpuk_chain.py     - lv_restart + DLL deploy + build_harness_variant --name=gpuk + run_timing.
  * HARNESS_gpuk.vi               - ALREADY BUILT in claudeDev (HARNESS_loadcal + IMAQ Create/ReadFile +
                                    windows + GPU_kernel_v1.vi). REUSED here, not rebuilt.
So the LabVIEW-side harness is reused as-is; only this driver (full fixture + per-axis accounting, the shape
gpu_n1_deltas.py uses) is new. Seeding and control names are COPIED from run_timing.py so the two agree.

DOES IT TOUCH LABVIEW?  YES - one COM client, HARNESS_gpuk.vi + HARNESS_loadcal.vi in claudeDev only.
NO original .vi is opened; md5(ORIGINAL) is recorded before and after anyway as rule-1 evidence.
NO motor, NO ASI, NO serial, NO camera (rig is 조립/ASSEMBLED; none of this needs the rig).

PREDICTION CONTRACT (machine-checkable; a miss = failed prediction => peer.ps1 -Agent claude -Role hypothesis):
  G1  the reference session carries exactly 10043 frames and 5 beads
  G2  HARNESS_gpuk.vi loads and ExecState == 1 BEFORE the sweep
  G3  the sweep completes every frame: XYZ shape == (10043, 5, 3)
  G4  over the FIRST 200 frames the scalar worst |dev| reproduces gpuk_repeat.log's 2.9253520219540974e-06
      to 1e-12 (same harness, same seeding, same frames)
  G5  the 13 recorded lost-bead rows (f11798...f11824) are found in the reference
  G6  the json is written and reloads with 10043 frame rows
  G7  md5(ORIGINAL) is c39f36e0675339673b707c59f0784fee before AND after
EXPECTED OUTPUT SHAPE: 10043 frames x 5 beads x 3 axes of |delta|, plus per-bead max/RMS per axis, the
number of frames exceeding 1e-6 px (x,y) / 1e-4 um (z), the cal-index flip list, and the k<10018 window.
Everything below the gates is REPORTED, not gated - it is the measurement.

Run:
  py tools/bgrun.py --material --max-min 45 --log tools/bench/n1_gpuk_vi_fixture.log -- py -u tools/bench/n1_gpuk_vi_fixture.py [N]
"""
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "gpu"))

import gscript as g  # noqa: E402
from fixture import CAL, DATA, read_cal, read_reference  # noqa: E402

g._lv = None
g._run.__defaults__ = (6.0, 120.0)

ORIGINAL = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
            r"\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
ORIGINAL_MD5 = "c39f36e0675339673b707c59f0784fee"
DEBUG = os.path.join(g.CLAUDEDEV, "Debug")
LOADER = os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")
GPUK = os.path.join(g.CLAUDEDEV, "HARNESS_gpuk.vi")
KERNEL = os.path.join(g.CLAUDEDEV, "GPU_kernel_v1.vi")
LABELS = json.load(open(os.path.join(HERE, "harness_gpuk_labels.json"), encoding="utf-8"))
OUT_JSON = os.path.join(HERE, "n1_gpuk_vi_fixture.json")
TOL_XY, TOL_Z = 1e-6, 1e-4
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10043

GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} {label}: {detail}", flush=True)
    return bool(ok)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print(f"N1 VI-LEVEL fixture comparison  N={N}  tol x,y {TOL_XY} px  z {TOL_Z} um", flush=True)
    print("nvidia-smi:", subprocess.run(["nvidia-smi", "--query-gpu=name,pstate,clocks.sm,clocks.mem",
                                         "--format=csv,noheader"], capture_output=True, text=True).stdout.strip(),
          flush=True)
    before = md5(ORIGINAL)
    print(f"md5(ORIGINAL) before = {before}", flush=True)

    ref = read_reference()
    rows = ref["frames"]
    cal = read_cal()
    nb = len(cal["xy"])
    F = min(N, len(rows))
    print(f"reference session {ref['meta']} frames {len(rows)} beads {nb}", flush=True)
    gate("G1 reference 10043 frames / 5 beads", len(rows) == 10043 and nb == 5,
         f"frames {len(rows)} beads {nb}")

    lost_frames = [int(r["frame"]) for r in rows if any(v == -1.0 for v in r["ff"])]
    gate("G5 recorded lost-bead rows found", len(lost_frames) == 13,
         f"{len(lost_frames)} rows carry -1.0: {lost_frames}")

    # --- fresh LabVIEW + the DLL the kernel calls (same as gpuk_chain.py) -------------------------
    rc = subprocess.run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], timeout=400, cwd=ROOT).returncode
    print(f"lv_restart rc {rc}", flush=True)
    g.reset()
    src = os.path.join(TOOLS, "gpu", "cuda", "mt_track.dll")
    import shutil
    for name in ("mt_track.dll", "GPU Tracking.dll"):
        shutil.copyfile(src, os.path.join(DEBUG, name))
    open(os.path.join(DEBUG, "mt_track_cal.txt"), "w").write(CAL)
    print(f"deployed {os.path.getsize(src)} B; cal fallback -> {CAL}", flush=True)

    # --- calibration through the harness loader, exactly as run_timing.py does -------------------
    ld = g.op(LOADER)
    ld.SetControlValue("file (use dialog)", CAL)
    g._run(ld)
    nb_lv = int(ld.GetControlValue("# of beads"))
    xyz0 = list(ld.GetControlValue("x,y,(blankz) array"))
    print(f"loader: # of beads {nb_lv}, seed len {len(xyz0)}", flush=True)

    vi = g.op(GPUK)
    es = int(vi.ExecState)
    gate("G2 HARNESS_gpuk ExecState == 1", es == 1, f"ExecState {es} ({GPUK})")
    try:
        kes = int(g.op(KERNEL).ExecState)
    except Exception as e:                                    # noqa: BLE001
        kes = f"ERR {e}"
    print(f"GPU_kernel_v1.vi ExecState {kes}  ({KERNEL})", flush=True)
    if es != 1:
        print("harness broken - sweep skipped", flush=True)
        return report(before, None, rows, nb, F, lost_frames, cal)

    C = LABELS["controls"]
    O = LABELS["outputs"]
    vi.SetControlValue(C["Image Name"], "n1_gpuk")
    vi.SetControlValue(C["# of bead 4 packs"], nb_lv // 4)
    vi.SetControlValue(C["4 pack remainder"], nb_lv % 4)

    XYZ = np.zeros((F, nb, 3))
    POSO = np.zeros((F, nb), np.int32)
    GOODO = np.zeros((F, nb), np.uint8)
    SKIP = np.zeros((F, nb), bool)
    t0 = time.time()
    for k in range(F):
        row = rows[k]
        if k == 0:
            state = (xyz0, [True] * nb, [0] * nb)
        else:
            prev = rows[k - 1]
            lost = any(v == -1.0 for v in prev["ff"])
            state = (xyz0, [True] * nb, prev["pos"]) if lost else (prev["ff"], prev["good"], prev["pos"])
        vi.SetControlValue(C["File Path"], os.path.join(DATA, f"img{row['frame']:05d}.tif"))
        vi.SetControlValue(C["x,y,z array"], state[0])
        vi.SetControlValue(C["Bead is good? array in"], state[1])
        vi.SetControlValue(C["pos in cal image in"], state[2])
        g._run(vi)
        out = [float(x) for x in vi.GetControlValue(O["x,y,z array out"])]
        XYZ[k] = np.array(out, np.float64).reshape(nb, 3)
        POSO[k] = [int(p) for p in vi.GetControlValue(O["pos in cal image out"])]
        GOODO[k] = [1 if bool(b) else 0 for b in vi.GetControlValue(O["Bead is good? array out"])]
        for b in range(nb):
            if not state[1][b] or row["ff"][3 * b] == -1.0:
                SKIP[k, b] = True
        if (k + 1) % 500 == 0 or k + 1 == F:
            print(f"   {k + 1}/{F} frames, {time.time() - t0:.0f}s", flush=True)
    print(f"sweep done: {F} frames in {time.time() - t0:.0f}s "
          f"({1000 * (time.time() - t0) / max(F, 1):.1f} ms/frame incl. COM)", flush=True)
    gate("G3 sweep frame/bead count", XYZ.shape == (F, nb, 3), f"XYZ shape {XYZ.shape} (expected ({F}, {nb}, 3))")
    return report(before, (XYZ, POSO, GOODO, SKIP), rows, nb, F, lost_frames, cal)


def report(before, sweep, rows, nb, F, lost_frames, cal):
    payload = {"meta": {"written": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "script": "tools/bench/n1_gpuk_vi_fixture.py",
                        "harness": GPUK, "kernel": KERNEL, "cal": CAL,
                        "reference": "tools/bench/fixture_compare_results.jsonl (CPU kernel, == .tra to 0.0)",
                        "frames": F, "beads": nb, "tol_xy_px": TOL_XY, "tol_z_um": TOL_Z,
                        "md5_original_before": before}}
    if sweep is not None:
        XYZ, POSO, GOODO, SKIP = sweep
        REF = np.array([r["ff"] for r in rows[:F]], np.float64).reshape(F, nb, 3)
        POS = np.array([r["pos"] for r in rows[:F]], np.int32)
        FRAMES = np.array([r["frame"] for r in rows[:F]], np.int64)
        FLIP = (POSO != POS) & ~SKIP
        DELTA = np.abs(XYZ - REF)
        VALID = ~SKIP & ~FLIP
        tol = [TOL_XY, TOL_XY, TOL_Z]

        # the scalar run_timing.py computes, over the first 200 frames, for gate G4
        w200 = 0.0
        for k in range(min(200, F)):
            w200 = max(w200, max(abs(a - b) for a, b in zip(XYZ[k].ravel().tolist(), rows[k]["ff"])))
        gate("G4 first 200 frames reproduce gpuk_repeat.log scalar worst |dev|",
             abs(w200 - 2.9253520219540974e-06) < 1e-12,
             f"worst |dev| first 200 = {w200:.10e} (gpuk_repeat.log: 2.9253520219540974e-06)")

        per_bead = []
        for b in range(nb):
            rec = {"bead": b, "cal_xy": cal["xy"][b].tolist(), "n_valid": int(VALID[:, b].sum()),
                   "n_skipped": int(SKIP[:, b].sum()), "n_flip": int(FLIP[:, b].sum())}
            for i, ax in enumerate("xyz"):
                col = np.where(VALID[:, b], DELTA[:, b, i], np.nan)
                ok = bool(np.any(~np.isnan(col)))
                mx = float(np.nanmax(col)) if ok else float("nan")
                kmax = int(np.nanargmax(col)) if ok else 0
                rms = float(np.sqrt(np.nanmean(col ** 2))) if ok else float("nan")
                exc = np.where(col > tol[i])[0]
                rec[ax] = {"max": mx, "rms": rms, "max_k": kmax, "max_frame": int(FRAMES[kmax]),
                           "n_exceed": int(exc.size), "tol": tol[i],
                           "first_k": int(exc[0]) if exc.size else None,
                           "first_frame": int(FRAMES[exc[0]]) if exc.size else None,
                           "exceed_k": exc.tolist()[:64]}
            per_bead.append(rec)
            print(f"bead {b}: " + "  ".join(
                f"|d{ax}| max {rec[ax]['max']:.3e} rms {rec[ax]['rms']:.3e} @k{rec[ax]['max_k']}"
                f"(f{rec[ax]['max_frame']}) exceed {rec[ax]['n_exceed']} first k{rec[ax]['first_k']}"
                for ax in "xyz"), flush=True)

        overall = {}
        for i, ax in enumerate("xyz"):
            col = np.where(VALID, DELTA[:, :, i], np.nan)
            overall[ax] = {"max": float(np.nanmax(col)), "rms": float(np.sqrt(np.nanmean(col ** 2))),
                           "tol": tol[i], "n_bead_frames_exceeding": int(np.nansum(col > tol[i]))}
        print("OVERALL: " + "  ".join(
            f"|d{ax}| max {overall[ax]['max']:.3e} rms {overall[ax]['rms']:.3e} tol {overall[ax]['tol']:.0e} "
            f"exceeding {overall[ax]['n_bead_frames_exceeding']}" for ax in "xyz"), flush=True)

        cut = 10018
        win = {}
        if F > cut:
            for i, ax in enumerate("xyz"):
                lo = np.where(VALID[:cut], DELTA[:cut, :, i], np.nan)
                hi = np.where(VALID[cut:], DELTA[cut:, :, i], np.nan)
                win[ax] = {"before_10018_max": float(np.nanmax(lo)),
                           "before_10018_rms": float(np.sqrt(np.nanmean(lo ** 2))),
                           "before_10018_exceed": int(np.nansum(lo > tol[i])),
                           "from_10018_max": float(np.nanmax(hi)) if np.any(~np.isnan(hi)) else None,
                           "from_10018_exceed": int(np.nansum(hi > tol[i]))}
            print("WINDOW k<10018 (before the first bead loss): " + "  ".join(
                f"|d{ax}| max {win[ax]['before_10018_max']:.3e} rms {win[ax]['before_10018_rms']:.3e} "
                f"exceeding {win[ax]['before_10018_exceed']}" for ax in "xyz"), flush=True)

        flips = [{"k": int(k), "frame": int(FRAMES[k]), "bead": int(b),
                  "cpu_idx": int(POS[k, b]), "gpu_idx": int(POSO[k, b]),
                  "cpu_z": float(REF[k, b, 2]), "gpu_z": float(XYZ[k, b, 2]),
                  "dz": float(XYZ[k, b, 2] - REF[k, b, 2])} for k, b in zip(*np.where(FLIP))]
        print(f"FLIPS {len(flips)}: " + json.dumps(flips[:10]), flush=True)
        goodmis = int(((GOODO != 0) != np.array([[bool(x) for x in r["good"]] for r in rows[:F]])).sum())
        print(f"good-flag mismatches vs reference: {goodmis} of {F * nb} bead-frames", flush=True)

        payload["per_bead"] = per_bead
        payload["overall"] = overall
        payload["window_10018"] = win
        payload["flips"] = flips
        payload["good_mismatches"] = goodmis
        payload["worst_dev_first200_scalar"] = w200
        payload["lost_bead_frames"] = lost_frames
        payload["frames"] = [[int(k), int(FRAMES[k])] + [None if SKIP[k, b] else float(DELTA[k, b, i])
                                                         for b in range(nb) for i in range(3)] for k in range(F)]

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    reread = json.load(open(OUT_JSON, encoding="utf-8"))
    gate("G6 json written and reloads", len(reread.get("frames", [])) == (F if sweep is not None else 0),
         f"{OUT_JSON} {os.path.getsize(OUT_JSON)} B, {len(reread.get('frames', []))} frame rows")

    after = md5(ORIGINAL)
    gate("G7 md5(ORIGINAL) unchanged", before == ORIGINAL_MD5 and after == ORIGINAL_MD5,
         f"before {before} after {after} (expected {ORIGINAL_MD5})")

    npass = sum(1 for _, ok, _ in GATES if ok)
    print(f"GATES {npass}/{len(GATES)} pass; failing: {[l for l, ok, _ in GATES if not ok] or 'none'}", flush=True)
    return 0 if npass == len(GATES) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        try:
            g.reset()
        except Exception:                                     # noqa: BLE001
            pass
