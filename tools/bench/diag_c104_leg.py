r"""diag_c104_leg.py - card 104-5 (PD210(c)/PD217(f)) = diag_c96_leg.py verbatim except: v5.stop_with_fallback is WRAPPED
so that, AFTER L11 has read `Total Lost Frames` and the frame counter (so the lost count is not perturbed) and just BEFORE
the stop, the plot indicator #8323 'Force (pN) vs Extension (nm) ' (trailing blank; label from
tools/bench/sim/disp/stageplan_disp_r4_open.json:606) and 'Display period (ms)' (:695, B only) are read by COM
(d0.getv = VI.GetControlValue); the plot is read again after the stop. The value is summarised as nested dims along the
first elements + leaf-number count + per-plot leaf counts; nothing else is kept. --dry: the reads run on a SYNTHETIC
value (15 plots x (x[500], y[500]) + 100.0), labelled synthetic - no saved real return of #8323 exists (never read).
FOUND FIRST: diag_c96_leg.py (copied), drive_original_copy_v5.py:235 stop_with_fallback / :469 call site (module global,
so rebinding v5.stop_with_fallback takes effect), drive_original_copy_v2.py:380 getv (never raises; 'ERR:<type>').
PREDICTION CONTRACT (new): D1 plot read before stop returns an array (no ERR) and is recorded; on B the elements >= 1 and
Display period is a number (both judged by diag_c104_abba.py per B leg, not here).
--- diag_c96_leg.py docstring ---
diag_c96_leg.py - card 96-1 (PD203(f)/PD204) = diag_c94_leg.py verbatim except: adds the #637 period PROXY read from
the leg's tra file (col 0 = camera frame number, m8b_replay_compare.tra layout: '<ii' dims then '<f8' rows; step x
1000/90 ms), labelled 'proxy'. Pick-1 capture release + everything else unchanged. PM adds P1 proxy parsed.
    py -u tools/bench/diag_c104_leg.py --src <vi> --picks 15 --run-s 120 --out <dir> [--dry]"""
import ctypes as C, ctypes.wintypes as W, glob, json, os, re, shutil, struct, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
A = sys.argv[1:]
SRC = os.path.normpath(A[A.index("--src") + 1]); OUT = os.path.normpath(A[A.index("--out") + 1])
NPICK = int(A[A.index("--picks") + 1]); RUN_S = A[A.index("--run-s") + 1] if "--run-s" in A else "120"; STAMPS = "--stamps" in A
DRY = "--dry" in A; SAVED = os.path.join(HERE, "t0_legs", "c92c_abba8_20260926_091948")
os.makedirs(OUT, exist_ok=True)
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"; DEF = os.path.join(CD, "t0stamp_out")
if STAMPS: os.environ["T0STAMP_DIR"] = OUT
def_before = set(glob.glob(os.path.join(DEF, "*.bin")))
print("[c104 leg] src %s picks %d run-s %s stamps %s out %s dry %s" % (SRC, NPICK, RUN_S, STAMPS, OUT, DRY), flush=True)
if not DRY:
    import bench_prep                                                           # noqa: E402
    bench_prep.restart_labview()
sys.argv = [sys.argv[0], "--leg", "replay_s1", "--src", SRC, "--picks", str(NPICK), "--run-s", RUN_S] + (["--dry"] if DRY else [])
import drive_m8                                                                 # noqa: E402
import drive_original_copy_v5 as v5                                             # noqa: E402
d4, d0 = v5.d4, v5.d0
PM, FACTS = {}, {"picks_target": NPICK, "stamps": STAMPS, "pre_pick": [], "release": None, "clicks": [], "plot_reads": []}
U32 = C.windll.user32
PLOT, DISP = "Force (pN) vs Extension (nm) ", "Display period (ms)"


class GTI(C.Structure):
    _fields_ = [("cbSize", W.DWORD), ("flags", W.DWORD), ("hwndActive", W.HWND), ("hwndFocus", W.HWND), ("hwndCapture", W.HWND),
                ("hwndMenuOwner", W.HWND), ("hwndMoveSize", W.HWND), ("hwndCaret", W.HWND), ("rcCaret", W.RECT)]


def win_class(h):
    if not h: return None
    b = C.create_unicode_buffer(256); U32.GetClassNameW(W.HWND(h), b, 256)
    t = C.create_unicode_buffer(512); U32.GetWindowTextW(W.HWND(h), t, 512)
    pid = W.DWORD(0); U32.GetWindowThreadProcessId(W.HWND(h), C.byref(pid))
    return {"hwnd": h, "class": b.value, "title": t.value, "pid": pid.value}


