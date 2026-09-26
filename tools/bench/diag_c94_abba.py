r"""diag_c94_abba.py - card 94-1 (PD201 amended) = diag_c93b_abba.py with 6 legs A11 B11 B15 A15 B15 B11 (picks per leg),
legs by diag_c94_leg.py, raw table tools/bench/t0_step4v2_94_raw.json, then diag_c94_sites.py writes t0_step4v2_94.json
(per B leg per site, slope us/bead 15 vs 11, repeat spread, lost ratio). Gates as below with 8 -> the leg's pick count.
PREDICTION CONTRACT additions: T14 overflow 0 on every site of every B leg (reported)  T15 sites summary written.
    py tools/bgrun.py --max-min 100 --log tools/bench/diag_c94_abba.log -- py -u tools/bench/diag_c94_abba.py [--dry]
--- diag_c93b_abba.py docstring ---
diag_c93b_abba.py - card 93-2 (PD200(c)(3)) = diag_c92c_abba.py with: legs by diag_c93b_leg.py; --dry EXECUTES the
leg script with --dry (PD199(h)) instead of writing a fake leg.json; B = t0at on the v2 DLL (gate T9: claudeDev
t0stamp.dll md5 == v2 before and after); per B leg the top-15 tracking periods (site 00) with iteration index and the
stamp_meta overflow lines; output tools/bench/m8_flushfree8_93.json. Clearance (PD199(c)) is NOT computed.
    py tools/bgrun.py --material --max-min 75 --log tools/bench/diag_c93b_abba.log -- py -u tools/bench/diag_c93b_abba.py [--dry]
--- original docstring ---
diag_c92c_abba.py - card 92-3 (PD199(b)+(c)): ABBA instrument-clearance legs at 8 picks, panel normal, 120 s, 90 Hz.
A = unstamped claudeDev\D1_s1_copy.vi, B = the any-thread copy D1_s1_t0at_20260926_090833.vi (fresh T0STAMP_DIR per leg).
Each leg by diag_c92c_leg.py (PD199(b) capture read before every pick + release before pick 1). A leg whose registered
picks (exact tra rule) != 8 is logged and rerun ONCE, never half-counted; a crashed leg (no tra) is not rerun.
FOUND FIRST: diag_c92_m2.py (camera(), registered_ok, lost_of, run_leg, pre-launch readers - copied, extended to 4 legs;
importing it would run it), diag_c91_step4_stats.table (the t0_step4_91.json per-site method - imported). Nothing edited.
PREDICTION CONTRACT: R1 tra rule on INDEX-51 leg == (True@8, False@7)  R2 lost reader == 144  R3 capture reader == ['723452']
 R4 stats reader on 91's leg1_ctl_p15_a2 == period median 13804.85 us, site 2 delta median 8423.0 us (t0_step4_91.json:1142,1157)
 per leg: T1 rc 0  T2 LabVIEW gone before  T3 0 TIFFs  T4 camera 90 Hz before  T5 fps within 15 %  T6 LabVIEW gone after
 T10 TMX 39  H2 no capture before pick 1   per slot: T12 registered == 8 (<= 1 rerun)   end: T7 camera 90 Hz  T8 S1/t0/t0at/
 kswap/bed md5 unchanged  T13 tools/bench/m8_anythread8_92.json written.  The clearance verdict (PD199(c)) is NOT computed.
    py tools/bgrun.py --max-min 75 --log tools/bench/diag_c92c_abba.log -- py -u tools/bench/diag_c92c_abba.py [--dry]
"""
import ctypes as C, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
import protocol as P                                                            # noqa: E402
import imaqdx_limits as L                                                       # noqa: E402
import diag_c91_step4_stats as ST                                               # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DRY = "--dry" in sys.argv; HZ, RUN_S, NPICK = 90, 120, 8
S1 = os.path.join(CD, "D1_s1_copy.vi"); T0AT = os.path.join(CD, "D1_s1_t0at_20260926_090833.vi")
PIN = {"S1": (S1, "3e3d23cefd3a334001aa9d6156bf1aee"), "t0at": (T0AT, "30a15c6772d5ef3336ed274abc4c2f40"),
       "bedL2A1": (os.path.join(CD, "D1_l2_a1_20260925_235224.vi"), "51d9b8a3af5b4240cdc2ad193d9b4f41"),
       "kswap": (os.path.join(CD, "D1_s1_kswap_20260926_004935.vi"), "e77b8d5805d90f76e426cb06fdc26d1c"),
       "t0": (os.path.join(CD, "D1_s1_t0_20260926_055551.vi"), "25ea4f7d10d91c41c4b5de64f850c945")}
