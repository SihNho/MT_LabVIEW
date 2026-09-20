"""build_opremovebadwires.py — OpRemoveBadWires_v0.vi: LabVIEW's own Ctrl+B for a target VI, headless:
Open VI Reference -> Invoke VI.'Block Diagram:Remove Bad Wires' (Unique ID 410) -> Clear Errors. Zero GUI.
Replaces gscript.remove_bad_wires (menu clicks that the GUI gate refuses).

Run (bgrun --max-min 6): tools/recipes/build_opremovebadwires.py
Steps: copy OpWire_v1 -> strip to {vi path -> Open VI Reference} (delete SubVIs 216/262/124/170, Functions 683/788,
Constants 755/834, IndexArrays 308/327, all wires but 106) -> build_invoke(VI, 410) at (420,300) <- 'vi reference'
(branch) -> error out -> Clear Errors 369 -> ExecState 1 -> save. Test: copy GUIBENCH_v0, delete IndexArray 0
(leaves dangling wires, ExecState 0), run the op -> ExecState 1 and the wire count drops.
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpWire_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpRemoveBadWires_v0.vi")
TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_rbw_target.vi")
g._run.__defaults__ = (6.0, 45.0)


def idx(cls, uid):
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def main():
    g._lv = None
    for p in (OP, TGT):
        if os.path.exists(p):
            try:
                g.close_panel(p)
            except Exception:
                pass
    shutil.copyfile(SRC, OP); g.open_panel(OP); time.sleep(1.0)
    for cls, uid in (("SubVI", 216), ("SubVI", 262), ("SubVI", 124), ("SubVI", 170), ("Function", 683), ("Function", 788),
                     ("Constant", 755), ("Constant", 834), ("IndexArray", 308), ("IndexArray", 327)):
        g.delete_object(OP, cls, idx(cls, uid))
    while True:
        ws = g.report(OP, "Wire")
        d = [i for i, o in enumerate(ws) if o["uid"] != 106]
        if not d:
            break
        g.delete_object(OP, "Wire", d[0])
    print("skeleton Wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)
    inv = g.build_invoke(OP, "VI Server:VI", "410", (420, 300))
    ui = inv[0]["uid"]
    print("invoke", inv[0]["pos"], "wire ref:", g.wire(OP, "Function", idx("Function", 43), "vi reference", "Invoke", idx("Invoke", ui), "reference", branch=True),
          "wire err:", g.wire(OP, "Invoke", idx("Invoke", ui), "error out", "SubVI", idx("SubVI", 369), "error in (no error)"), "ExecState", g.exec_state(OP), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: broken - not saving", flush=True); return 2
    print("saved", g.save(OP), flush=True)
    shutil.copyfile(TGT_SRC, TGT); g.open_panel(TGT); time.sleep(0.8)
    g.delete_object(TGT, "IndexArray", 0)
    print("target after node delete: Wires", g.count(TGT, "Wire"), "ExecState", g.exec_state(TGT), flush=True)
    vi = g.op(OP); vi.SetControlValue("vi path", TGT); vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    t0 = time.time(); g._run(vi)
    print(f"after Remove Bad Wires ({time.time() - t0:.2f}s): Wires", g.count(TGT, "Wire"), "ExecState", g.exec_state(TGT), flush=True)
    g.close_panel(TGT); os.remove(TGT); print("scratch deleted", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
