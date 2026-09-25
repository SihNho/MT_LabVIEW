r"""diag_c91_step4_leg.py - card 91-3 (PD196(d) step 4): ONE real `replay_s1` leg of the instrumented copy
D1_s1_t0_<ts>.vi through drive_m8 (fresh dated run copy beside it, v5 L1..L13 with the bead-pick GUI, own motor-gate
session, stop by the VI's own control, LabVIEW gone, TMX re-read), with
  * T0STAMP_DIR = a FRESH per-leg directory set in THIS process and LabVIEW started from it by
    bench_prep.restart_labview (Start-Process inherits the environment) - exactly diag_c90_t0_smoke.py's shape;
  * --minimize | --control: the run copy's front panel minimized through COM FPState from the moment the experiment
    loop starts until just before the stop - exactly drive_m8_panelmin89_leg.py's MinCom + the two name patches
    (d0.answer_save_dialog, v5.stop_with_fallback); no VI is edited, nothing is clicked for the minimize.
FOUND FIRST: drive_m8_panelmin89_leg.py (hard-codes --leg s1, no --src, no T0STAMP_DIR) and diag_c90_t0_smoke.py
(replay_s1 + T0STAMP_DIR, no panel state) - this file is the union of the two; neither is edited.
    py -u tools/bench/diag_c91_step4_leg.py --src <vi> --picks N --run-s 120 --minimize|--control --out <dir>
PREDICTION CONTRACT (printed as GATE lines; drive_m8 M1..M8 stand unchanged):
 PM1 FPState before the write == 1   PM2 (min) after FPState=4 readback == 4   PM3 (min) panel rect iconic
 PM4 (min) restore: FPState == 1 and rect on screen   K2 a stamp file for sites 00/10/20 in --out
 K3 no file landed in the default claudeDev\t0stamp_out during the leg
Registered picks (card: "from the saved .cal/.tra, not the marker count") = the tra row width: N = (bytes/rows - 24)/24.
"""
import glob, json, os, re, struct, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
A = sys.argv[1:]
MIN = "--minimize" in A
assert MIN or "--control" in A, "--minimize or --control"
SRC = os.path.normpath(A[A.index("--src") + 1]); OUT = os.path.normpath(A[A.index("--out") + 1])
NPICK = int(A[A.index("--picks") + 1]); RUN_S = A[A.index("--run-s") + 1] if "--run-s" in A else "120"
os.makedirs(OUT, exist_ok=True); os.environ["T0STAMP_DIR"] = OUT
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"; DEF = os.path.join(CD, "t0stamp_out")
def_before = set(glob.glob(os.path.join(DEF, "*.bin")))
MODE = "min" if MIN else "ctl"
print("[step4 leg %s] T0STAMP_DIR %s src %s picks %d run-s %s" % (MODE, OUT, SRC, NPICK, RUN_S), flush=True)
import bench_prep                                                               # noqa: E402
bench_prep.restart_labview()                                                    # LabVIEW started WITH the env var
sys.argv = [sys.argv[0], "--leg", "replay_s1", "--src", SRC, "--picks", str(NPICK), "--run-s", RUN_S]
import drive_m8                                                                 # noqa: E402  (argv parsed here)
import drive_original_copy_v5 as v5                                             # noqa: E402
d0 = v5.d0
PM, FACTS = {}, {"mode": MODE, "events": [], "picks_target": NPICK}
STD, MINI = 1, 4


def log(m):
    print("[step4 leg %s] %s" % (MODE, m), flush=True); FACTS["events"].append("%.1f %s" % (time.time(), m))


class MinCom(threading.Thread):
    """Private COM apartment (drive_m8_panelmin89_leg.py verbatim): open / get -> int(FPState) / set / release."""
    def __init__(self):
        super().__init__(daemon=True); self.q, self.res, self.ev, self.n = [], {}, {}, 0
        self.lk = threading.Lock(); self.cv = threading.Condition(self.lk); self.start()

    def run(self):
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize(); app = vi = None
        while True:
            with self.cv:
                while not self.q: self.cv.wait()
                sid, kind, a = self.q.pop(0)
            try:
                if kind == "open":
                    app = dynamic.Dispatch("LabVIEW.Application"); vi = app.GetVIReference(a[0], "", False, 0); out = "ref ok"
                elif kind == "get": out = int(vi.FPState)
                elif kind == "set": vi.FPState = int(a[0]); out = int(vi.FPState)
                elif kind == "release": vi = app = None; out = "released"
                else: out = RuntimeError(kind)
            except Exception as e:                                             # noqa: BLE001
                out = e
            with self.lk:
                self.res[sid] = out; ev = self.ev.get(sid)
            if ev: ev.set()

    def call(self, kind, *a, timeout=15.0):
        with self.cv:
            self.n += 1; sid = self.n; ev = threading.Event(); self.ev[sid] = ev; self.q.append((sid, kind, a)); self.cv.notify()
        if not ev.wait(timeout): raise TimeoutError("MinCom %s blocked >%.0fs" % (kind, timeout))
        with self.lk: out = self.res.pop(sid); self.ev.pop(sid, None)
        if isinstance(out, Exception): raise out
        return out