KNOWN = os.path.join(HERE, "t0_legs", "step4_20260926_071816", "leg2_ctl_p8_a1", "leg.json")
KNOWN_ST = os.path.join(HERE, "t0_legs", "step4_20260926_062630", "leg1_ctl_p15_a2")
LEG_MAX_MIN = 12.0
ORDER = [("A", S1, False, 11), ("B", T0AT, True, 11), ("B", T0AT, True, 15), ("A", S1, False, 15), ("B", T0AT, True, 15), ("B", T0AT, True, 11)]
T0 = time.time(); TS = time.strftime("%Y%m%d_%H%M%S")
LEGDIR = os.path.join(HERE, "t0_legs", "c94_step4v2_%s%s" % (TS, "_dry" if DRY else "")); os.makedirs(LEGDIR, exist_ok=True)
V2DLL, V2MD5 = os.path.join(CD, "t0stamp.dll"), "b35b398d59b35743e2669d043f701fe6"   # selftest_v2 r2 I4 (diag_c93b_t0v2_selftest_r2.log:27)
rows, gates, stats = [], {}, {}
lv_running = lambda: "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()   # noqa: E731


def md5(p):
    import hashlib; return hashlib.md5(open(p, "rb").read()).hexdigest()


def camera(hz=None):
    """diag_c92_m2.camera, verbatim."""
    if DRY: return {"camera": "DRY", "hz": 90.0}
    n = C.c_uint32(0); L.dx.IMAQdxEnumerateCameras(None, C.byref(n), C.c_uint32(1))
    if not n.value: return None
    arr = (L.CameraInformation * n.value)(); L.dx.IMAQdxEnumerateCameras(arr, C.byref(n), C.c_uint32(1))
    sess = C.c_uint32(0); name = arr[0].InterfaceName.decode()
    if L.dx.IMAQdxOpenCamera(name.encode(), C.c_uint32(0), C.byref(sess)): return {"error": "open failed"}
    try:
        rc = None
        if hz is not None:
            rc = L.dx.IMAQdxSetAttribute(sess, (L.ACQ + "AcquisitionFrameRate").encode(), C.c_uint32(L.F64), C.c_double(float(hz))); time.sleep(0.2)
        return {"camera": name, "set_rc": rc, "hz": L.get(sess, L.ACQ + "AcquisitionFrameRate", L.F64)}
    finally:
        L.dx.IMAQdxCloseCamera(sess)


def registered_ok(tra, N):
    try: return any(isinstance(t, dict) and t.get("rows_hdr") and (t["data_bytes"] - 8) == t["rows_hdr"] * (24 + 24 * N) for t in (tra or {}).values())
    except (TypeError, ValueError, AttributeError): return False


def lost_of(F):
    try: return int(F.get("lost"))
    except (TypeError, ValueError): return None


kj = json.load(open(KNOWN)); KF = kj.get("facts") or {}
gates["R1 tra rule on INDEX-51 leg == (True@8, False@7)"] = (registered_ok(KF.get("tra"), 8), registered_ok(KF.get("tra"), 7)) == (True, False)
gates["R2 lost reader on INDEX-51 leg == 144"] = lost_of(KF) == 144
gates["R3 capture reader on INDEX-51 leg == ['723452']"] = KF.get("foreign_capture_nonzero") == ["723452"]
kt = ST.table(KNOWN_ST)["loops"]["637_tracking"]
gates["R4 stats reader == 13804.85 / 8423.0"] = abs(kt["period_us"]["median"] - 13804.85) < 0.01 and kt["sites"][2]["delta_us"]["median"] == 8423.0
print("PRELAUNCH readers: %s" % gates, flush=True)
if not all(gates.values()):
    print(P.result_line(P.make_result(sum(gates.values()), len(gates) - sum(gates.values()), next(k for k, v in gates.items() if not v))), flush=True); sys.exit(1)


gates["T9 claudeDev t0stamp.dll == v2 before legs"] = md5(V2DLL) == V2MD5


def outliers(d, n=15):
    S = ST.load(d); f, I = S.get(0, (None, []))
    if len(I) < 2: return []
    per = [(I[k + 1] - I[k]) * 1e3 / f for k in range(len(I) - 1)]
    return [[k, round(per[k], 3)] for k in sorted(range(len(per)), key=lambda k: -per[k])[:n]]


