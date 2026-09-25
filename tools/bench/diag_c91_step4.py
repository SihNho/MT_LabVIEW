r"""diag_c91_step4.py - card 91-3 (PD196(d) step 4): FOUR REAL legs of the instrumented copy
claudeDev\D1_s1_t0_20260926_055551.vi (md5 25ea4f7d...) at 90 Hz, RUN_S 120 s, order 15/ctl, 15/min, 8/min, 8/ctl
(A B B A), each leg by diag_c91_step4_leg.py (drive_m8 replay_s1 + fresh T0STAMP_DIR + COM FPState minimize), then the
per-site time table (diag_c91_step4_stats.py, PD197(b) bucketing) and the 15-minus-8 slope.
FOUND FIRST: drive_m8_panelmin89b.py (the ABBA sequencer; camera() and the T-gates copied verbatim, legs re-pointed),
diag_c90_t0_smoke.py, drive_m8_panelmin89_leg.py. Nothing in them is edited.
Card rule: a leg whose REGISTERED picks (tra row width) differ from the target is logged and rerun ONCE; never half-counted.
PREDICTION CONTRACT (per leg): T1 rc 0 (drive_m8 M1..M8 + PM1..PM4 + K2/K3)  T2 LabVIEW gone before start  T3 0 TIFFs
 T4 camera 90 Hz before (+-0.5)  T5 frames/s within 15 % of 90  T6 LabVIEW gone after  T10 motor TMX 39 after
 T12 registered picks == target (after at most one rerun).  End: T7 camera 90 Hz; T8 S1 + bed + kswap + t0 md5 unchanged;
 T13 table written tools/bench/t0_step4_91.json with all 4 cells.
    MATERIAL=1 py tools/bgrun.py --max-min 60 --log tools/bench/diag_c91_step4.log -- py -u tools/bench/diag_c91_step4.py [--dry]
"""
import ctypes as C, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
import protocol as P                                                            # noqa: E402
import imaqdx_limits as L                                                       # noqa: E402
import diag_c91_step4_stats as ST                                               # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DRY = "--dry" in sys.argv; HZ, RUN_S = 90, 120
T0VI = os.path.join(CD, "D1_s1_t0_20260926_055551.vi")
PIN = {"S1": (os.path.join(CD, "D1_s1_copy.vi"), "3e3d23cefd3a334001aa9d6156bf1aee"),
       "bedL2A1": (os.path.join(CD, "D1_l2_a1_20260925_235224.vi"), "51d9b8a3af5b4240cdc2ad193d9b4f41"),
       "kswap": (os.path.join(CD, "D1_s1_kswap_20260926_004935.vi"), "e77b8d5805d90f76e426cb06fdc26d1c"),
       "t0": (T0VI, "25ea4f7d10d91c41c4b5de64f850c945")}
LEGS = [(15, "ctl", "--control"), (15, "min", "--minimize"), (8, "min", "--minimize"), (8, "ctl", "--control")]
# --legs 15ctl,8ctl runs a subset (a follow-up launch for cells the HARD_MIN skipped); --merge <json> carries the
# earlier launch's rows into this table so cells/slope are computed over both launches (a leg is never half-counted).
if "--legs" in sys.argv:
    want = sys.argv[sys.argv.index("--legs") + 1].split(","); LEGS = [l for l in LEGS if "%d%s" % (l[0], l[1]) in want]
MERGE = sys.argv[sys.argv.index("--merge") + 1] if "--merge" in sys.argv else None
HARD_MIN, LEG_MAX_MIN = 55.0, 12.0
T0 = time.time(); TS = time.strftime("%Y%m%d_%H%M%S")
LEGDIR = os.path.join(HERE, "t0_legs", "step4_%s%s" % (TS, "_dry" if DRY else "")); os.makedirs(LEGDIR, exist_ok=True)


def lv_running():
    return "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()


def md5(p):
    import hashlib; return hashlib.md5(open(p, "rb").read()).hexdigest()


def camera(hz=None):
    """drive_m8_panelmin89b.camera, verbatim."""
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
                "w": L.get(sess, L.IMG + "Width"), "h": L.get(sess, L.IMG + "Height")}
    finally:
        L.dx.IMAQdxCloseCamera(sess)