mc = MinCom()


def rect():
    try: return d0.win_rect(d0.COPY_TITLE)
    except Exception as e:                                                     # noqa: BLE001
        return "ERR %r" % e


real_save = d0.answer_save_dialog
real_stop = v5.stop_with_fallback


def counters(key):
    try: FACTS[key] = {"lost": v5.getv(d0.I_LOST), "frame": v5.getv(v5.I_FRAME), "t": time.time()}
    except Exception as e:                                                     # noqa: BLE001
        FACTS[key] = "ERR %r" % e
    log("%s: %r" % (key, FACTS[key]))


def save_then_minimize(tag, base_path):
    r = real_save(tag, base_path)
    try:
        mc.call("open", v5.COPY, timeout=60); s0 = mc.call("get"); FACTS["fpstate_before"] = s0; FACTS["rect_before"] = rect()
        counters("counters_at_minimize")
        PM["PM1 FPState before == 1 (Standard)"] = (s0 == STD)
        if MIN:
            s1 = mc.call("set", MINI); time.sleep(1.5); s2 = mc.call("get"); rc2 = rect()
            FACTS.update({"fpstate_set_ret": s1, "fpstate_after_min": s2, "rect_after_min": rc2, "t_minimized": time.time()})
            PM["PM2 FPState after write == 4 (Minimized)"] = (s2 == MINI)
            PM["PM3 panel rect iconic after minimize"] = (isinstance(rc2, tuple) and rc2[0] <= -30000) or (rc2 is None and s2 == MINI)
            log("minimized: set->%r get->%r rect=%r" % (s1, s2, rc2))
        else:
            PM["PM2 control: FPState not written"] = True; PM["PM3 control: rect recorded"] = isinstance(FACTS["rect_before"], tuple)
    except Exception as e:                                                     # noqa: BLE001
        log("minimize step RAISED %r" % e); FACTS["minimize_error"] = repr(e)
        PM.setdefault("PM1 FPState before == 1 (Standard)", False); PM["PM2 FPState after write == 4 (Minimized)"] = False
    return r


_restored = []


def restore_then_stop(tag):
    if _restored: return real_stop(tag)
    _restored.append(tag)
    counters("counters_at_restore")
    if MIN:
        try:
            s3 = mc.call("set", STD); time.sleep(1.5); s4 = mc.call("get"); rc4 = rect()
            FACTS.update({"fpstate_after_restore": s4, "rect_after_restore": rc4, "t_restored": time.time()})
            PM["PM4 restore: FPState == 1 and rect on screen"] = (s4 == STD) and isinstance(rc4, tuple) and rc4[0] > -30000
            log("restored: set->%r get->%r rect=%r" % (s3, s4, rc4))
        except Exception as e:                                                 # noqa: BLE001
            log("restore RAISED %r" % e); FACTS["restore_error"] = repr(e); PM["PM4 restore: FPState == 1 and rect on screen"] = False
    else:
        PM["PM4 control: nothing to restore"] = True
    try: mc.call("release")
    except Exception as e:                                                     # noqa: BLE001
        log("release raised %r" % e)
    return real_stop(tag)


d0.answer_save_dialog = save_then_minimize
v5.stop_with_fallback = restore_then_stop