def run_leg(slot, arm, src, stamps, attempt, NPICK):
    tag = "leg%d %s@%d%s" % (slot, arm, NPICK, "" if attempt == 1 else " rerun")
    out = os.path.join(LEGDIR, "leg%d_%s_p%d_a%d" % (slot, arm, NPICK, attempt)); os.makedirs(out, exist_ok=True)
    gates["T2 %s LabVIEW gone before" % tag] = DRY or not lv_running()
    cb = camera(HZ); print("=== LEG %s start %.1f min; camera %s" % (tag, (time.time() - T0) / 60, json.dumps(cb)), flush=True)
    gates["T4 %s camera 90 Hz before" % tag] = bool(cb) and cb.get("hz") is not None and abs(cb["hz"] - HZ) <= 0.5
    cmd = [sys.executable, "-u", os.path.join(HERE, "diag_c94_leg.py"), "--src", src, "--picks", str(NPICK), "--run-s", str(RUN_S), "--out", out] + (["--stamps"] if stamps else []) + (["--dry"] if DRY else [])
    t = time.time()
    if True:                                                                    # PD199(h): the dry run EXECUTES the leg script
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=LEG_MAX_MIN * 60 + 180); rc, o, err = r.returncode, r.stdout or "", r.stderr or ""
        except subprocess.TimeoutExpired as e:
            rc, o, err = "TIMEOUT", (e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")), ""
    for ln in o.splitlines():
        if ln.startswith(("GATE ", "RESULT ", "[c92c", "REGISTERED")) or "FAILING" in ln: print("  " + ln[:400], flush=True)
    if err: print("  STDERR tail: " + err[-800:], flush=True)
    t2 = time.time()
    while not DRY and lv_running() and time.time() - t2 < 90: time.sleep(5)
    if not DRY and lv_running(): subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True); time.sleep(5); print("  taskkill LabVIEW", flush=True)
    gates["T6 %s LabVIEW gone after" % tag] = DRY or not lv_running()
    lj = os.path.join(out, "leg.json"); j = json.load(open(lj)) if os.path.isfile(lj) else {}
    F = j.get("facts") or {}; pm = j.get("pm") or {}; fd = F.get("frames_delta")
    row = {"leg": tag, "arm": arm, "picks": NPICK, "slot": slot, "attempt": attempt, "rc": rc, "secs": round(time.time() - t), "dir": os.path.relpath(out, ROOT),
           "lost_frames": lost_of(F), "frames_delta": fd, "measured_hz": round(fd / RUN_S, 1) if isinstance(fd, (int, float)) and fd else None,
           "picks_registered_tra": F.get("picks_registered_tra"), "capture_class_before_pick1": F.get("capture_class_before_pick1"),
           "releases": F.get("releases"), "release": F.get("release"), "pre_pick_capture": [(r.get("tag"), r.get("hwndCapture"), (r.get("capture_win") or {}).get("class")) for r in F.get("pre_pick") or []],
           "clicks_capture": F.get("clicks"), "stamp_counts": F.get("stamp_counts"), "pm": pm, "v5_failing": F.get("v5_failing"),
           "stop_latency_s": (F.get("stop") or {}).get("latency_s"), "motor_tmx_after": F.get("motor_tmx_after"), "tiffs": F.get("tiffs"), "source_md5": F.get("source_md5"),
           "stamp_meta": F.get("stamp_meta"), "period_top15_iter_ms": outliers(out) if stamps else None}
    row["registered_ok"] = True if DRY else registered_ok(F.get("tra"), NPICK)
    if stamps and os.path.isdir(out):
        try: stats[tag] = ST.table(out)
        except Exception as e: stats[tag] = {"err": repr(e)}                  # noqa: BLE001
    rows.append(row); print("ROW " + json.dumps({k: v for k, v in row.items() if k not in ("release", "clicks_capture", "pre_pick_capture")}, default=str)[:1500], flush=True)
    print("  PRE-PICK CAPTURE %s" % row["pre_pick_capture"], flush=True)
    gates["T1 %s rc 0" % tag] = rc == 0
    gates["T3 %s 0 TIFFs" % tag] = DRY or row["tiffs"] == 0
    gates["T5 %s fps within 15%%" % tag] = DRY or (row["measured_hz"] is not None and abs(row["measured_hz"] - HZ) <= 0.15 * HZ)
    gates["T10 %s TMX 39" % tag] = DRY or row["motor_tmx_after"] == 39.0
    gates["H2 %s no capture before pick 1" % tag] = any(k.startswith("H2") and v for k, v in pm.items())
    return row