def panel_hwnd(sub):
    found = []
    CB = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
    def cb(h, _):
        t = C.create_unicode_buffer(512); U32.GetWindowTextW(h, t, 512)
        if sub.lower() in t.value.lower() and U32.IsWindowVisible(h): found.append(h)
        return True
    U32.EnumWindows(CB(cb), 0)
    return found[0] if found else None


def read_capture(tag):
    """a READ: GUITHREADINFO of the thread owning the run copy's panel window."""
    rec = {"tag": tag, "t": time.time()}
    try:
        h = panel_hwnd(d0.COPY_TITLE); rec["panel_hwnd"] = h
        if h:
            tid = U32.GetWindowThreadProcessId(W.HWND(h), None); g = GTI(); g.cbSize = C.sizeof(GTI)
            ok = U32.GetGUIThreadInfo(tid, C.byref(g)); cap = g.hwndCapture or 0
            rec.update({"tid": tid, "ok": bool(ok), "hwndCapture": cap, "capture_win": win_class(cap), "flags": g.flags})
    except Exception as e:                                                     # noqa: BLE001
        rec["err"] = repr(e)
    print("[c104 leg] CAPTURE %s" % json.dumps(rec, default=str), flush=True)
    return rec


real_probe = d4.clickprobe
SHOTDIR = os.path.join(HERE, "gui_shots", "c104"); os.makedirs(SHOTDIR, exist_ok=True)


def shot(name):
    p = os.path.join(SHOTDIR, "%s_%s.png" % (time.strftime("%Y%m%d_%H%M%S"), name)); d0.gui("-Action", "shot", "-Out", "'%s'" % p)
    return p if os.path.isfile(p) else None


def probe(title, x, y, why):
    try:
        pre(why)
    except Exception as e:                                                     # noqa: BLE001
        print("[c104 leg] pre-pick step RAISED %r" % e, flush=True); FACTS.setdefault("pre_errors", []).append(repr(e))
    j = real_probe(title, x, y, why)
    g = (j or {}).get("gti_before_click") or {}
    FACTS["clicks"].append({"why": why[:60], "gti_before_click_capture": g.get("hwndCapture"), "gti_after_click_capture": ((j or {}).get("gti_after_click") or {}).get("hwndCapture")})
    return j


def pre(why):
    if why.lower().startswith("bead"):
        r = read_capture(why[:12]); FACTS["pre_pick"].append(r)
        if why.lower().startswith("bead 1 ") and FACTS["release"] is None:
            rel = {"before": r, "acts": []}
            for k in (1, 2):
                if not (r.get("hwndCapture") or 0): break
                rc = d0.win_rect(d0.COPY_TITLE) or (0, 0, 800, 600)
                tx, ty = (rc[0] + rc[2]) // 2, max(rc[1] + 18, 4)
                s1 = shot("release%d_before" % k)
                o = d0.click(tx, ty, "PD199(b) release foreign capture before pick 1: panel title bar (%d,%d)" % (tx, ty))
                time.sleep(0.6); s2 = shot("release%d_after" % k)
                r = read_capture("after-release-%d" % k); rel["acts"].append({"xy": [tx, ty], "shots": [s1, s2], "out": str(o)[:200], "after": r})
            rel["final"] = r; FACTS["release"] = rel


def _dims(v):
    return [len(v)] + (_dims(v[0]) if len(v) else []) if isinstance(v, (tuple, list)) else []


def _leaves(v):
    if isinstance(v, (tuple, list)): return sum(_leaves(x) for x in v)
    return 1 if isinstance(v, (int, float)) and not isinstance(v, bool) else 0


def read_plot(tag, getv):
    """a READ by COM: #8323 value summary + Display period (ms)."""
    t = time.time(); v = getv(PLOT, timeout=90.0); dt = round(time.time() - t, 2)
    r = {"tag": tag, "secs": dt, "type": type(v).__name__, "err": v if isinstance(v, str) and v.startswith("ERR") else None,
         "dims_first": _dims(v), "elements": _leaves(v), "per_plot_leaves": [_leaves(x) for x in v][:40] if isinstance(v, (tuple, list)) else None,
         "display_period": getv(DISP, timeout=20.0), "synthetic": DRY}
    FACTS["plot_reads"].append(r); print("[c104 leg] PLOT %s" % json.dumps(r, default=str)[:600], flush=True)
    return r


