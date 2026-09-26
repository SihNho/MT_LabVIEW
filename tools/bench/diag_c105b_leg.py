r"""diag_c105b_leg.py - card 105-2 C1-C4: ONE leg A of a scratch byte copy of claudeDev\D1_s1_copy.vi, exactly the 105-1
leg (diag_c105_leg.py, md5 9c7621dc: same ctypes EnumWindows logger every 0.25 s, same full-screen shooter, same
drive_m8 replay_s1 -> v5 path, same stop_with_fallback end, forced kill allowed) PLUS a content capture of every
newly visible LVDChild window by PrintWindow(hwnd, PW_RENDERFULLCONTENT=2) - no focus, key, click or dismiss:
  (a) in-process ctypes PrintWindow at detection (the <= 1 s capture), (b) `lv_gui.ps1 -Action shotwin -Hwnd <n>`
  (T0: 1.42 s per call incl. powershell start, diag_c105b_t0.log), (c) again at t=5 s and t=20 s after Run for every
  visible LVDChild. Captures run in their own threads with a join deadline (PrintWindow can block on a hung thread).
The stop (stop_with_fallback) starts only after the t=20 captures are written. Windows born after the stop (e.g. the
105-1 post-Abort LVDChild) are captured by the same rule. MEASURE ONLY; which hypothesis the text favours is judgement's.
PREDICTION CONTRACT:
 C1a Run->L2 max logger gap <= 0.5 s  C1b every LVDChild made visible after Run captured in-process <= 1 s after detection
 C1c each also captured by shotwin -Hwnd (rc 0)  C1d t=5 and t=20 captures written before the stop  C3 no GUI act before
 L2 and stop called after C1d  C4a one leg, no picks  C4b LabVIEW gone  C4c S1 md5 3e3d23ce unchanged  C4d TMX 39 read
 back  C4e COM5 T0 and T2 probes FREE/BUSY (no bytes). 105-1's C3a-c reads are logged as INFO, not gated.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c105b_leg.log -- py -u tools/bench/diag_c105b_leg.py"""
