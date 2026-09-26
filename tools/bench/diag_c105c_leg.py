r"""diag_c105c_leg.py - card 105-3 C3/C3b/C4: ONE leg A of a scratch byte copy of claudeDev\D1_s1_copy.vi on the 105-2
path (diag_c105b_leg.py md5 355eb180: same EnumWindows logger every 0.25 s, same drive_m8 replay_s1 -> v5 route, same
stop_with_fallback end, forced kill allowed), with its PrintWindow captures removed and a PROBER added: once the first
LVDChild made visible after Run is seen (the 105-1/105-2 error dialog, visible at t=0.41 s), at +2 s and +10 s:
  (a) COM5 exclusive CreateFile + CloseHandle, no bytes (the com5() of diag_c105b_leg.py:129-133) -> FREE/BUSY/ERR + win32 error,
  (b) a full-screen shot and the LabVIEW/#32770 window list at that instant,
  (c) Win32_Process with command lines + CreationDate (the query of diag_c104f_leg.py:22-27, name filter widened).
No handle-enumeration tool exists on this PC (no handle.exe / handle64.exe on PATH or under tools/) -> C3b holders = NOT MEASURED.
The stop starts only after the +10 probe is written. A second leg() call from v5 (drive_original_copy_v5.py:564-565, review
c105b-leg-rc1) is SUPPRESSED here: it returns False without running anything. MEASURE ONLY; no fix, no dismiss/click/key/focus.
PREDICTION CONTRACT: P1 dialog LVDChild seen after Run <= 5 s  P2 COM5 probe at +2 and +10 s recorded (FREE/BUSY/ERR)
 P3 process lists at +2 and +10 s recorded  P4 dialog still visible at both probes  C3 no GUI act before the +10 probe
 C4a one real leg, no picks  C4b LabVIEW gone  C4c S1 md5 3e3d23ce unchanged  C4d TMX 39 read back  C4e COM5 T0/T2 recorded
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c105c_leg.log -- py -u tools/bench/diag_c105c_leg.py"""
import ctypes as C, ctypes.wintypes as W, hashlib, json, os, queue, shutil, subprocess, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
S1 = os.path.join(CD, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
OUT = os.path.join(HERE, "diag_c105_out", "c105c"); os.makedirs(OUT, exist_ok=True)
TS = time.strftime("%Y%m%d_%H%M%S"); F, G = {"shots": [], "probes": {}}, {}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                   # noqa: E731
def say(k, v): print("[c105c] %s %s" % (k, json.dumps(v, default=str)[:2500]), flush=True)
u32, k32 = C.windll.user32, C.windll.kernel32; k32.OpenProcess.restype = W.HANDLE; PN = {}; EP = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
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
        if pname(pid.value) == "labview.exe" or c == "#32770":
            r = W.RECT(); u32.GetWindowRect(h, C.byref(r)); out.append((int(h), wtxt(h), c, bool(u32.IsWindowVisible(h)), (r.left, r.top, r.right, r.bottom)))
        return True
    u32.EnumWindows(EP(cb), 0); return out
RUN, STOP, SQ, TIMES, DLG, PDONE = {"t0": None}, threading.Event(), queue.Queue(), [], {}, threading.Event()
rel = lambda t: round(t - RUN["t0"], 2) if RUN["t0"] else None                  # noqa: E731
def logger():
    prev, wl = None, open(os.path.join(OUT, "windows_%s.jsonl" % TS), "w", encoding="utf-8")
    while not STOP.is_set():
        now = time.time(); w = snap(); r = {"abs": round(now, 2), "t": rel(now), "n": len(w)}
        if w != prev:
            r["new"] = [list(x) for x in w if prev is None or x not in prev]; r["gone"] = [list(x) for x in (prev or []) if x not in w]
            say("WINCHANGE", {k: r[k] for k in ("t", "new", "gone")}); prev = w
            for x in w:
                if RUN["t0"] and x[2] == "LVDChild" and x[3] and "t" not in DLG and x[0] not in PRE:
                    DLG.update(hwnd=x[0], t=r["t"], abs=now, rect=x[4]); say("DIALOG", DLG)
        wl.write(json.dumps(r) + "\n"); wl.flush(); TIMES.append(now); time.sleep(max(0.0, 0.25 - (time.time() - now)))
PRE = set()
def shot(tag):
    p = os.path.join(OUT, "c105c_%s_%s.png" % (TS, tag))
    try:
        from PIL import ImageGrab; ImageGrab.grab(all_screens=True).save(p); F["shots"].append([tag, os.path.relpath(p, ROOT)])
    except Exception as e: F["shots"].append([tag, "ERR %r" % e])              # noqa: BLE001, E701
def com5(tag):
    k32.CreateFileW.restype = C.c_void_p; h = k32.CreateFileW("\\\\.\\COM5", 0xC0000000, 0, None, 3, 0, None); e = k32.GetLastError()
    ok = h not in (None, C.c_void_p(-1).value)
    if ok: k32.CloseHandle(C.c_void_p(h))                                      # noqa: E701
    r = {"tag": tag, "t": rel(time.time()), "state": "FREE" if ok else ("BUSY" if e == 5 else "ERR"), "win32_error": 0 if ok else e}; say("COM5", r); return r
def procs():
    ps = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|py|pythonw|powershell|pwsh|LabVIEW|NI.*|ni.*|visa.*|.*serial.*|.*com[0-9].*|lv.*)' } "
          "| Select-Object Name,ProcessId,ParentProcessId,@{n='Created';e={$_.CreationDate.ToString('yyyy-MM-dd HH:mm:ss')}},CommandLine | ConvertTo-Json -Compress")
    try:
        o = json.loads(subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60).stdout or "[]")
        return [dict(x, CommandLine=(x.get("CommandLine") or "")[:300]) for x in (o if isinstance(o, list) else [o])]
    except Exception as e: return "ERR %r" % e                                 # noqa: BLE001, E701
