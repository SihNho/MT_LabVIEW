r"""diag_c96_abba.py - card 96-1 (PD203(f)/PD204) = diag_c94_abba.py with 4 legs A15 B15 B15 A15, 120 s, panel normal, 90 Hz:
A = claudeDev\D1_s1_copy.vi, B = claudeDev\D1_s1_par1359_20260926_133751.vi (#1359 parallel, 95-4 STRUCTURAL). Both UNSTAMPED
(no T0STAMP_DIR, no DLL gates, no site stats). Files run as they are (drive_m8 replay_s1 --src byte copy); nothing saved/edited.
Per leg (diag_c96_leg.py): lost frames, #637 period PROXY (tra frame-step x 11.11 ms, labelled proxy) median/p95/max, and here
a sysload() READ before AND after the leg: claude.exe/node.exe processes not in this script's ancestor chain ("foreign") + 3
Win32_Processor LoadPercentage samples. Output tools/bench/par1359_96_abba.json + one archive/benchmarks/INDEX.md row (real run).
FOUND FIRST: diag_c94_abba.py / diag_c94_leg.py (copied, pick-1 capture release + rerun-once rule kept), m8b_replay_compare.tra
(tra layout), diag_c95_peek.log (saved leg's proxy: step median 1, p95 3). No judgement is applied (PD204(a) is judgement's).
PREDICTION CONTRACT: R1 tra rule on INDEX-51 leg == (True@8, False@7)  R2 lost reader == 144  R3 capture reader == ['723452']
 R5 proxy reader on the saved 94-1 A15 run dir == rows 6854, step median 1.0, p95 3.0
 M1 S1 + par1359 md5 read in-run before leg 1: par1359 == 5bef83f0..., S1 == 3e3d23ce... (recorded in full)
 per leg: T1 rc 0  T2 LabVIEW gone before  T3 0 TIFFs  T4 camera 90 Hz before  T5 fps within 15 %  T6 LabVIEW gone after
 T10 TMX 39  H2 no capture before pick 1  L1 proxy parsed  S1/S2 sysload read before/after   per slot: T12 registered == 15
 (<= 1 rerun)   end: T7 camera 90 Hz  M2 both md5 after last leg == before  T13 par1359_96_abba.json written  T16 INDEX row.
    py tools/bgrun.py --max-min 70 --log tools/bench/diag_c96_abba.log -- py -u tools/bench/diag_c96_abba.py [--dry]
"""
import ctypes as C, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
import protocol as P                                                            # noqa: E402
import imaqdx_limits as L                                                       # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DRY = "--dry" in sys.argv; HZ, RUN_S = 90, 120
S1 = os.path.join(CD, "D1_s1_copy.vi"); PAR = os.path.join(CD, "D1_s1_par1359_20260926_133751.vi")
PIN = {"S1": (S1, "3e3d23cefd3a334001aa9d6156bf1aee"), "par1359": (PAR, "5bef83f0007266b90b7ffd65d2422480")}
KNOWN = os.path.join(HERE, "t0_legs", "step4_20260926_071816", "leg2_ctl_p8_a1", "leg.json")
LEG_MAX_MIN = 12.0
ORDER = [("A", S1, False, 15), ("B", PAR, False, 15), ("B", PAR, False, 15), ("A", S1, False, 15)]
T0 = time.time(); TS = time.strftime("%Y%m%d_%H%M%S")
LEGDIR = os.path.join(HERE, "t0_legs", "c96_par1359_%s%s" % (TS, "_dry" if DRY else "")); os.makedirs(LEGDIR, exist_ok=True)
rows, gates = [], {}
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


