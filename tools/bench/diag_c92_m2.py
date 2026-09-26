r"""diag_c92_m2.py - card 92-1 M2 (PD198(c)(2)): ONE unstamped D1_s1_copy.vi leg, 8 picks, panel normal, 120 s, 90 Hz,
on today's harness, by diag_c92_unstamped_leg.py; rerun ONCE when the registered picks (exact tra rule) != 8.
FOUND FIRST: diag_c91_step4.py (the ABBA sequencer: camera(), T-gates, registered_ok, rerun rule - copied, re-pointed to
the unstamped S1 and one leg); drive_m8_load83.py. Nothing in them is edited.
PRE-LAUNCH (card M2 pre-launch): the two leg-gating readers run on the EXISTING INDEX-51 leg
tools/bench/t0_legs/step4_20260926_071816/leg2_ctl_p8_a1/leg.json with known answers: registered_ok(tra, 8) True,
registered_ok(tra, 7) False, lost 144, hwndCapture nonzero ['723452'].
PREDICTION CONTRACT: R1 tra rule on INDEX-51 leg == (True@8, False@7)  R2 lost reader on INDEX-51 leg == 144
 R3 capture reader on INDEX-51 leg == ['723452']  per leg: T1 rc 0  T2 LabVIEW gone before  T3 0 TIFFs  T4 camera 90 Hz
 before  T5 frames/s within 15 % of 90  T6 LabVIEW gone after  T10 TMX 39 after  T12 registered picks == 8 (<= 1 rerun)
 end: T7 camera 90 Hz  T8 S1 / t0 / kswap / bed md5 unchanged  T13 table tools/bench/m8_unstamped8_92.json written.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/m8_unstamped8_92.log -- py -u tools/bench/diag_c92_m2.py
"""
import ctypes as C, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
import protocol as P                                                            # noqa: E402
import imaqdx_limits as L                                                       # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DRY = "--dry" in sys.argv; HZ, RUN_S, NPICK = 90, 120, 8
S1 = os.path.join(CD, "D1_s1_copy.vi")
PIN = {"S1": (S1, "3e3d23cefd3a334001aa9d6156bf1aee"),
       "bedL2A1": (os.path.join(CD, "D1_l2_a1_20260925_235224.vi"), "51d9b8a3af5b4240cdc2ad193d9b4f41"),
       "kswap": (os.path.join(CD, "D1_s1_kswap_20260926_004935.vi"), "e77b8d5805d90f76e426cb06fdc26d1c"),
       "t0": (os.path.join(CD, "D1_s1_t0_20260926_055551.vi"), "25ea4f7d10d91c41c4b5de64f850c945")}
KNOWN = os.path.join(HERE, "t0_legs", "step4_20260926_071816", "leg2_ctl_p8_a1", "leg.json")
LEG_MAX_MIN = 12.0
T0 = time.time(); TS = time.strftime("%Y%m%d_%H%M%S")
LEGDIR = os.path.join(HERE, "t0_legs", "c92_unstamped8_%s%s" % (TS, "_dry" if DRY else "")); os.makedirs(LEGDIR, exist_ok=True)
rows, gates = [], {}


def lv_running():
    return "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()


def md5(p):
    import hashlib; return hashlib.md5(open(p, "rb").read()).hexdigest()


def camera(hz=None):
    """diag_c91_step4.camera, verbatim (drive_m8_panelmin89b.camera)."""
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
                "period_us": L.get(sess, L.ACQ + "AcquisitionFrameRateRaw"), "w": L.get(sess, L.IMG + "Width"), "h": L.get(sess, L.IMG + "Height")}
    finally:
        L.dx.IMAQdxCloseCamera(sess)


def registered_ok(tra, N):
    """EXACT rule (review archive/peer/2026-09-26-c91-step4-t12.md s1): (data_bytes - 8) == rows_hdr x (24 + 24N)."""
    try:
        return any(isinstance(t, dict) and t.get("rows_hdr") and (t["data_bytes"] - 8) == t["rows_hdr"] * (24 + 24 * N) for t in (tra or {}).values())
    except (TypeError, ValueError, AttributeError): return False


