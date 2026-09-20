"""build_opsetautoerr.py — OpSetAutoErr_v0.vi: write VI.'Automatic Error Handling' (ID 242, R/W) of a target VI from a
boolean control. Turning it OFF on an op silences the automatic error dialog for every unwired error output in
that op (the 8 s watchdog penalty per error goes away; errors then just flow or vanish). Zero GUI.
Chain: OpWire_v1 skeleton stripped to {vi path -> Open VI Reference} -> PN VI [242 write] <- 'vi reference';
control on the PN's value input (create_control, label 'Automatic Error Handling'); PN error out -> Clear Errors 369.

Run (bgrun --max-min 8): tools/recipes/build_opsetautoerr.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpWire_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpSetAutoErr_v0.vi")
g._run.__defaults__ = (6.0, 60.0)


def idx(cls, uid):
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def main():
    g._lv = None
    if os.path.exists(OP):
        try:
            g.close_panel(OP)
        except Exception:
            pass
    shutil.copyfile(SRC, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    for cls, uid in (("SubVI", 216), ("SubVI", 262), ("SubVI", 124), ("SubVI", 170), ("Function", 683), ("Function", 788),
                     ("Constant", 755), ("Constant", 834), ("IndexArray", 308), ("IndexArray", 327)):
        g.delete_object(OP, cls, idx(cls, uid))
    while True:
        ws = g.report(OP, "Wire")
        d = [i for i, o in enumerate(ws) if o["uid"] != 106]
        if not d:
            break
        g.delete_object(OP, "Wire", d[0])
    print("skeleton wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)
    pn = g.build_property(OP, "VI Server:VI", [("242", True)], (420, 300)); up = pn[0]["uid"]
    print("PN", pn[0]["pos"], "wire ref:", g.wire(OP, "Function", idx("Function", 43), "vi reference", "Property", idx("Property", up), "reference", branch=True), flush=True)
    print("error out -> Clear Errors:", g.wire(OP, "Property", idx("Property", up), "error out", "SubVI", idx("SubVI", 369), "error in (no error)"), flush=True)
    n = g.count(OP, "Node") - 1
    label = None
    for t in (4, 5, 3, 2, 6):
        wb = g.uids(OP, "Wire")
        new, lab = g.create_control(OP, n, t)
        print(f"   PN terminal {t}: {[(o['uid'], o['pos']) for o in new]} label={lab!r}", flush=True)
        if new and lab and lab.startswith("Automatic"):
            label = lab; break
        if new:
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            g.delete_object(OP, "ControlTerminal", ct.index(new[0]["uid"])); g.remove_bad_wires_scripted(OP)
    es = g.exec_state(OP)
    print("assembled: control", label, "wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if not label or es != 1:
        print("STOP: not saving", flush=True); return 2
    print("saved", g.save(OP), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
