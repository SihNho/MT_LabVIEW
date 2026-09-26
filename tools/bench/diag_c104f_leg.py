r"""diag_c104f_leg.py - card 104-6: ONE leg A (claudeDev\D1_s1_copy.vi) to the v5 L2 point only, with reads. MEASURE ONLY.
FOUND FIRST: diag_c104_leg.py (drive_m8 replay_s1 -> v5; restart via bench_prep), drive_original_copy_v5.py:268-305 (leg L1/L2,
copied here minus the picks), v2 PollCom/RunThread/windows()/dialogs() (reused), motor_gate.py:59-61 (PORTS), visaconf.ini.
Configure.vi 'error out' is read in a SEPARATE COM apartment (own thread, joined with a deadline), the main VI through v2's PollCom.
COM5 probe = CreateFileW(\\.\COM5, exclusive) then CloseHandle: NO byte written; taken before LabVIEW, after the VI opened (before
Run) and after LabVIEW is gone - never while the VI runs. Picks, done, bandpass, save: NOT done. The leg returns False after L2, the
v5 cleanup stops the VI (if still running), closes LabVIEW, re-reads TMX. No VI is saved or edited (drive_m8 byte copy, deleted).
PREDICTION CONTRACT (reads recorded; which hypothesis they favour is judgement's):
 P1 processes listed  P2 COM5 probe T0 recorded  P3 alias 'Rotor' read  P4 motor start log port lines read
 L1 VI left idle  L2 capture taken at the L2 point  R1 main ExecState read  R2 window list read  R3 Configure.vi error out read (no ERR)
 E1 LabVIEW gone  E2 S1 md5 3e3d23ce unchanged  E3 TMX 39 read back
    MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/diag_c104f_leg.log -- py -u tools/bench/diag_c104f_leg.py"""
import ctypes as C, hashlib, json, os, re, subprocess, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
S1 = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s1_copy.vi"; S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
CONF = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor\Configure.vi"
F, G = {}, {}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                   # noqa: E731
def say(k, v): print("[c104f] %s %s" % (k, json.dumps(v, default=str)[:1500]), flush=True)
def procs():
    ps = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python|py|pythonw|powershell|pwsh|LabVIEW|NI.*|ni.*|visa.*)' } "
          "| Select-Object Name,ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Compress")
    try:
        o = json.loads(subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=90).stdout or "[]")
        return [dict(x, CommandLine=(x.get("CommandLine") or "")[:260]) for x in (o if isinstance(o, list) else [o])]
    except Exception as e:                                                     # noqa: BLE001
        return [{"err": repr(e)}]
def com5(tag):
    k = C.windll.kernel32; k.CreateFileW.restype = C.c_void_p
    h = k.CreateFileW("\\\\.\\COM5", 0xC0000000, 0, None, 3, 0, None); err = k.GetLastError()
    r = {"tag": tag, "t": time.strftime("%H:%M:%S")}
    if h in (None, C.c_void_p(-1).value, 0xFFFFFFFFFFFFFFFF): r.update(state="BUSY" if err == 5 else "ERR", win32_error=err)
    else: k.CloseHandle(C.c_void_p(h)); r.update(state="FREE", win32_error=0)
    F.setdefault("com5", []).append(r); say("COM5", r); return r
# ---------------- before LabVIEW ----------------
F["procs_T0"] = procs(); say("PROCS_T0", F["procs_T0"]); G["P1 processes listed"] = bool(F["procs_T0"]) and "err" not in F["procs_T0"][0]
G["P2 COM5 probe T0 recorded"] = com5("T0 before LabVIEW")["state"] in ("FREE", "BUSY")
ini = r"C:\ProgramData\National Instruments\NIvisa\visaconf.ini"; L = open(ini, errors="replace").read().splitlines()
F["alias"] = ["%s:%d %s" % (ini, i + 1, s) for i, s in enumerate(L) if "Rotor" in s or "ASRL5" in s or 'SystemName2' in s or "BaudRate2" in s]
say("ALIAS", F["alias"]); G["P3 alias 'Rotor' read"] = any("'Rotor'" in a for a in F["alias"])
ml = os.path.join(HERE, "motor_session_start_cycle104.log"); ML = open(ml, errors="replace").read().splitlines()
F["motor_log_port_lines"] = ["%s:%d %s" % (os.path.basename(ml), i + 1, s) for i, s in enumerate(ML) if re.search(r"COM\d|ASRL|[Rr]otor", s)]
F["motor_log_lines"] = len(ML); say("MOTORLOG", F["motor_log_port_lines"]); G["P4 motor start log read"] = len(ML) > 0
F["s1_md5_before"] = md5(S1)
import bench_prep                                                               # noqa: E402
bench_prep.restart_labview()
sys.argv = [sys.argv[0], "--leg", "replay_s1", "--src", S1, "--picks", "15", "--run-s", "120"]
import drive_m8                                                                 # noqa: E402
import drive_original_copy_v5 as v5                                             # noqa: E402
d0, L5 = v5.d0, {}
def read_conf(tag, deadline=40.0):
    res = {"tag": tag}
    def work():
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()
        try:
            app = dynamic.Dispatch("LabVIEW.Application"); vi = app.GetVIReference(CONF, "", False, 0)
            res["exec_state"] = int(vi.ExecState)
            for n in ("error out", "VISA resource name", "VISA resource name out"):
                try: res[n] = vi.GetControlValue(n)
                except Exception as e: res[n] = "ERR %r" % e                   # noqa: BLE001, E701
            vi = app = None
        except Exception as e:                                                 # noqa: BLE001
            res["err"] = repr(e)[:300]
    th = threading.Thread(target=work, daemon=True); t = time.time(); th.start(); th.join(deadline)
    res["secs"] = round(time.time() - t, 2); res["timed_out"] = th.is_alive(); say("CONF", res); return res
