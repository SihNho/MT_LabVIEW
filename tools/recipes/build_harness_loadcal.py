"""build_harness_loadcal.py — HARNESS_loadcal.vi: the lab's `Load and prep N cal images.vi` with its File Dialog
replaced by a path control, so Python can load a .cal file headlessly and get `Array of cal clusters`,
`cross size`, `# of beads`, `# slices in stack`, `x,y,(blankz) array`, `exp/ref array` by the lab's own code.
Zero GUI. The original in background VIs is never modified (copy in claudeDev).

Run through the deadline runner (bgrun --max-min 10): tools/recipes/build_harness_loadcal.py [--cal=<path>]

Steps (prediction contract per step):
  1. copy -> claudeDev\\HARNESS_loadcal.vi; node_info: File Dialog index F, Read from Binary File index R
  2. delete the File Dialog SubVI (uid at (-345,44)); delete the wires that hung off it (candidates: bbox top-left
     x in [-360,-100], y in [30,140]; then remaining-broken check) -> ExecState 1 (Read's file input is optional)
  3. create_control (v1, label reported) on Read from Binary File terminals t = 0.. until the label is
     'file (use dialog)'; strays (other labels) are deleted together with their wire
  4. ExecState 1 -> COM save; run with --cal (default cal002) -> print # of beads, cross size, # slices,
     x,y,(blankz) array, exp/ref array, and the cluster array's shape (types/lengths per field)
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

BG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs"
SRC = os.path.join(BG, "Load and prep N cal images.vi")
OP = os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")
CAL = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--cal=")),
           r"G:\Data\SiHyeong\20260906 Kimlab - 50bp 16X WT 90Hz 1p2 Ramp_Newbatch\test\cal002")
g._run.__defaults__ = (6.0, 60.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def shape(v, depth=0):
    if isinstance(v, (tuple, list)):
        if not v:
            return "[]"
        if depth >= 3:
            return f"[{len(v)}]"
        inner = shape(v[0], depth + 1)
        return f"[{len(v)} x {inner}]" if all(isinstance(x, (tuple, list)) for x in v) else f"[{len(v)}: {inner}, ...]" if isinstance(v[0], (tuple, list)) else f"[{len(v)} {type(v[0]).__name__}]"
    return type(v).__name__


def main():
    g._lv = None
    if os.path.exists(OP):
        try:
            g.close_panel(OP)
        except Exception:
            pass
    shutil.copyfile(SRC, OP)
    g.open_panel(OP); time.sleep(1.0)
    info = g.node_info(OP)
    F = next(i for i, s, l in info if s == "File Dialog")
    R = next(i for i, s, l in info if s == "Read from Binary File")
    print("nodes", len(info), "File Dialog =", F, "Read from Binary File =", R, "ExecState", g.exec_state(OP), flush=True)
    subs = g.report(OP, "SubVI")
    dlg = min(subs, key=lambda o: abs(o["pos"][0] + 345) + abs(o["pos"][1] - 44))
    print("dialog SubVI", dlg, flush=True)
    w0 = g.count(OP, "Wire")
    g.delete_object(OP, "SubVI", [o["uid"] for o in g.report(OP, "SubVI")].index(dlg["uid"]))
    print("dialog deleted; ExecState", g.exec_state(OP), flush=True)
    print("Remove Bad Wires (scripted):", g.remove_bad_wires_scripted(OP), "(wires before", w0, ")", flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: still broken after Remove Bad Wires - a required input lost its source; not saving", flush=True)
        print("   nodes:", g.node_info(OP), flush=True)
        return 2

    hit = None
    for t in range(12):
        wb = g.uids(OP, "Wire")
        new, label = g.create_control(OP, R, t)
        print(f"   Read terminal {t}: new {[(o['uid'], o['pos']) for o in new]} label={label!r}", flush=True)
        if new and label and label.startswith("file"):
            hit = (t, label); break
        if new:
            # stray: remove the control and the wire it brought
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            g.delete_object(OP, "ControlTerminal", ct.index(new[0]["uid"]))
            for u in g.uids(OP, "Wire") - wb:
                ws = [o["uid"] for o in g.report(OP, "Wire")]
                if u in ws:
                    g.delete_object(OP, "Wire", ws.index(u))
    if not hit:
        print("STOP: no 'file' control created", flush=True); return 3
    es = g.exec_state(OP)
    print("path control", hit, "ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 4
    step("4 COM save", "size > 0", lambda: g.save(OP))

    vi = g.op(OP)
    vi.SetControlValue(hit[1], CAL)
    t0 = time.time()
    try:
        g._run(vi)
    except Exception as e:
        print("run:", str(e)[:120], flush=True)
    print(f"run {time.time() - t0:.2f}s", flush=True)
    for n in ("# of beads", "cross size", "# slices in stack", "x,y,(blankz) array", "exp/ref array"):
        try:
            print("  ", n, "=", vi.GetControlValue(n), flush=True)
        except Exception as e:
            print("  ", n, "ERR", str(e)[:60], flush=True)
    clusters = vi.GetControlValue("Array of cal clusters")
    print("   Array of cal clusters:", shape(clusters), flush=True)
    if clusters:
        c0 = clusters[0]
        print("   cluster[0] fields:", [shape(f) for f in c0], flush=True)
        for k, f in enumerate(c0):
            if not isinstance(f, (tuple, list)):
                print(f"      field {k} scalar = {f!r}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
