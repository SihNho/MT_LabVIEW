r"""diag_c105_leg.py - card 105-1 C2-C5: ONE leg A of a scratch byte copy of claudeDev\D1_s1_copy.vi, Run -> L2 with a
Win32 window log every 0.25 s, NO GUI act at all, then the stop, reads, LabVIEW exit. MEASURE ONLY.
FOUND FIRST: diag_c104f_leg.py (drive_m8 replay_s1 -> v5, probe_leg override, read_conf in its own apartment, COM5
probe), drive_original_copy_v5.py:268-305/589-668 (leg, cleanup = stop_with_fallback, G92 exit, TMX re-read), v2
windows()/dialogs() (lv_gui, ~1 s per call: too slow for 0.5 s, so the logger here is ctypes EnumWindows, reads only).
The logger starts BEFORE LabVIEW is restarted. L2 = 20 s after Run (or Run-return + 5 s, cap 60 s). c104f's pre-L2
d0.focus is DROPPED: nothing clicks, keys or focuses. After L2: VI stopped by v5.stop_with_fallback if still running,
then C3 reads. drive_m8 outputs go under tools/bench/diag_c105_out (drive_m8.HERE retargeted). ONE leg (drive_m8 runs
only the first; probe_leg returns False). The run copy is scratch_c105_s1_<ts>_run_<ts>.vi (drive_m8 deletes it).
PREDICTION CONTRACT (reads recorded; which hypothesis they favour is judgement's):
 P1 COM5 T0 probe  L1 Run issued  C2 Run->L2 max sample gap <= 0.5 s  C2b no GUI act before L2  C2c L2 sample logged
 C3a main ExecState read after stop  C3b >=1 error/string indicator read  C3c Configure.vi resource read  C4 one leg,
 no picks  C5a LabVIEW gone  C5b S1 md5 3e3d23ce unchanged  C5c TMX 39 read back  C5d COM5 T2 probe
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c105_leg.log -- py -u tools/bench/diag_c105_leg.py"""
import ctypes as C, ctypes.wintypes as W, hashlib, json, os, queue, shutil, subprocess, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
S1 = os.path.join(CD, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
CONF = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor\Configure.vi"
OUT = os.path.join(HERE, "diag_c105_out"); SH = os.path.join(OUT, "shots"); os.makedirs(SH, exist_ok=True)
TS = time.strftime("%Y%m%d_%H%M%S"); F, G = {"shots": []}, {}; L2_S = 20.0
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                   # noqa: E731
def say(k, v): print("[c105] %s %s" % (k, json.dumps(v, default=str)[:1800]), flush=True)
u32, k32 = C.windll.user32, C.windll.kernel32; k32.OpenProcess.restype = W.HANDLE; PN = {}
EP = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
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
def logger():
    prev, pvis, wl = None, None, open(os.path.join(OUT, "windows_%s.jsonl" % TS), "w", encoding="utf-8")
    while not STOP.is_set():
        now = time.time(); w = snap(); r = {"abs": round(now, 2), "t": rel(now), "n": len(w)}
        if w != prev:
            r["new"] = [list(x) + [kids(x[0]) if x[3] else []] for x in w if prev is None or x not in prev]
            r["gone"] = [list(x) for x in (prev or []) if x not in w]; vis = sorted((x[1], x[2]) for x in w if x[3])
            if vis != pvis: r["shot"] = True; SQ.put(r["t"]); say("WINCHANGE", {k: r[k] for k in ("t", "new", "gone")})   # noqa: E701
            prev, pvis = w, vis
        wl.write(json.dumps(r) + "\n"); wl.flush(); TIMES.append(now); time.sleep(max(0.0, 0.25 - (time.time() - now)))
def shooter():
    while True:
        t = SQ.get()
        if t == "END": return                                                  # noqa: E701
        p = os.path.join(SH, "c105_%s_%s.png" % (TS, ("t%+08.2f" % t) if isinstance(t, float) else ("abs%d" % time.time()) if t is None else t))
        try:
            from PIL import ImageGrab; ImageGrab.grab(all_screens=True).save(p)
        except Exception:                                                      # noqa: BLE001
            subprocess.run(["powershell", "-NoProfile", "-Command", "& .\\tools\\lv_gui.ps1 -Action shot -Out '%s'" % p], cwd=ROOT, capture_output=True, timeout=30)
        F["shots"].append([t, os.path.relpath(p, ROOT), os.path.isfile(p)])
def com5(tag):
    k32.CreateFileW.restype = C.c_void_p; h = k32.CreateFileW("\\\\.\\COM5", 0xC0000000, 0, None, 3, 0, None); e = k32.GetLastError()
    ok = h not in (None, C.c_void_p(-1).value)
    if ok: k32.CloseHandle(C.c_void_p(h))                                      # noqa: E701
    r = {"tag": tag, "state": "FREE" if ok else ("BUSY" if e == 5 else "ERR"), "win32_error": 0 if ok else e}; say("COM5", r); return r
for fn in (logger, shooter): threading.Thread(target=fn, daemon=True).start()
time.sleep(1.0); F["com5_T0"] = com5("T0 before LabVIEW"); G["P1 COM5 T0 probe"] = F["com5_T0"]["state"] in ("FREE", "BUSY")
SRC = os.path.join(CD, "scratch_c105_s1_%s.vi" % TS); shutil.copyfile(S1, SRC)
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
    rt = d0.RunThread(v5.COPY, "c105_%s" % tag); RUN["t0"] = time.time(); rt.start(); tl = []
    while True:
        time.sleep(0.5); t = time.time() - RUN["t0"]; ret = (rt.returned - RUN["t0"]) if rt.returned else None
        tl.append([round(t, 1), d0.state(), None if ret is None else round(ret, 1)])
        if (t >= L2_S and (ret is None or t >= ret + 5)) or t >= 60: break    # noqa: E701
    RUN["L2"] = time.time()
    while TIMES[-1] <= RUN["L2"]: time.sleep(0.05)                             # noqa: E701
    gui_l2 = d0.GUI_ACTIONS[0]; SQ.put("L2")
    F["timeline"], F["t_L2"] = tl, rel(RUN["L2"]); F["dialogs_L2"] = d0.dialogs()
    F["run_thread"] = {"issued_rel": rel(rt.issued) if rt.issued else None, "returned_rel": rel(rt.returned) if rt.returned else None, "err": repr(rt.error) if rt.error else None}
    gaps = [b - a for a, b in zip(TIMES, TIMES[1:]) if RUN["t0"] <= b <= RUN["L2"]]
    F["gaps"] = {"n": len(gaps), "max": round(max(gaps), 3) if gaps else None}
    G["L1 Run issued"] = rt.issued is not None; G["C2 Run->L2 max sample gap <= 0.5 s"] = bool(gaps) and max(gaps) <= 0.5
    G["C2b no GUI act before L2"] = gui_l2 == GUI0; G["C2c L2 sample logged"] = TIMES[-1] > RUN["L2"]
    for k in ("timeline", "t_L2", "dialogs_L2", "run_thread", "gaps"): say(k, F[k])  # noqa: E701
    st = d0.state(); F["exec_main_L2"] = st
    if st not in (0, 1, -1): F["stop"] = v5.stop_with_fallback("c105")         # noqa: E701
    F["exec_main_after_stop"] = d0.state(); ind = {lab: d0.getv(lab, timeout=4.0) for lab in OUTS}
    F["indicators"] = {k: repr(v)[:300] for k, v in ind.items()}
    F["error_ind"] = {k: v for k, v in ind.items() if isinstance(v, (list, tuple)) and len(v) == 3 and isinstance(v[2], str)}
    F["string_ind"] = {k: v for k, v in ind.items() if isinstance(v, str) and not v.startswith("ERR:")}
    F["conf_after"] = read_conf("after")
    for k in ("exec_main_L2", "stop", "exec_main_after_stop", "error_ind", "string_ind"): say(k, F.get(k))  # noqa: E701
    G["C3a main ExecState read after stop"] = F["exec_main_after_stop"] != -1; G["C3b >=1 error/string indicator read"] = bool(F["error_ind"] or F["string_ind"])
    G["C3c Configure.vi resource read"] = "VISA resource name" in F["conf_after"] and not str(F["conf_after"]["VISA resource name"]).startswith("ERR")
    return False                                                               # C4: stop here, no picks
v5.leg = probe_leg
drive_m8.main()
m8 = json.load(open(os.path.join(OUT, "m8_replay_s1_p15_r120.json"))); F["tmx_after"] = m8.get("motor_after"); F["v5_failing"] = m8.get("v5_failing_steps")
time.sleep(3); gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
F["com5_T2"] = com5("T2 after LabVIEW gone"); SQ.put("end"); STOP.set(); time.sleep(1.0); SQ.put("END"); time.sleep(3.0)
try: os.remove(SRC)
except OSError as e: say("SRC_DELETE_ERR", repr(e))                              # noqa: E701
G["C4 one leg, no picks"] = NLEG[0] == 1 and not m8.get("picks"); G["C5a LabVIEW gone"] = gone
G["C5b S1 md5 3e3d23ce unchanged"] = md5(S1) == S1_MD5; G["C5c TMX 39 read back"] = F["tmx_after"] == 39.0
G["C5d COM5 T2 probe"] = F["com5_T2"]["state"] in ("FREE", "BUSY"); F["scratch_deleted"] = not os.path.exists(SRC)
jp = os.path.join(ROOT, "tools", "bench", "facts_c105_rotor.json"); json.dump({"gates": G, "facts": F}, open(jp, "w"), indent=1, default=str)
for k, v in G.items(): print("GATE %-46s %s" % (k, "PASS" if v else "FAIL"), flush=True)  # noqa: E701
bad = [k for k, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
sys.stdout.flush(); os._exit(1 if bad else 0)
