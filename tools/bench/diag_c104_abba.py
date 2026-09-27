r"""diag_c104_abba.py - card 104-5 (PD210(c)/PD217(f)) = diag_c96_abba.py with 4 legs A15 B15 B15 A15, 120 s, panel normal, 90 Hz:
A = claudeDev\D1_s1_copy.vi, B = claudeDev\D1_s1_disp_20260927_041648.vi (Force plot #8323 in its own display loop, 104-4
STRUCTURAL, never run). Both unstamped; files run as they are (drive_m8 replay_s1 --src byte copy); nothing saved/edited.
Per leg (diag_c104_leg.py): lost frames, tracking iterations (tra rows), #637 period PROXY, foreign claude/node + CPU % before
AND after, and #8323's value summary read by COM just before the stop (after L11's lost read) and after it, + 'Display period
(ms)'. Output tools/bench/disp_104_abba.json + one archive/benchmarks/INDEX.md row (real run). No judgement (PD217(f) is judgement's).
FOUND FIRST: diag_c96_abba.py / diag_c96_leg.py (copied; pick-1 capture release + rerun-once rule kept).
PREDICTION CONTRACT: R1 tra rule on INDEX-51 leg == (True@8, False@7)  R2 lost reader == 144  R3 capture reader == ['723452']
 R5 proxy reader on the saved 94-1 A15 run dir == (6854, 1.0, 3.0)
 M1 disp == 245a1020... and S1 == 3e3d23ce... read in-run before leg 1
 per leg: T1 rc 0  T2 LabVIEW gone before  T3 0 TIFFs  T4 camera 90 Hz before  T5 fps within 15 %  T6 LabVIEW gone after
 T10 TMX 39  H2 no capture before pick 1  L1 proxy parsed  S1 sysload read before/after  D1 plot read recorded
 per B leg: F1 #8323 non-empty before stop (elements >= 1, no ERR)  F2 Display period is a number
 per slot: T12 registered == 15 (<= 1 rerun)   end: T7 camera 90 Hz  M2 md5 after == before  T13 json written  T16 INDEX row.
    MATERIAL=1 py tools/bgrun.py --max-min 60 --log tools/bench/diag_c104_abba.log -- py -u tools/bench/diag_c104_abba.py [--dry]
"""
import ctypes as C, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
import protocol as P                                                            # noqa: E402
import imaqdx_limits as L                                                       # noqa: E402
import drive_legguard as LG                                                     # noqa: E402  card 106-2
# card 106-2 (PD218(d)/PD217(g)): every leg starts with LG.visa_precheck() BEFORE LabVIEW is started (nonzero -> leg REFUSED,
# nothing launched); the slot loop is LG.leg_loop (a refused leg or an A leg failing before pick 1 ends it); the dialog watch +
# direct kill live in drive_original_copy_v5.leg. Optional: --json <path> (output name; default unchanged), --max-legs N.
# The INDEX row is appended only when at least one leg produced numbers (104-5's all-null row had to be marked by hand).
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DRY = "--dry" in sys.argv; HZ, RUN_S = 90, 120
_A = sys.argv[1:]; JSON_OUT = _A[_A.index("--json") + 1] if "--json" in _A else None
MAX_LEGS = int(_A[_A.index("--max-legs") + 1]) if "--max-legs" in _A else None
S1 = os.path.join(CD, "D1_s1_copy.vi"); DSP = os.path.join(CD, "D1_s1_disp_20260927_041648.vi")
PIN = {"S1": (S1, "3e3d23cefd3a334001aa9d6156bf1aee"), "disp": (DSP, "245a10206b565cba0ba186bd891f5cb8")}
KNOWN = os.path.join(HERE, "t0_legs", "step4_20260926_071816", "leg2_ctl_p8_a1", "leg.json")
LEG_MAX_MIN = 12.0
ORDER = [("A", S1, False, 15), ("B", DSP, False, 15), ("B", DSP, False, 15), ("A", S1, False, 15)]
T0 = time.time(); TS = time.strftime("%Y%m%d_%H%M%S")
LEGDIR = os.path.join(HERE, "t0_legs", "c104_disp_%s%s" % (TS, "_dry" if DRY else "")); os.makedirs(LEGDIR, exist_ok=True)
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
gates["M1 disp == 245a1020 and S1 == 3e3d23ce before leg 1 (in-run)"] = all(MD5_BEFORE[k] == m for k, (_, m) in PIN.items())