def sysload(tag):
    """a READ: claude/node processes outside this script's ancestor chain + 3 CPU LoadPercentage samples (0.7 s apart)."""
    ps = ("$p=@(Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name); $c=@(); foreach($i in 1..3){"
          "$c+=(Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average; Start-Sleep -Milliseconds 700};"
          "@{p=$p;cpu=$c} | ConvertTo-Json -Depth 3 -Compress")
    try:
        j = json.loads(subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=90).stdout)
        par = {x["ProcessId"]: x["ParentProcessId"] for x in j["p"]}; anc, q = set(), os.getpid()
        while q and q not in anc: anc.add(q); q = par.get(q)
        cn = [x for x in j["p"] if (x.get("Name") or "").lower() in ("claude.exe", "node.exe")]
        fo = [[x["ProcessId"], x["Name"], x["ParentProcessId"]] for x in cn if x["ProcessId"] not in anc]
        cpu = [float(v) for v in j["cpu"] if v is not None]
        r = {"tag": tag, "claude_node_total": len(cn), "foreign": len(fo), "foreign_claude": sum(1 for f in fo if f[1].lower() == "claude.exe"),
             "foreign_node": sum(1 for f in fo if f[1].lower() == "node.exe"), "foreign_list": fo[:40], "ancestors": sorted(anc),
             "cpu_pct_samples": cpu, "cpu_pct_mean": round(sum(cpu) / len(cpu), 1) if cpu else None}
    except Exception as e:                                                     # noqa: BLE001
        r = {"tag": tag, "err": repr(e)}
    print("SYSLOAD %s" % json.dumps({k: v for k, v in r.items() if k not in ("foreign_list", "ancestors")}), flush=True)
    return r


kj = json.load(open(KNOWN)); KF = kj.get("facts") or {}
gates["R1 tra rule on INDEX-51 leg == (True@8, False@7)"] = (registered_ok(KF.get("tra"), 8), registered_ok(KF.get("tra"), 7)) == (True, False)
gates["R2 lost reader on INDEX-51 leg == 144"] = lost_of(KF) == 144
gates["R3 capture reader on INDEX-51 leg == ['723452']"] = KF.get("foreign_capture_nonzero") == ["723452"]
_rp = None                                                                      # R5: the leg's reader arithmetic on the saved real tra
try:
    import numpy as np, struct                                                  # noqa: E401
    b = open(os.path.join(HERE, "m8_out", "replay_s1_20260926_115922", "tra001-000"), "rb").read(); k = b.find(b"not in z!)") + 10
    r_, c_ = struct.unpack("<ii", b[k:k + 8]); st = np.diff(np.frombuffer(b[k + 8:k + 8 + 8 * r_ * c_], dtype="<f8").reshape(r_, c_)[:, 0])
    _rp = (r_, float(np.median(st)), float(np.percentile(st, 95)))
except Exception as e:                                                         # noqa: BLE001
    _rp = repr(e)
gates["R5 proxy reader on saved 94-1 A15 == (6854, 1.0, 3.0)"] = _rp == (6854, 1.0, 3.0)
print("PRELAUNCH readers: %s  R5=%r" % (gates, _rp), flush=True)
if not all(gates.values()):
    print(P.result_line(P.make_result(sum(gates.values()), len(gates) - sum(gates.values()), next(k for k, v in gates.items() if not v))), flush=True); sys.exit(1)
MD5_BEFORE = {k: md5(p) for k, (p, _) in PIN.items()}; print("MD5 BEFORE %s" % MD5_BEFORE, flush=True)
gates["M1 par1359 == 5bef83f0 and S1 == 3e3d23ce before leg 1 (in-run)"] = all(MD5_BEFORE[k] == m for k, (_, m) in PIN.items())