import ctypes as C, ctypes.wintypes as W, hashlib, json, os, queue, shutil, subprocess, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
S1 = os.path.join(CD, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
CONF = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor\Configure.vi"
OUT = os.path.join(HERE, "diag_c105b_out"); SH = os.path.join(OUT, "shots"); PW = os.path.join(OUT, "pw"); os.makedirs(SH, exist_ok=True); os.makedirs(PW, exist_ok=True)
TS = time.strftime("%Y%m%d_%H%M%S"); F, G = {"shots": [], "pw": []}, {}; L2_S = 20.0
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                   # noqa: E731
def say(k, v): print("[c105b] %s %s" % (k, json.dumps(v, default=str)[:1800]), flush=True)
u32, k32, gdi = C.windll.user32, C.windll.kernel32, C.windll.gdi32; k32.OpenProcess.restype = W.HANDLE; PN = {}
EP = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
VP = C.c_void_p
for fn, rt, at in ((u32.GetDC, VP, [VP]), (u32.ReleaseDC, C.c_int, [VP, VP]), (gdi.CreateCompatibleDC, VP, [VP]),
                   (gdi.CreateCompatibleBitmap, VP, [VP, C.c_int, C.c_int]), (gdi.SelectObject, VP, [VP, VP]),
                   (gdi.DeleteObject, W.BOOL, [VP]), (gdi.DeleteDC, W.BOOL, [VP]), (u32.PrintWindow, W.BOOL, [VP, VP, W.UINT]),
                   (gdi.GetDIBits, C.c_int, [VP, VP, W.UINT, W.UINT, VP, VP, W.UINT])):
    fn.restype, fn.argtypes = rt, at
def pname(pid):
    if pid not in PN:
        h, n = k32.OpenProcess(0x1000, False, pid), ""
        if h:
            b, sz = C.create_unicode_buffer(520), W.DWORD(520)
            if k32.QueryFullProcessImageNameW(h, 0, b, C.byref(sz)): n = os.path.basename(b.value).lower()   # noqa: E701
            k32.CloseHandle(h)
        PN[pid] = n
    return PN[pid]
def wtxt(h, f=u32.GetWindowTextW):
    b = C.create_unicode_buffer(512); f(h, b, 512); return b.value
def snap():
    out = []
    def cb(h, _):
        pid = W.DWORD(); u32.GetWindowThreadProcessId(h, C.byref(pid)); c = wtxt(h, u32.GetClassNameW)
        if pname(pid.value) == "labview.exe" or c == "#32770": out.append((int(h), wtxt(h), c, bool(u32.IsWindowVisible(h))))
        return True
    u32.EnumWindows(EP(cb), 0); return out
def kids(h):
    out = []
    def cb(c, _): out.append((wtxt(c, u32.GetClassNameW), wtxt(c))); return len(out) < 40   # noqa: E704
    u32.EnumChildWindows(h, EP(cb), 0); return out
RUN, STOP, SQ, TIMES = {"t0": None, "L2": None}, threading.Event(), queue.Queue(), []
rel = lambda t: round(t - RUN["t0"], 2) if RUN["t0"] else None                  # noqa: E731
class BIH(C.Structure):
    _fields_ = [("biSize", W.DWORD), ("biWidth", W.LONG), ("biHeight", W.LONG), ("biPlanes", W.WORD), ("biBitCount", W.WORD),
                ("biCompression", W.DWORD), ("biSizeImage", W.DWORD), ("biXPelsPerMeter", W.LONG), ("biYPelsPerMeter", W.LONG),
                ("biClrUsed", W.DWORD), ("biClrImportant", W.DWORD)]
def pw_inproc(h, path):
    r = W.RECT(); u32.GetWindowRect(W.HWND(h), C.byref(r)); w, ht = r.right - r.left, r.bottom - r.top
    if w <= 0 or ht <= 0: return {"ok": False, "why": "rect %dx%d" % (w, ht)}                       # noqa: E701
    sdc = u32.GetDC(None); mem = gdi.CreateCompatibleDC(sdc); bmp = gdi.CreateCompatibleBitmap(sdc, w, ht); old = gdi.SelectObject(mem, bmp)
    ok = bool(u32.PrintWindow(VP(h), mem, 2)); gdi.SelectObject(mem, old)
    bi = BIH(40, w, -ht, 1, 32, 0, 0, 0, 0, 0, 0); buf = C.create_string_buffer(w * ht * 4)
    n = gdi.GetDIBits(sdc, bmp, 0, ht, buf, C.byref(bi), 0); gdi.DeleteObject(bmp); gdi.DeleteDC(mem); u32.ReleaseDC(None, sdc)
    from PIL import Image
    im = Image.frombuffer("RGB", (w, ht), buf.raw, "raw", "BGRX", 0, 1); im.save(path)
    cols = im.getcolors(maxcolors=1 << 20)
    return {"ok": ok, "lines": n, "rect": [r.left, r.top, r.right, r.bottom], "distinct_colours": len(cols) if cols else 1 << 20}
def capture(h, tag, t_det):
    base = os.path.join(PW, "c105b_%s_h%d_%s" % (TS, h, tag)); rec = {"hwnd": h, "tag": tag, "t_detect": t_det}
    def a():
        t = time.time(); rec["inproc"] = pw_inproc(h, base + "_pw.png"); rec["inproc"]["secs"] = round(time.time() - t, 2)
        rec["inproc"]["t_done"] = rel(time.time()); rec["inproc"]["png"] = os.path.relpath(base + "_pw.png", ROOT)
    def b():
        t = time.time()
        try:
            p = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "& .\\tools\\lv_gui.ps1 -Action shotwin -Hwnd %d -Out '%s'" % (h, base + "_shotwin.png")],
                               cwd=ROOT, capture_output=True, text=True, timeout=30)
            rec["shotwin"] = {"rc": p.returncode, "out": (p.stdout + p.stderr).strip()[:300]}
        except Exception as e: rec["shotwin"] = {"rc": -1, "out": repr(e)[:300]}                  # noqa: BLE001, E701
        rec["shotwin"]["secs"] = round(time.time() - t, 2); rec["shotwin"]["png"] = os.path.relpath(base + "_shotwin.png", ROOT)
    ta, tb = threading.Thread(target=a, daemon=True), threading.Thread(target=b, daemon=True); ta.start(); tb.start()
    ta.join(5.0); tb.join(35.0); rec["inproc_timed_out"], rec["shotwin_timed_out"] = ta.is_alive(), tb.is_alive()
    F["pw"].append(rec); say("PW", rec); return rec