def plot_of(F, tag):
    r = next((x for x in (F.get("plot_reads") or []) if x.get("tag") == tag), None) or {}
    return {k: r.get(k) for k in ("type", "err", "dims_first", "elements", "per_plot_leaves", "display_period", "secs", "synthetic")}


def run_leg(slot, arm, src, attempt, NPICK):
    tag = "leg%d %s@%d%s" % (slot, arm, NPICK, "" if attempt == 1 else " rerun")
    out = os.path.join(LEGDIR, "leg%d_%s_p%d_a%d" % (slot, arm, NPICK, attempt)); os.makedirs(out, exist_ok=True)
    gates["T2 %s LabVIEW gone before" % tag] = DRY or not lv_running()
    pc = LG.visa_precheck(dry=DRY, log=lambda s: print("  " + s, flush=True))   # card 106-2 L2: before LabVIEW is started
    gates["V1 %s VISA precheck Rotor+ASRL5 status 0" % tag] = pc["ok"]
    if not pc["ok"]:
        lv = lv_running(); print("=== LEG %s REFUSED by the VISA precheck: %s; LabVIEW running=%s; leg script NOT launched" % (
            tag, [(t["name"], t["hex"]) for t in pc.get("trials") or []] or pc.get("why"), lv), flush=True)
        row = {"leg": tag, "arm": arm, "picks": NPICK, "slot": slot, "attempt": attempt, "rc": "REFUSED", "refused": True, "precheck": pc,
               "labview_running_at_refusal": lv, "registered_ok": False, "picks_clicked": 0, "picks_registered_tra": None, "lost_frames": None,
               "tracking_iterations_tra_rows": None, "plot_before_stop": {}, "plot_after_stop": {}, "sysload_before": {}, "sysload_after": {},
               "motor_tmx_after": None, "capture_class_before_pick1": None, "releases": None, "dir": os.path.relpath(out, ROOT)}
        rows.append(row); print("ROW " + json.dumps({k: v for k, v in row.items() if k != "precheck"}, default=str), flush=True)
        return row
    s_before = sysload("before " + tag)
    cb = camera(HZ); print("=== LEG %s start %.1f min; camera %s" % (tag, (time.time() - T0) / 60, json.dumps(cb)), flush=True)
    gates["T4 %s camera 90 Hz before" % tag] = bool(cb) and cb.get("hz") is not None and abs(cb["hz"] - HZ) <= 0.5
    cmd = [sys.executable, "-u", os.path.join(HERE, "diag_c104_leg.py"), "--src", src, "--picks", str(NPICK), "--run-s", str(RUN_S), "--out", out] + (["--dry"] if DRY else [])
    t = time.time()
    try:                                                                        # PD199(h): the dry run EXECUTES the leg script
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=LEG_MAX_MIN * 60 + 180); rc, o, err = r.returncode, r.stdout or "", r.stderr or ""   # 106-2: cp949 decode crash seen
    except subprocess.TimeoutExpired as e:
        rc, o, err = "TIMEOUT", (e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")), ""
    for ln in o.splitlines():
        if ln.startswith(("GATE ", "RESULT ", "[c104 leg] PLOT", "REGISTERED")) or "FAILING" in ln: print("  " + ln[:600], flush=True)
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
           "tracking_iterations_tra_rows": px.get("rows"),
           "period637_proxy": {k: px.get(k) for k in ("label", "median_ms", "p95_ms", "max_ms", "step_median", "step_p95", "step_max", "steps", "steps_gt1", "rows", "cols", "parsed", "err")},
           "plot_before_stop": plot_of(F, "before-stop"), "plot_after_stop": plot_of(F, "after-stop"),
           "sysload_before": s_before, "sysload_after": s_after,
           "picks_registered_tra": F.get("picks_registered_tra"), "capture_class_before_pick1": F.get("capture_class_before_pick1"),
           "releases": F.get("releases"), "release": F.get("release"), "pre_pick_capture": [(r.get("tag"), r.get("hwndCapture"), (r.get("capture_win") or {}).get("class")) for r in F.get("pre_pick") or []],
           "pm": pm, "v5_failing": F.get("v5_failing"), "stop_latency_s": (F.get("stop") or {}).get("latency_s"), "motor_tmx_after": F.get("motor_tmx_after"),
           "tiffs": F.get("tiffs"), "source_md5": F.get("source_md5"), "run_dir": F.get("run_dir")}
    row["registered_ok"] = True if DRY else registered_ok(F.get("tra"), NPICK)
    row["picks_clicked"] = len(F.get("clicks") or []); row["precheck"] = pc
    rows.append(row); print("ROW " + json.dumps({k: v for k, v in row.items() if k not in ("release", "pre_pick_capture", "sysload_before", "sysload_after")}, default=str)[:1800], flush=True)
    gates["T1 %s rc 0" % tag] = rc == 0
    gates["T3 %s 0 TIFFs" % tag] = DRY or row["tiffs"] == 0
    gates["T5 %s fps within 15%%" % tag] = DRY or (row["measured_hz"] is not None and abs(row["measured_hz"] - HZ) <= 0.15 * HZ)
    gates["T10 %s TMX 39" % tag] = DRY or row["motor_tmx_after"] == 39.0
    gates["H2 %s no capture before pick 1" % tag] = any(k.startswith("H2") and v for k, v in pm.items())
    gates["L1 %s period proxy parsed" % tag] = bool(px.get("parsed"))
    gates["S1 %s sysload before+after read" % tag] = "err" not in s_before and "err" not in s_after
    gates["D1 %s plot read recorded" % tag] = any(k.startswith("D1") and v for k, v in pm.items())
    if arm == "B":
        pb = row["plot_before_stop"]
        gates["F1 %s #8323 non-empty before stop" % tag] = not pb.get("err") and (pb.get("elements") or 0) >= 1
        gates["F2 %s Display period is a number" % tag] = isinstance(pb.get("display_period"), (int, float)) and not isinstance(pb.get("display_period"), bool)
    return row


