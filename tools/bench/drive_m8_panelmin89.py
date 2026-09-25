r"""drive_m8_panelmin89.py - card 89-4 Part 1 (PD195(d), review A2): TWO REAL `s1` legs of the unmodified D1_s1_copy.vi at
15 picks, 90 Hz, RUN_S 120 s - L-min (front panel MINIMIZED by COM during the experiment loop) then L-ctl (same-session
control, panel left as the driver leaves it). Lost frames are REPORTED, not gated (the measurement).
FOUND FIRST: tools/bench/drive_m8_load83_kswap88.py (card 88-2) - this is that sequencer with the legs replaced and the
per-leg command pointed at drive_m8_panelmin89_leg.py (camera() copied verbatim; that module has no main guard).
PREDICTION CONTRACT (per leg): T1 rc 0 (drive_m8 M1..M8 + PM1..PM4)  T2 LabVIEW gone before start  T3 0 TIFFs
 T4 camera 90 Hz before (+-0.5)  T5 frames/s within 15 % of 90  T6 LabVIEW gone after. End: T7 camera 90 Hz; T8 S1 + L2-A1
 bed + kswap md5 unchanged; T9 backed-up jsons restored.
    MATERIAL=1 py tools/bgrun.py --max-min 40 --log tools/bench/m8_panelmin_89.log -- py -u tools/bench/drive_m8_panelmin89.py [--dry]
"""
import ctypes as C, json, os, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
import protocol as P                                                            # noqa: E402
import imaqdx_limits as L                                                       # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DRY = "--dry" in sys.argv; HZ, N, RUN_S = 90, 15, 120
PIN = {"S1": (os.path.join(CD, "D1_s1_copy.vi"), "3e3d23cefd3a334001aa9d6156bf1aee"),
       "bedL2A1": (os.path.join(CD, "D1_l2_a1_20260925_235224.vi"), "51d9b8a3af5b4240cdc2ad193d9b4f41"),
       "kswap": (os.path.join(CD, "D1_s1_kswap_20260926_004935.vi"), "e77b8d5805d90f76e426cb06fdc26d1c")}
LEGS = [("ctl", "--control"), ("min", "--minimize")]   # control FIRST: cycle 88's later legs lost MORE (3410->3490->3776), so a
                                                       # collapse on the second leg cannot be the order effect (review c89-panelmin-dry-t5 §order)
HARD_MIN, LEG_MAX_MIN = 36.0, 12.0
T0 = time.time()


def lv_running():
    return "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()


def md5(p):
    import hashlib; return hashlib.md5(open(p, "rb").read()).hexdigest()


def camera(hz=None):
    """drive_m8_load83.camera, verbatim."""
    if DRY: return {"camera": "DRY", "hz": 90.0}
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


SUF = "_dry" if DRY else ""
FIXED = ["m8_s1_p%d_r%d%s.json" % (N, RUN_S, SUF)] + ["m8_v5_s1_p%d_r%d%s%s.json" % (N, RUN_S, SUF, x) for x in ("", "_clicks")]
BK = {}
for f in FIXED:
    p = os.path.join(HERE, f)
    if os.path.isfile(p):
        b = os.path.join(HERE, "m8_panelmin_89_bak_" + f); shutil.copyfile(p, b); BK[p] = (b, md5(p))