CAPQ, SEEN = queue.Queue(), {}
def capworker():
    while True:
        it = CAPQ.get()
        if it == "END": return                                                 # noqa: E701
        threading.Thread(target=capture, args=it, daemon=True).start()
def logger():
    prev, pvis, wl = None, None, open(os.path.join(OUT, "windows_%s.jsonl" % TS), "w", encoding="utf-8")
    while not STOP.is_set():
        now = time.time(); w = snap(); r = {"abs": round(now, 2), "t": rel(now), "n": len(w)}
        if w != prev:
            r["new"] = [list(x) + [kids(x[0]) if x[3] else []] for x in w if prev is None or x not in prev]
            r["gone"] = [list(x) for x in (prev or []) if x not in w]; vis = sorted((x[1], x[2]) for x in w if x[3])
            if vis != pvis: r["shot"] = True; SQ.put(r["t"]); say("WINCHANGE", {k: r[k] for k in ("t", "new", "gone")})   # noqa: E701
            for x in w:                                                        # 105-2 addition: enqueue only, never blocks
                if x[2] == "LVDChild" and x[3] and x[0] not in SEEN:
                    SEEN[x[0]] = {"t_visible": r["t"], "abs": r["abs"], "title": x[1]}; CAPQ.put((x[0], "birth", r["t"]))
            prev, pvis = w, vis
        wl.write(json.dumps(r) + "\n"); wl.flush(); TIMES.append(now); time.sleep(max(0.0, 0.25 - (time.time() - now)))
def shooter():
    while True:
        t = SQ.get()
        if t == "END": return                                                  # noqa: E701
        p = os.path.join(SH, "c105b_%s_%s.png" % (TS, ("t%+08.2f" % t) if isinstance(t, float) else ("abs%d" % time.time()) if t is None else t))
        try:
            from PIL import ImageGrab; ImageGrab.grab(all_screens=True).save(p)
        except Exception:                                                      # noqa: BLE001
            subprocess.run(["powershell", "-NoProfile", "-Command", "& .\\tools\\lv_gui.ps1 -Action shot -Out '%s'" % p], cwd=ROOT, capture_output=True, timeout=30)
        F["shots"].append([t, os.path.relpath(p, ROOT), os.path.isfile(p)])
TIMED = {}
def timed():                                                                    # t=5 and t=20 re-captures of every visible LVDChild
    while RUN["t0"] is None: time.sleep(0.05)                                  # noqa: E701
    for T in (5.0, 20.0):
        while time.time() - RUN["t0"] < T: time.sleep(0.05)                    # noqa: E701
        hs = [x[0] for x in snap() if x[2] == "LVDChild" and x[3]][:12]; th = []
        for h in hs:
            t_ = threading.Thread(target=capture, args=(h, "t%02d" % T, rel(time.time())), daemon=True); t_.start(); th.append(t_)
        for t_ in th: t_.join(40.0)                                            # noqa: E701
        TIMED[T] = {"hwnds": hs, "t_done": rel(time.time())}; say("TIMED", {T: TIMED[T]})
