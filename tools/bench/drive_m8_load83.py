r"""drive_m8_load83.py - cycle 83 (steer_82 / PD188(d), user load D-2026-09-25-01): S1 vs S3 REAL RUNS at the
user's load - 8 and 15 bead picks, 90 Hz then 150 Hz, RUN_S = 120 s per leg. Total Lost Frames per cell.

FOUND FIRST: tools/bench/drive_m8_s1s3.py (card 77-6, INDEX row 46) - this file is that sequencer with (1) the
user's cells, (2) `--run-s 120`, (3) the camera's AcquisitionFrameRate written through the IMAQdx C API between legs
(LabVIEW not running, camera session free) and READ BACK before and after each leg. The VI does not write the rate
(docs/camera-acquisition-facts.md:25 - the rate is a camera attribute the VI inherits); the ceiling is 247.95 Hz at the
full 1280x1024 frame (:29-37), so no ROI change is needed for 150 Hz - the ROI used is recorded from the read-back.
PREDICTION CONTRACT (per leg): T1 leg rc == 0 (drive_m8 M1..M8)  T2 LabVIEW gone before the leg starts
 T3 0 TIFFs  T4 camera rate read back before the leg == the cell's Hz (+-0.5)  T5 frames_delta / RUN_S within 15 % of
 the cell's Hz (else the camera ran at another rate during the VI - reported, not hidden).
A leg is not STARTED past HARD_MIN. The camera is restored to 90 Hz at the end (the rig's configured condition).
"""
import ctypes as C, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
import protocol as P                                                            # noqa: E402
import imaqdx_limits as L                                                       # noqa: E402
RUN_S = 120
CELLS = [(90, 8), (90, 15), (150, 8), (150, 15)]              # (Hz, picks); each cell = s1 leg then s3 leg
HARD_MIN, LEG_MAX_MIN = 120.0, 12.0
T0 = time.time()

def lv_running():
    return "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()

def md5(p):
    import hashlib; return hashlib.md5(open(p, "rb").read()).hexdigest()

def camera(hz=None):
    """Open the camera, optionally write AcquisitionFrameRate = hz, read back rate + ROI. None if no camera."""
    n = C.c_uint32(0); L.dx.IMAQdxEnumerateCameras(None, C.byref(n), C.c_uint32(1))
    if not n.value: return None
    arr = (L.CameraInformation * n.value)(); L.dx.IMAQdxEnumerateCameras(arr, C.byref(n), C.c_uint32(1))
    sess = C.c_uint32(0); name = arr[0].InterfaceName.decode()
    if L.dx.IMAQdxOpenCamera(name.encode(), C.c_uint32(0), C.byref(sess)): return {"error": "open failed"}
    try:
        rc = None
        if hz is not None:
            rc = L.dx.IMAQdxSetAttribute(sess, (L.ACQ + "AcquisitionFrameRate").encode(), C.c_uint32(L.F64), C.c_double(float(hz)))
            time.sleep(0.2)
        return {"camera": name, "set_rc": rc, "hz": L.get(sess, L.ACQ + "AcquisitionFrameRate", L.F64),
                "period_us": L.get(sess, L.ACQ + "AcquisitionFrameRateRaw"),
                "w": L.get(sess, L.IMG + "Width"), "h": L.get(sess, L.IMG + "Height"),
                "ox": L.get(sess, L.IMG + "OffsetX"), "oy": L.get(sess, L.IMG + "OffsetY")}
    finally:
        L.dx.IMAQdxCloseCamera(sess)

