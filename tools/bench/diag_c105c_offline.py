r"""diag_c105c_offline.py - card 105-3 C1 + C2, OFFLINE (no LabVIEW, no port opened, no byte to any COM port).
Existing pieces reused: the Win32_Process query of diag_c104f_leg.py:22-27 (not needed here), motor_gate.PORTS
(tools/motor_gate.py:59-61) and visaconf.ini [ALIASES]/[ASRL-RSRC-ALIAS]. No COM-port inventory tool existed in tools/
(grep for list_ports / SERIALCOMM / Get-PnpDevice: none), so this file is the inventory.
C1: every COM port present now, from 4 read-only sources: pyserial list_ports (registry/SetupAPI read, no open),
    HKLM\HARDWARE\DEVICEMAP\SERIALCOMM (live device -> COMn map), Get-PnpDevice -Class Ports incl. non-present,
    COM Name Arbiter ComDB bitmask; joined with visaconf aliases and motor_gate PORTS.
C2: System-log PnP events (Kernel-PnP, UserPnp, DriverFrameworks-UserMode) + the Kernel-PnP/Configuration log,
    2026-09-26 12:00 -> now, time + id + provider + message head; serial/USB-looking ones flagged.
PREDICTION CONTRACT: O1 list_ports ran (>=1 port) O2 SERIALCOMM read O3 PnP Ports list read O4 visaconf parsed
(7 aliases, Rotor -> ASRL5 -> COM5) O5 motor_gate PORTS rotor == COM5 O6 event query ran (count may be 0).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c105c_offline.log -- py -u tools/bench/diag_c105c_offline.py"""
import configparser, hashlib, json, os, re, subprocess, sys, winreg
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
OUTJ = os.path.join(HERE, "facts_c105c_offline.json"); F, G = {}, {}
def say(k, v): print("[c105c-off] %s %s" % (k, json.dumps(v, default=str, ensure_ascii=False)[:3000]), flush=True)
def ps(cmd, t=120):
    p = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=t, encoding="utf-8", errors="replace")
    return json.loads(p.stdout) if p.stdout.strip() else [], p.stderr.strip()[:400]
# C1a pyserial
try:
    from serial.tools import list_ports
    F["list_ports"] = [{"device": p.device, "description": p.description, "hwid": p.hwid, "vid": p.vid, "pid": p.pid,
                        "serial_number": p.serial_number, "location": p.location, "manufacturer": p.manufacturer} for p in list_ports.comports()]
except Exception as e:                                                         # noqa: BLE001  run 1: pyserial not installed
    F["list_ports_pyserial"] = "ERR %r" % e; o, _ = ps("@(Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match '\\(COM\\d+\\)' } | ForEach-Object { "
        "[pscustomobject]@{device=([regex]::Match($_.Name,'COM\\d+').Value);description=$_.Name;hwid=$_.PNPDeviceID;manufacturer=$_.Manufacturer;status=$_.Status;"
        "location=(Get-PnpDeviceProperty -InstanceId $_.PNPDeviceID -KeyName DEVPKEY_Device_LocationInfo -ErrorAction SilentlyContinue).Data} }) | ConvertTo-Json -Compress")
    F["list_ports"] = o if isinstance(o, list) else [o]
say("list_ports", F["list_ports"]); G["O1 port list (pyserial or Win32_PnPEntity) has COM5"] = isinstance(F["list_ports"], list) and any(p.get("device") == "COM5" for p in F["list_ports"] if isinstance(p, dict))
# C1b SERIALCOMM
try:
    k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM"); i, sc = 0, {}
    while True:
        try: n, v, _ = winreg.EnumValue(k, i); sc[n] = v; i += 1
        except OSError: break                                                  # noqa: E701
    F["serialcomm"] = sc