try:
    for slot, (arm, src, stamps, npk) in enumerate(ORDER, 1):
        for attempt in (1, 2):
            row = run_leg(slot, arm, src, stamps, attempt, npk)
            if row["registered_ok"]: break
            if row["rc"] != 0 and row.get("picks_registered_tra") is None:
                print("  crashed leg (no tra) -> harness fault, no rerun", flush=True); break
            print("  REGISTERED %r != %d -> %s" % (row["picks_registered_tra"], npk, "rerun once" if attempt == 1 else "logged, no third run"), flush=True)
        gates["T12 slot%d %s@%d registered == target (<= 1 rerun)" % (slot, arm, npk)] = bool(row.get("registered_ok"))
finally:
    restore = camera(90)
print("camera restored: %s" % json.dumps(restore), flush=True)
gates["T7 camera restored 90 Hz"] = bool(restore) and restore.get("hz") is not None and abs(restore["hz"] - 90) <= 0.5
gates["T8 S1/t0/t0at/kswap/bed md5 unchanged"] = all(md5(p) == m for p, m in PIN.values())
gates["T9b claudeDev t0stamp.dll == v2 after legs"] = md5(V2DLL) == V2MD5
counted = {}
for r in rows:
    if r["registered_ok"]: counted.setdefault("%s%d" % (r["arm"], r["picks"]), []).append(r["lost_frames"])
site_tab = {}
for tag, T in stats.items():
    lp = (T.get("loops") or {}) if isinstance(T, dict) else {}
    site_tab[tag] = {ln: {"iterations": L_.get("iterations"), "period_median_us": (L_.get("period_us") or {}).get("median"), "period_p95_us": (L_.get("period_us") or {}).get("p95"),
                          "sites": {s: {"stamps": v.get("stamps"), "median_us": (v.get("delta_us") or {}).get("median"), "p95_us": (v.get("delta_us") or {}).get("p95")} for s, v in (L_.get("sites") or {}).items()}}
                     for ln, L_ in lp.items()}
out = {"schema": "t0-step4v2-raw/1", "card": "94-1 PD201", "A": S1, "B": T0AT, "B_dll": [V2DLL, V2MD5], "run_s": RUN_S, "hz": HZ, "picks": [o[3] for o in ORDER], "mode": "ctl", "order": "A11 B11 B15 A15 B15 B11",
       "lost_counted_by_arm": counted, "rows": rows, "site_table": site_tab, "stats_full": stats, "gates": gates, "camera_restore": restore,
       "lv_running_at_end": lv_running(), "minutes": round((time.time() - T0) / 60, 1), "legdir": os.path.relpath(LEGDIR, ROOT),
       "criterion_PD199c_not_applied_here": "B cleared iff lost(B) <= 2 x mean lost(A) + 20 (judgement applies it)"}
jp = os.path.join(HERE, "t0_step4v2_94_raw%s.json" % ("_dry" if DRY else "")); json.dump(out, open(jp, "w"), indent=1, default=str)
gates["T13 table written"] = os.path.isfile(jp)
import diag_c94_sites                                                           # noqa: E402
sp, SUM = diag_c94_sites.summarize(jp)
gates["T14 overflow 0 on every site of every B leg"] = SUM["overflow_total"] == 0
gates["T15 sites summary written"] = os.path.isfile(sp)
for k, v in gates.items(): print("GATE %-58s %s" % (k, "PASS" if v else "FAIL"), flush=True)
print("SUMMARY " + json.dumps({r["leg"]: {"lost": r["lost_frames"], "reg": r["picks_registered_tra"], "cap1": r["capture_class_before_pick1"], "rel": r["releases"]} for r in rows}, default=str), flush=True)
print("LOST BY ARM %s" % json.dumps(counted), flush=True)
for tag, v in site_tab.items(): print("SITES %s %s" % (tag, json.dumps(v, default=str)[:1500]), flush=True)
bad = [k for k, v in gates.items() if not v]
print(P.result_line(P.make_result(len(gates) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(p, ROOT), "md5": md5(p)} for p in (jp, sp)])), flush=True)
sys.exit(1 if bad else 0)
