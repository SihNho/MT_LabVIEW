"""build_harness_variant.py - HARNESS_<name>.vi for the three-way timing benchmark, built from scratch like
build_harness_compare.py (deleting a kernel SubVI from a copy of HARNESS_compare hangs LabVIEW's traverse, 2026-09-08):
  --name=base : HARNESS_loadcal + IMAQ Create/ReadFile + make both cosine bandpass, NO kernel   (COM/file/window overhead)
  --name=seq  : ... + READONLY_fourfold_COPY (the original sequential kernel)
  --name=par  : ... + PARALLEL_kernel_v3 (clean, P=4)
  --name=gpu  : ... + GPU_kernel.vi (the CUDA DLL wrapper, same connector pane)          [later]
Controls/indicators are created on the kernel's terminals (create_control / create_indicator); labels saved to
tools/bench/harness_<name>_labels.json.  Zero GUI.
  py tools/bgrun.py --max-min 15 --log tools/bench/build_harness_<name>.log -- py -u tools/recipes/build_harness_variant.py --name=<name>
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

VIS = r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision"
BG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs"
BASE = os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi")
L_VI = os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")
C_VI = os.path.join(VIS, "Basics.llb", "IMAQ Create"); R_VI = os.path.join(VIS, "Files.llb", "IMAQ ReadFile")
W_VI = os.path.join(BG, "make both cosine bandpass.vi")
KERNELS = {"seq": os.path.join(g.CLAUDEDEV, "READONLY_fourfold_COPY.vi"), "par": os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi"),
           "gpu": os.path.join(g.CLAUDEDEV, "GPU_kernel.vi"),
           # 2026-09-09: the GPU backend as a DROP-IN kernel (same pane as par) -> the three rows are measured in identical harnesses
           "gpuk": os.path.join(g.CLAUDEDEV, "GPU_kernel_v1.vi"),
           # 2026-09-10: the backend-selectable kernel (case: frame 0 = PARALLEL_kernel_v3, frame 1 = GPU_kernel_v1; selector =
           # the non-pane control `index`, chosen by its saved default value)
           "track": os.path.join(g.CLAUDEDEV, "TRACK_kernel_v1.vi"), "base": None}
COS_HIL = "Cosine bandpass\nfor Hilbert "; COS_RS = "Real-space cosine window"
g._run.__defaults__ = (6.0, 60.0)
OP = None


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


# terminal indices of the kernel connector pane (READONLY_fourfold_COPY = PARALLEL_kernel_v3, read 2026-09-08) and of the
# IMAQ VIs: creating at a KNOWN index avoids trial creations on output terminals, which left an unremovable broken wire
KNOWN = {"x,y,z array": 7, "Bead is good? array in": 0, "pos in cal image in": 13, "4 pack remainder": 11, "# of bead 4 packs": 9,
         "x,y,z array out": 4, "Bead is good? array out": 3, "pos in cal image out": 8, "Image Name": 2, "File Path": 7}


def make_control(node_index, wanted, max_t=16):
    if wanted in KNOWN:
        new, label = g.create_control(OP, node_index, KNOWN[wanted])
        if new and label == wanted:
            return KNOWN[wanted], label
        raise RuntimeError(f"known terminal {KNOWN[wanted]} for {wanted!r} gave {label!r}")
    for t in range(max_t):
        wb = g.uids(OP, "Wire")
        new, label = g.create_control(OP, node_index, t)
        if new and label == wanted:
            return t, label
        if new:
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            g.delete_object(OP, "ControlTerminal", ct.index(new[0]["uid"]))
            for u in g.uids(OP, "Wire") - wb:
                ws = [o["uid"] for o in g.report(OP, "Wire")]
                if u in ws:
                    g.delete_object(OP, "Wire", ws.index(u))
    raise RuntimeError(f"no terminal labelled {wanted!r} on Nodes[{node_index}]")


def make_indicator(node_index, wanted, max_t=16):
    if wanted in KNOWN:
        new = g.create_indicator(OP, node_index, KNOWN[wanted]); label = g.fp_labels(OP)[-1][1]
        if new and (label == wanted or label.startswith(wanted + " ")):
            return KNOWN[wanted], label
        raise RuntimeError(f"known terminal {KNOWN[wanted]} for {wanted!r} gave {label!r}")
    for t in range(max_t):
        wb = g.uids(OP, "Wire")
        new = g.create_indicator(OP, node_index, t)
        if not new:
            continue
        label = g.fp_labels(OP)[-1][1]
        if label == wanted or label.startswith(wanted + " "):
            return t, label
        ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
        g.delete_object(OP, "ControlTerminal", ct.index(new[0]["uid"]))
        for u in g.uids(OP, "Wire") - wb:
            ws = [o["uid"] for o in g.report(OP, "Wire")]
            if u in ws:
                g.delete_object(OP, "Wire", ws.index(u))
    raise RuntimeError(f"no output labelled {wanted!r} on Nodes[{node_index}]")


def main():
    global OP
    name = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--name=")), "base")
    kernel = KERNELS[name]
    OP = os.path.join(g.CLAUDEDEV, f"HARNESS_{name}.vi")
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)                                   # never through LabVIEW first (error 1012 lesson)
    shutil.copyfile(BASE, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    while g.count(OP, "Node"):
        g.delete_object(OP, "Node", 0)
    g.remove_bad_wires_scripted(OP)
    print("base wiped: nodes", g.count(OP, "Node"), "ExecState", g.exec_state(OP), flush=True)
    uL = step("drop HARNESS_loadcal", "+1", lambda: drop(L_VI, (100, 100)))
    uC = step("drop IMAQ Create", "+1", lambda: drop(C_VI, (100, 300)))
    uR = step("drop IMAQ ReadFile", "+1", lambda: drop(R_VI, (300, 300)))
    uW = step("drop make both cosine bandpass", "+1", lambda: drop(W_VI, (300, 500)))
    uK = step(f"drop kernel {os.path.basename(kernel) if kernel else '-'}", "+1", lambda: drop(kernel, (700, 150))) if kernel else None
    if None in (uL, uC, uR, uW) or (kernel and uK is None):
        return 2
    nL, nC, nR, nW, nK = 0, 1, 2, 3, 4
    w = lambda su, st, du, dt, br=False: g.wire(OP, "SubVI", sub_index(su), st, "SubVI", sub_index(du), dt, branch=br)
    step("C.New Image -> R.Image", "+1", lambda: w(uC, "New Image", uR, "Image"))
    step("L.cross size -> W.cross length", "+1", lambda: w(uL, "cross size", uW, "cross length"))
    if kernel:
        step("R.Image Out -> K.Image In", "+1", lambda: w(uR, "Image Out", uK, "Image In"))
        step("L.Array of cal clusters -> K", "+1", lambda: w(uL, "Array of cal clusters", uK, "Array of cal clusters"))
        step("L.cross size -> K.cross size (branch)", "accepted", lambda: w(uL, "cross size", uK, "cross size", True))
        step("W.Hilbert -> K", "+1", lambda: w(uW, "Cosine bandpass for Hilbert", uK, COS_HIL))
        step("W.real-space -> K", "+1", lambda: w(uW, COS_RS, uK, COS_RS))
    labels = {}
    wanted = [(nC, "Image Name"), (nR, "File Path")]
    if kernel:
        wanted += [(nK, "x,y,z array"), (nK, "Bead is good? array in"), (nK, "pos in cal image in"), (nK, "4 pack remainder"), (nK, "# of bead 4 packs")]
    for node, nm in wanted:
        r = step(f"control {nm!r} on Nodes[{node}]", "label == name", lambda node=node, nm=nm: make_control(node, nm))
        if not r:
            return 3
        labels[nm] = r[1]
    outs = {}
    if kernel:
        for nm in ("x,y,z array out", "Bead is good? array out", "pos in cal image out"):
            r = step(f"indicator {nm!r}", "label", lambda nm=nm: make_indicator(nK, nm))
            if not r:
                return 4
            outs[nm] = r[1]
    es = g.exec_state(OP)
    print("\nassembled: wires", g.count(OP, "Wire"), "ExecState", es, "CONTROLS", labels, "OUTPUTS", outs, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 5
    print("saved", g.save(OP), flush=True)
    json.dump({"controls": labels, "outputs": outs}, open(os.path.join(os.path.dirname(HERE), "bench", f"harness_{name}_labels.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
