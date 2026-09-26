r"""diag_c105_const.py - card 105-1 C1: READ-ONLY value of VISAResourceNameConstant #30488 (S1's rotor Configure.vi
call #30064 'VISA resource name') on a unique scratch BYTE COPY of D1_s1_copy.vi (claudeDev\scratch_c105_read_<ts>.vi,
deleted by close()). Nothing is run, nothing is saved.
FOUND FIRST: diag_c99b_lvread.py (template, 13/0), diag_constvalue_siblings.py (OpConstValue_v1 byte route; void
variant = 20-byte hex 26008000 00000001 0004 0000 0001 00000000), toolkit-capabilities.md:62-63 (OpConstValue_v1 =
base-Constant cast, strings only measured; OpConstValueN_v1 = DigitalNumericConstant-typed). No VISA-typed reader
exists; C1b (scratch positive/negative) is triggered only if every VISA constant reads VOID here.
Extra read (same instance, no run): instr.lib Autonics Configure.vi 'VISA resource name' load-time value (default).
PREDICTION CONTRACT: R1 report_all('VISAResourceNameConstant') lists #30488 (7 in wiki D1_s1_copy.json);
R2 OpConstValue_v1 on #30488 returns uid 30488 (identity) and no op error; R3 the 7 VISA constants are read;
R4 Configure.vi default read; input md5 unchanged; nothing saved; no VI run; LabVIEW gone at exit (Z).
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c105_const.log -- py -u tools/bench/diag_c105_const.py
"""
import json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K
g = K.g

S1 = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
OP = os.path.join(g.CLAUDEDEV, "OpConstValue_v1.vi")
LAB = json.load(open(os.path.join(HERE, "opconstvalue_labels.json"), encoding="utf-8"))
CONF = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor\Configure.vi"
VOID_HEX = "2600800000000001000400000001000000000000"
s = K.Stage(S1, S1_MD5, "diag_c105_const", work_name="scratch_c105_read_%s.vi" % time.strftime("%Y%m%d_%H%M%S"),
            deadline_min=12, reserve_s=120, task="105-1", out_json=os.path.join(HERE, "diag_c105_const.json"))


def u8(v):
    if v is None or isinstance(v, str):
        return b""
    try:
        return bytes(v)
    except (TypeError, ValueError):
        return bytes(int(x) & 0xFF for x in v)


def read_const(target, cls, index):
    vi = g.op(OP)
    vi.SetControlValue(LAB["hex"], "POISON"); vi.SetControlValue("UID", 0); vi.SetControlValue(LAB["size"], False)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", index)
    err = ""
    try:
        g._run(vi); err = g._err(vi, "error out") or ""
    except Exception as e:                                                          # noqa: BLE001
        err = "EXC %s" % str(e)[:90]
    b = u8(vi.GetControlValue(LAB["u8"])); hx = vi.GetControlValue(LAB["hex"])
    td = b[10:12].hex() if len(b) >= 12 else None
    asc = re.findall(rb"[\x20-\x7e]{3,}", b)
    return dict(uid_back=int(vi.GetControlValue("UID")), hex=str(hx)[:400], nbytes=len(b), td_code=td,
                void=(str(hx).lower() == VOID_HEX), ascii=[a.decode() for a in asc], err=str(err)[:200])


def body(_):
    s.start(); s.scratches.append(s.work)
    bp = K.mod("bench_prep"); h0 = bp.labview_handles(); s.fact("HANDLES before reads: %r" % h0)
    objs, err = s.safe("report_all VISAResourceNameConstant", lambda: g.report_all(s.work, "VISAResourceNameConstant"))
    uids = [o["uid"] for o in (objs or [])]
    s.fact("VISA constants (report_all order): %r err %r" % (uids, err)); s.R["visa_uids"] = uids
    s.gate("R1 #30488 listed among VISAResourceNameConstant", 30488 in uids, repr(uids))
    got = {}
    for i, u in enumerate(uids):
        r, e = s.safe("read_const(#%d)" % u, lambda i=i: read_const(s.work, "VISAResourceNameConstant", i))
        got[u] = r if r else {"err": e}
        s.fact("CONST #%d [VISAResourceNameConstant %d] -> %s" % (u, i, json.dumps(got[u])))
    r30 = got.get(30488) or {}
    s.gate("R2 #30488 read with identity and no op error", r30.get("uid_back") == 30488 and not r30.get("err"), repr(r30)[:300])
    s.gate("R3 all VISA constants read", len(got) == len(uids) and all(not v.get("err") for v in got.values()), "%d" % len(got))
    base, e = s.safe("report_all Constant", lambda: g.report_all(s.work, "Constant"))
    bu = [o["uid"] for o in (base or [])]
    if 30488 in bu:
        rb, e2 = s.safe("read_const(#30488 as Constant)", lambda: read_const(s.work, "Constant", bu.index(30488)))
        s.fact("CONST #30488 [Constant %d] -> %s" % (bu.index(30488), json.dumps(rb if rb else {"err": e2})))
        s.R["as_constant"] = rb
    else:
        s.fact("#30488 not in report_all('Constant') (%d objects, err %r)" % (len(bu), e))
    s.R["consts"] = got
    s.R["verdict_void_all"] = bool(got) and all(v.get("void") for v in got.values())
    s.fact("ALL VISA constants VOID (C1b trigger): %r" % s.R["verdict_void_all"])

    def rd():
        with g.vi_ref(CONF) as vi:
            return int(vi.ExecState), vi.GetControlValue("VISA resource name")
    v, e = s.safe("Configure.vi load-time 'VISA resource name'", rd)
    s.R["configure_default"] = {"value": v, "err": e}; s.fact("Configure.vi (ExecState, 'VISA resource name') at load: %r err %r" % (v, e))
    s.gate("R4 Configure.vi default read", v is not None and not e, repr(v))
    h1 = bp.labview_handles(); s.fact("HANDLES after reads: %r" % h1); s.R["handles"] = [h0, h1]


rc = K.run(body, s)
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
               capture_output=True)
time.sleep(4)
gone = "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True).stdout
s.gate("Z LabVIEW gone after the run", gone); s.gate("Z2 S1 md5 unchanged", K.md5(S1) == S1_MD5); s.dump(); rc = s.summary()
sys.exit(rc)