LOOP_STOP = None
try:                                                                            # card 106-2: the slot loop is LG.leg_loop
    finals, LOOP_STOP = LG.leg_loop(ORDER, run_leg, log=lambda s: print(s, flush=True), max_legs=MAX_LEGS)
    for slot, arm, npk, row in finals:
        gates["T12 slot%d %s@%d registered == target (<= 1 rerun)" % (slot, arm, npk)] = bool(row.get("registered_ok"))
    if LOOP_STOP: gates["T17 leg loop ran every slot (stopped: %s)" % LOOP_STOP["reason"]] = False
finally:
    restore = camera(90)
print("camera restored: %s" % json.dumps(restore), flush=True)
gates["T7 camera restored 90 Hz"] = bool(restore) and restore.get("hz") is not None and abs(restore["hz"] - 90) <= 0.5
MD5_AFTER = {k: md5(p) for k, (p, _) in PIN.items()}; print("MD5 AFTER %s" % MD5_AFTER, flush=True)
gates["M2 S1 + disp md5 after last leg == before"] = MD5_AFTER == MD5_BEFORE
counted = {}
for r in rows:
    if r["registered_ok"]: counted.setdefault("%s%d" % (r["arm"], r["picks"]), []).append({"lost": r["lost_frames"], "iters": r["tracking_iterations_tra_rows"],
                                                                                              "plot_elements": r["plot_before_stop"].get("elements"), "display_period": r["plot_before_stop"].get("display_period")})
out = {"schema": "disp-abba/1", "card": "104-5 PD210(c)/PD217(f)", "A": S1, "B": DSP, "md5_before": MD5_BEFORE, "md5_after": MD5_AFTER, "run_s": RUN_S, "hz": HZ,
       "picks": 15, "panel": "normal", "order": "A15 B15 B15 A15", "counted_by_arm": counted, "rows": rows, "gates": gates, "camera_restore": restore,
       "lv_running_at_end": lv_running(), "minutes": round((time.time() - T0) / 60, 1), "legdir": os.path.relpath(LEGDIR, ROOT),
       "proxy_note": "#637 period PROXY = tra col-0 frame-number step x 11.11 ms; not a timer", "judgement_not_applied": "PD217(f)",
       "leg_loop_stop": LOOP_STOP, "max_legs": MAX_LEGS}
