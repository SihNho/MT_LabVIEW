"""gpu_n1_deltas.py - LOCALISE the GPU/CPU divergence over the full 10,043-frame fixture (measurement only; no fix).

WHAT ALREADY EXISTS (checked before writing, per CLAUDE.md "before creating any new op/tool/recipe"):
  * tools/gpu/test_mt2.py         - the run that produced tools/bench/gpu_n1_full_fixture.log. It keeps only running
                                    maxima (`worst`) and a flip COUNT; nothing per frame is saved. -> must be re-run.
  * tools/gpu/check_all.py        - the same shape for the NumPy reference, and it DOES write per-frame jsonl
                                    ({frame, ex, ey, ez, out, ref}). This script is its analogue for the CUDA DLL:
                                    same seeding rule, same tolerances (TOL_XY 1e-6 px, TOL_Z 1e-4 um as check_all.py:17
                                    has it after the user's 2026-09-07 relaxation), per-bead instead of per-frame max.
  * tools/gpu/fixture.py          - read_cal/read_reference/read_image. NO LabVIEW, NO COM anywhere in the import
                                    chain (test_mt2 -> test_dll -> ref_numpy, fixture: numpy/ctypes/PIL only).
  * tools/gscript.py              - irrelevant here (LabVIEW COM); not imported.
No existing script answers "which bead, which frame, clustered or scattered, reproducible run-to-run", so this one is new.

DOES IT TOUCH LABVIEW?  NO. ctypes -> tools/gpu/cuda/mt_track.dll + recorded files under G:\Data\... and
tools/bench/fixture_compare_results.jsonl. No VI Server, no ActiveX, no lock needed. Gate G0 asserts no LabVIEW.exe
appears while we run.

PREDICTION CONTRACT (machine-checkable; a miss = failed prediction => peer review before anything else):
  G0  no LabVIEW.exe process exists at start or at end                                          (rule 3 / lock)
  G1  run A processes exactly 10043 frames, 5 beads                                             (= the logged run)
  G2  run A reproduces tools/bench/gpu_n1_full_fixture.log EXACTLY to the printed 3 s.f.:
      max|dx| 4.13e-06 px, max|dy| 3.13e-05 px, max|dz| 1.28e-05 um, flips 1
  G3  run B processes the same 10043 frames
  G4  GPU outputs of run B are BIT-IDENTICAL to run A (xyz, idx, good). <- the reproducibility question; a FAIL here
      is a real measurement, not a defect of this script, and is reported as such.
  G5  the json is written and reloads with 10043 frame records
  G6  the 13 recorded lost-bead frames named in archive/bench-2026-09-07-fixture/REPORT.md:49-51 are found
      (rows whose ff carries -1.0); count reported, not assumed.
Everything else (the per-bead table, the flip record, clustering) is REPORTED, not gated - it is the measurement.

Run:  MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/gpu_n1_deltas.log -- py -u tools/bench/gpu_n1_deltas.py
"""
import ctypes as C
import json
import os
import re
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GPU = os.path.join(ROOT, "tools", "gpu") if os.path.basename(ROOT) != "tools" else os.path.join(ROOT, "gpu")
sys.path.insert(0, GPU)
from fixture import CAL, read_cal, read_image, read_reference  # noqa: E402
import test_dll as T  # noqa: E402  (same DLL search-path setup: cudart/cufft)

OUT_JSON = os.path.join(HERE, "gpu_n1_deltas.json")
TOL_XY, TOL_Z = 1e-6, 1e-4
CROSS = 120
KA = int(os.environ.get("KA", "0"))

GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} {label}: {detail}", flush=True)
    return ok


def labview_running():
    try:
        out = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=30).stdout
    except Exception as e:
        return f"tasklist failed: {e}"
    return [l.split()[0] for l in out.splitlines() if "labview" in l.lower()]


lib = T.lib
lib.mt2_open.restype = C.c_int64
lib.mt2_open.argtypes = [C.c_char_p, C.c_int, C.c_int, C.c_char_p, C.c_int]
lib.mt2_set_image.argtypes = [C.c_int64, C.c_uint64, C.c_int, C.c_int, C.c_int]
lib.mt2_set_image.restype = C.c_int
D = C.POINTER(C.c_double); U8 = C.POINTER(C.c_ubyte); I = C.POINTER(C.c_int)
lib.mt2_track.argtypes = [C.c_int64, C.c_int, D, U8, D, I, U8, C.c_char_p, C.c_int]
lib.mt2_track.restype = C.c_int
lib.mt2_close.argtypes = [C.c_int64]


