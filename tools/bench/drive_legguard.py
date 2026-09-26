r"""drive_legguard.py - card 106-2 (PD218(d) + PD217(g)): the three leg guards every leg driver shares.
FOUND FIRST (reused, not rebuilt): diag_c106a_visa.py / diag_c105d_visa.py (ctypes viOpen on NI's visa64.dll - the probe),
diag_c105b_leg.py (EnumWindows logger + LVDChild detection), lv_gui.ps1 -Action shotwin -Hwnd (card 105-2, read-only),
lv_errorlist.ocr_engine/ocr_lines (RapidOCR; read the 105-2 dialog png verbatim in 1.8 s). This file only packages them.
  visa_precheck()  NI-VISA open+close of 'Rotor' and 'ASRL5::INSTR' (no byte, no attribute). ok only if every status == 0.
                   Test bypass: env LEGGUARD_TEST_BYPASS_VISA=1 (default OFF); dry=True -> not opened, recorded as dry.
  DialogWatch      thread, polls LabVIEW's top-level windows every 0.25 s from before Run to the end of L2. A NEW visible
                   enabled LVDChild/#32770 window while another visible LabVIEW window is DISABLED = a modal dialog ->
                   shotwin -Hwnd capture, LabVIEW killed directly (taskkill /F, no COM Abort), then its text OCR'd + logged.
  leg_loop()       the ABBA slot loop (rerun-once rule of diag_c104_abba.py kept) + stop_reason(): a REFUSED leg or an
                   A leg that failed before pick 1 ends the whole loop; later legs are never called.
Env LEGGUARD_TEST_STOP_AT_L2=1 (default OFF) is read by drive_original_copy_v5.leg: stop after L2 by a direct kill (no picks)."""
import ctypes as C, ctypes.wintypes as W, json, os, subprocess, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
PRECHECK_NAMES = ("Rotor", "ASRL5::INSTR")
BYPASS_ENV, STOP_L2_ENV = "LEGGUARD_TEST_BYPASS_VISA", "LEGGUARD_TEST_STOP_AT_L2"


def test_stop_at_l2():
    return os.environ.get(STOP_L2_ENV) == "1"


def visa_precheck(names=PRECHECK_NAMES, dry=False, dll=None, log=print):
    """-> {"ok", "bypassed", "dry", "rm_status", "trials": [{name, status, hex, text, close, ms}]}. Never raises."""
    r = {"ok": False, "bypassed": os.environ.get(BYPASS_ENV) == "1", "dry": bool(dry), "names": list(names), "trials": [], "t": time.strftime("%H:%M:%S")}
    if r["bypassed"] or dry:
        r["ok"] = True; r["why"] = "TEST BYPASS %s=1 (not opened)" % BYPASS_ENV if r["bypassed"] else "dry (not opened)"
        log("PRECHECK %s" % json.dumps(r)); return r
    try:
        V = dll or C.WinDLL("visa64.dll"); rm = C.c_uint32(); r["rm_status"] = st = V.viOpenDefaultRM(C.byref(rm))
        if st != 0:
            r["why"] = "viOpenDefaultRM %d" % st; log("PRECHECK %s" % json.dumps(r)); return r
        for nm in names:
            v = C.c_uint32(); t0 = time.perf_counter(); s = V.viOpen(rm, nm.encode(), 0, 2000, C.byref(v)); ms = round((time.perf_counter() - t0) * 1e3, 1)
            b = C.create_string_buffer(256); V.viStatusDesc(rm, C.c_int32(s), b)
            r["trials"].append({"name": nm, "status": s, "hex": "0x%08X" % (s & 0xFFFFFFFF), "text": b.value.decode("latin-1"),
                                "close": V.viClose(v) if v.value else None, "ms": ms})
        V.viClose(rm)
        r["ok"] = bool(r["trials"]) and all(t["status"] == 0 for t in r["trials"])
    except Exception as e:                                                     # noqa: BLE001
        r["why"] = "raised %r" % e
    log("PRECHECK %s" % json.dumps(r)); return r


def lv_running():
    return "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()


def kill_labview(wait_s=20.0):
    """direct kill (standing restart permission); -> (gone, secs)."""
    t = time.time(); subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True)
    while lv_running() and time.time() - t < wait_s: time.sleep(0.25)
    return (not lv_running()), round(time.time() - t, 2)


_u32, _k32 = C.windll.user32, C.windll.kernel32; _k32.OpenProcess.restype = W.HANDLE; _PN = {}
_EP = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)


def _pname(pid):
    if pid not in _PN:
        h, n = _k32.OpenProcess(0x1000, False, pid), ""
        if h:
            b, sz = C.create_unicode_buffer(520), W.DWORD(520)
            if _k32.QueryFullProcessImageNameW(h, 0, b, C.byref(sz)): n = os.path.basename(b.value).lower()
            _k32.CloseHandle(h)
        _PN[pid] = n
    return _PN[pid]


def lv_windows():
    """-> [(hwnd, title, class, visible, enabled)] of labview.exe's top-level windows."""
    out = []

    def cb(h, _):
        pid = W.DWORD(); _u32.GetWindowThreadProcessId(h, C.byref(pid))
        if _pname(pid.value) == "labview.exe":
            t, c = C.create_unicode_buffer(512), C.create_unicode_buffer(256); _u32.GetWindowTextW(h, t, 512); _u32.GetClassNameW(h, c, 256)
            out.append((int(h), t.value, c.value, bool(_u32.IsWindowVisible(h)), bool(_u32.IsWindowEnabled(h))))
        return True
    _u32.EnumWindows(_EP(cb), 0); return out