def prober():
    while RUN["t0"] is None: time.sleep(0.05)                                  # noqa: E701
    while "t" not in DLG and time.time() - RUN["t0"] < 30: time.sleep(0.05)    # noqa: E701
    if "t" not in DLG: F["probes"]["none"] = "no LVDChild within 30 s"; PDONE.set(); return   # noqa: E701
    for dt in (2.0, 10.0):
        while time.time() < DLG["abs"] + dt: time.sleep(0.02)                  # noqa: E701
        tag = "p%02d" % dt; rec = {"gui_actions": d0.GUI_ACTIONS[0], "com5": com5(tag)}
        rec["windows"] = [list(x) for x in snap()]; rec["dialog_visible"] = any(x[0] == DLG["hwnd"] and x[3] for x in snap())
        th = threading.Thread(target=lambda: rec.__setitem__("procs", procs()), daemon=True); th.start(); shot(tag); th.join(70)
        F["probes"][tag] = rec; say("PROBE", rec)
    PDONE.set()
time.sleep(0.5); F["com5_T0"] = com5("T0 before LabVIEW")
SRC = os.path.join(CD, "scratch_c105c_s1_%s.vi" % TS); shutil.copyfile(S1, SRC)
import bench_prep                                                               # noqa: E402
bench_prep.restart_labview()
sys.argv = [sys.argv[0], "--leg", "replay_s1", "--src", SRC, "--picks", "15", "--run-s", "120"]
import drive_m8                                                                 # noqa: E402
drive_m8.HERE = OUT
import drive_original_copy_v5 as v5                                             # noqa: E402
d0, NLEG, GUI0 = v5.d0, [0, 0], v5.d0.GUI_ACTIONS[0]
for fn in (logger, prober): threading.Thread(target=fn, daemon=True).start()   # noqa: E701
def probe_leg(tag, n, base, cal):
    if NLEG[0] >= 1: NLEG[1] += 1; say("SECOND_LEG_SUPPRESSED", tag); return False   # noqa: E701, E702
    NLEG[0] += 1; time.sleep(0.6); PRE.update(x[0] for x in snap() if x[2] == "LVDChild" and x[3])
    for c in (v5.C_STOP, v5.C_STOP2, v5.C_DONE):
        try: d0.com.call("set", c, False, timeout=10.0)
        except Exception as e: say("RESET_ERR", repr(e))                      # noqa: BLE001, E701
    rt = d0.RunThread(v5.COPY, "c105c_%s" % tag); RUN["t0"] = time.time(); rt.start(); tl = []
    while not PDONE.is_set() and time.time() - RUN["t0"] < 90:
        time.sleep(0.5); tl.append([rel(time.time()), d0.state()])
    F["gui_at_probe_end"] = d0.GUI_ACTIONS[0]; F["t_L2"] = rel(time.time()); F["timeline"] = tl; F["dialogs_L2"] = d0.dialogs(); shot("L2")
    F["run_thread"] = {"returned_rel": rel(rt.returned) if rt.returned else None, "err": repr(rt.error) if rt.error else None}
    F["dialog"] = dict(DLG); F["pre_lvdchild"] = sorted(PRE)
    for k in ("dialog", "timeline", "t_L2", "dialogs_L2", "run_thread"): say(k, F[k])   # noqa: E701
    st = d0.state(); F["exec_main_L2"] = st
    if st not in (0, 1, -1): F["stop"] = v5.stop_with_fallback("c105c")        # noqa: E701
    F["exec_main_after_stop"] = d0.state(); say("INFO stop", [st, F.get("stop"), F["exec_main_after_stop"]]); return False