except OSError as e: F["serialcomm"] = "ERR %r" % e                             # noqa: E701
say("serialcomm", F["serialcomm"]); G["O2 SERIALCOMM read"] = isinstance(F["serialcomm"], dict)
# C1c PnP Ports (present and ghost) with the port name from the device registry
F["pnp_ports"], err = ps("@(Get-PnpDevice -Class Ports | ForEach-Object { $pn=(Get-ItemProperty ('HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\'+$_.InstanceId+'\\Device Parameters') -ErrorAction SilentlyContinue).PortName; "
                         "$la=(Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LastArrivalDate -ErrorAction SilentlyContinue).Data; "
                         "$lr=(Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_LastRemovalDate -ErrorAction SilentlyContinue).Data; "
                         "[pscustomobject]@{FriendlyName=$_.FriendlyName;InstanceId=$_.InstanceId;Status=\"$($_.Status)\";Present=$_.Present;PortName=$pn;Manufacturer=$_.Manufacturer;"
                         "LastArrival=$(if($la){$la.ToString('yyyy-MM-dd HH:mm:ss')});LastRemoval=$(if($lr){$lr.ToString('yyyy-MM-dd HH:mm:ss')})} }) | ConvertTo-Json -Compress")
F["pnp_ports"] = F["pnp_ports"] if isinstance(F["pnp_ports"], list) else [F["pnp_ports"]]; F["pnp_err"] = err
say("pnp_ports", F["pnp_ports"]); G["O3 PnP Ports list read"] = bool(F["pnp_ports"])
try:
    k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\COM Name Arbiter"); db = winreg.QueryValueEx(k, "ComDB")[0]
    F["comdb_reserved"] = ["COM%d" % (b * 8 + j + 1) for b, x in enumerate(db) for j in range(8) if x >> j & 1]
except OSError as e: F["comdb_reserved"] = "ERR %r" % e                         # noqa: E701
say("comdb_reserved", F["comdb_reserved"])
# visaconf + motor_gate
VC = r"C:\ProgramData\National Instruments\NIvisa\visaconf.ini"; cp = configparser.ConfigParser(); cp.optionxform = str; cp.read(VC)
al = {m.group(1): m.group(2) for v in cp["ALIASES"].values() for m in [re.match(r"\"'([^']*)','([^']*)'\"", v)] if m}
asrl = {cp["ASRL-RSRC-ALIAS"]["Name%d" % i].strip('"'): {"system": cp["ASRL-RSRC-ALIAS"]["SystemName%d" % i].strip('"'), "baud": cp["ASRL-RSRC-ALIAS"]["BaudRate%d" % i],
        "enabled": cp["ASRL-RSRC-ALIAS"]["Enabled%d" % i]} for i in range(int(cp["ASRL-RSRC-ALIAS"]["NumOfResources"]))}
F["visaconf"] = {"md5": hashlib.md5(open(VC, "rb").read()).hexdigest(), "aliases": al, "asrl": asrl}; say("visaconf", F["visaconf"])
G["O4 visaconf parsed, Rotor -> ASRL5 -> COM5"] = len(al) == 7 and al.get("Rotor") == "ASRL5::INSTR" and asrl.get("ASRL5::INSTR", {}).get("system") == "COM5"
src = open(os.path.join(ROOT, "tools", "motor_gate.py"), encoding="utf-8").read(); m = re.search(r"PORTS = \{.*?\}\s*\n(?=\S)", src, re.S)
F["motor_gate_ports"] = m.group(0).strip() if m else None; say("motor_gate_ports", F["motor_gate_ports"])
G["O5 motor_gate PORTS rotor == COM5"] = bool(m) and '"rotor": ("COM5"' in m.group(0)
# join table
present = {p["device"]: p for p in F["list_ports"]} if isinstance(F["list_ports"], list) else {}
F["join"] = [{"com": c, "present_now": c in present, "desc": present.get(c, {}).get("description"), "hwid": present.get(c, {}).get("hwid"),
              "serialcomm_dev": [d for d, v in (F["serialcomm"] if isinstance(F["serialcomm"], dict) else {}).items() if v == c],
              "pnp": [(x.get("FriendlyName"), x.get("Status"), x.get("Present"), x.get("InstanceId")) for x in F["pnp_ports"] if x.get("PortName") == c],
              "visa": [r for r, a in asrl.items() if a["system"] == c], "alias": [a for a, r in al.items() if asrl.get(r, {}).get("system") == c]}
             for c in sorted(set(present) | {a["system"] for a in asrl.values()} | {x.get("PortName") for x in F["pnp_ports"] if x.get("PortName")}, key=lambda s: int(re.sub(r"\D", "", s) or 0))]