rows, gates = [], {}
for hz, n in CELLS:
    for leg in ("s1", "s3"):
        tag = "%s@%d@%dHz" % (leg, n, hz); el = (time.time() - T0) / 60
        if el + LEG_MAX_MIN > HARD_MIN:
            print("SKIP %s: elapsed %.1f min + %.0f > hard stop %.0f" % (tag, el, LEG_MAX_MIN, HARD_MIN), flush=True)
            rows.append({"leg": tag, "skipped": "hard stop"}); continue
        gates["T2 %s LabVIEW gone before start" % tag] = not lv_running()
        cam_before = camera(hz)
        print("=== LEG %s start at %.1f min; camera before: %s" % (tag, el, json.dumps(cam_before)), flush=True)
        gates["T4 %s camera rate %d Hz before leg" % (tag, hz)] = bool(cam_before) and cam_before.get("hz") is not None \
            and abs(cam_before["hz"] - hz) <= 0.5
        t = time.time()
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "drive_m8.py"), "--leg", leg, "--picks", str(n),
                            "--run-s", str(RUN_S)], capture_output=True, text=True, timeout=LEG_MAX_MIN * 60 + 120)
        out = r.stdout or ""
        for ln in out.splitlines():
            if ln.startswith(("GATE ", "RESULT ", "|")) or "FAILING" in ln or "=== D0" in ln: print("  " + ln[:300], flush=True)
        if r.stderr: print("  STDERR tail: " + r.stderr[-800:], flush=True)
        t2 = time.time()
        while lv_running() and time.time() - t2 < 90: time.sleep(5)
        cam_after = camera()
        jp = os.path.join(HERE, "m8_%s_p%d_r%d.json" % (leg, n, RUN_S))
        j = json.load(open(jp)) if os.path.isfile(jp) and os.path.getmtime(jp) >= t else {}
        hdr = j.get("tra_header_points") or {}
        fd = j.get("frame_counter_delta"); secs_run = RUN_S
        row = {"leg": tag, "hz_cell": hz, "picks": n, "run_s": RUN_S, "rc": r.returncode, "secs": round(time.time() - t),
               "json": os.path.relpath(jp, ROOT) if j else None, "camera_before": cam_before, "camera_after": cam_after,
               "reached_experiment_loop": (j.get("gates") or {}).get("M2 reached experiment loop"),
               "frames_delta": fd, "measured_hz": (round(fd / secs_run, 1) if isinstance(fd, (int, float)) and fd else None),
               "lost_frames": j.get("total_lost_frames"),
               "tra_rows_header": {k: (v[0] if v else None) for k, v in hdr.items()}, "tra_rows_bytes": j.get("tra_rows"),
               "tiffs": (j.get("tiffs_deleted") or {}).get("count"), "stop_latency_s": (j.get("stop") or {}).get("latency_s"),
               "labview_exited": (j.get("gates") or {}).get("M6 LabVIEW gone (tasklist)"),
               "picks_done": j.get("picks"), "bandpass": j.get("bandpass"), "motor_tmx_after": j.get("motor_after"),
               "gates": j.get("gates"), "v5_failing": j.get("v5_failing_steps")}
        rows.append(row); print("ROW " + json.dumps(row, default=str)[:1200], flush=True)
        gates["T1 %s leg rc 0" % tag] = r.returncode == 0
        gates["T3 %s 0 TIFFs" % tag] = row["tiffs"] == 0
        gates["T5 %s frames/s within 15%% of %d Hz" % (tag, hz)] = row["measured_hz"] is not None and abs(row["measured_hz"] - hz) <= 0.15 * hz
restore = camera(90)
print("camera restored: %s" % json.dumps(restore), flush=True)
gates["T6 camera restored to 90 Hz"] = bool(restore) and restore.get("hz") is not None and abs(restore["hz"] - 90) <= 0.5
out = {"schema": "m8-load/1", "card": "cycle 83 PD188(d)", "run_s": RUN_S, "cells": CELLS, "rows": rows, "gates": gates,
       "camera_restore": restore, "lv_running_at_end": lv_running(), "minutes": round((time.time() - T0) / 60, 1)}
jp = os.path.join(HERE, "m8_load_83.json"); json.dump(out, open(jp, "w"), indent=1, default=str)
for k, v in gates.items(): print("GATE %-55s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in gates.items() if not v]
print(P.result_line(P.make_result(len(gates) - len(bad), len(bad), bad[0] if bad else None,
                                  [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
sys.exit(1 if bad else 0)