def modal_of(snap, baseline):
    """the first NEW visible enabled dialog-class window while another visible LabVIEW window is disabled, else None."""
    if not any(w[3] and not w[4] for w in snap): return None
    return next((w for w in snap if w[3] and w[4] and w[0] not in baseline and w[2] in ("LVDChild", "#32770")), None)


def shotwin(h, png):
    t = time.time()
    try:
        p = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "& .\\tools\\lv_gui.ps1 -Action shotwin -Hwnd %d -Out '%s'" % (h, png)],
                           cwd=ROOT, capture_output=True, text=True, timeout=20)
        return {"rc": p.returncode, "out": (p.stdout + p.stderr).strip()[:300], "secs": round(time.time() - t, 2), "png": png, "exists": os.path.isfile(png)}
    except Exception as e:                                                     # noqa: BLE001
        return {"rc": -1, "out": repr(e)[:300], "secs": round(time.time() - t, 2), "png": png, "exists": os.path.isfile(png)}


def ocr_text(png):
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools")); import lv_errorlist as E
        from PIL import Image
        run, name = E.ocr_engine()
        if run is None: return {"engine": name, "text": None}
        lines = E.ocr_lines(Image.open(png), scale=2)
        return {"engine": name, "text": " | ".join(x[0] for x in lines), "lines": [[x[0], round(x[1], 3)] for x in lines]}
    except Exception as e:                                                     # noqa: BLE001
        return {"engine": None, "text": None, "err": repr(e)[:300]}


class DialogWatch(threading.Thread):
    """start() BEFORE Run (baseline = windows visible then); stop() after L2. .fired / .record carry the result."""

    def __init__(self, tag, outdir, log=print, interval=0.25, snap=lv_windows, shoot=shotwin, kill=kill_labview, ocr=ocr_text):
        super().__init__(daemon=True)
        self.tag, self.outdir, self.log, self.iv = tag, outdir, log, interval
        self.snap, self.shoot, self.kill, self.ocr = snap, shoot, kill, ocr
        self.fired, self.done, self._stop = False, threading.Event(), threading.Event()
        self.record = {"tag": tag, "new_windows": [], "modal": None, "polls": 0, "max_gap_s": None}
        os.makedirs(outdir, exist_ok=True)

    def run(self):
        try:
            self._run()
        finally:
            self.done.set()

    def _run(self):
        t0 = time.time(); base = {w[0] for w in self.snap() if w[3]}; self.record["baseline"] = sorted(base); seen, last, gap = set(), t0, 0.0
        while not self._stop.is_set():
            now = time.time(); gap = max(gap, now - last); last = now; s = self.snap(); self.record["polls"] += 1
            self.record["max_gap_s"] = round(gap, 3)
            for w in s:
                if w[3] and w[0] not in base and w[0] not in seen:
                    seen.add(w[0]); self.record["new_windows"].append({"t": round(now - t0, 2), "win": list(w)}); self.log("  WATCH %s new window %r" % (self.tag, w))
            m = modal_of(s, base)
            if m:
                self.fired = True
                rec = {"t_visible_rel_watch": round(now - t0, 2), "abs_visible": now, "win": list(m),
                       "others": [list(w) for w in s if w[3]]}
                png = os.path.join(self.outdir, "dialog_%s_%s_h%d.png" % (self.tag, time.strftime("%Y%m%d_%H%M%S"), m[0]))
                rec["shotwin"] = self.shoot(m[0], png)
                rec["kill"] = dict(zip(("gone", "secs"), self.kill())); rec["abs_killed"] = time.time()
                rec["kill_after_visible_s"] = round(rec["abs_killed"] - now, 2)
                rec["ocr"] = self.ocr(png) if rec["shotwin"].get("exists") else {"text": None, "err": "no png"}
                self.record["modal"] = rec
                self.log("  WATCH %s MODAL DIALOG -> %s" % (self.tag, json.dumps(rec, default=str)[:1500]))
                return
            time.sleep(max(0.0, self.iv - (time.time() - now)))

    def stop(self, timeout=60.0):
        self._stop.set(); self.done.wait(timeout); return self.record


def stop_reason(arm, row):
    """PD217(g)/PD218(d): the rule that ends the whole leg loop; None = continue."""
    if row.get("refused"): return "leg refused by the VISA precheck (LabVIEW not started)"
    if arm == "A" and not row.get("registered_ok") and not (row.get("picks_clicked") or 0):
        return "A leg failed before pick 1 (rc %r)" % (row.get("rc"),)
    return None


def leg_loop(order, run_leg, log=print, max_legs=None):
    """order = [(arm, src, _, npick)]; run_leg(slot, arm, src, attempt, npick) -> row. Returns (finals, stop)."""
    finals, stop = [], None
    for slot, (arm, src, _st, npk) in enumerate(order, 1):
        for attempt in (1, 2):
            row = run_leg(slot, arm, src, attempt, npk)
            if row.get("refused") or row.get("registered_ok"): break
            if row.get("rc") != 0 and row.get("picks_registered_tra") is None:
                log("  crashed leg (no tra) -> harness fault, no rerun"); break
            log("  REGISTERED %r != %d -> %s" % (row.get("picks_registered_tra"), npk, "rerun once" if attempt == 1 else "logged, no third run"))
        finals.append((slot, arm, npk, row))
        r = stop_reason(arm, row)
        if r:
            stop = {"slot": slot, "arm": arm, "reason": r}; log("LEGLOOP STOP at slot %d (%s): %s -> no later leg is called" % (slot, arm, r)); break
        if max_legs is not None and slot >= max_legs and slot < len(order):
            stop = {"slot": slot, "arm": arm, "reason": "--max-legs %d" % max_legs}; log("LEGLOOP STOP at slot %d: --max-legs %d" % (slot, max_legs)); break
    return finals, stop
