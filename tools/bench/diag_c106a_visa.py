r"""diag_c105d_visa.py - card 105-4: NI-VISA viOpen separator WITHOUT LabVIEW (open/close only, no byte, no attribute set).
Existing pieces: diag_c105c_offline.py (inventory, visaconf parse), diag_c105c_leg.py (CreateFileW probe inside the LabVIEW
leg). No stand-alone VISA open probe existed in tools/ (grep viOpen / pyvisa: none), so this file is the probe. ctypes on
NI's visa64.dll/visa32.dll (the NI backend itself); pyvisa presence is only recorded.
P0  LabVIEW.exe absent before and after; process list for port clients by name (NIMax, putty, ttermpro, python cmdlines w/ COM|visa).
V1  viOpenDefaultRM, then viOpen('Rotor') and viOpen('ASRL5::INSTR') x3 each, viClose each: status + viStatusDesc.
V2  two sessions to ASRL5::INSTR in ONE process (open A, open B, close both): status of B.
V3  CreateFileW(COM5) open+close, then viOpen ASRL5 after 0/100/1000 ms; reverse: viOpen held -> CreateFileW probe (GetLastError);
    calibration: COM5 held by CreateFileW in a CHILD process -> viOpen ASRL5 from this process.
V4  V1 on 'COM6' and 'ASRL6::INSTR' (other FTDI) as control.
PREDICTION CONTRACT (measurement completeness only; the values are the facts, not gates): every trial above records an integer
status; P0 LabVIEW count 0 before and after.
    MATERIAL=1 py tools/bgrun.py --max-min 8 --log tools/bench/diag_c105d_visa.log -- py -u tools/bench/diag_c105d_visa.py"""
import ctypes, hashlib, importlib.util, json, os, subprocess, sys, time
from ctypes import wintypes as W
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
OUTJ = os.path.join(HERE, "facts_c106a_visa.json"); F, G = {"py_bits": ctypes.sizeof(ctypes.c_void_p) * 8}, {}
def say(k, v): print("[c105d] %s %s" % (k, json.dumps(v, default=str, ensure_ascii=False)[:2500]), flush=True)
def procs():
    cmd = ("@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'LabVIEW|NIMax|putty|ttermpro|realterm|python|lvrt|nimxs' } | "
           "ForEach-Object { [pscustomobject]@{name=$_.Name;pid=$_.ProcessId;start=\"$($_.CreationDate)\";cmd=(\"$($_.CommandLine)\").Substring(0,[Math]::Min(220,(\"$($_.CommandLine)\").Length))} }) | ConvertTo-Json -Compress")
    o = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace").stdout
    o = json.loads(o) if o.strip() else []; return o if isinstance(o, list) else [o]
F["procs_before"] = procs(); say("procs_before", F["procs_before"])
G["P0a LabVIEW absent before"] = not any("labview" in p["name"].lower() for p in F["procs_before"])
F["pyvisa_installed"] = importlib.util.find_spec("pyvisa") is not None
# ---- VISA via ctypes
V = None
for n in ("visa64.dll", "visa32.dll"):
    try: V = ctypes.WinDLL(n); F["visa_dll"] = n; break                         # noqa: E702
    except OSError as e: F.setdefault("visa_dll_err", []).append("%s %r" % (n, e))  # noqa: E701
say("env", {k: F.get(k) for k in ("py_bits", "pyvisa_installed", "visa_dll", "visa_dll_err")})
VI = ctypes.c_uint32; RM = VI()
st = V.viOpenDefaultRM(ctypes.byref(RM)); F["rm_status"] = st; say("viOpenDefaultRM", st)
def desc(s):
    b = ctypes.create_string_buffer(256); V.viStatusDesc(RM, ctypes.c_int32(s), b); return b.value.decode("latin-1")
def vopen(name, tmo=2000):
    v = VI(); t0 = time.perf_counter(); s = V.viOpen(RM, name.encode(), 0, tmo, ctypes.byref(v))
    return {"name": name, "status": s, "hex": "0x%08X" % (s & 0xFFFFFFFF), "text": desc(s), "ms": round((time.perf_counter() - t0) * 1e3, 1)}, v
def vclose(v):
    return V.viClose(v) if v.value else None
K = ctypes.WinDLL("kernel32", use_last_error=True)
K.CreateFileW.restype = W.HANDLE; K.CreateFileW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, W.LPVOID, W.DWORD, W.DWORD, W.HANDLE]
K.CloseHandle.argtypes = [W.HANDLE]; INV = W.HANDLE(-1).value
def cf_open(port):
    h = K.CreateFileW("\\\\.\\" + port, 0xC0000000, 0, None, 3, 0, None); e = ctypes.get_last_error()
    return (h if h not in (None, INV) else None), (0 if h not in (None, INV) else e)