ok = drive_m8.main()
if not PM: PM["PM0 minimize point never reached (leg did not get to L9)"] = False
m8p = os.path.join(HERE, "m8_replay_s1_p%d_r%d.json" % (NPICK, int(float(RUN_S))))
m8 = json.load(open(m8p)) if os.path.isfile(m8p) else {}
# registered picks from the saved tra: width 3 + 3N f64 per row, rows = header 'actual data points'
reg = None; tra = {}
for f, s in (m8.get("files") or {}).items():
    if f.lower().startswith("tra"):
        p = os.path.join(m8.get("run_dir", ""), f)
        try:
            b = open(p, "rb").read(); k = b.find(b"not in z!)"); d = len(b) - (k + 10)
            mm = re.search(rb"actual data points/nominal: (\d+)/(\d+)", b[:2000]); rows = int(mm.group(1)) if mm else 0
            n = ((d / rows) - 24) / 24 if rows else None
            # review c91-step4-t12 §1: the 8 leftover bytes are the 2-D array's dimension prefix, so the EXACT rule is
            # (d - 8) == rows_hdr x (24 + 24N); the prefix decoded both ways is recorded, never assumed
            pre = b[k + 10:k + 18]; dims = {"be": struct.unpack(">ii", pre), "le": struct.unpack("<ii", pre)} if len(pre) == 8 else None
            n_exact = (((d - 8) / rows) - 24) / 24 if rows else None
            exact = bool(rows) and (d - 8) == rows * (24 + 24 * NPICK)
            tra[f] = {"data_bytes": d, "rows_hdr": rows, "bytes_per_row": (d / rows) if rows else None, "n_beads": n,
                      "n_beads_exact": n_exact, "exact_for_target": exact, "leftover_bytes": (d - 8) - rows * (24 + 24 * NPICK) if rows else None, "dims_prefix": dims}
            if n_exact is not None: reg = n_exact
        except Exception as e:                                                 # noqa: BLE001
            tra[f] = "ERR %r" % e
bp = (m8.get("bandpass") or {}).get("answered")
# review c91-smoke-k1 §3: .cal size = 96 + 57152 n; and hwndCapture per pick click from v5's clicks json (recorded, not new)
cal_n = None
for f, s in (m8.get("files") or {}).items():
    if f.lower().startswith("cal"): cal_n = (s - 96) / 57152.0
caps = []
try:
    import shutil
    cp = os.path.join(HERE, "m8_v5_replay_s1_p%d_r%d_clicks.json" % (NPICK, int(float(RUN_S))))
    if os.path.isfile(cp):
        shutil.copyfile(cp, os.path.join(OUT, "clicks.json"))
        txt = open(cp, encoding="utf-8", errors="replace").read()
        caps = re.findall(r'"hwndCapture":\s*(\d+)', txt)
except Exception as e:                                                         # noqa: BLE001
    caps = ["ERR %r" % e]
FACTS.update({"picks_registered_cal": cal_n, "hwndCapture_seq": caps, "foreign_capture_nonzero": [c for c in caps if c not in ("0",)]})
FACTS.update({"tra": tra, "picks_registered_tra": reg, "bandpass_answered": bp, "picks_markers": m8.get("picks"),
              "lost": m8.get("total_lost_frames"), "frames_delta": m8.get("frame_counter_delta"),
              "tra_header_points": m8.get("tra_header_points"), "motor_tmx_after": m8.get("motor_after"),
              "m8_gates": m8.get("gates"), "v5_failing": m8.get("v5_failing_steps"), "stop": m8.get("stop"),
              "run_dir": m8.get("run_dir"), "source_md5": m8.get("source_md5")})
counts = {}
for p in sorted(glob.glob(os.path.join(OUT, "t0_site*.bin"))):
    counts[os.path.basename(p)] = max(0, len(open(p, "rb").read()) // 8 - 1)
FACTS["stamp_counts"] = counts
have = lambda z: any(("site%02d_" % z) in k and v >= 1 for k, v in counts.items())              # noqa: E731
PM["K2 files for sites 00/10/20 with >= 1 stamp"] = all(have(z) for z in (0, 10, 20))
new_def = sorted(set(glob.glob(os.path.join(DEF, "*.bin"))) - def_before)
PM["K3 no file landed in the default dir"] = not new_def
print("STAMP FILES %s" % json.dumps(counts), flush=True)
print("REGISTERED picks target=%d tra=%r cal=%r bandpass_answered=%r lost=%r hwndCapture=%s" % (NPICK, reg, cal_n, bp, FACTS["lost"], caps), flush=True)
jp = os.path.join(OUT, "leg.json")
json.dump({"pm": PM, "facts": FACTS, "drive_m8_ok": ok, "m8": m8}, open(jp, "w"), indent=1, default=str)
for k, v in PM.items(): print("GATE %-52s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in PM.items() if not v] + ([] if ok else ["drive_m8 M-gates"])
print(P.result_line(P.make_result(len(PM) + (1 if ok else 0), len(bad), bad[0] if bad else None,
                                  [{"path": os.path.relpath(jp, ROOT), "md5": drive_m8.md5(jp)}])), flush=True)
sys.stdout.flush(); os._exit(0 if not bad else 1)
