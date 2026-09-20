"""clfn_sample.py - OpCLFNPre_v0 (set the wizard's functional globals) then OpCLFNBuild_v0 on a scratch VI, SAME process
(the FGV VIs stay loaded through g.op).  Library GPU Tracking.dll / mt2_track_simple / C / reentrant.  'binary string' empty
=> the Parameter Info Set stage is skipped and 'data string' / 'data string 2' both show the FRESH node's flattened
Parameter Info (layout sample); 'Prototype' and 'Terms[]' are read back.  Pass --flat <hexfile> to set parameters."""
import os, shutil, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
OP = os.path.join(g.CLAUDEDEV, "OpCLFNBuild_v0.vi"); PRE = os.path.join(g.CLAUDEDEV, "OpCLFNPre_v0.vi"); TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_clfn.vi")
DLL = os.path.join(g.CLAUDEDEV, "Debug", "GPU Tracking.dll"); FN = "mt2_track_simple"
if "--dll" in sys.argv: DLL = sys.argv[sys.argv.index("--dll") + 1]
if "--fn" in sys.argv: FN = sys.argv[sys.argv.index("--fn") + 1]
print("DLL", DLL, "FN", FN, flush=True)
flat_hex = None
if "--flat" in sys.argv:
    flat_hex = open(sys.argv[sys.argv.index("--flat") + 1]).read().strip()
if os.path.exists(TGT):
    os.remove(TGT)
shutil.copyfile(os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi"), TGT); g.report(TGT, "SubVI"); g.open_panel(TGT); time.sleep(0.8)
# 0. Parameter Info global from flattened bytes (--params <hexfile>): OpCLFNParams_v0, BEFORE Create.vi (empty array = crash)
if "--params" in sys.argv:
    labs = json.load(open(os.path.join(HERE, "opclfnparams_labels.json")))
    hexs = open(sys.argv[sys.argv.index("--params") + 1]).read().strip()
    pv = g.op(os.path.join(g.CLAUDEDEV, "OpCLFNParams_v0.vi"))
    pv.SetControlValue(labs["binary string"], bytes.fromhex(hexs).decode("latin-1")); pv.SetControlValue(labs["operation"], 1)
    try:
        g._run(pv); print("params op ran (Parameter Info global SET,", len(hexs) // 2, "bytes)", flush=True)
    except Exception as e:
        print("params op:", str(e)[:200], flush=True)
    for name in (labs["error out"], labs["data string"]):
        try:
            v = pv.GetControlValue(name)
            if isinstance(v, str) and name == labs["data string"]:
                v = v.encode("latin-1").hex()
            print(f"   params {name} = {repr(v)[:300]}", flush=True)
        except Exception as e:
            print("   params", name, "EXC", str(e)[:100], flush=True)
    # read back: run again in Get mode -> data string must equal what we sent
    pv.SetControlValue(labs["operation"], 0); pv.SetControlValue(labs["binary string"], "")
    try:
        g._run(pv); rb = pv.GetControlValue(labs["data string"]).encode("latin-1").hex()
        print("   read-back equal:", rb == hexs, "(", len(rb) // 2, "bytes )", flush=True)
    except Exception as e:
        print("   read-back:", str(e)[:120], flush=True)
# 1. functional globals (labels from the pre-op build)
table = json.load(open(os.path.join(HERE, "opclfnpre_labels.json")))
pre = g.op(PRE)


def setc(vi, label, value):
    try:
        vi.SetControlValue(label, value); return True
    except Exception as e:
        print(f"   set {label!r}: {str(e)[:80]}", flush=True); return False


SET = sys.argv[sys.argv.index("--set") + 1].split(",") if "--set" in sys.argv else ["Function Name", "Path", "Calling Convention", "Reentrant"]
for vi_name, labs in table.items():
    ops = [l for l in labs if l.lower().startswith("operation")]; vals = [l for l in labs if not l.lower().startswith("operation")]
    do_set = any(vi_name.startswith(n) for n in SET)
    for l in ops:
        setc(pre, l, 1 if do_set else 0)                                    # Set only the requested globals; the rest stay Get (untouched)
    print(f"   {vi_name}: {'SET' if do_set else 'get'}", flush=True)
    for l in vals:
        low = l.lower()
        if "function name" in low: setc(pre, l, FN)
        elif low.startswith("path"): setc(pre, l, DLL)
        elif "calling" in low: setc(pre, l, 0)
        elif "reentrant" in low: setc(pre, l, True)
        elif low.startswith("string"): setc(pre, l, f"int32_t {FN}(void);")
        else: print("   (left default)", vi_name, l, flush=True)
try:
    g._run(pre); print("pre-op ran (FGVs set)", flush=True)
except Exception as e:
    print("pre-op:", str(e)[:200], flush=True)
# 2. builder
vi = g.op(OP)
vi.SetControlValue("vi path", TGT); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0); vi.SetControlValue("location (0, 0)", [600, 300])
vi.SetControlValue("path", DLL); vi.SetControlValue("function name", FN); vi.SetControlValue("calling convention", 0); vi.SetControlValue("reentrant", True)
for lab in ("operation", "operation 2", "operation 3", "operation 4", "operation 5"):
    vi.SetControlValue(lab, 1)
vi.SetControlValue("binary string", bytes.fromhex(flat_hex).decode("latin-1") if flat_hex else "")
t0 = time.time()
try:
    g._run(vi)
except Exception as e:
    print("run:", str(e)[:200], flush=True)
print(f"run {time.time() - t0:.1f} s", flush=True)
for name in ("error out", "error out 2", "Prototype", "Terms[]", "data string", "data string 2"):
    try:
        v = vi.GetControlValue(name)
        if isinstance(v, (bytes, bytearray, memoryview)):
            v = bytes(v).hex()
        elif isinstance(v, str) and name.startswith("data string"):
            v = v.encode("latin-1").hex()
        print(f"{name} = {repr(v)[:6000]}", flush=True)
    except Exception as e:
        print(name, "EXC", str(e)[:120], flush=True)
try:
    print("target now: CallLibrary", g.count(TGT, "CallLibrary"), "nodes", g.count(TGT, "Node"), "ExecState", g.exec_state(TGT), flush=True)
except Exception as e:
    print("target read failed (LabVIEW gone?):", str(e)[:100], flush=True)