rows, gates = [], {}


def registered_ok(tra, N):
    """EXACT rule (review archive/peer/2026-09-26-c91-step4-t12.md §1): the tra holds an 8-byte 2-D dimension prefix
    after the header, so (data_bytes - 8) == rows_hdr x (24 + 24N) exactly. Launch 1 (06:26) compared a float width
    with 1e-9 and called a correct 15 a mismatch; a rounded tolerance was rejected by the review as too loose."""
    try:
        return any(isinstance(t, dict) and t.get("rows_hdr") and (t["data_bytes"] - 8) == t["rows_hdr"] * (24 + 24 * N) for t in (tra or {}).values())
    except (TypeError, ValueError, AttributeError): return False


def run_leg(i, N, tag0, flag, attempt):
    tag = "leg%d %s@%d%s" % (i, tag0, N, "" if attempt == 1 else " rerun")
    out = os.path.join(LEGDIR, "leg%d_%s_p%d_a%d" % (i, tag0, N, attempt)); os.makedirs(out, exist_ok=True)
    gates["T2 %s LabVIEW gone before start" % tag] = DRY or not lv_running()
    cam_before = camera(HZ)
    print("=== LEG %s start at %.1f min; camera before: %s" % (tag, (time.time() - T0) / 60, json.dumps(cam_before)), flush=True)
    gates["T4 %s camera 90 Hz before" % tag] = bool(cam_before) and cam_before.get("hz") is not None and abs(cam_before["hz"] - HZ) <= 0.5
    cmd = [sys.executable, "-u", os.path.join(HERE, "diag_c91_step4_leg.py"), flag, "--src", T0VI, "--picks", str(N),
           "--run-s", str(RUN_S), "--out", out]
    t = time.time()
    if DRY:
        rc, o, err = 0, "", ""; json.dump({"pm": {}, "facts": {"picks_registered_tra": N, "lost": "0", "stamp_counts": {}}, "m8": {}}, open(os.path.join(out, "leg.json"), "w"))
    else:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=LEG_MAX_MIN * 60 + 180); rc, o, err = r.returncode, r.stdout or "", r.stderr or ""
        except subprocess.TimeoutExpired as e:
            rc, o, err = "TIMEOUT", (e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")), ""
    for ln in o.splitlines():
        if ln.startswith(("GATE ", "RESULT ", "[step4", "STAMP", "REGISTERED")) or "FAILING" in ln or "=== D0" in ln: print("  " + ln[:300], flush=True)
    if err: print("  STDERR tail: " + err[-800:], flush=True)
    t2 = time.time()
    while not DRY and lv_running() and time.time() - t2 < 90: time.sleep(5)
    if not DRY and lv_running():
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True); time.sleep(5)
        print("  LabVIEW still up after the leg -> taskkill", flush=True)
    gates["T6 %s LabVIEW gone after" % tag] = DRY or not lv_running()
    cam_after = camera()
    lj = os.path.join(out, "leg.json"); j = json.load(open(lj)) if os.path.isfile(lj) else {}
    F = j.get("facts") or {}; m8 = j.get("m8") or {}
    try: lost = int(F.get("lost"))
    except (TypeError, ValueError): lost = None
    fd = m8.get("frame_counter_delta")
    row = {"leg": tag, "mode": tag0, "picks": N, "attempt": attempt, "rc": rc, "secs": round(time.time() - t), "dir": os.path.relpath(out, ROOT),
           "camera_before": cam_before, "camera_after": cam_after, "lost_frames": lost, "frames_delta": fd,
           "measured_hz": (round(fd / RUN_S, 1) if isinstance(fd, (int, float)) and fd else None),
           "picks_registered_tra": F.get("picks_registered_tra"), "picks_registered_cal": F.get("picks_registered_cal"),
           "hwndCapture_nonzero": F.get("foreign_capture_nonzero"), "bandpass_answered": F.get("bandpass_answered"),
           "picks_markers": F.get("picks_markers"), "tra": F.get("tra"), "tra_header_points": F.get("tra_header_points"),
           "stamp_counts": F.get("stamp_counts"), "fpstate": {k: F.get(k) for k in ("fpstate_before", "fpstate_after_min", "rect_after_min", "fpstate_after_restore") if k in F},
           "lost_at_minimize": (F.get("counters_at_minimize") or {}).get("lost") if isinstance(F.get("counters_at_minimize"), dict) else None,
           "lost_at_restore": (F.get("counters_at_restore") or {}).get("lost") if isinstance(F.get("counters_at_restore"), dict) else None,
           "pm_gates": j.get("pm"), "m8_gates": m8.get("gates"), "v5_failing": m8.get("v5_failing_steps"),
           "stop_latency_s": (m8.get("stop") or {}).get("latency_s"), "motor_tmx_after": m8.get("motor_after"),
           "tiffs": (m8.get("tiffs_deleted") or {}).get("count"), "source_md5": m8.get("source_md5")}
    reg_ok = registered_ok(row["tra"], N) if not DRY else True
    row["registered_ok"] = reg_ok
    rows.append(row); print("ROW " + json.dumps(row, default=str)[:1800], flush=True)
    gates["T1 %s leg rc 0" % tag] = rc == 0
    gates["T3 %s 0 TIFFs" % tag] = DRY or row["tiffs"] == 0
    gates["T5 %s frames/s within 15%% of 90" % tag] = DRY or (row["measured_hz"] is not None and abs(row["measured_hz"] - HZ) <= 0.15 * HZ)
    if not DRY: gates["T10 %s motor TMX 39 after" % tag] = row["motor_tmx_after"] == 39.0
    return reg_ok, row