print("backed up %s" % sorted(os.path.basename(k) for k in BK), flush=True)
rows, gates = [], {}
try:
    for i, (tag0, flag) in enumerate(LEGS, 1):
        tag = "leg%d %s@%d@%dHz" % (i, tag0, N, HZ); el = (time.time() - T0) / 60
        if el + LEG_MAX_MIN > HARD_MIN:
            print("SKIP %s: elapsed %.1f min" % (tag, el), flush=True); rows.append({"leg": tag, "skipped": "hard stop"}); continue
        gates["T2 %s LabVIEW gone before start" % tag] = DRY or not lv_running()
        cam_before = camera(HZ)
        print("=== LEG %s start at %.1f min; camera before: %s" % (tag, el, json.dumps(cam_before)), flush=True)
        gates["T4 %s camera 90 Hz before" % tag] = bool(cam_before) and cam_before.get("hz") is not None and abs(cam_before["hz"] - HZ) <= 0.5
        cmd = [sys.executable, "-u", os.path.join(HERE, "drive_m8_panelmin89_leg.py"), flag, "--picks", str(N), "--run-s", str(RUN_S)] + (["--dry"] if DRY else [])
        t = time.time()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=LEG_MAX_MIN * 60 + 120); rc, out, err = r.returncode, r.stdout or "", r.stderr or ""
        except subprocess.TimeoutExpired as e:
            rc, out, err = "TIMEOUT", (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), ""
        pm = {}
        for ln in out.splitlines():
            if ln.startswith(("GATE ", "RESULT ", "|", "[panelmin")) or "FAILING" in ln or "=== D0" in ln: print("  " + ln[:300], flush=True)
            if ln.startswith("GATE PM"): pm[ln[5:].rsplit(None, 1)[0].strip()] = ln.endswith("PASS")
        if err: print("  STDERR tail: " + err[-800:], flush=True)
        t2 = time.time()
        while not DRY and lv_running() and time.time() - t2 < 90: time.sleep(5)
        gates["T6 %s LabVIEW gone after" % tag] = DRY or not lv_running()
        cam_after = camera()
        jp = os.path.join(HERE, "m8_s1_p%d_r%d%s.json" % (N, RUN_S, SUF))
        j = json.load(open(jp)) if os.path.isfile(jp) and os.path.getmtime(jp) >= t else {}
        if j: shutil.copyfile(jp, os.path.join(HERE, "m8_panelmin_89_leg%d%s.json" % (i, SUF)))
        pmp = os.path.join(HERE, "m8_panelmin_89_%s_pm.json" % tag0)
        pmj = json.load(open(pmp)) if os.path.isfile(pmp) and os.path.getmtime(pmp) >= t else {}
        hdr = j.get("tra_header_points") or {}; fd = j.get("frame_counter_delta")
        row = {"leg": tag, "mode": tag0, "vi": PIN["S1"][0], "hz_cell": HZ, "picks": N, "run_s": RUN_S,
               "rc": rc, "secs": round(time.time() - t), "json": ("tools/bench/m8_panelmin_89_leg%d%s.json" % (i, SUF)) if j else None,
               "camera_before": cam_before, "camera_after": cam_after,
               "reached_experiment_loop": (j.get("gates") or {}).get("M2 reached experiment loop"),
               "frames_delta": fd, "measured_hz": (round(fd / RUN_S, 1) if isinstance(fd, (int, float)) and fd else None),
               "lost_frames": j.get("total_lost_frames"), "pm_gates": pm, "pm_facts": (pmj.get("facts") or {}),
               "tra_rows_header": {k: (v[0] if v else None) for k, v in hdr.items()},
               "tiffs": (j.get("tiffs_deleted") or {}).get("count"), "stop_latency_s": (j.get("stop") or {}).get("latency_s"),
               "labview_exited": (j.get("gates") or {}).get("M6 LabVIEW gone (tasklist)"),
               "picks_done": j.get("picks"), "motor_tmx_after": j.get("motor_after"),
               "gates": j.get("gates"), "v5_failing": j.get("v5_failing_steps")}
        rows.append(row); print("ROW " + json.dumps(row, default=str)[:1500], flush=True)
        gates["T1 %s leg rc 0" % tag] = rc == 0
        gates["T3 %s 0 TIFFs" % tag] = row["tiffs"] == 0
        gates["T5 %s frames/s within 15%% of 90" % tag] = row["measured_hz"] is not None and abs(row["measured_hz"] - HZ) <= 0.15 * HZ
        if not DRY:   # review c89-panelmin-dry-t5: the controller limit is read back after the run and GATED, not only recorded
            gates["T10 %s motor TMX 39 after" % tag] = row["motor_tmx_after"] == 39.0
finally:
    restore = camera(90)
    for p, (b, m) in BK.items():
        shutil.copyfile(b, p)
    gates["T9 backed-up jsons restored"] = all(md5(p) == m for p, (b, m) in BK.items())
    for p, (b, m) in BK.items():
        if md5(p) == m: os.remove(b)
print("camera restored: %s" % json.dumps(restore), flush=True)
gates["T7 camera restored to 90 Hz"] = bool(restore) and restore.get("hz") is not None and abs(restore["hz"] - 90) <= 0.5
gates["T8 S1 + bed + kswap md5 unchanged"] = all(md5(p) == m for p, m in PIN.values())
out = {"schema": "m8-panelmin/1", "card": "89-4 PD195(d) A2", "run_s": RUN_S, "hz": HZ, "picks": N, "pins": PIN, "rows": rows,
       "gates": gates, "camera_restore": restore, "lv_running_at_end": lv_running(), "minutes": round((time.time() - T0) / 60, 1)}
jp = os.path.join(HERE, "m8_panelmin_89%s.json" % SUF); json.dump(out, open(jp, "w"), indent=1, default=str)
for k, v in gates.items(): print("GATE %-55s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in gates.items() if not v]
print(P.result_line(P.make_result(len(gates) - len(bad), len(bad), bad[0] if bad else None,
                                  [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
sys.exit(1 if bad else 0)