def probe_leg(tag, n, base, cal):
    com5("T1 VI opened, before Run")
    for c in (v5.C_STOP, v5.C_STOP2, v5.C_DONE):
        try: d0.com.call("set", c, False, timeout=10.0)
        except Exception as e: say("RESET_ERR", repr(e))                      # noqa: BLE001, E701
    rt = d0.RunThread(v5.COPY, "c104f_%s" % tag); rt.start(); t0 = time.time(); left = False; tl = []
    while time.time() - t0 < v5.RUN_SETTLE:
        time.sleep(2.0); st = d0.state()
        tl.append({"t": round(time.time() - t0, 1), "exec": st, "conf_wins": [w for w in d0.windows().splitlines() if "onfigure" in w]})
        say("L1POLL", tl[-1])
        if st not in (1, -1): left = True; break
    L5["timeline"] = tl; G["L1 VI left idle"] = left
    d0.focus(d0.COPY_TITLE); time.sleep(1.5)
    L5["t_L2"] = round(time.time() - t0, 1); L5["shot_L2"] = v5.capture("c104f_%s_L2" % tag)
    L5["exec_main_L2"] = d0.state(); L5["windows_L2"] = d0.windows(); L5["dialogs_L2"] = d0.dialogs()
    L5["conf_L2"] = read_conf("L2"); L5["exec_main_after_conf"] = d0.state(); L5["shot_L2b"] = v5.capture("c104f_%s_L2b" % tag)
    L5["run_thread"] = {"returned": rt.returned is not None, "err": repr(rt.error) if rt.error else None,
                        "run_secs": round(rt.returned - rt.issued, 1) if rt.returned and rt.issued else None}
    for k in ("t_L2", "exec_main_L2", "windows_L2", "dialogs_L2", "exec_main_after_conf", "run_thread", "shot_L2", "shot_L2b"): say(k, L5[k])
    G["L2 capture taken at the L2 point"] = bool(L5["shot_L2"]); G["R1 main ExecState read"] = L5["exec_main_L2"] != -1
    G["R2 window list read"] = bool(L5["windows_L2"]) and L5["windows_L2"] != "GUI_TIMEOUT"
    eo = L5["conf_L2"].get("error out"); G["R3 Configure.vi error out read (no ERR)"] = isinstance(eo, (tuple, list))
    return False                                                               # stop here: no picks
v5.leg = probe_leg
ok = drive_m8.main()
m8 = json.load(open(os.path.join(HERE, "m8_replay_s1_p15_r120.json")))
F["tmx_after"] = m8.get("motor_after"); F["m8_gates"] = m8.get("gates"); F["v5_failing"] = m8.get("v5_failing_steps")
time.sleep(3); gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
com5("T2 after LabVIEW gone"); F["procs_T2"] = procs(); F["s1_md5_after"] = md5(S1); F["leg"] = L5
G["E1 LabVIEW gone"] = gone; G["E2 S1 md5 unchanged"] = F["s1_md5_before"] == F["s1_md5_after"] == S1_MD5; G["E3 TMX 39 read back"] = F["tmx_after"] == 39.0
jp = os.path.join(HERE, "facts_c104f_rotor.json"); json.dump({"gates": G, "facts": F}, open(jp, "w"), indent=1, default=str)
for k, v in G.items(): print("GATE %-46s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": md5(jp)}])), flush=True)
sys.stdout.flush(); os._exit(1 if bad else 0)