jp = os.path.join(ROOT, JSON_OUT) if JSON_OUT else os.path.join(HERE, "disp_104_abba%s.json" % ("_dry" if DRY else ""))
json.dump(out, open(jp, "w"), indent=1, default=str)
gates["T13 disp_104_abba.json written"] = os.path.isfile(jp)
if not DRY and not any(r.get("registered_ok") for r in rows):
    print("INDEX row SKIPPED: no leg produced numbers (leg loop stop: %s)" % (LOOP_STOP,), flush=True)
elif not DRY:
    ix = os.path.join(ROOT, "archive", "benchmarks", "INDEX.md"); last = [ln for ln in open(ix, encoding="utf-8").read().splitlines() if ln.startswith("| ")][-1]
    n = int(last.split("|")[1]) + 1
    cell = "; ".join("%s: lost %s, tra rows %s, #8323 elements %s (dims %s), Display period %s, foreign claude+node %s->%s, CPU %% %s->%s" % (
        r["leg"], r["lost_frames"], r["tracking_iterations_tra_rows"], r["plot_before_stop"].get("elements"), r["plot_before_stop"].get("dims_first"),
        r["plot_before_stop"].get("display_period"), r["sysload_before"].get("foreign"), r["sysload_after"].get("foreign"),
        r["sysload_before"].get("cpu_pct_mean"), r["sysload_after"].get("cpu_pct_mean")) for r in rows)
    line = ("| %d | %s | **Card 104-5 (PD210(c)/PD217(f)): does moving the Force plot #8323 to its own display loop cut frame loss at 15 beads? ABBA A15 B15 B15 A15, panel normal, 120 s, 90 Hz: "
            "A = `claudeDev\\D1_s1_copy.vi` (md5 `%s`), B = `claudeDev\\D1_s1_disp_20260927_041648.vi` (md5 `%s`), both unstamped.** `tools/bench/diag_c104_abba.py` -> `diag_c104_leg.py` "
            "(row 56's scripts + #8323 value read by COM before/after the stop) | env as row 45; fixed picks 15, `RUN_S` 120 s, panel normal, 90 Hz; varied VI A/B | **%s**. md5 before == after: %s; "
            "LabVIEW gone at end: %s; gates %d/%d. Level: OPERATION + frame loss, %d real runs | `tools/bench/disp_104_abba.json`, legs `%s/`, log `tools/bench/diag_c104_abba.log` |"
            % (n, time.strftime("%Y-%m-%d"), MD5_BEFORE["S1"][:8] + "…", MD5_BEFORE["disp"][:8] + "…", cell, MD5_AFTER == MD5_BEFORE,
               not lv_running(), sum(gates.values()), len(gates), len(rows), os.path.relpath(LEGDIR, ROOT).replace("\\", "/")))
    open(ix, "a", encoding="utf-8").write(("" if open(ix, encoding="utf-8").read().endswith("\n") else "\n") + line + "\n")
    gates["T16 INDEX row %d appended" % n] = line in open(ix, encoding="utf-8").read()
for k, v in gates.items(): print("GATE %-58s %s" % (k, "PASS" if v else "FAIL"), flush=True)
print("SUMMARY " + json.dumps({r["leg"]: {"lost": r["lost_frames"], "iters": r["tracking_iterations_tra_rows"], "reg": r["picks_registered_tra"],
                               "plot": [r["plot_before_stop"].get(k) for k in ("elements", "dims_first", "display_period", "err")],
                               "plot_after": [r["plot_after_stop"].get(k) for k in ("elements", "err")],
                               "foreign": [r["sysload_before"].get("foreign"), r["sysload_after"].get("foreign")], "cpu": [r["sysload_before"].get("cpu_pct_mean"), r["sysload_after"].get("cpu_pct_mean")],
                               "tmx": r["motor_tmx_after"], "cap1": r["capture_class_before_pick1"], "rel": r["releases"]} for r in rows}, default=str), flush=True)
print("COUNTED BY ARM %s" % json.dumps(counted, default=str), flush=True)
ST, NP, NF, FIRST = LG.refusal_verdict(gates, rows, LOOP_STOP)                 # card 108-5: a VISA-refused leg -> SKIP, not FAIL
print(P.result_line(P.make_result(NP, NF, FIRST, [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}], status=ST)), flush=True)
sys.exit(1 if ST == "FAIL" else 0)
