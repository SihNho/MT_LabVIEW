r"""diag_c104_rotorport.py - card 104-5: the cheap separator named by review archive/peer/2026-09-27-c104-5-configure-popup.md:63-67.
READS ONLY (no LabVIEW, no VISA open, no write to any VI): (1) LastWriteTime/size/md5/saved-version bytes of the Autonics rotor
instr.lib Configure.vi, Close.vi, SetCommand.vi; (2) Get-PnpDevice -Class Ports (is an FTDI/USB serial COM5 present and OK).
PREDICTION CONTRACT: G1 Configure.vi stat read  G2 PnP port list read. Numbers only; which hypothesis they favour is judgement's.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c104_rotorport.log -- py -u tools/bench/diag_c104_rotorport.py
"""
import hashlib, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor"
G, facts = {}, {}
for n in ("Configure.vi", "Close.vi", "SetCommand.vi"):
    p = os.path.join(LIB, n)
    try:
        b = open(p, "rb").read(); st = os.stat(p)
        i = b.find(b"\x00\x80\x00"); ver = b[i - 1:i + 3].hex() if i > 0 else None
        facts[n] = {"mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)), "size": st.st_size, "md5": hashlib.md5(b).hexdigest(), "ver_bytes_first": ver}
    except Exception as e:                                                     # noqa: BLE001
        facts[n] = {"err": repr(e)}
    print("FILE %s %s" % (n, json.dumps(facts[n])), flush=True)
G["G1 Configure.vi stat read"] = "mtime" in facts.get("Configure.vi", {})
ps = "Get-PnpDevice -Class Ports | Select-Object Status,FriendlyName,InstanceId | ConvertTo-Json -Compress"
try:
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60).stdout
    ports = json.loads(out) if out.strip() else []; ports = ports if isinstance(ports, list) else [ports]
except Exception as e:                                                         # noqa: BLE001
    ports = [{"err": repr(e)}]
for x in ports: print("PORT %s" % json.dumps(x), flush=True)
G["G2 PnP port list read"] = bool(ports) and "err" not in ports[0]
facts["com5"] = [x for x in ports if "(COM5)" in str(x.get("FriendlyName"))]
print("COM5 %s" % json.dumps(facts["com5"]), flush=True)
jp = os.path.join(HERE, "diag_c104_rotorport.json"); json.dump({"facts": facts, "ports": ports, "gates": G}, open(jp, "w"), indent=1)
for k, v in G.items(): print("GATE %-40s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": hashlib.md5(open(jp, "rb").read()).hexdigest()}])), flush=True)
sys.exit(1 if bad else 0)