def run_pass(tag, rows, cal, nb, images):
    """One full sweep, identical in semantics to tools/gpu/test_mt2.py (same seeding, same skip rules).
    Returns xyz_out (F,nb,3), idx (F,nb), gout (F,nb), skip mask (F,nb) and the DLL-internal times."""
    status = C.create_string_buffer(128)
    ctx = lib.mt2_open(CAL.encode("mbcs"), CROSS, KA, status, 128)
    print(f"[{tag}] mt2_open -> {ctx != 0} {status.value}", flush=True)
    assert ctx
    H, W = 1024, 1280
    LW = W + 64
    buf = np.zeros((H, LW), np.uint8)
    F = len(rows)
    XYZ = np.zeros((F, nb, 3)); IDX = np.zeros((F, nb), np.int32); GO = np.zeros((F, nb), np.uint8)
    SKIP = np.zeros((F, nb), bool); ts = np.zeros(F)
    t_start = time.time()
    for k in range(F):
        row = rows[k]
        if k == 0:
            state = [[x, y, 0.0] for x, y in cal["xy"]]; good_in = [1] * nb
        else:
            prev = rows[k - 1]
            lost = any(v == -1.0 for v in prev["ff"])
            state = [[x, y, 0.0] for x, y in cal["xy"]] if lost else np.array(prev["ff"]).reshape(-1, 3).tolist()
            good_in = [1] * nb if lost else [int(g) for g in prev["good"]]
        img = images[k] if images is not None else read_image(row["frame"])
        buf[:, :W] = img
        assert lib.mt2_set_image(ctx, buf.ctypes.data, LW, W, H) == 0
        xyz_in = np.array(state, np.float64).ravel(); gin = np.array(good_in, np.uint8)
        xyz_out = np.zeros(3 * nb); idx = np.zeros(nb, np.int32); gout = np.zeros(nb, np.uint8)
        rc = lib.mt2_track(ctx, nb, xyz_in.ctypes.data_as(D), gin.ctypes.data_as(U8), xyz_out.ctypes.data_as(D),
                           idx.ctypes.data_as(I), gout.ctypes.data_as(U8), status, 128)
        assert rc == 0, status.value
        m = re.search(rb"t=([\d.]+)", status.value)
        ts[k] = float(m.group(1)) if m else np.nan
        XYZ[k] = xyz_out.reshape(nb, 3); IDX[k] = idx; GO[k] = gout
        for b in range(nb):
            if not good_in[b] or row["ff"][3 * b] == -1.0:
                SKIP[k, b] = True
        if (k + 1) % 2000 == 0:
            print(f"[{tag}] {k + 1}/{F} frames, {time.time() - t_start:.0f}s", flush=True)
    lib.mt2_close(ctx)
    print(f"[{tag}] done {F} frames in {time.time() - t_start:.0f}s; DLL median {np.median(ts[1:]):.2f} ms", flush=True)
    return XYZ, IDX, GO, SKIP, ts


