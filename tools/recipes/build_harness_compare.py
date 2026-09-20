"""build_harness_compare.py — HARNESS_compare.vi: one frame through BOTH tracking kernels on identical inputs.
  HARNESS_loadcal (cal file -> Array of cal clusters, cross size; path set on its own front panel)
  IMAQ Create -> IMAQ ReadFile(File Path) -> Image Out -> PARALLEL_kernel_v3 + READONLY_fourfold_COPY
  make both cosine bandpass(cross length <- cross size) -> both kernels' windows
  controls (made by create_control, labels read back): Image Name, File Path, x,y,z array, Bead is good? array in,
  pos in cal image in, 4 pack remainder, # of bead 4 packs   (created on the v3 node, branched to the four-fold)
  indicators (create_indicator): x,y,z array out / Bead is good? array out / pos in cal image out for v3 and four-fold
No loop: Python drives frame by frame (tools/bench/run_fixture_compare.py). Zero GUI. No instrument VI is loaded.

Run (bgrun --max-min 15): tools/recipes/build_harness_compare.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

VIS = r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision"
BG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs"
BASE = os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "HARNESS_compare.vi")
L_VI = os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")
C_VI = os.path.join(VIS, "Basics.llb", "IMAQ Create")
R_VI = os.path.join(VIS, "Files.llb", "IMAQ ReadFile")
W_VI = os.path.join(BG, "make both cosine bandpass.vi")
K3_VI = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi")
K4_VI = os.path.join(g.CLAUDEDEV, "READONLY_fourfold_COPY.vi")
COS_HIL = "Cosine bandpass\nfor Hilbert "
COS_RS = "Real-space cosine window"
g._run.__defaults__ = (6.0, 60.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def sub_index(uid):
    return [o["uid"] for o in g.report(OP, "SubVI")].index(uid)


def drop(path, pos):
    before = g.uids(OP, "SubVI")
    g.drop_subvi(OP, path, 0, pos)
    new = [o for o in g.report(OP, "SubVI") if o["uid"] not in before]
    assert len(new) == 1, f"drop {os.path.basename(path)}: {len(new)} new SubVIs"
    return new[0]["uid"]


def make_control(node_index, wanted, max_t=16):
    """create_control on Nodes[node_index] terminals until the reported label == wanted; strays removed."""
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
    g._lv = None
    if os.path.exists(OP):
        try:
            g.close_panel(OP)
        except Exception:
            pass
    shutil.copyfile(BASE, OP)
    g.open_panel(OP); time.sleep(1.0)
    while g.count(OP, "Node"):
        g.delete_object(OP, "Node", 0)
    g.remove_bad_wires_scripted(OP)
    print("base wiped: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "controls", g.count(OP, "ControlTerminal"), "ExecState", g.exec_state(OP), flush=True)

    uL = step("drop HARNESS_loadcal", "+1 SubVI", lambda: drop(L_VI, (100, 100)))
    uC = step("drop IMAQ Create", "+1 SubVI", lambda: drop(C_VI, (100, 300)))
    uR = step("drop IMAQ ReadFile", "+1 SubVI", lambda: drop(R_VI, (300, 300)))
    uW = step("drop make both cosine bandpass", "+1 SubVI", lambda: drop(W_VI, (300, 500)))
    uK3 = step("drop PARALLEL_kernel_v3", "+1 SubVI", lambda: drop(K3_VI, (700, 150)))
    uK4 = step("drop READONLY_fourfold_COPY", "+1 SubVI", lambda: drop(K4_VI, (700, 550)))
    if None in (uL, uC, uR, uW, uK3, uK4):
        return 2
    info = g.node_info(OP)
    print("nodes:", info, flush=True)
    nL, nC, nR, nW, nK3, nK4 = range(6)              # creation order

    w = lambda su, st, du, dt, br=False: g.wire(OP, "SubVI", sub_index(su), st, "SubVI", sub_index(du), dt, branch=br)
    step("C.New Image -> R.Image", "Wire +1", lambda: w(uC, "New Image", uR, "Image"))
    step("R.Image Out -> K3.Image In", "Wire +1", lambda: w(uR, "Image Out", uK3, "Image In"))
    step("R.Image Out -> K4.Image In (branch)", "accepted", lambda: w(uR, "Image Out", uK4, "Image In", True))
    step("L.Array of cal clusters -> K3", "Wire +1", lambda: w(uL, "Array of cal clusters", uK3, "Array of cal clusters"))
    step("L.Array of cal clusters -> K4 (branch)", "accepted", lambda: w(uL, "Array of cal clusters", uK4, "Array of cal clusters", True))
    step("L.cross size -> K3.cross size", "Wire +1", lambda: w(uL, "cross size", uK3, "cross size"))
    step("L.cross size -> K4 (branch)", "accepted", lambda: w(uL, "cross size", uK4, "cross size", True))
    step("L.cross size -> W.cross length (branch)", "accepted", lambda: w(uL, "cross size", uW, "cross length", True))
    step("W.Hilbert -> K3", "Wire +1", lambda: w(uW, "Cosine bandpass for Hilbert", uK3, COS_HIL))
    step("W.Hilbert -> K4 (branch)", "accepted", lambda: w(uW, "Cosine bandpass for Hilbert", uK4, COS_HIL, True))
    step("W.real-space -> K3", "Wire +1", lambda: w(uW, COS_RS, uK3, COS_RS))
    step("W.real-space -> K4 (branch)", "accepted", lambda: w(uW, COS_RS, uK4, COS_RS, True))
    print("   wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)

    labels = {}
    for node, name in ((nC, "Image Name"), (nR, "File Path"), (nK3, "x,y,z array"), (nK3, "Bead is good? array in"),
                       (nK3, "pos in cal image in"), (nK3, "4 pack remainder"), (nK3, "# of bead 4 packs")):
        r = step(f"control {name!r} on Nodes[{node}]", "label == name", lambda node=node, name=name: make_control(node, name))
        if not r:
            return 3
        labels[name] = r[1]
    for name in ("x,y,z array", "Bead is good? array in", "pos in cal image in", "4 pack remainder", "# of bead 4 packs"):
        step(f"branch control {name!r} -> K4", "accepted", lambda name=name: g.wire_control(OP, [labels[name]], "SubVI", sub_index(uK4), [name], branch=True))
    print("   wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)

    outs = {}
    for tag, node in (("v3", nK3), ("ff", nK4)):
        for name in ("x,y,z array out", "Bead is good? array out", "pos in cal image out"):
            r = step(f"indicator {name!r} of {tag}", "label starts with name", lambda node=node, name=name: make_indicator(node, name))
            if not r:
                return 4
            outs[(tag, name)] = r[1]
    es = g.exec_state(OP)
    print("\nassembled: wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    print("CONTROLS", labels, flush=True)
    print("OUTPUTS", outs, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 5
    print("saved", g.save(OP), flush=True)
    import json
    json.dump({"controls": labels, "outputs": {f"{k[0]}|{k[1]}": v for k, v in outs.items()}},
              open(os.path.join(os.path.dirname(HERE), "bench", "harness_compare_labels.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
