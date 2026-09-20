"""capture_harness_inputs.py - ground truth for the NumPy/CUDA port: the kernel INPUTS the harness computes inside LabVIEW
(the two cosine windows from 'make both cosine bandpass.vi' and the per-bead calibration clusters from HARNESS_loadcal).
Route 1 (direct COM reads): run the SPEC copy of 'make both cosine bandpass.vi' (cross length 120) and HARNESS_loadcal
(cal002) and read their indicators.  Route 2 (if the array-of-clusters indicator cannot be read over COM): throwaway COPY
of HARNESS_compare.vi with a script-built Index Array + indicator + index control on the loader's cluster output, one
fixture frame per bead, then the copy is deleted.  Saves tools/gpu/harness_inputs.npz.  Zero GUI.
  py tools/bgrun.py --max-min 15 --log tools/bench/capture_inputs.log -- py -u tools/bench/capture_harness_inputs.py
"""
import json, os, shutil, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 120.0)
SRC = os.path.join(g.CLAUDEDEV, "HARNESS_compare.vi"); CAP = os.path.join(g.CLAUDEDEV, "HARNESS_capture.vi")
LOADER = os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")
BANDPASS = os.path.join(g.CLAUDEDEV, "SPEC", "make both cosine bandpass.vi")
DATA = r"G:\Data\SiHyeong\20260906 Kimlab - 50bp 16X WT 90Hz 1p2 Ramp_Newbatch\test"
LABELS = json.load(open(os.path.join(HERE, "harness_compare_labels.json")))["controls"]
OUT = os.path.join(os.path.dirname(HERE), "gpu", "harness_inputs.npz")
NAMES = ["forget_radius", "z_step", "cosband", "ampl", "cork", "real", "n_slices"]


def term_index(nodes, n, name):
    for t, nm, w in nodes[n][2]:
        if nm.replace("\n", " ").strip() == name:
            return t
    raise KeyError(f"node {n}: terminal {name!r} not in {[x[1] for x in nodes[n][2]]}")


def describe(x):
    if hasattr(x, "__len__") and not isinstance(x, str):
        return f"{type(x).__name__}[{len(x)}]" + (f"x{len(x[0])}" if len(x) and hasattr(x[0], "__len__") else "")
    return repr(x)


def route2(out, nb, xyz0):
    if os.path.exists(CAP):
        try:
            g.close_panel(CAP)
        except Exception:
            pass
        os.remove(CAP)
    shutil.copyfile(SRC, CAP); g.report(CAP, "SubVI"); g.open_panel(CAP); time.sleep(1.0)
    print("copy ExecState", g.exec_state(CAP), "nodes", g.count(CAP, "Node"), flush=True)
    nodes, nets = g.net_map(CAP, 0, max_nodes=8, max_terms=40)
    for n in nodes:
        print(f"  node {n} uid {nodes[n][0]}: {[x[1].replace(chr(10), ' ') for x in nodes[n][2]]}", flush=True)
    tL = term_index(nodes, 0, "Array of cal clusters")
    fp0 = {l for _, l, _ in g.fp_labels(CAP)}
    n_ia = g.count(CAP, "Node")
    ia = g.build_index_array(CAP, (400, 800)); print("  IA:", ia, "node index", n_ia, flush=True)
    print("  connect clusters -> IA.array:", g.connect_terminals(CAP, n_ia, 0, 0, tL), flush=True)
    g.create_indicator(CAP, n_ia, 1); labs = [l for _, l, _ in g.fp_labels(CAP) if l not in fp0]; fp0 |= set(labs)
    el = labs[-1] if labs else None; print("  IA element indicator:", labs, flush=True)
    new, idx = g.create_control(CAP, n_ia, 2); print("  IA index control:", idx, flush=True)
    print("  ExecState", g.exec_state(CAP), flush=True)
    if g.exec_state(CAP) != 1 or not el or not idx:
        print("STOP: capture copy broken / labels missing", flush=True); return False
    vi = g.op(CAP)
    vi.SetControlValue(LABELS["Image Name"], "capture"); vi.SetControlValue(LABELS["# of bead 4 packs"], nb // 4)
    vi.SetControlValue(LABELS["4 pack remainder"], nb % 4); vi.SetControlValue(LABELS["File Path"], os.path.join(DATA, "img00004.tif"))
    vi.SetControlValue(LABELS["x,y,z array"], xyz0); vi.SetControlValue(LABELS["Bead is good? array in"], [True] * nb)
    vi.SetControlValue(LABELS["pos in cal image in"], [0] * nb)
    for b in range(nb):
        vi.SetControlValue(idx, b); g._run(vi)
        c = vi.GetControlValue(el)
        print(f"  bead {b} cluster: {[describe(x) for x in c]}", flush=True)
        for name, x in zip(NAMES, c):
            out[f"b{b}_{name}"] = np.array(x)
        if b == 0:
            out["xyz_out_frame4"] = np.array(vi.GetControlValue("x,y,z array out 2"))
    try:
        g.close_panel(CAP)
    except Exception:
        pass
    time.sleep(1.0)
    try:
        os.remove(CAP); print("capture VI deleted", flush=True)
    except Exception as e:
        print("capture VI NOT deleted:", e, flush=True)
    return True


def main():
    out = {}
    bp = g.op(BANDPASS); bp.SetControlValue("cross length", 120); g._run(bp)
    for tag, label in (("hilbert", "Cosine bandpass for Hilbert"), ("realspace", "Real-space cosine window")):
        v = bp.GetControlValue(label); out[tag] = np.array(v)
        print(f"{tag}: {out[tag].shape} {out[tag].dtype} first {out[tag][:4]} last {out[tag][-2:]}", flush=True)
    ld = g.op(LOADER); ld.SetControlValue("file (use dialog)", os.path.join(DATA, "cal002")); g._run(ld)
    nb = int(ld.GetControlValue("# of beads")); xyz0 = list(ld.GetControlValue("x,y,(blankz) array"))
    print("loader:", nb, "beads; cross", ld.GetControlValue("cross size"), "slices", ld.GetControlValue("# slices in stack"), flush=True)
    ok = False
    try:
        arr = ld.GetControlValue("Array of cal clusters")
        print("direct cluster-array read:", describe(arr), flush=True)
        if hasattr(arr, "__len__") and len(arr) == nb and hasattr(arr[0], "__len__") and len(arr[0]) == 7:
            for b, c in enumerate(arr):
                print(f"  bead {b}: {[describe(x) for x in c]}", flush=True)
                for name, x in zip(NAMES, c):
                    out[f"b{b}_{name}"] = np.array(x)
            ok = True
    except Exception as e:
        print("direct cluster-array read FAILED:", str(e)[:160], flush=True)
    if not ok:
        print("-> route 2 (harness copy + Index Array)", flush=True)
        if not route2(out, nb, xyz0):
            return 2
    np.savez(OUT, **out); print("saved", OUT, {k: v.shape for k, v in out.items()}, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
