"""diag_c127_1_tlb - card 127-1 STEP B pre-check, OFFLINE (no LabVIEW launch): does the exported LabVIEW ActiveX typelib's
VirtualInstrument interface carry an Automatic-Error-Handling property? The typelib is resolved from the registry
(LabVIEW.Application -> CLSID -> TypeLib) and loaded with LoadRegTypeLib / LoadTypeLib; LabVIEW.exe holds none (first run).
PREDICTION: unknown (measurement); prints the member list. Prior art: none for an AEH READ (gscript.set_auto_error_handling
writes only, OpSetAutoErr_v0)."""
import os, sys, winreg, pythoncom
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import protocol
def rd(path, name=""):
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, path) as k:
        return winreg.QueryValueEx(k, name)[0]
def keys(path):
    out = []
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, path) as k:
        i = 0
        while True:
            try:
                out.append(winreg.EnumKey(k, i)); i += 1
            except OSError:
                return out
files = []
for tlid in keys("TypeLib"):           # "LabVIEW 8.0 Type Library" (kb_com.py:11) - found by description, not by CLSID
    try:
        vers = keys(r"TypeLib\%s" % tlid)
    except OSError:
        continue
    for ver in vers:
        try:
            desc = rd(r"TypeLib\%s\%s" % (tlid, ver))
        except OSError:
            continue
        if "labview" not in str(desc).lower():
            continue
        print("TYPELIB", tlid, ver, desc)
        for arch in ("win64", "win32"):
            try:
                files.append((ver, arch, rd(r"TypeLib\%s\%s\0\%s" % (tlid, ver, arch))))
            except OSError:
                pass
print("FILES", files)
hit, nf = [], 0
for ver, arch, p in files:
    try:
        tl = pythoncom.LoadTypeLib(p)
    except Exception as e:
        print("FAIL", p, e); continue
    for i in range(tl.GetTypeInfoCount()):
        name = tl.GetDocumentation(i)[0]
        if "VirtualInstrument" not in name:
            continue
        ti = tl.GetTypeInfo(i); ta = ti.GetTypeAttr()
        names = set(ti.GetNames(ti.GetFuncDesc(f).memid)[0] for f in range(ta.cFuncs))
        nf += len(names)
        print(ver, arch, name, len(names), sorted(names))
        hit += [(ver, name, n) for n in sorted(names) if "err" in n.lower()]
print("ERR-LIKE MEMBERS", hit)
print(protocol.result_line({"status": "PASS" if nf else "FAIL", "gates": {"pass": int(bool(nf)), "fail": int(not nf)},
                            "first_fail": None if nf else "no VirtualInstrument interface read", "artefacts": []}))
