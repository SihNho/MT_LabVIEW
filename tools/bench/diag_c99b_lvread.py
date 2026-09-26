r"""diag_c99b_lvread.py - card 99-2 F1 type/dims + F5 default: READ-ONLY COM reads on a unique scratch BYTE COPY of
D1_s1_copy.vi (claudeDev\scratch_c99b_read_<ts>.vi, deleted by close()). Nothing is run, nothing is saved.
Template: diag_c99_lvread.py (99-1, 12/0). Existing calls only: vi_ref GetControlValue; OpConstValueN_v1 via the reader
body of tools/recipes/build_opcreateconstonterm_v0.py:392-419 (copied, not imported: that module imports a build chain).
Offline prior (diag_c99b_files.log): ring = Initialize Array #8953 element <- const #8972, dims (x-1 #9179, const #8984,
'# FD points'); IndexArray #8741 rows <- consts #8775/#8795; TurnOff #24444 indicator; BooleanConstant #25261 -> #8603 Value.
PREDICTION CONTRACT: R1 #8972 reads (value + Representation); R2 #8984 reads a positive integer; R3 #8775/#8795 read;
R4 'TurnOff' GetControlValue returns a bool; input md5 unchanged; nothing saved; no VI run; LabVIEW gone at exit (Z).
"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K
g = K.g

S1 = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
CONSTN_LABELS = os.path.join(HERE, "opconstvaluen_v1_labels.json")
s = K.Stage(S1, S1_MD5, "diag_c99b_lvread", work_name="scratch_c99b_read_%s.vi" % time.strftime("%Y%m%d_%H%M%S"),
            deadline_min=15, reserve_s=120, task="99-2", out_json=os.path.join(HERE, "diag_c99b_lvread.json"))


def read_const(target, uid):
    lab = json.load(open(CONSTN_LABELS, encoding="utf-8"))
    for cls in ("DigitalNumericConstant", "Constant", "BooleanConstant"):
        order = [o["uid"] for o in g.report_all(target, cls)]
        if uid not in order:
            continue
        vi = g.op(os.path.join(g.CLAUDEDEV, "OpConstValueN_v1.vi"))
        for k in ("text", "hex"):
            vi.SetControlValue(lab[k], "POISON")
        vi.SetControlValue(lab["u8"], []); vi.SetControlValue(lab["wire"], -1); vi.SetControlValue("UID", 0)
        vi.SetControlValue(lab["size"], False); vi.SetControlValue("vi path", target)
        vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", order.index(uid))
        err = ""
        try:
            g._run(vi); err = g._err(vi, "error out") or ""
        except Exception as e:                                                      # noqa: BLE001
            err = "EXC %s" % str(e)[:90]
        return dict(cls=cls, uid_back=int(vi.GetControlValue("UID")), text=vi.GetControlValue(lab["text"]),
                    repr=vi.GetControlValue(lab["repr"]), wire=int(vi.GetControlValue(lab["wire"])), err=err)
    return dict(cls=None, err="uid not among DigitalNumericConstant/Constant/BooleanConstant")


def body(_):
    s.start(); s.scratches.append(s.work)
    bp = K.mod("bench_prep"); h0 = bp.labview_handles(); s.fact("HANDLES before reads: %r" % h0)
    got = {}
    for u in (8972, 8984, 8775, 8795, 25261):
        r, err = s.safe("read_const(#%d)" % u, lambda u=u: read_const(s.work, u))
        got[u] = r if r else {"err": err}
        s.fact("CONST #%d -> %r" % (u, got[u]))
    s.R["consts"] = got
    s.gate("R1 #8972 (ring element) read with a Representation", bool(got[8972]) and got[8972].get("repr") not in (None, "") and not got[8972].get("err"), repr(got[8972]))
    t = str((got[8984] or {}).get("text", ""))
    s.gate("R2 #8984 (ring dim 1) reads a positive integer", t.strip().isdigit() and int(t) > 0, t)
    s.gate("R3 #8775/#8795 (row indices) read", all(not (got[u] or {}).get("err") for u in (8775, 8795)), repr([got[8775], got[8795]]))

    def rd():
        with g.vi_ref(s.work) as vi:
            return vi.GetControlValue("TurnOff")
    v, err = s.safe("GetControlValue('TurnOff')", rd)
    s.R["turnoff_saved_value"] = {"value": v, "type": type(v).__name__, "err": err}
    s.fact("TurnOff saved (load-time) value %r type %s err %r" % (v, type(v).__name__, err))
    s.gate("R4 'TurnOff' reads as a bool", isinstance(v, bool) and not err, repr(v))
    h1 = bp.labview_handles(); s.fact("HANDLES after reads: %r" % h1); s.R["handles"] = [h0, h1]


rc = K.run(body, s)
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
               capture_output=True)
time.sleep(4)
gone = "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True).stdout
s.gate("Z LabVIEW gone after the run", gone); s.dump(); rc = s.summary()
sys.exit(rc)
