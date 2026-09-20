"""build_opmoveout.py - OpMoveOut_v0.vi: move Nodes[index 2] of Traverse "Diagram"[index] of a target VI to the TOP-LEVEL
diagram at control 'position' (GObject.Move 632A400 with `owner` = VI.Block Diagram).  Lets a node be pulled out of a
structure (needed for the Saleh-lab Call Library Function Node, which lives inside a For Loop; copy_into cannot reach it).
Base: OpNetInfo_v1 ladder (Open VI Ref -> Traverse Diagram -> IA -> TMSC(Diagram) -> Nodes[] -> IA_n -> Node).  Zero GUI.
  py tools/bgrun.py --max-min 15 --log tools/bench/build_opmoveout.log -- py -u tools/recipes/build_opmoveout.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpNetInfo_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpMoveOut_v0.vi")
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
    ias = g.report(OP, "IndexArray"); ia_n = sorted(ias, key=lambda o: o["pos"][0])[-2]          # Nodes[] indexer (see build_opsetlabel)
    ovr = [o for o in g.report(OP, "Function") if o["pos"][0] < 300][0]                            # Open VI Reference
    print("IA_n", ia_n, "OpenVIRef", ovr, flush=True)
    inv = step("build_invoke GObject.Move (632A400)", "+1 Invoke", lambda: g.build_invoke(OP, "VI Server:GObject", "632A400", (900, 700)))
    ui = inv[0]["uid"]
    step("IA_n.element -> Move.reference (branch)", "accepted", lambda: g.wire(OP, "IndexArray", idx("IndexArray", ia_n["uid"]), "element", "Invoke", idx("Invoke", ui), "reference", branch=True))
    pn = step("PN VI.Block Diagram (23C)", "+1 Property", lambda: g.build_property(OP, "VI Server:VI", [("23C", False)], (700, 820)))
    up = pn[0]["uid"]
    step("OpenVIRef.vi reference -> PN (branch)", "accepted", lambda: g.wire(OP, "Function", idx("Function", ovr["uid"]), "vi reference", "Property", idx("Property", up), "reference", branch=True))
    r = step("PN.Diagram -> Move.owner", "+1", lambda: g.wire(OP, "Property", idx("Property", up), "Diagram", "Invoke", idx("Invoke", ui), "owner"))
    if r is None:
        for name in ("Owner", "new owner", "New Owner"):
            r = step(f"PN.Diagram -> Move.{name}", "+1", lambda name=name: g.wire(OP, "Property", idx("Property", up), "Diagram", "Invoke", idx("Invoke", ui), name))
            if r is not None:
                break
    inv_index = g.count(OP, "Node") - 2            # Nodes[] = creation order: the Invoke was created before the PN (last)
    print("Invoke node index in Nodes[]:", inv_index, flush=True)
    label = None
    for t in range(3, 9):
        w0 = g.count(OP, "Wire")
        new, lab = g.create_control(OP, inv_index, t)
        print(f"   Move terminal {t}: {[(o['uid'], o['pos']) for o in new]} label={lab!r} wires {w0}->{g.count(OP, 'Wire')}", flush=True)
        if new and lab and "position" in lab.lower() and g.count(OP, "Wire") > w0:
            label = lab; break
        if new:
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            g.delete_object(OP, "ControlTerminal", ct.index(new[0]["uid"])); g.remove_bad_wires_scripted(OP)
    g.set_auto_error_handling(OP, False)
    es = g.exec_state(OP)
    print("assembled: position control", label, "wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        g.remove_bad_wires_scripted(OP); es = g.exec_state(OP); print("after Remove Bad Wires: ExecState", es, flush=True)
    if not label or es != 1:
        print("STOP: not saving", flush=True); return 2
    print("saved", g.save(OP), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