def lost_of(F):
    try: return int(F.get("lost"))
    except (TypeError, ValueError): return None


# ---- pre-launch: the readers on the INDEX-51 leg with known answers -------------------------------------------------
kj = json.load(open(KNOWN)); KF = kj.get("facts") or {}
gates["R1 tra rule on INDEX-51 leg == (True@8, False@7)"] = (registered_ok(KF.get("tra"), 8), registered_ok(KF.get("tra"), 7)) == (True, False)
gates["R2 lost reader on INDEX-51 leg == 144"] = lost_of(KF) == 144
gates["R3 capture reader on INDEX-51 leg == ['723452']"] = KF.get("foreign_capture_nonzero") == ["723452"]
print("PRELAUNCH readers: %s" % {k: v for k, v in gates.items()}, flush=True)
if not all(gates.values()):
    print("STOP: a reader failed its known-answer test; no leg launched", flush=True)
    print(P.result_line(P.make_result(sum(gates.values()), len(gates) - sum(gates.values()), next(k for k, v in gates.items() if not v))), flush=True)
    sys.exit(1)


def run_leg(attempt):
    tag = "leg1 ctl@8%s" % ("" if attempt == 1 else " rerun")
    out = os.path.join(LEGDIR, "leg1_ctl_p8_a%d" % attempt); os.makedirs(out, exist_ok=True)
    gates["T2 %s LabVIEW gone before start" % tag] = DRY or not lv_running()
    cam_before = camera(HZ)
    print("=== LEG %s start at %.1f min; camera before: %s" % (tag, (time.time() - T0) / 60, json.dumps(cam_before)), flush=True)
    gates["T4 %s camera 90 Hz before" % tag] = bool(cam_before) and cam_before.get("hz") is not None and abs(cam_before["hz"] - HZ) <= 0.5
    cmd = [sys.executable, "-u", os.path.join(HERE, "diag_c92_unstamped_leg.py"), "--src", S1, "--picks", str(NPICK), "--run-s", str(RUN_S), "--out", out]
    t = time.time()
    if DRY:
        rc, o, err = 0, "", ""; json.dump({"pm": {}, "facts": {"picks_registered_tra": NPICK, "lost": "0"}, "m8": {}}, open(os.path.join(out, "leg.json"), "w"))
    else:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=LEG_MAX_MIN * 60 + 180); rc, o, err = r.returncode, r.stdout or "", r.stderr or ""
        except subprocess.TimeoutExpired as e:
            rc, o, err = "TIMEOUT", (e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")), ""
    for ln in o.splitlines():
        if ln.startswith(("GATE ", "RESULT ", "[c92", "REGISTERED", "FIRST CLICK")) or "FAILING" in ln or "=== D0" in ln: print("  " + ln[:400], flush=True)
    if err: print("  STDERR tail: " + err[-800:], flush=True)
    t2 = time.time()
    while not DRY and lv_running() and time.time() - t2 < 90: time.sleep(5)
    if not DRY and lv_running():
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True); time.sleep(5); print("  LabVIEW still up after the leg -> taskkill", flush=True)
    gates["T6 %s LabVIEW gone after" % tag] = DRY or not lv_running()
    cam_after = camera()
    lj = os.path.join(out, "leg.json"); j = json.load(open(lj)) if os.path.isfile(lj) else {}
    F = j.get("facts") or {}; m8 = j.get("m8") or {}; fd = m8.get("frame_counter_delta")
    row = {"leg": tag, "mode": "ctl", "picks": NPICK, "attempt": attempt, "rc": rc, "secs": round(time.time() - t), "dir": os.path.relpath(out, ROOT),
           "camera_before": cam_before, "camera_after": cam_after, "lost_frames": lost_of(F), "frames_delta": fd,
           "measured_hz": (round(fd / RUN_S, 1) if isinstance(fd, (int, float)) and fd else None),
           "picks_registered_tra": F.get("picks_registered_tra"), "picks_registered_cal": F.get("picks_registered_cal"),
           "hwndCapture_nonzero": F.get("foreign_capture_nonzero"), "hwndCapture_seq": F.get("hwndCapture_seq"), "first_click": F.get("first_click"),
           "clicks_capture": F.get("clicks"), "bandpass_answered": F.get("bandpass_answered"), "picks_markers": F.get("picks_markers"),
           "tra": F.get("tra"), "tra_header_points": F.get("tra_header_points"), "pm_gates": j.get("pm"), "m8_gates": m8.get("gates"),
           "v5_failing": m8.get("v5_failing_steps"), "stop_latency_s": (m8.get("stop") or {}).get("latency_s"), "motor_tmx_after": m8.get("motor_after"),
           "tiffs": (m8.get("tiffs_deleted") or {}).get("count"), "source_md5": m8.get("source_md5")}
    row["registered_ok"] = registered_ok(row["tra"], NPICK) if not DRY else True
    rows.append(row); print("ROW " + json.dumps({k: v for k, v in row.items() if k not in ("clicks_capture", "picks_markers", "tra")}, default=str)[:1800], flush=True)
    gates["T1 %s leg rc 0" % tag] = rc == 0
    gates["T3 %s 0 TIFFs" % tag] = DRY or row["tiffs"] == 0
    gates["T5 %s frames/s within 15%% of 90" % tag] = DRY or (row["measured_hz"] is not None and abs(row["measured_hz"] - HZ) <= 0.15 * HZ)
    if not DRY: gates["T10 %s motor TMX 39 after" % tag] = row["motor_tmx_after"] == 39.0
    return row["registered_ok"], row