try:
    for i, (N, tag0, flag) in enumerate(LEGS, 1):
        for attempt in (1, 2):
            el = (time.time() - T0) / 60
            if el + LEG_MAX_MIN > HARD_MIN:
                print("SKIP leg%d %s@%d a%d: elapsed %.1f min" % (i, tag0, N, attempt, el), flush=True)
                rows.append({"leg": "leg%d %s@%d" % (i, tag0, N), "mode": tag0, "picks": N, "attempt": attempt, "skipped": "hard stop"}); break
            reg_ok, row = run_leg(i, N, tag0, flag, attempt)
            if reg_ok: break
            print("  REGISTERED picks %r != target %d -> %s" % (row["picks_registered_tra"], N, "rerun once" if attempt == 1 else "logged, no third run"), flush=True)
        gates["T12 leg%d %s@%d registered picks == target" % (i, tag0, N)] = bool(rows[-1].get("registered_ok"))
finally:
    restore = camera(90)
print("camera restored: %s" % json.dumps(restore), flush=True)
gates["T7 camera restored to 90 Hz"] = bool(restore) and restore.get("hz") is not None and abs(restore["hz"] - 90) <= 0.5
gates["T8 S1 + bed + kswap + t0 md5 unchanged"] = all(md5(p) == m for p, m in PIN.values())

# ---- per-site time table -------------------------------------------------------------------------------------------
cells = {}
prev_rows = []
if MERGE and os.path.isfile(MERGE):
    prev_rows = [dict(r, merged_from=os.path.relpath(MERGE, ROOT)) for r in json.load(open(MERGE)).get("rows", []) if not r.get("skipped")]
    for r in prev_rows:                      # re-judge launch 1's rows with the rounded rule; keep its verdict beside it
        r["registered_ok_launch1"] = r.get("registered_ok"); r["registered_ok"] = registered_ok(r.get("tra"), r.get("picks"))
    print("MERGED %d rows from %s: registered_ok now %s" % (len(prev_rows), MERGE, [(r["leg"], r["registered_ok"]) for r in prev_rows]), flush=True)
    for (N, m) in {(r["picks"], r["mode"]) for r in prev_rows}:
        ok_rows = [r for r in prev_rows if r["picks"] == N and r["mode"] == m and r["registered_ok"]]
        gates["T12 merged %s@%d registered picks == target" % (m, N)] = bool(ok_rows)