def com5(tag):
    k32.CreateFileW.restype = C.c_void_p; h = k32.CreateFileW("\\\\.\\COM5", 0xC0000000, 0, None, 3, 0, None); e = k32.GetLastError()
    ok = h not in (None, C.c_void_p(-1).value)
    if ok: k32.CloseHandle(C.c_void_p(h))                                      # noqa: E701
    r = {"tag": tag, "state": "FREE" if ok else ("BUSY" if e == 5 else "ERR"), "win32_error": 0 if ok else e}; say("COM5", r); return r
for fn in (logger, shooter, capworker, timed): threading.Thread(target=fn, daemon=True).start()
time.sleep(1.0); F["com5_T0"] = com5("T0 before LabVIEW")
SRC = os.path.join(CD, "scratch_c105b_s1_%s.vi" % TS); shutil.copyfile(S1, SRC)
import bench_prep                                                               # noqa: E402
bench_prep.restart_labview()
sys.argv = [sys.argv[0], "--leg", "replay_s1", "--src", SRC, "--picks", "15", "--run-s", "120"]
import drive_m8                                                                 # noqa: E402
drive_m8.HERE = OUT
import drive_original_copy_v5 as v5                                             # noqa: E402
d0, NLEG, GUI0 = v5.d0, [0], v5.d0.GUI_ACTIONS[0]
OUTS = [c["label"] for c in json.load(open(os.path.join(ROOT, "docs", "wiki", "subvi", "D1_s1_copy.json"), encoding="utf-8"))["connector_pane"] if c.get("direction") == "output"]
def read_conf(tag, deadline=40.0):
    res = {"tag": tag}
    def work():
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()
        try:
            app = dynamic.Dispatch("LabVIEW.Application"); vi = app.GetVIReference(CONF, "", False, 0); res["exec_state"] = int(vi.ExecState)
            for n in ("VISA resource name", "VISA resource name out"):
                try: res[n] = vi.GetControlValue(n)
                except Exception as e: res[n] = "ERR %r" % e                   # noqa: BLE001, E701
            vi = app = None
        except Exception as e: res["err"] = repr(e)[:300]                      # noqa: BLE001, E701
    th = threading.Thread(target=work, daemon=True); t = time.time(); th.start(); th.join(deadline)
    res["secs"], res["timed_out"] = round(time.time() - t, 2), th.is_alive(); say("CONF", res); return res