def main():
    print("nvidia-smi:", subprocess.run(["nvidia-smi", "--query-gpu=name,pstate,clocks.sm,clocks.mem",
                                         "--format=csv,noheader"], capture_output=True, text=True).stdout.strip(), flush=True)
    lv0 = labview_running()
    gate("G0a no LabVIEW at start", lv0 == [], f"tasklist labview -> {lv0}")

    cal = read_cal(); ref = read_reference(); rows = ref["frames"]; nb = len(cal["xy"])
    F = len(rows)
    print(f"reference session {ref['meta']} frames {F} beads {nb}", flush=True)

    REF = np.array([r["ff"] for r in rows], np.float64).reshape(F, nb, 3)
    POS = np.array([r["pos"] for r in rows], np.int32)
    FRAMES = np.array([r["frame"] for r in rows], np.int64)
    lost_rows = [int(FRAMES[k]) for k in range(F) if any(v == -1.0 for v in rows[k]["ff"])]
    gate("G6 recorded lost-bead frames found", len(lost_rows) > 0,
         f"{len(lost_rows)} rows carry -1.0: {lost_rows}")

    A = run_pass("A", rows, cal, nb, None)
    gate("G1 run A frame/bead count", A[0].shape == (10043, 5, 3), f"XYZ shape {A[0].shape}")

    # --- deltas, run A ------------------------------------------------------
    XYZ, IDX, GO, SKIP, tsA = A
    FLIP = (IDX != POS) & ~SKIP
    DELTA = np.abs(XYZ - REF)
    VALID = ~SKIP & ~FLIP                       # exactly what test_mt2 accumulates `worst` over
    dm = np.where(VALID[:, :, None], DELTA, np.nan)
    wx, wy, wz = [np.nanmax(dm[:, :, i]) for i in range(3)]
    nflip = int(FLIP.sum())
    gate("G2 reproduces gpu_n1_full_fixture.log",
         f"{wx:.2e}" == "4.13e-06" and f"{wy:.2e}" == "3.13e-05" and f"{wz:.2e}" == "1.28e-05" and nflip == 1,
         f"max|dx| {wx:.2e} |dy| {wy:.2e} |dz| {wz:.2e} flips {nflip} (log: 4.13e-06 / 3.13e-05 / 1.28e-05 / 1)")

    # --- per bead, per axis -------------------------------------------------
    tol = [TOL_XY, TOL_XY, TOL_Z]
    per_bead = []
    for b in range(nb):
        rec = {"bead": b, "cal_xy": cal["xy"][b].tolist(), "n_valid": int(VALID[:, b].sum()),
               "n_skipped": int(SKIP[:, b].sum()), "n_flip": int(FLIP[:, b].sum())}
        for i, ax in enumerate("xyz"):
            col = np.where(VALID[:, b], DELTA[:, b, i], np.nan)
            any_valid = bool(np.any(~np.isnan(col)))
            mx = float(np.nanmax(col)) if any_valid else float("nan")
            kmax = int(np.nanargmax(col)) if any_valid else 0
            exc = np.where(col > tol[i])[0]
            rec[ax] = {"max": mx, "max_k": kmax, "max_frame": int(FRAMES[kmax]),
                       "n_exceed": int(exc.size), "tol": tol[i],
                       "first_k": int(exc[0]) if exc.size else None,
                       "first_frame": int(FRAMES[exc[0]]) if exc.size else None,
                       "exceed_k": exc.tolist()}
        per_bead.append(rec)
        print(f"bead {b}: " + "  ".join(
            f"|d{ax}| max {rec[ax]['max']:.3e} @k{rec[ax]['max_k']}(f{rec[ax]['max_frame']}) "
            f"exceed {rec[ax]['n_exceed']} first k{rec[ax]['first_k']}" for ax in "xyz"), flush=True)

    # --- the flip(s) --------------------------------------------------------
    flips = []
    for k, b in zip(*np.where(FLIP)):
        k = int(k); b = int(b)
        nbhd = []
        for kk in range(max(0, k - 3), min(F, k + 4)):
            nbhd.append({"k": kk, "frame": int(FRAMES[kk]),
                         "cpu_xyz": REF[kk, b].tolist(), "gpu_xyz": XYZ[kk, b].tolist(),
                         "cpu_idx": int(POS[kk, b]), "gpu_idx": int(IDX[kk, b]),
                         "skipped": bool(SKIP[kk, b]), "flip": bool(FLIP[kk, b])})
        flips.append({"k": k, "frame": int(FRAMES[k]), "bead": b,
                      "cpu_z": float(REF[k, b, 2]), "gpu_z": float(XYZ[k, b, 2]),
                      "cpu_idx": int(POS[k, b]), "gpu_idx": int(IDX[k, b]),
                      "dz": float(XYZ[k, b, 2] - REF[k, b, 2]),
                      "dx": float(XYZ[k, b, 0] - REF[k, b, 0]), "dy": float(XYZ[k, b, 1] - REF[k, b, 1]),
                      "neighbourhood": nbhd})
        print(f"FLIP k={k} frame={FRAMES[k]} bead={b} cpu_idx={POS[k,b]} gpu_idx={IDX[k,b]} "
              f"cpu_z={REF[k,b,2]:.6f} gpu_z={XYZ[k,b,2]:.6f} dz={XYZ[k,b,2]-REF[k,b,2]:.3e}", flush=True)
        for n in nbhd:
            print(f"   k{n['k']} f{n['frame']} cpu z {n['cpu_xyz'][2]:.6f} idx {n['cpu_idx']} | "
                  f"gpu z {n['gpu_xyz'][2]:.6f} idx {n['gpu_idx']} | skip {n['skipped']}", flush=True)

    # --- clustering ---------------------------------------------------------
    exceed_any = np.zeros(F, bool)
    for i in range(3):
        exceed_any |= (np.where(VALID, DELTA[:, :, i], 0.0) > tol[i]).any(axis=1)
    ks = np.where(exceed_any)[0]
    runs = []
    for k in ks:
        if runs and k == runs[-1][1] + 1:
            runs[-1][1] = int(k)
        else:
            runs.append([int(k), int(k)])
    lost_k = [k for k in range(F) if any(v == -1.0 for v in rows[k]["ff"])]
    first_lost_k = lost_k[0] if lost_k else None
    clustering = {"n_frames_exceeding_any_axis": int(ks.size),
                  "runs": [{"k0": a, "k1": b, "len": b - a + 1, "f0": int(FRAMES[a]), "f1": int(FRAMES[b])} for a, b in runs],
                  "beads_involved": sorted({int(b) for i in range(3)
                                            for b in np.where((np.where(VALID, DELTA[:, :, i], 0.0) > tol[i]).any(axis=0))[0]}),
                  "lost_bead_k": lost_k, "lost_bead_frames": lost_rows, "first_lost_k": first_lost_k,
                  "exceed_k_ge_first_lost": int((ks >= first_lost_k).sum()) if first_lost_k is not None else None,
                  "exceed_k_ge_10018": int((ks >= 10018).sum()),
                  "exceed_k_in_lost_rows": sorted(set(ks.tolist()) & set(lost_k)),
                  "min_exceed_k": int(ks.min()) if ks.size else None,
                  "max_exceed_k": int(ks.max()) if ks.size else None}
    print("CLUSTER:", json.dumps({k: v for k, v in clustering.items() if k not in ("lost_bead_k", "lost_bead_frames")}), flush=True)

    # --- run B: reproducibility --------------------------------------------
    B = run_pass("B", rows, cal, nb, None)
    gate("G3 run B frame/bead count", B[0].shape == A[0].shape, f"XYZ shape {B[0].shape}")
    same_xyz = A[0].tobytes() == B[0].tobytes()
    same_idx = np.array_equal(A[1], B[1]); same_good = np.array_equal(A[2], B[2])
    ndiff = int((A[0] != B[0]).sum())
    maxdiff = float(np.max(np.abs(A[0] - B[0]))) if ndiff else 0.0
    gate("G4 run B bit-identical to run A", same_xyz and same_idx and same_good,
         f"xyz bit-identical={same_xyz} idx={same_idx} good={same_good} differing_doubles={ndiff}/{A[0].size} "
         f"max|A-B|={maxdiff:.3e}")

    # --- write the raw per-frame deltas ------------------------------------
    payload = {
        "meta": {"written": time.strftime("%Y-%m-%d %H:%M:%S"), "script": "tools/bench/gpu_n1_deltas.py",
                 "dll": os.path.join("tools", "gpu", "cuda", "mt_track.dll"), "cal": CAL,
                 "reference": "tools/bench/fixture_compare_results.jsonl (CPU kernel, == .tra to 0.0)",
                 "frames": F, "beads": nb, "tol_xy_px": TOL_XY, "tol_z_um": TOL_Z,
                 "seeding": "state for frame k = reference ff of frame k-1 (cal xy after a lost bead) - CPU seeds "
                            "EVERY frame, so deltas do not accumulate across frames",
                 "runA_summary": {"max_dx": wx, "max_dy": wy, "max_dz": wz, "flips": nflip,
                                  "dll_median_ms": float(np.median(tsA[1:]))},
                 "runB_bit_identical": {"xyz": bool(same_xyz), "idx": bool(same_idx), "good": bool(same_good),
                                        "differing_doubles": ndiff, "max_abs_diff": maxdiff,
                                        "dll_median_ms": float(np.median(B[4][1:]))}},
        "per_bead": per_bead, "flips": flips, "clustering": clustering,
        "columns": "frames[i] = [k, frame, d0x,d0y,d0z, d1x,... ] with null where the bead was skipped "
                   "(bad in / reference -1) and the flip marked in flip_bk",
        "flip_bk": [[f["k"], f["bead"]] for f in flips],
        "frames": [[int(k), int(FRAMES[k])] + [None if SKIP[k, b] else float(DELTA[k, b, i])
                                               for b in range(nb) for i in range(3)] for k in range(F)],
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    reread = json.load(open(OUT_JSON, encoding="utf-8"))
    gate("G5 json written and reloads", len(reread["frames"]) == F,
         f"{OUT_JSON} {os.path.getsize(OUT_JSON)} B, {len(reread['frames'])} frame rows")

    lv1 = labview_running()
    gate("G0b no LabVIEW at end", lv1 == [], f"tasklist labview -> {lv1}")

    npass = sum(1 for _, ok, _ in GATES if ok)
    print(f"GATES {npass}/{len(GATES)} pass; failing: "
          f"{[l for l, ok, _ in GATES if not ok] or 'none'}", flush=True)
    return 0 if npass == len(GATES) else 1


if __name__ == "__main__":
    sys.exit(main())
