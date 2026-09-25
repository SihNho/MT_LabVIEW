r"""drive_m8_panelmin89b.py - card 89-5 (ABBA repeat of 89-4 Part 1, PD195(d)): FOUR REAL `s1` legs of the unmodified
D1_s1_copy.vi at 90 Hz, RUN_S 120 s, in REVERSED order: 15 picks L-min then L-ctl; then 8 picks L-min then L-ctl.
Lost frames are REPORTED, not gated (the measurement). Result -> tools/bench/m8_panelmin_89b.json and a
`part1b_abba` block appended to tools/bench/t0_insitu_89.json.
FOUND FIRST: tools/bench/drive_m8_panelmin89.py (card 89-4) - this is that sequencer with LEGS carrying the pick count and
the fixed-name backups covering both N; the leg wrapper drive_m8_panelmin89_leg.py is reused UNCHANGED (same scripted
FPState minimize through COM; no GUI act beyond the driver's bead picking).
PREDICTION CONTRACT (per leg): T1 rc 0 (drive_m8 M1..M8 + PM1..PM4)  T2 LabVIEW gone before start  T3 0 TIFFs
 T4 camera 90 Hz before (+-0.5)  T5 frames/s within 15 % of 90  T6 LabVIEW gone after  T10 motor TMX 39 after.
 End: T7 camera 90 Hz; T8 S1 + L2-A1 bed + kswap md5 unchanged; T9 backed-up jsons restored; T11 t0_insitu_89 appended.
    MATERIAL=1 py tools/bgrun.py --max-min 52 --log tools/bench/m8_panelmin_89b.log -- py -u tools/bench/drive_m8_panelmin89b.py [--dry]
"""
import ctypes as C, json, os, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
import protocol as P                                                            # noqa: E402
import imaqdx_limits as L                                                       # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DRY = "--dry" in sys.argv; HZ, RUN_S = 90, 120
PIN = {"S1": (os.path.join(CD, "D1_s1_copy.vi"), "3e3d23cefd3a334001aa9d6156bf1aee"),
       "bedL2A1": (os.path.join(CD, "D1_l2_a1_20260925_235224.vi"), "51d9b8a3af5b4240cdc2ad193d9b4f41"),
       "kswap": (os.path.join(CD, "D1_s1_kswap_20260926_004935.vi"), "e77b8d5805d90f76e426cb06fdc26d1c")}
LEGS = [(15, "min", "--minimize"), (15, "ctl", "--control"), (8, "min", "--minimize"), (8, "ctl", "--control")]   # ABBA: min FIRST this time
HARD_MIN, LEG_MAX_MIN = 48.0, 12.0
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
FIXED = []
for n_ in (15, 8):
    FIXED += ["m8_s1_p%d_r%d%s.json" % (n_, RUN_S, SUF)] + ["m8_v5_s1_p%d_r%d%s%s.json" % (n_, RUN_S, SUF, x) for x in ("", "_clicks")]
FIXED += ["m8_panelmin_89_%s_pm.json" % m for m in ("min", "ctl")]      # the leg wrapper's fixed pm names (89-4 files kept)
BK = {}
for f in FIXED:
    p = os.path.join(HERE, f)
    if os.path.isfile(p):
        b = os.path.join(HERE, "m8_panelmin_89b_bak_" + f); shutil.copyfile(p, b); BK[p] = (b, md5(p))