def probe_leg(tag, n, base, cal):
    NLEG[0] += 1
    for c in (v5.C_STOP, v5.C_STOP2, v5.C_DONE):
        try: d0.com.call("set", c, False, timeout=10.0)
        except Exception as e: say("RESET_ERR", repr(e))                      # noqa: BLE001, E701
    rt = d0.RunThread(v5.COPY, "c105b_%s" % tag); RUN["t0"] = time.time(); rt.start(); tl = []
    while True:
        time.sleep(0.5); t = time.time() - RUN["t0"]; ret = (rt.returned - RUN["t0"]) if rt.returned else None
        tl.append([round(t, 1), d0.state(), None if ret is None else round(ret, 1)])
        if (t >= L2_S and (ret is None or t >= ret + 5)) or t >= 60: break    # noqa: E701
    RUN["L2"] = time.time()
    while TIMES[-1] <= RUN["L2"]: time.sleep(0.05)                             # noqa: E701
    gui_l2 = d0.GUI_ACTIONS[0]; SQ.put("L2")
    dl = time.time() + 60
    while 20.0 not in TIMED and time.time() < dl: time.sleep(0.2)              # noqa: E701
    F["timed_before_stop"] = sorted(TIMED); F["t_stop_call"] = rel(time.time())
    F["timeline"], F["t_L2"] = tl, rel(RUN["L2"]); F["dialogs_L2"] = d0.dialogs()
    F["run_thread"] = {"issued_rel": rel(rt.issued) if rt.issued else None, "returned_rel": rel(rt.returned) if rt.returned else None, "err": repr(rt.error) if rt.error else None}
    gaps = [b - a for a, b in zip(TIMES, TIMES[1:]) if RUN["t0"] <= b <= RUN["L2"]]
    F["gaps"] = {"n": len(gaps), "max": round(max(gaps), 3) if gaps else None}
    G["C1a Run->L2 max logger gap <= 0.5 s"] = bool(gaps) and max(gaps) <= 0.5
    G["C1d t=5 and t=20 captures before the stop"] = 5.0 in TIMED and 20.0 in TIMED
    G["C3 no GUI act before L2"] = gui_l2 == GUI0 and d0.GUI_ACTIONS[0] == GUI0
    for k in ("timeline", "t_L2", "dialogs_L2", "run_thread", "gaps", "timed_before_stop", "t_stop_call"): say(k, F[k])  # noqa: E701
    st = d0.state(); F["exec_main_L2"] = st
    if st not in (0, 1, -1): F["stop"] = v5.stop_with_fallback("c105b")        # noqa: E701
    F["exec_main_after_stop"] = d0.state(); ind = {lab: d0.getv(lab, timeout=4.0) for lab in OUTS}
    F["indicators"] = {k: repr(v)[:300] for k, v in ind.items()}
    F["conf_after"] = read_conf("after")
    for k in ("exec_main_L2", "stop", "exec_main_after_stop", "indicators"): say("INFO " + k, F.get(k))  # noqa: E701
    return False                                                               # C4: stop here, no picks
v5.leg = probe_leg
drive_m8.main()
m8 = json.load(open(os.path.join(OUT, "m8_replay_s1_p15_r120.json"))); F["tmx_after"] = m8.get("motor_after")
time.sleep(3); gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
F["com5_T2"] = com5("T2 after LabVIEW gone"); time.sleep(2.0); SQ.put("end"); CAPQ.put("END"); STOP.set(); time.sleep(1.0); SQ.put("END"); time.sleep(3.0)
try: os.remove(SRC)
except OSError as e: say("SRC_DELETE_ERR", repr(e))                              # noqa: E701
F["seen_lvdchild"] = SEEN
after = [h for h, s in SEEN.items() if s["t_visible"] is not None and s["t_visible"] >= 0]
birth = {r["hwnd"]: r for r in F["pw"] if r["tag"] == "birth"}
F["after_run_lvdchild"] = after
G["C1b each post-Run LVDChild captured in-process <= 1 s"] = bool(after) and all(
    h in birth and not birth[h]["inproc_timed_out"] and birth[h].get("inproc", {}).get("ok") and birth[h]["inproc"]["t_done"] - SEEN[h]["t_visible"] <= 1.0 for h in after)
G["C1c each post-Run LVDChild captured by shotwin -Hwnd"] = bool(after) and all(h in birth and birth[h].get("shotwin", {}).get("rc") == 0 for h in after)
G["C4a one leg, no picks"] = NLEG[0] == 1 and not m8.get("picks"); G["C4b LabVIEW gone"] = gone
G["C4c S1 md5 3e3d23ce unchanged"] = md5(S1) == S1_MD5; G["C4d TMX 39 read back"] = F["tmx_after"] == 39.0
G["C4e COM5 T0 and T2 probes"] = F["com5_T0"]["state"] in ("FREE", "BUSY") and F["com5_T2"]["state"] in ("FREE", "BUSY"); F["scratch_deleted"] = not os.path.exists(SRC)
jp = os.path.join(ROOT, "tools", "bench", "facts_c105b_dialog.json"); json.dump({"gates": G, "facts": F}, open(jp, "w"), indent=1, default=str)
for k, v in G.items(): print("GATE %-52s %s" % (k, "PASS" if v else "FAIL"), flush=True)  # noqa: E701
bad = [k for k, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
sys.stdout.flush(); os._exit(1 if bad else 0)