_SYN = {PLOT: tuple((tuple(float(i) for i in range(500)), tuple(0.5 * i for i in range(500))) for _ in range(15)), DISP: 100.0}
_real_stop = v5.stop_with_fallback


def stop_hook(tag):
    read_plot("before-stop", d0.getv)
    out = _real_stop(tag)
    read_plot("after-stop", d0.getv)
    return out


v5.stop_with_fallback = stop_hook
d4.clickprobe = probe
if DRY:                                                                         # PD199(h): saved real returns, 92-3 leg1
    import m8_dry                                                               # noqa: E402
    _cj = iter([c.get("json") for c in json.load(open(os.path.join(SAVED, "leg1_A_p8_a1", "clicks.json")))])
    _lf = json.load(open(os.path.join(SAVED, "leg1_A_p8_a1", "leg.json")))["facts"]
    _pp = {r["tag"]: r for r in _lf["pre_pick"]}; _rel = [a["after"] for a in _lf["release"]["acts"]]
    real_probe = lambda title, x, y, why: next(_cj, {})                         # noqa: E731
    d0.click = lambda x, y, why: "DRY saved: click logged in tools/gui_actions.log:3588"   # noqa: E731
    d0.win_rect = lambda t: (-6, 51, 1930, 1107)                                # saved target rect (clicks.json)

    def read_capture(tag):
        r = dict(_pp.get(tag) or (_rel[0] if tag.startswith("after") else {}), tag=tag, dry=True)
        print("[c104 leg] CAPTURE(DRY) %s" % json.dumps(r, default=str)[:300], flush=True); return r
    _stub0 = m8_dry.stub

    def _stub(v5_, d4_, d0_):
        _stub0(v5_, d4_, d0_); fl = v5_.leg

        def leg(tag, n, base, cal):
            for k in range(1, NPICK + 1): d4_.clickprobe(d0_.COPY_TITLE, 100, 100, "bead %d (%s) DRY" % (k, "reference" if k == 1 else "magnetic"))
            ok_ = fl(tag, n, base, cal)
            read_plot("before-stop", lambda name, timeout=None: _SYN.get(name, "ERR:KeyError"))   # fake leg never stops: hook reads here
            read_plot("after-stop", lambda name, timeout=None: _SYN.get(name, "ERR:KeyError"))
            return ok_
        v5_.leg = leg
    m8_dry.stub = _stub
T_START = time.time()
ok = drive_m8.main()
m8p = os.path.join(HERE, "m8_replay_s1_p%d_r%d%s.json" % (NPICK, int(float(RUN_S)), "_dry" if DRY else ""))
m8 = json.load(open(m8p)) if os.path.isfile(m8p) and os.path.getmtime(m8p) >= T_START else {}
reg, tra = None, {}
for f in (m8.get("files") or {}):
    if f.lower().startswith("tra"):
        try:
            b = open(os.path.join(m8.get("run_dir", ""), f), "rb").read(); k = b.find(b"not in z!)"); d = len(b) - (k + 10)
            mm = re.search(rb"actual data points/nominal: (\d+)/(\d+)", b[:2000]); rows = int(mm.group(1)) if mm else 0
            n_exact = (((d - 8) / rows) - 24) / 24 if rows else None
            tra[f] = {"data_bytes": d, "rows_hdr": rows, "n_beads_exact": n_exact, "exact_for_target": bool(rows) and (d - 8) == rows * (24 + 24 * NPICK)}
            if n_exact is not None: reg = n_exact
        except Exception as e:                                                 # noqa: BLE001
            tra[f] = "ERR %r" % e
SAVED_RD = os.path.join(HERE, "m8_out", "replay_s1_20260926_115922"); FRAME_MS = 1000.0 / 90