print("backed up %s" % sorted(os.path.basename(k) for k in BK), flush=True)
rows, gates = [], {}
try:
    for i, (N, tag0, flag) in enumerate(LEGS, 1):
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
        if j: shutil.copyfile(jp, os.path.join(HERE, "m8_panelmin_89b_leg%d%s.json" % (i, SUF)))
        pmp = os.path.join(HERE, "m8_panelmin_89_%s_pm.json" % tag0)
        pmj = json.load(open(pmp)) if os.path.isfile(pmp) and os.path.getmtime(pmp) >= t else {}
        if pmj: shutil.copyfile(pmp, os.path.join(HERE, "m8_panelmin_89b_leg%d_pm%s.json" % (i, SUF)))
        hdr = j.get("tra_header_points") or {}; fd = j.get("frame_counter_delta")
        pf = pmj.get("facts") or {}; c0 = pf.get("counters_at_minimize") or {}; c1 = pf.get("counters_at_restore") or {}
        row = {"leg": tag, "mode": tag0, "vi": PIN["S1"][0], "hz_cell": HZ, "picks": N, "run_s": RUN_S,
               "rc": rc, "secs": round(time.time() - t), "json": ("tools/bench/m8_panelmin_89b_leg%d%s.json" % (i, SUF)) if j else None,
               "camera_before": cam_before, "camera_after": cam_after,
               "reached_experiment_loop": (j.get("gates") or {}).get("M2 reached experiment loop"),
               "frames_delta": fd, "measured_hz": (round(fd / RUN_S, 1) if isinstance(fd, (int, float)) and fd else None),
               "lost_frames": j.get("total_lost_frames"), "pm_gates": pm,
               "lost_at_start": c0.get("lost") if isinstance(c0, dict) else None, "lost_at_stop": c1.get("lost") if isinstance(c1, dict) else None,
               "frame_at_start": c0.get("frame") if isinstance(c0, dict) else None, "frame_at_stop": c1.get("frame") if isinstance(c1, dict) else None,
               "fpstate": {k: pf.get(k) for k in ("fpstate_before", "fpstate_after_min", "rect_after_min", "fpstate_after_restore") if k in pf},
               "tra_rows_header": {k: (v[0] if v else None) for k, v in hdr.items()},
               "tiffs": (j.get("tiffs_deleted") or {}).get("count"), "stop_latency_s": (j.get("stop") or {}).get("latency_s"),
               "labview_exited": (j.get("gates") or {}).get("M6 LabVIEW gone (tasklist)"),
               "picks_done": j.get("picks"), "motor_tmx_after": j.get("motor_after"),
               "gates": j.get("gates"), "v5_failing": j.get("v5_failing_steps")}
        rows.append(row); print("ROW " + json.dumps(row, default=str)[:1500], flush=True)
        gates["T1 %s leg rc 0" % tag] = rc == 0
        gates["T3 %s 0 TIFFs" % tag] = row["tiffs"] == 0
        gates["T5 %s frames/s within 15%% of 90" % tag] = row["measured_hz"] is not None and abs(row["measured_hz"] - HZ) <= 0.15 * HZ
        if not DRY:
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


def _lost(r):
    try: return int(r.get("lost_frames"))
    except (TypeError, ValueError): return None


summary = {}
for N in (15, 8):
    mn = next((r for r in rows if r.get("picks") == N and r.get("mode") == "min"), {})
    ct = next((r for r in rows if r.get("picks") == N and r.get("mode") == "ctl"), {})
    lm, lc = _lost(mn), _lost(ct)
    summary["p%d" % N] = {"min_lost": lm, "ctl_lost": lc, "min_minus_ctl": (lm - lc) if lm is not None and lc is not None else None,
                          "min_frames": mn.get("frames_delta"), "ctl_frames": ct.get("frames_delta"),
                          "min_tra": mn.get("tra_rows_header"), "ctl_tra": ct.get("tra_rows_header"), "order": "min then ctl"}
out = {"schema": "m8-panelmin/1", "card": "89-5 PD195(d) ABBA", "run_s": RUN_S, "hz": HZ, "legs": [l[:2] for l in LEGS], "pins": PIN, "rows": rows,
       "summary": summary, "gates": gates, "camera_restore": restore, "lv_running_at_end": lv_running(), "minutes": round((time.time() - T0) / 60, 1)}
jp = os.path.join(HERE, "m8_panelmin_89b%s.json" % SUF); json.dump(out, open(jp, "w"), indent=1, default=str)
arts = [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}]
if not DRY:
    tp = os.path.join(HERE, "t0_insitu_89.json")
    try:
        t0j = json.load(open(tp))
        t0j["part1b_abba_legs"] = {"source": "tools/bench/m8_panelmin_89b.json (sequencer tools/bench/drive_m8_panelmin89b.py, leg wrapper drive_m8_panelmin89_leg.py unchanged, log tools/bench/m8_panelmin_89b.log)",
                                   "conditions": "90 Hz, RUN_S 120 s, order 15 min, 15 ctl, 8 min, 8 ctl; LabVIEW gone after each leg; motor TMX 39 read back after each leg",
                                   "rows": [{k: r.get(k) for k in ("leg", "mode", "picks", "rc", "lost_frames", "lost_at_start", "lost_at_stop", "frames_delta", "measured_hz", "tra_rows_header", "fpstate", "secs", "motor_tmx_after")} for r in rows],
                                   "summary": summary, "gates_fail": [k for k, v in gates.items() if not v]}
        json.dump(t0j, open(tp, "w"), indent=1, default=str); gates["T11 t0_insitu_89 appended"] = True
        arts.append({"path": os.path.relpath(tp, ROOT), "md5": md5(tp)})
    except Exception as e:                                                     # noqa: BLE001
        print("t0_insitu append failed %r" % e, flush=True); gates["T11 t0_insitu_89 appended"] = False
for k, v in gates.items(): print("GATE %-55s %s" % (k, "PASS" if v else "FAIL"), flush=True)
print("SUMMARY " + json.dumps(summary, default=str), flush=True)
bad = [k for k, v in gates.items() if not v]
print(P.result_line(P.make_result(len(gates) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
sys.exit(1 if bad else 0)