def v1(names, tag):
    out = []
    for nm in names:
        for i in range(3):
            r, v = vopen(nm); r["close"] = vclose(v); r["i"] = i; out.append(r); say(tag, r); time.sleep(0.2)
    F[tag] = out; G["%s every trial has a status" % tag] = len(out) == 3 * len(names) and all(isinstance(x["status"], int) for x in out)
if st == 0:
    v1(["Rotor", "ASRL5::INSTR"], "V1")
    # V2 two sessions, one process
    a, va = vopen("ASRL5::INSTR"); b, vb = vopen("ASRL5::INSTR"); F["V2"] = {"A": a, "B": b, "closeB": vclose(vb), "closeA": vclose(va)}
    say("V2", F["V2"]); G["V2 status of B recorded"] = isinstance(b["status"], int); time.sleep(0.2)
    # V3 CreateFileW open+close then viOpen after d ms
    F["V3_fwd"] = []
    for d in (0, 100, 1000):
        h, e = cf_open("COM5"); c = K.CloseHandle(h) if h else None; time.sleep(d / 1000.0)
        r, v = vopen("ASRL5::INSTR"); r["close"] = vclose(v); rec = {"delay_ms": d, "cf_err": e, "cf_closed": c, "visa": r}
        F["V3_fwd"].append(rec); say("V3_fwd", rec); time.sleep(0.2)
    # reverse: VISA session held, CreateFileW probe
    r, v = vopen("ASRL5::INSTR"); h, e = cf_open("COM5"); c = K.CloseHandle(h) if h else None
    F["V3_rev"] = {"visa": r, "cf_err_while_visa_held": e, "cf_got_handle": bool(h), "cf_closed": c, "visa_close": vclose(v)}; say("V3_rev", F["V3_rev"])
    # calibration: COM5 held by CreateFileW in a child process
    child = ("import ctypes,sys,time;from ctypes import wintypes as W;K=ctypes.WinDLL('kernel32',use_last_error=True);"
             "K.CreateFileW.restype=W.HANDLE;K.CreateFileW.argtypes=[W.LPCWSTR,W.DWORD,W.DWORD,W.LPVOID,W.DWORD,W.DWORD,W.HANDLE];"
             "h=K.CreateFileW('\\\\\\\\.\\\\COM5',0xC0000000,0,None,3,0,None);e=ctypes.get_last_error();"
             "print('HOLD',h not in (None,W.HANDLE(-1).value),e,flush=True);time.sleep(4);print('CLOSE',K.CloseHandle(h),flush=True)")
    ch = subprocess.Popen([sys.executable, "-u", "-c", child], stdout=subprocess.PIPE, text=True)
    hold = ch.stdout.readline().strip(); time.sleep(0.3); r, v = vopen("ASRL5::INSTR"); r["close"] = vclose(v)
    rest = ch.communicate(timeout=20)[0].strip(); F["V3_cal"] = {"child_hold": hold, "visa_while_child_holds": r, "child_end": rest, "child_rc": ch.returncode}
    say("V3_cal", F["V3_cal"]); time.sleep(0.3)
    G["V3 fwd x3 + rev + calibration recorded"] = len(F["V3_fwd"]) == 3 and isinstance(F["V3_rev"]["visa"]["status"], int) \
        and hold.startswith("HOLD") and isinstance(r["status"], int)
    v1(["COM6", "ASRL6::INSTR"], "V4")
    F["rm_close"] = V.viClose(RM)
else:
    G["VISA RM opened"] = False
F["procs_after"] = procs(); say("procs_after", F["procs_after"])
G["P0b LabVIEW absent after"] = not any("labview" in p["name"].lower() for p in F["procs_after"])
json.dump({"gates": G, "facts": F}, open(OUTJ, "w", encoding="utf-8"), indent=1, default=str, ensure_ascii=False)
for k_, v_ in G.items(): print("GATE %-40s %s" % (k_, "PASS" if v_ else "FAIL"), flush=True)   # noqa: E701
bad = [k_ for k_, v_ in G.items() if not v_]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None,
      [{"path": os.path.relpath(OUTJ, ROOT), "md5": hashlib.md5(open(OUTJ, "rb").read()).hexdigest()}])), flush=True)
sys.exit(1 if bad else 0)
