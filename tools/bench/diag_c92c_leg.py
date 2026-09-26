r"""diag_c92c_leg.py - card 92-3 (PD199(b)+(c)): ONE real leg through drive_m8 `replay_s1 --src` (fresh dated byte run
copy, v5 L1..L13 with the bead-pick GUI, own motor-gate session, stop by the VI's control, LabVIEW gone), panel NORMAL,
WITH the PD199(b) harness change: before EVERY pick the capture-holding window is read (GetGUIThreadInfo on the panel's
thread, ctypes, a read) and logged with its class; before PICK 1 a held capture is RELEASED by one lv_gui.ps1 `click` on
the panel's own title bar (-Exception Approved, bead-pick option 1; full-screen shot before and after), then re-read.
--stamps: T0STAMP_DIR = --out (fresh), LabVIEW started from it; stamp-file counts per site + K3 (nothing in default dir).
FOUND FIRST: diag_c92_unstamped_leg.py (A-leg shape + capture class read, reused as is), diag_c91_step4_leg.py (T0STAMP_DIR,
K2/K3, stamp counts). Neither is edited. d0.click / d0.shot = drive_original_copy_v2 (lv_gui wrappers, logged).
    py -u tools/bench/diag_c92c_leg.py --src <vi> --picks 8 --run-s 120 --out <dir> [--stamps]
PREDICTION CONTRACT: H1 capture read before every pick (count == picks) H2 before pick 1 capture 0 after any release
 U1 >=1 pick click  U2 tra exact for N (reported; sequencer reruns)  [--stamps] K2 sites 00/10/20 have stamps  K3 default empty."""
import ctypes as C, ctypes.wintypes as W, glob, json, os, re, shutil, struct, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
A = sys.argv[1:]
SRC = os.path.normpath(A[A.index("--src") + 1]); OUT = os.path.normpath(A[A.index("--out") + 1])
NPICK = int(A[A.index("--picks") + 1]); RUN_S = A[A.index("--run-s") + 1] if "--run-s" in A else "120"; STAMPS = "--stamps" in A
os.makedirs(OUT, exist_ok=True)
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"; DEF = os.path.join(CD, "t0stamp_out")
if STAMPS: os.environ["T0STAMP_DIR"] = OUT
def_before = set(glob.glob(os.path.join(DEF, "*.bin")))
print("[c92c leg] src %s picks %d run-s %s stamps %s out %s" % (SRC, NPICK, RUN_S, STAMPS, OUT), flush=True)
import bench_prep                                                               # noqa: E402
bench_prep.restart_labview()                                                    # started WITH the env var (B legs)
sys.argv = [sys.argv[0], "--leg", "replay_s1", "--src", SRC, "--picks", str(NPICK), "--run-s", RUN_S]
import drive_m8                                                                 # noqa: E402
import drive_original_copy_v5 as v5                                             # noqa: E402
d4, d0 = v5.d4, v5.d0
PM, FACTS = {}, {"picks_target": NPICK, "stamps": STAMPS, "pre_pick": [], "release": None, "clicks": []}
U32 = C.windll.user32


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
    print("[c92c leg] CAPTURE %s" % json.dumps(rec, default=str), flush=True)
    return rec


real_probe = d4.clickprobe
SHOTDIR = os.path.join(HERE, "gui_shots", "c92c"); os.makedirs(SHOTDIR, exist_ok=True)


def shot(name):
    p = os.path.join(SHOTDIR, "%s_%s.png" % (time.strftime("%Y%m%d_%H%M%S"), name)); d0.gui("-Action", "shot", "-Out", "'%s'" % p)
    return p if os.path.isfile(p) else None


def probe(title, x, y, why):
    try:
        pre(why)
    except Exception as e:                                                     # noqa: BLE001
        print("[c92c leg] pre-pick step RAISED %r" % e, flush=True); FACTS.setdefault("pre_errors", []).append(repr(e))
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


d4.clickprobe = probe
T_START = time.time()
ok = drive_m8.main()
m8p = os.path.join(HERE, "m8_replay_s1_p%d_r%d.json" % (NPICK, int(float(RUN_S))))
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
cp = os.path.join(HERE, "m8_v5_replay_s1_p%d_r%d_clicks.json" % (NPICK, int(float(RUN_S))))
if os.path.isfile(cp) and os.path.getmtime(cp) >= T_START: shutil.copyfile(cp, os.path.join(OUT, "clicks.json"))
counts = {os.path.basename(p): max(0, len(open(p, "rb").read()) // 8 - 1) for p in sorted(glob.glob(os.path.join(OUT, "t0_site*.bin")))}
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
if STAMPS:
    have = lambda z: any(("site%02d_" % z) in k and v >= 1 for k, v in counts.items())     # noqa: E731
    PM["K2 stamp files sites 00/10/20 >= 1"] = all(have(z) for z in (0, 10, 20))
    PM["K3 nothing in the default stamp dir"] = not (set(glob.glob(os.path.join(DEF, "*.bin"))) - def_before)
print("REGISTERED picks target=%d tra=%r lost=%r releases=%d cap_class_pick1=%r" % (NPICK, reg, FACTS["lost"], FACTS["releases"], FACTS["capture_class_before_pick1"]), flush=True)
jp = os.path.join(OUT, "leg.json"); json.dump({"pm": PM, "facts": FACTS, "drive_m8_ok": ok, "m8": m8}, open(jp, "w"), indent=1, default=str)
for k, v in PM.items(): print("GATE %-52s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in PM.items() if not v and not k.startswith("U2")] + ([] if ok else ["drive_m8 M-gates"])
print(P.result_line(P.make_result(len(PM) + 1 - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": drive_m8.md5(jp)}])), flush=True)
sys.stdout.flush(); os._exit(0 if not bad else 1)