v5.leg = probe_leg
drive_m8.main()
m8 = json.load(open(os.path.join(OUT, "m8_replay_s1_p15_r120.json"))); F["tmx_after"] = m8.get("motor_after")
time.sleep(3); gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
F["com5_T2"] = com5("T2 after LabVIEW gone"); STOP.set(); time.sleep(0.5)
try: os.remove(SRC)
except OSError as e: say("SRC_DELETE_ERR", repr(e))                              # noqa: E701
pr = F["probes"]; G["P1 dialog LVDChild seen after Run <= 5 s"] = DLG.get("t") is not None and DLG["t"] <= 5.0
G["P2 COM5 probe at +2 and +10 s"] = all(pr.get(t, {}).get("com5", {}).get("state") in ("FREE", "BUSY", "ERR") for t in ("p02", "p10"))
G["P3 process lists at +2 and +10 s"] = all(isinstance(pr.get(t, {}).get("procs"), list) for t in ("p02", "p10"))
G["P4 dialog still visible at both probes"] = all(pr.get(t, {}).get("dialog_visible") for t in ("p02", "p10"))
G["C3 no GUI act before the +10 probe"] = F.get("gui_at_probe_end") == GUI0 and all(pr.get(t, {}).get("gui_actions") == GUI0 for t in ("p02", "p10"))
G["C4a one real leg, no picks"] = NLEG[0] == 1 and not m8.get("picks"); G["C4b LabVIEW gone"] = gone
G["C4c S1 md5 3e3d23ce unchanged"] = md5(S1) == S1_MD5; G["C4d TMX 39 read back"] = F["tmx_after"] == 39.0
G["C4e COM5 T0/T2 recorded"] = all(F[k]["state"] in ("FREE", "BUSY", "ERR") for k in ("com5_T0", "com5_T2")); F["suppressed_legs"] = NLEG[1]
jp = os.path.join(HERE, "facts_c105c_com5.json"); json.dump({"gates": G, "facts": F}, open(jp, "w"), indent=1, default=str)
for k, v in G.items(): print("GATE %-46s %s" % (k, "PASS" if v else "FAIL"), flush=True)  # noqa: E701
bad = [k for k, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
sys.stdout.flush(); os._exit(1 if bad else 0)