for j in F["join"]: say("JOIN", j)                                               # noqa: E701
# C2 events
# run 2 (review archive/peer/2026-09-27-c105c-offline-o1.md): one query PER source, errors NOT silenced, classified
SRCS = [("System", "Microsoft-Windows-Kernel-PnP"), ("System", "Microsoft-Windows-UserPnp"), ("System", "Microsoft-Windows-DriverFrameworks-UserMode"),
        ("Microsoft-Windows-Kernel-PnP/Configuration", None), ("System", None)]
F["events"], F["event_sources"] = [], []
for lg, pv in SRCS:
    flt = "LogName='%s';StartTime=$s%s" % (lg, (";ProviderName='%s'" % pv) if pv else "")
    q = ("$s=[datetime]'2026-09-26 12:00'; & { try { $e=@(Get-WinEvent -FilterHashtable @{%s} -ErrorAction Stop); "
         "@{err='';ev=@($e | Sort-Object TimeCreated | ForEach-Object { $m=(($_.Message -replace '\\s+',' ')+''); [pscustomobject]@{t=$_.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss');"
         "log=$_.LogName;prov=$_.ProviderName;id=$_.Id;lvl=$_.LevelDisplayName;msg=$m.Substring(0,[Math]::Min(260,$m.Length))} })} } "
         "catch { @{err=$_.Exception.Message;ev=@()} } } | ConvertTo-Json -Depth 4 -Compress") % flt
    try: r, se = ps(q, 180)
    except Exception as e: r, se = {"err": "PYERR %r" % e, "ev": []}, ""     # noqa: BLE001, E701
    r = r if isinstance(r, dict) else {"err": "no JSON; stderr " + se, "ev": []}; ev = [x for x in (r.get("ev") or []) if x]
    cls = "events" if ev else ("no-events" if "No events were found" in (r.get("err") or "") else ("no-events" if not r.get("err") else "ERROR"))
    rec = {"log": lg, "provider": pv, "n": len(ev), "class": cls, "err": (r.get("err") or "")[:300]}; F["event_sources"].append(rec); say("EVSRC", rec)
    if pv or lg != "System": F["events"] += ev                                  # noqa: E701  the unfiltered System count is the liveness control only
G["O6 every event source classified (events|no-events|ERROR)"] = len(F["event_sources"]) == len(SRCS)
G["O7 unfiltered System log non-empty since start (query live)"] = F["event_sources"][-1]["n"] > 0
SER = re.compile(r"USB|VID_|COM\d|Serial|FTDI|Prolific|CH34|Silicon Lab|CP210|Ports|ASRL", re.I)
F["events_serialish"] = [x for x in F["events"] if SER.search(json.dumps(x))]
say("events_n", {"all": len(F["events"]), "serialish": len(F["events_serialish"])})
for x in F["events_serialish"][:80]: say("EV", x)                                # noqa: E701
json.dump({"gates": G, "facts": F}, open(OUTJ, "w", encoding="utf-8"), indent=1, default=str, ensure_ascii=False)
for k_, v in G.items(): print("GATE %-46s %s" % (k_, "PASS" if v else "FAIL"), flush=True)   # noqa: E701
bad = [k_ for k_, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None,
      [{"path": os.path.relpath(OUTJ, ROOT), "md5": hashlib.md5(open(OUTJ, "rb").read()).hexdigest()}])), flush=True)
sys.exit(1 if bad else 0)
