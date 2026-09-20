"""build_opsetlabel.py - OpSetLabel_v0.vi: WRITE the label of Nodes[index 2] of Traverse "Diagram"[index] of a target VI
(any diagram, top level = 0) from a string control 'Label Text'.  Ladder = OpNetInfo_v1's (Open VI Ref -> Traverse Diagram
-> Index Array -> TMSC(Diagram) -> Nodes[] -> Index Array -> Node) + PN Node.Label (6359001) -> PN Text.Text (632D800, write).
Needed to copy an unlabeled donor node (the Saleh-lab Call Library Function Node) with copy_into, which selects by label.
Zero GUI.  Run (bgrun --max-min 15): tools/recipes/build_opsetlabel.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpNetInfo_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpSetLabel_v0.vi")
g._run.__defaults__ = (6.0, 60.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def idx(cls, uid):
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    print("base ExecState", g.exec_state(OP), "wires", g.count(OP, "Wire"), flush=True)
    # OpNetInfo_v1 layout (build_opnetinfo.py): ... Nodes[] -> IA_n (element = Node) -> PN Node.Terminals[] -> IA_t ; the
    # Node element also feeds the 'UID' PN. Find the Index Array whose element is the Node: the IA feeding the Terminals[] PN.
    ias = g.report(OP, "IndexArray"); pns = g.report(OP, "Property")
    print("IAs", [(o["uid"], tuple(o["pos"])) for o in ias], "PNs", [(o["uid"], tuple(o["pos"])) for o in pns], flush=True)
    # the Node-typed element: the IA immediately left of the Terminals[] PN (x just below its x); pick by position heuristics
    ia_n = sorted(ias, key=lambda o: o["pos"][0])[-2]       # second-rightmost IA = Nodes[] indexer (the rightmost = terminal indexer)
    print("IA_n", ia_n, flush=True)
    p1 = step("PN Node.Label (6359001)", "+1", lambda: g.build_property(OP, "VI Server:Node", [("6359001", False)], (900, 700)))
    u1 = p1[0]["uid"]
    step("IA_n.element -> PN Label.reference (branch)", "accepted", lambda: g.wire(OP, "IndexArray", idx("IndexArray", ia_n["uid"]), "element", "Property", idx("Property", u1), "reference", branch=True))
    p2 = step("PN Text.Text WRITE (632D800)", "+1", lambda: g.build_property(OP, "VI Server:Text", [("632D800", True)], (1100, 700)))
    u2 = p2[0]["uid"]
    step("Label -> Text PN reference", "+1", lambda: g.wire(OP, "Property", idx("Property", u1), "Label", "Property", idx("Property", u2), "reference"))
    n = g.count(OP, "Node") - 1
    label = None
    for t in (4, 5, 3, 2, 6):
        new, lab = g.create_control(OP, n, t)
        print(f"   Text PN terminal {t}: {[(o['uid'], o['pos']) for o in new]} label={lab!r}", flush=True)
        if new and lab and lab.startswith("Text"):
            label = lab; break
        if new:
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            g.delete_object(OP, "ControlTerminal", ct.index(new[0]["uid"])); g.remove_bad_wires_scripted(OP)
    step("Text PN error out -> Clear Errors", "+1", lambda: g.wire(OP, "Property", idx("Property", u2), "error out", "SubVI", idx("SubVI", 369) if 369 in [o["uid"] for o in g.report(OP, "SubVI")] else 0, "error in (no error)"))
    es = g.exec_state(OP)
    print("assembled: control", label, "wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if not label or es != 1:
        print("STOP: not saving (check the log; the Clear Errors sink may already be taken -> leave error out unwired and set auto error handling off)", flush=True)
        if label and es != 1:
            g.remove_bad_wires_scripted(OP); es = g.exec_state(OP); print("after Remove Bad Wires: ExecState", es, flush=True)
        if not label or es != 1:
            return 2
    g.set_auto_error_handling(OP, False)
    print("saved", g.save(OP), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