def period_proxy(rd):
    """#637 period PROXY: tra col 0 frame-number step x 11.11 ms (NOT a timer; a skipped frame shows as a step > 1)."""
    import numpy as np
    try:
        f = [x for x in sorted(os.listdir(rd)) if x.lower().startswith("tra")][0]
        b = open(os.path.join(rd, f), "rb").read(); k = b.find(b"not in z!)") + 10
        r, c = struct.unpack("<ii", b[k:k + 8]); n = (len(b) - k - 8) // 8
        a = np.frombuffer(b[k + 8:k + 8 + 8 * r * c], dtype="<f8").reshape(r, c); st = np.diff(a[:, 0]); ms = st * FRAME_MS
        return {"label": "proxy: tra frame-step x 11.11 ms", "file": os.path.join(rd, f), "rows": r, "cols": c, "parsed": r * c == n,
                "cols_eq_3_3N": c == 3 + 3 * NPICK, "steps": int(st.size), "step_median": float(np.median(st)), "step_p95": float(np.percentile(st, 95)),
                "step_max": float(st.max()), "median_ms": round(float(np.median(ms)), 3), "p95_ms": round(float(np.percentile(ms, 95)), 3),
                "max_ms": round(float(ms.max()), 3), "steps_gt1": int((st > 1).sum()), "steps_le0": int((st <= 0).sum()), "frame_span": float(a[-1, 0] - a[0, 0])}
    except Exception as e:                                                     # noqa: BLE001
        return {"label": "proxy", "err": repr(e), "run_dir": rd}


FACTS["period_proxy_637"] = period_proxy(SAVED_RD if DRY else (m8.get("run_dir") or ""))
print("[c104 leg] PROXY637 %s" % json.dumps(FACTS["period_proxy_637"]), flush=True)
cp = os.path.join(HERE, "m8_v5_replay_s1_p%d_r%d_clicks.json" % (NPICK, int(float(RUN_S))))
if os.path.isfile(cp) and os.path.getmtime(cp) >= T_START: shutil.copyfile(cp, os.path.join(OUT, "clicks.json"))
counts = {os.path.basename(p): max(0, len(open(p, "rb").read()) // 8 - 1) for p in sorted(glob.glob(os.path.join(OUT, "t0_site*.bin")))}
FACTS["stamp_meta"] = {os.path.basename(p): open(p).read().split("\n") for p in glob.glob(os.path.join(OUT, "t0_meta_pid*.txt"))}
picks = [r for r in FACTS["pre_pick"] if not r["tag"].startswith("after")]
rel = FACTS["release"] or {}; fin = rel.get("final") or (picks[0] if picks else {})
FACTS.update({"tra": tra, "picks_registered_tra": reg, "lost": m8.get("total_lost_frames"), "frames_delta": m8.get("frame_counter_delta"),
              "bandpass_answered": (m8.get("bandpass") or {}).get("answered"), "motor_tmx_after": m8.get("motor_after"), "m8_gates": m8.get("gates"),
              "v5_failing": m8.get("v5_failing_steps"), "stop": m8.get("stop"), "run_dir": m8.get("run_dir"), "source_md5": m8.get("source_md5"),
              "tiffs": (m8.get("tiffs_deleted") or {}).get("count"), "stamp_counts": counts, "m8_json_fresh": bool(m8),
              "capture_class_before_pick1": ((rel.get("before") or {}).get("capture_win") or {}).get("class") if rel else None,
              "releases": len(rel.get("acts") or [])})
PM["H1 capture read before every pick (== picks)"] = len(picks) == NPICK
PM["H2 before pick 1 no capture held (after any release)"] = bool(fin) and not (fin.get("hwndCapture") or 0) and bool(fin.get("ok"))
PM["U1 >=1 pick click"] = len(FACTS["clicks"]) >= 1
PM["U2 tra exact for target N (reported; sequencer reruns)"] = any(isinstance(t, dict) and t.get("exact_for_target") for t in tra.values())
_pp637 = FACTS["period_proxy_637"]
PM["P1 period proxy parsed (rows*cols == data, cols == 3+3N)"] = bool(_pp637.get("parsed")) and bool(_pp637.get("cols_eq_3_3N"))
PM["D1 plot read before stop recorded (no ERR)"] = any(r["tag"] == "before-stop" and not r["err"] for r in FACTS["plot_reads"])
print("REGISTERED picks target=%d tra=%r lost=%r releases=%d cap_class_pick1=%r" % (NPICK, reg, FACTS["lost"], FACTS["releases"], FACTS["capture_class_before_pick1"]), flush=True)
jp = os.path.join(OUT, "leg.json"); json.dump({"pm": PM, "facts": FACTS, "drive_m8_ok": ok, "m8": m8}, open(jp, "w"), indent=1, default=str)
for k, v in PM.items(): print("GATE %-52s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in PM.items() if not v and not k.startswith("U2")] + ([] if ok else ["drive_m8 M-gates"])
print(P.result_line(P.make_result(len(PM) + 1 - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": drive_m8.md5(jp)}])), flush=True)
sys.stdout.flush(); os._exit(0 if not bad else 1)