def run_leg(slot, arm, src, attempt, NPICK):
    tag = "leg%d %s@%d%s" % (slot, arm, NPICK, "" if attempt == 1 else " rerun")
    out = os.path.join(LEGDIR, "leg%d_%s_p%d_a%d" % (slot, arm, NPICK, attempt)); os.makedirs(out, exist_ok=True)
    gates["T2 %s LabVIEW gone before" % tag] = DRY or not lv_running()
    s_before = sysload("before " + tag)
    cb = camera(HZ); print("=== LEG %s start %.1f min; camera %s" % (tag, (time.time() - T0) / 60, json.dumps(cb)), flush=True)
    gates["T4 %s camera 90 Hz before" % tag] = bool(cb) and cb.get("hz") is not None and abs(cb["hz"] - HZ) <= 0.5
    cmd = [sys.executable, "-u", os.path.join(HERE, "diag_c96_leg.py"), "--src", src, "--picks", str(NPICK), "--run-s", str(RUN_S), "--out", out] + (["--dry"] if DRY else [])
    t = time.time()
    try:                                                                        # PD199(h): the dry run EXECUTES the leg script
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
    s_after = sysload("after " + tag)
    lj = os.path.join(out, "leg.json"); j = json.load(open(lj)) if os.path.isfile(lj) else {}
    F = j.get("facts") or {}; pm = j.get("pm") or {}; fd = F.get("frames_delta"); px = F.get("period_proxy_637") or {}
    row = {"leg": tag, "arm": arm, "picks": NPICK, "slot": slot, "attempt": attempt, "rc": rc, "secs": round(time.time() - t), "dir": os.path.relpath(out, ROOT),
           "lost_frames": lost_of(F), "frames_delta": fd, "measured_hz": round(fd / RUN_S, 1) if isinstance(fd, (int, float)) and fd else None,
           "period637_proxy": {k: px.get(k) for k in ("label", "median_ms", "p95_ms", "max_ms", "step_median", "step_p95", "step_max", "steps", "steps_gt1", "rows", "cols", "parsed", "err")},
           "sysload_before": s_before, "sysload_after": s_after,
           "picks_registered_tra": F.get("picks_registered_tra"), "capture_class_before_pick1": F.get("capture_class_before_pick1"),
           "releases": F.get("releases"), "release": F.get("release"), "pre_pick_capture": [(r.get("tag"), r.get("hwndCapture"), (r.get("capture_win") or {}).get("class")) for r in F.get("pre_pick") or []],
           "pm": pm, "v5_failing": F.get("v5_failing"), "stop_latency_s": (F.get("stop") or {}).get("latency_s"), "motor_tmx_after": F.get("motor_tmx_after"),
           "tiffs": F.get("tiffs"), "source_md5": F.get("source_md5"), "run_dir": F.get("run_dir")}
    row["registered_ok"] = True if DRY else registered_ok(F.get("tra"), NPICK)
    rows.append(row); print("ROW " + json.dumps({k: v for k, v in row.items() if k not in ("release", "pre_pick_capture", "sysload_before", "sysload_after")}, default=str)[:1500], flush=True)
    gates["T1 %s rc 0" % tag] = rc == 0
    gates["T3 %s 0 TIFFs" % tag] = DRY or row["tiffs"] == 0
    gates["T5 %s fps within 15%%" % tag] = DRY or (row["measured_hz"] is not None and abs(row["measured_hz"] - HZ) <= 0.15 * HZ)
    gates["T10 %s TMX 39" % tag] = DRY or row["motor_tmx_after"] == 39.0
    gates["H2 %s no capture before pick 1" % tag] = any(k.startswith("H2") and v for k, v in pm.items())
    gates["L1 %s period proxy parsed" % tag] = bool(px.get("parsed"))
    gates["S1 %s sysload before+after read" % tag] = "err" not in s_before and "err" not in s_after
    return row


try:
    for slot, (arm, src, _st, npk) in enumerate(ORDER, 1):
        for attempt in (1, 2):
            row = run_leg(slot, arm, src, attempt, npk)
            if row["registered_ok"]: break
            if row["rc"] != 0 and row.get("picks_registered_tra") is None:
                print("  crashed leg (no tra) -> harness fault, no rerun", flush=True); break
            print("  REGISTERED %r != %d -> %s" % (row["picks_registered_tra"], npk, "rerun once" if attempt == 1 else "logged, no third run"), flush=True)
        gates["T12 slot%d %s@%d registered == target (<= 1 rerun)" % (slot, arm, npk)] = bool(row.get("registered_ok"))
finally:
    restore = camera(90)
print("camera restored: %s" % json.dumps(restore), flush=True)
gates["T7 camera restored 90 Hz"] = bool(restore) and restore.get("hz") is not None and abs(restore["hz"] - 90) <= 0.5
MD5_AFTER = {k: md5(p) for k, (p, _) in PIN.items()}; print("MD5 AFTER %s" % MD5_AFTER, flush=True)
gates["M2 S1 + par1359 md5 after last leg == before"] = MD5_AFTER == MD5_BEFORE
counted = {}
for r in rows:
    if r["registered_ok"]: counted.setdefault("%s%d" % (r["arm"], r["picks"]), []).append({"lost": r["lost_frames"], "proxy_med_ms": r["period637_proxy"].get("median_ms"),
                                                                                              "proxy_p95_ms": r["period637_proxy"].get("p95_ms"), "proxy_max_ms": r["period637_proxy"].get("max_ms")})