try:
    for attempt in (1, 2):
        reg_ok, row = run_leg(attempt)
        if reg_ok: break
        if row["rc"] != 0 and row.get("picks_registered_tra") is None:      # a crashed leg is not a lost pick: no rerun (launch 1 lost 7 min this way)
            print("  leg rc %r with no tra read -> script/harness fault, NOT a lost pick; no rerun" % row["rc"], flush=True); break
        print("  REGISTERED picks %r != target %d -> %s" % (row["picks_registered_tra"], NPICK, "rerun once" if attempt == 1 else "logged, no third run"), flush=True)
    gates["T12 registered picks == 8 (<= 1 rerun)"] = bool(rows[-1].get("registered_ok"))
finally:
    restore = camera(90)
print("camera restored: %s" % json.dumps(restore), flush=True)
gates["T7 camera restored to 90 Hz"] = bool(restore) and restore.get("hz") is not None and abs(restore["hz"] - 90) <= 0.5
gates["T8 S1 + bed + kswap + t0 md5 unchanged"] = all(md5(p) == m for p, m in PIN.values())
out = {"schema": "m8-unstamped8/1", "card": "92-1 PD198(c)(2)", "vi": S1, "vi_md5": PIN["S1"][1], "run_s": RUN_S, "hz": HZ, "picks": NPICK, "mode": "ctl",
       "rows": rows, "gates": gates, "camera_restore": restore, "lv_running_at_end": lv_running(), "minutes": round((time.time() - T0) / 60, 1), "legdir": os.path.relpath(LEGDIR, ROOT),
       "compare": {"stamped_8ctl_INDEX51": 144, "stamped_8min_INDEX51": 138, "unstamped_S1_8_INDEX48_50": [16, 12, 16]}}
jp = os.path.join(HERE, "m8_unstamped8_92%s.json" % ("_dry" if DRY else "")); json.dump(out, open(jp, "w"), indent=1, default=str)
gates["T13 table written"] = os.path.isfile(jp)
for k, v in gates.items(): print("GATE %-55s %s" % (k, "PASS" if v else "FAIL"), flush=True)
print("SUMMARY " + json.dumps({r["leg"]: {"lost": r.get("lost_frames"), "reg": r.get("picks_registered_tra"), "cap": r.get("hwndCapture_nonzero"),
                                          "first_click_capture": ((r.get("first_click") or {}).get("gti_before_click") or {}).get("capture_win")} for r in rows}, default=str), flush=True)
bad = [k for k, v in gates.items() if not v]
print(P.result_line(P.make_result(len(gates) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
sys.exit(1 if bad else 0)