rows = prev_rows + rows
extra = {}
for r in rows:
    if r.get("registered_ok") and not r.get("skipped"):
        key = (r["picks"], r["mode"]); tgt = cells if key not in cells else extra    # FIRST valid attempt = the cell; a valid rerun = extra
        try: tgt[key] = dict(ST.table(os.path.join(ROOT, r["dir"])), leg=r["leg"], attempt=r.get("attempt"), lost_frames=r.get("lost_frames"))
        except Exception as e:                                                 # noqa: BLE001
            tgt[key] = {"error": repr(e), "leg": r["leg"]}
slope = {}
for mode in ("ctl", "min"):
    a, b = cells.get((15, mode)), cells.get((8, mode))
    if not a or not b or "error" in a or "error" in b: slope[mode] = None; continue
    S = {}
    for ln, la in a["loops"].items():
        lb = b["loops"].get(ln) or {}
        if "sites" not in la or "sites" not in lb: continue
        S[ln] = {"period_median_15_minus_8_us": (la["period_us"]["median"] or 0) - (lb["period_us"]["median"] or 0),
                 "period_slope_us_per_bead": ((la["period_us"]["median"] or 0) - (lb["period_us"]["median"] or 0)) / 7.0, "sites": {}}
        for s, sa in la["sites"].items():
            sb = lb["sites"].get(s) or {}
            if "delta_us" in sa and "delta_us" in sb:
                d = (sa["delta_us"]["median"] or 0) - (sb["delta_us"]["median"] or 0)
                dl = (sa["last_in_iter_us"]["median"] or 0) - (sb["last_in_iter_us"]["median"] or 0)
                S[ln]["sites"][s] = {"median_15": sa["delta_us"]["median"], "median_8": sb["delta_us"]["median"], "diff_15_minus_8_us": d, "slope_us_per_bead": d / 7.0,
                                     "last_median_15": sa["last_in_iter_us"]["median"], "last_median_8": sb["last_in_iter_us"]["median"], "last_diff_us": dl, "last_slope_us_per_bead": dl / 7.0,
                                     "p95_15": sa["delta_us"]["p95"], "p95_8": sb["delta_us"]["p95"]}
    slope[mode] = S
gates["T13 table has all 4 cells"] = DRY or all((n, m) in cells and "error" not in cells[(n, m)] for n in (15, 8) for m in ("ctl", "min"))
out = {"schema": "t0-step4/1", "card": "91-3 PD196(d) step 4", "vi": T0VI, "vi_md5": PIN["t0"][1], "run_s": RUN_S, "hz": HZ,
       "order": [l[:2] for l in LEGS], "rows": rows, "cells": {"%d_%s" % k: v for k, v in cells.items()},
       "cells_extra_valid_reruns": {"%d_%s" % k: v for k, v in extra.items()}, "slope_15_vs_8": slope,
       "gates": gates, "camera_restore": restore, "lv_running_at_end": lv_running(), "minutes": round((time.time() - T0) / 60, 1), "legdir": os.path.relpath(LEGDIR, ROOT)}
jp = os.path.join(HERE, "t0_step4_91%s%s.json" % ("_dry" if DRY else "", "" if not ("--legs" in sys.argv and not MERGE) else "_part")); json.dump(out, open(jp, "w"), indent=1, default=str)
for k, v in gates.items(): print("GATE %-55s %s" % (k, "PASS" if v else "FAIL"), flush=True)
print("SUMMARY lost " + json.dumps({r["leg"]: r.get("lost_frames") for r in rows}), flush=True)
for mode, S in slope.items():
    for ln, v in (S or {}).items():
        print("SLOPE %s %s period 15-8 %.1f us (%.1f us/bead); sites: %s" % (mode, ln, v["period_median_15_minus_8_us"], v["period_slope_us_per_bead"],
              {s: (round(x["median_8"], 1), round(x["median_15"], 1), round(x["slope_us_per_bead"], 1)) for s, x in v["sites"].items()}), flush=True)
bad = [k for k, v in gates.items() if not v]
print(P.result_line(P.make_result(len(gates) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
sys.exit(1 if bad else 0)