out = {"schema": "par1359-abba/1", "card": "96-1 PD203(f)/PD204", "A": S1, "B": PAR, "md5_before": MD5_BEFORE, "md5_after": MD5_AFTER, "run_s": RUN_S, "hz": HZ,
       "picks": 15, "panel": "normal", "order": "A15 B15 B15 A15", "counted_by_arm": counted, "rows": rows, "gates": gates, "camera_restore": restore,
       "lv_running_at_end": lv_running(), "minutes": round((time.time() - T0) / 60, 1), "legdir": os.path.relpath(LEGDIR, ROOT),
       "proxy_note": "#637 period PROXY = tra col-0 frame-number step x 11.11 ms; not a timer", "judgement_not_applied": "PD204(a)"}
jp = os.path.join(HERE, "par1359_96_abba%s.json" % ("_dry" if DRY else "")); json.dump(out, open(jp, "w"), indent=1, default=str)
gates["T13 par1359_96_abba.json written"] = os.path.isfile(jp)
if not DRY:
    ix = os.path.join(ROOT, "archive", "benchmarks", "INDEX.md"); last = [ln for ln in open(ix, encoding="utf-8").read().splitlines() if ln.startswith("| ")][-1]
    n = int(last.split("|")[1]) + 1; lg = lambda r: "%s %s/%s/%s" % (r["lost_frames"], *(r["period637_proxy"].get(k) for k in ("median_ms", "p95_ms", "max_ms")))  # noqa: E731
    cell = "; ".join("%s: lost %s, #637 proxy med/p95/max ms %s, foreign claude+node %s->%s, CPU %% %s->%s" % (r["leg"], r["lost_frames"], lg(r).split(" ", 1)[1],
                     r["sysload_before"].get("foreign"), r["sysload_after"].get("foreign"), r["sysload_before"].get("cpu_pct_mean"), r["sysload_after"].get("cpu_pct_mean")) for r in rows)
    ok_all = all(gates.values())
    line = ("| %d | %s | **Card 96-1 (PD203(f)/PD204): does ForLoop #1359 in parallel (95-4, scheduling only) cut frame loss at 15 beads? ABBA A15 B15 B15 A15, panel normal, 120 s, 90 Hz: "
            "A = `claudeDev\\D1_s1_copy.vi` (md5 `%s`), B = `claudeDev\\D1_s1_par1359_20260926_133751.vi` (md5 `%s`), both unstamped.** `tools/bench/diag_c96_abba.py` -> `diag_c96_leg.py` "
            "(row 55's scripts; #637 period PROXY from the tra frame-step x 11.11 ms; claude/node + CPU read before/after each leg) | env as row 45; fixed picks 15, `RUN_S` 120 s, panel normal, 90 Hz; "
            "varied VI A/B | **%s**. md5 before == after: %s; TMX 39 each leg; LabVIEW gone at end: %s; gates %d/%d. Level: OPERATION + frame loss, %d real runs | `tools/bench/par1359_96_abba.json`, "
            "legs `%s/`, log `tools/bench/diag_c96_abba.log` |" % (n, time.strftime("%Y-%m-%d"), MD5_BEFORE["S1"][:8] + "…", MD5_BEFORE["par1359"][:8] + "…", cell, MD5_AFTER == MD5_BEFORE,
                                                                   not lv_running(), sum(gates.values()), len(gates), len(rows), os.path.relpath(LEGDIR, ROOT).replace("\\", "/")))
    open(ix, "a", encoding="utf-8").write(("" if open(ix, encoding="utf-8").read().endswith("\n") else "\n") + line + "\n")
    gates["T16 INDEX row %d appended" % n] = line in open(ix, encoding="utf-8").read()
for k, v in gates.items(): print("GATE %-58s %s" % (k, "PASS" if v else "FAIL"), flush=True)
print("SUMMARY " + json.dumps({r["leg"]: {"lost": r["lost_frames"], "reg": r["picks_registered_tra"], "proxy": [r["period637_proxy"].get(k) for k in ("median_ms", "p95_ms", "max_ms")],
                               "foreign": [r["sysload_before"].get("foreign"), r["sysload_after"].get("foreign")], "cpu": [r["sysload_before"].get("cpu_pct_mean"), r["sysload_after"].get("cpu_pct_mean")],
                               "tmx": r["motor_tmx_after"], "cap1": r["capture_class_before_pick1"], "rel": r["releases"]} for r in rows}, default=str), flush=True)
print("COUNTED BY ARM %s" % json.dumps(counted), flush=True)
bad = [k for k, v in gates.items() if not v]
print(P.result_line(P.make_result(len(gates) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
sys.exit(1 if bad else 0)
