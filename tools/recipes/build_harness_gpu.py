"""build_harness_gpu.py - HARNESS_gpu.vi: the GPU kernel (CUDA DLL through the Call Library Function Node copied from the
Saleh-lab demo, GPU_kernel_base.vi) driven like HARNESS_seq/par: HARNESS_loadcal + IMAQ Create/ReadFile + make both cosine
bandpass + Omars IMAQ ImageToArray -> CLFN.  Parameter assignment = tools/gpu/cuda/mt_track.cu GPUTracking_lv:
  X Array = 'x,y,z array' DBL[3nb] in/out | Y Array = 'pos in cal image' I32[nb] in/out | Array of Images = U8 2D
  Y Output = win_h | Test Array = win_rs | Z Output = Bead good in/out | Array Cal Cluster | Bead Is Good Array | Error Message
The CLFN's parameters are 'Adapt to Type': a terminal takes the type of what is wired, so the DBL control for X Array is
made by wiring the loader's DBL 'x,y,(blankz) array' first, deleting that wire, then Create Control (adapt trick). Zero GUI.
  py tools/bgrun.py --max-min 20 --log tools/bench/build_harness_gpu.log -- py -u tools/recipes/build_harness_gpu.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

VIS = r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision"
BG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs"
BASE = os.path.join(g.CLAUDEDEV, "GPU_kernel_base.vi")
OP = os.path.join(g.CLAUDEDEV, "HARNESS_gpu.vi")
L_VI = os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")
C_VI = os.path.join(VIS, "Basics.llb", "IMAQ Create"); R_VI = os.path.join(VIS, "Files.llb", "IMAQ ReadFile")
W_VI = os.path.join(BG, "make both cosine bandpass.vi"); I2A_VI = os.path.join(BG, "Omars IMAQ ImageToArray.vi")
g._run.__defaults__ = (6.0, 60.0)
T = {"X Array": 16, "Y Array": 18, "Cross Size": 20, "Array of Images": 24, "Y Output": 28, "Z Output": 30, "Array Cal Cluster": 32,
     "Bead Is Good Array": 34, "Error Message": 36, "Test Array": 38}          # CLFN input terminal indices (extract_clfn4)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def sub_index(uid):
    return [o["uid"] for o in g.report(OP, "SubVI")].index(uid)


def drop(path, pos):
    before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, 0, pos)
    new = [o for o in g.report(OP, "SubVI") if o["uid"] not in before]
    assert len(new) == 1, f"drop {os.path.basename(path)}: {len(new)} new SubVIs"
    return new[0]["uid"]


def clfn_wire_at(t):
    """wire uid at CLFN (Nodes[0]) terminal t, via OpNetInfo (its junk Invoke is purged by the caller at the end)."""
    vi = g.op(g.OP_NET_INFO)
    vi.SetControlValue("vi path", OP); vi.SetControlValue("Class Name", "Diagram"); vi.SetControlValue("index", 0)
    vi.SetControlValue("error in (no error)", (False, 0, "")); vi.SetControlValue("error in", (True, 1, "x"))
    vi.SetControlValue("Class Name 3", ""); vi.SetControlValue("Class Name 2", ""); vi.SetControlValue("index 2", 0); vi.SetControlValue("index 3", t)
    g._run(vi); return int(vi.GetControlValue("UID 2"))


def unwire(t, what):
    w = clfn_wire_at(t)
    if not w:
        print(f"   {what}: terminal {t} already unwired", flush=True); return
    ws = [o["uid"] for o in g.report(OP, "Wire")]
    if w in ws:
        g.delete_object(OP, "Wire", ws.index(w)); print(f"   {what}: wire {w} deleted", flush=True)
    else:
        print(f"   {what}: wire {w} not in report", flush=True)


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(BASE, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    print("base ExecState", g.exec_state(OP), "nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), flush=True)
    inv0 = g.uids(OP, "Invoke")
    # 1. free the parameters that get real sources (placeholder controls stay on the panel, unwired)
    for name in ("X Array", "Cross Size", "Array of Images", "Y Output", "Z Output", "Array Cal Cluster", "Test Array"):
        unwire(T[name], name)
    unwire(T["X Array"] + 1, "X Array out (placeholder indicator)")
    g.remove_bad_wires_scripted(OP)
    # 2. sources
    uL = step("drop HARNESS_loadcal", "+1", lambda: drop(L_VI, (100, 100)))
    uC = step("drop IMAQ Create", "+1", lambda: drop(C_VI, (100, 300)))
    uR = step("drop IMAQ ReadFile", "+1", lambda: drop(R_VI, (300, 300)))
    uW = step("drop make both cosine bandpass", "+1", lambda: drop(W_VI, (300, 500)))
    uI = step("drop Omars IMAQ ImageToArray", "+1", lambda: drop(I2A_VI, (500, 300)))
    if None in (uL, uC, uR, uW, uI):
        return 2
    nC, nR = g.count(OP, "Node") - 4, g.count(OP, "Node") - 3      # Nodes[] = creation order: ... L, C, R, W, I2A (junk Invokes
                                                                   # from the earlier OpNetInfo calls sit BETWEEN the CLFN and L)
    cl = g.report(OP, "CallLibrary")[0]["uid"]
    w = lambda su, st, dt, br=False: g.wire(OP, "SubVI", sub_index(su), st, "CallLibrary", 0, dt, branch=br)
    ws = lambda su, st, du, dt, br=False: g.wire(OP, "SubVI", sub_index(su), st, "SubVI", sub_index(du), dt, branch=br)
    step("C.New Image -> R.Image", "+1", lambda: ws(uC, "New Image", uR, "Image"))
    step("R.Image Out -> I2A.Image", "+1", lambda: ws(uR, "Image Out", uI, "Image"))
    step("L.cross size -> W.cross length", "+1", lambda: ws(uL, "cross size", uW, "cross length"))
    step("I2A.Image Pixels (U8) -> CLFN.Array of Images", "+1", lambda: w(uI, "Image Pixels (U8)", "Array of Images"))
    step("L.Array of cal clusters -> CLFN.Array Cal Cluster", "+1", lambda: w(uL, "Array of cal clusters", "Array Cal Cluster"))
    step("L.cross size -> CLFN.Cross Size (branch)", "accepted", lambda: w(uL, "cross size", "Cross Size", True))
    step("W.Hilbert -> CLFN.Y Output", "+1", lambda: w(uW, "Cosine bandpass for Hilbert", "Y Output"))
    step("W.real-space -> CLFN.Test Array", "+1", lambda: w(uW, "Real-space cosine window", "Test Array"))
    # 3. adapt trick: X Array <- loader DBL array, unwire, then controls/indicator of the adapted (DBL) type
    step("L.x,y,(blankz) array -> CLFN.X Array (adapt)", "+1", lambda: w(uL, "x,y,(blankz) array", "X Array"))
    unwire(T["X Array"], "X Array (adapt wire)")
    fp0 = {l for _, l, _ in g.fp_labels(OP)}
    new, lab_x = g.create_control(OP, 0, T["X Array"]); print("   X Array DBL control:", lab_x, flush=True)
    fp0 |= {lab_x}
    g.create_indicator(OP, 0, T["X Array"] + 1); labs = [l for _, l, _ in g.fp_labels(OP) if l not in fp0]; lab_xo = labs[-1] if labs else None
    print("   X Array out indicator:", lab_xo, flush=True)
    # 4. Bead good control -> also Z Output (in/out good flags)
    step("Bead Is Good Array -> CLFN.Z Output (branch)", "accepted", lambda: g.wire_control(OP, ["Bead Is Good Array"], "CallLibrary", 0, ["Z Output"], branch=True))
    # 5. harness controls on IMAQ Create / ReadFile
    labels = {"x,y,z array": lab_x, "Bead is good? array in": "Bead Is Good Array", "pos in cal image in": "Y Array", "Error Message": "Error Message"}
    for nidx, nm, t in ((nC, "Image Name", 2), (nR, "File Path", 7)):
        new, lab = g.create_control(OP, nidx, t); print(f"   control {nm!r} on Nodes[{nidx}] t{t}: {lab!r}", flush=True)
        if not new or lab != nm:
            print("STOP: control label mismatch", flush=True); return 3
        labels[nm] = lab
    # purge OpNetInfo's junk Invokes, then verify
    for o in g.new_since(OP, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(OP, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(OP, "Invoke", ids.index(o["uid"]))
    g.remove_bad_wires_scripted(OP)
    es = g.exec_state(OP)
    outs = {"x,y,z array out": lab_xo, "Bead is good? array out": "Z Output 2", "pos in cal image out": "Y Array 2", "Error Message out": "Error Message 2"}
    print("\nassembled: wires", g.count(OP, "Wire"), "ExecState", es, "CONTROLS", labels, "OUTPUTS", outs, flush=True)
    if es != 1 or not lab_x or not lab_xo:
        print("STOP: broken / missing labels - NOT saving", flush=True); return 5
    print("saved", g.save(OP), flush=True)
    json.dump({"controls": labels, "outputs": outs}, open(os.path.join(os.path.dirname(HERE), "bench", "harness_gpu_labels.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
