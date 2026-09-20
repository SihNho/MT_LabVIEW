"""build_opcreatecontrol.py — OpCreateControl_v0.vi: create a front-panel control wired to terminal t of node n
of a target VI (Terminal.Create Control, 6349C01), addressing by the script-only ladder
  VI (Open VI Reference) -> PN VI.Block Diagram (23C, output 'Diagram') -> PN AbstractDiagram.Nodes[] (6375809)
  -> IA308[index] -> PN Node.Terminals[] (6359000) -> IA327[index 2] -> Invoke Terminal.Create Control.
Built entirely by script from OpWire_v1 (docs/keystone-op-spec.md §24). No class constant, no GUI.

Run through the deadline runner:
  py tools/bgrun.py --max-min 10 --log tools/bench/build_keystone.log -- py -u tools/recipes/build_opcreatecontrol.py [--no-test]

Steps (prediction contract per step):
  1. copy OpWire_v1 -> OpCreateControl_v0; delete SubVIs 216, 262, 124, 170; Functions 683, 788; Constants 755, 834
  2. delete every wire except uids 106 (vi path -> Open VI Reference), 1066 (index -> IA308), 1108 (index 2 -> IA327)
     -> ExecState 0 (IA arrays unwired), Wires 3
  3. build_property VI.Block Diagram at (420,300); wire OpenVIRef 'vi reference' -> reference
  4. build_property Diagram.Nodes[] at (520,300); wire PN1 'Diagram' -> reference; wire PN2 'Nodes[]' -> IA308 'array'
  5. build_property Node.Terminals[] at (700,300); wire IA308 'element' -> reference; wire PN3 'Terminals[]' -> IA327 'array'
  6. build_invoke Terminal.Create Control (6349C01) at (700,450); wire IA327 'element' -> reference;
     wire Invoke 'error out' -> Clear Errors 369 'error in (no error)'
  7. ExecState 1 -> COM save; else STOP
  8. test on a scratch copy of GUIBENCH_v0: sweep node index n = 0..N-1 with terminal 1 (Index Array 'index');
     the run whose new ControlTerminal lands near IndexArray 534 (975,350) identifies that node's Nodes[] index.
     Contract: >= 1 run yields exactly +1 ControlTerminal (and ExecState of the scratch unchanged or 1).
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpWire_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpCreateControl_v0.vi")
TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_cc_target.vi")
KEEP = {106, 1066, 1108}
g._run.__defaults__ = (6.0, 45.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def del_uid(cls, uid):
    i = [o["uid"] for o in g.report(OP, cls)].index(uid)
    return g.delete_object(OP, cls, i)


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
    shutil.copyfile(SRC, OP)
    g.open_panel(OP); time.sleep(1.0)
    print("baseline Wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)

    def strip():
        for cls, uid in (("SubVI", 216), ("SubVI", 262), ("SubVI", 124), ("SubVI", 170),
                         ("Function", 683), ("Function", 788), ("Constant", 755), ("Constant", 834)):
            del_uid(cls, uid)
        while True:
            ws = g.report(OP, "Wire")
            d = [i for i, o in enumerate(ws) if o["uid"] not in KEEP]
            if not d:
                break
            g.delete_object(OP, "Wire", d[0])
        return [(o["uid"], o["pos"]) for o in g.report(OP, "Wire")], g.exec_state(OP)
    step("1-2 strip to skeleton (OpenVIRef, IA308, IA327, controls, sinks)", "Wires [106,1066,1108]; ExecState 0", strip)
    ovr = idx("Function", 43)

    pn1 = step("3 build_property VI.Block Diagram", "+1 Property", lambda: g.build_property(OP, "VI Server:VI", [("23C", False)], (420, 300)))
    if not pn1:
        return 3
    p1 = idx("Property", pn1[0]["uid"])
    step("3b OpenVIRef.vi reference -> PN1.reference", "accepted", lambda: g.wire(OP, "Function", ovr, "vi reference", "Property", p1, "reference", branch=True))

    pn2 = step("4 build_property Diagram.Nodes[]", "+1 Property", lambda: g.build_property(OP, "VI Server:Diagram", [("6375809", False)], (520, 300)))
    if not pn2:
        return 4
    p2 = idx("Property", pn2[0]["uid"]); p1 = idx("Property", pn1[0]["uid"])
    step("4b PN1.Diagram -> PN2.reference", "Wire +1", lambda: g.wire(OP, "Property", p1, "Diagram", "Property", p2, "reference"))
    step("4c PN2.Nodes[] -> IA308.array", "Wire +1", lambda: g.wire(OP, "Property", p2, "Nodes[]", "IndexArray", idx("IndexArray", 308), "array"))

    pn3 = step("5 build_property Node.Terminals[]", "+1 Property", lambda: g.build_property(OP, "VI Server:Node", [("6359000", False)], (700, 300)))
    if not pn3:
        return 5
    p3 = idx("Property", pn3[0]["uid"])
    step("5b IA308.element -> PN3.reference (Node-typed)", "Wire +1", lambda: g.wire(OP, "IndexArray", idx("IndexArray", 308), "element", "Property", p3, "reference"))
    step("5c PN3.Terms[] (short name of Terminals[]) -> IA327.array", "Wire +1", lambda: g.wire(OP, "Property", p3, "Terms[]", "IndexArray", idx("IndexArray", 327), "array"))

    inv = step("6 build_invoke Terminal.Create Control", "+1 Invoke", lambda: g.build_invoke(OP, "VI Server:Terminal", "6349C01", (700, 450)))
    if not inv:
        return 6
    ii = idx("Invoke", inv[0]["uid"])
    step("6b IA327.element -> Invoke.reference (Terminal-typed)", "Wire +1", lambda: g.wire(OP, "IndexArray", idx("IndexArray", 327), "element", "Invoke", ii, "reference"))
    step("6c Invoke.error out -> Clear Errors 369", "Wire +1", lambda: g.wire(OP, "Invoke", ii, "error out", "SubVI", idx("SubVI", 369), "error in (no error)"))
    es = g.exec_state(OP)
    print("\nassembled Wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 7
    step("7 COM save", "size > 0", lambda: g.save(OP))
    if "--no-test" in sys.argv:
        return 0

    shutil.copyfile(TGT_SRC, TGT); g.open_panel(TGT); time.sleep(0.8)
    n_nodes = g.count(TGT, "Node")
    print("target nodes (Traverse count)", n_nodes, "ControlTerminals", g.count(TGT, "ControlTerminal"), "ExecState", g.exec_state(TGT), flush=True)
    vi = g.op(OP)
    vi.SetControlValue("vi path", TGT); vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    hits = []
    for n in range(n_nodes + 2):
        before = g.uids(TGT, "ControlTerminal")
        vi.SetControlValue("index", n); vi.SetControlValue("index 2", 1)
        t0 = time.time()
        try:
            g._run(vi)
        except Exception as e:
            print(f"   n={n}: run {str(e)[:60]}", flush=True)
        new = g.new_since(TGT, "ControlTerminal", before)
        err = g._err(vi)
        print(f"   n={n}: {time.time() - t0:.2f}s new controls {[(o['uid'], o['pos']) for o in new]} err={err}", flush=True)
        if new:
            hits.append((n, [(o["uid"], o["pos"]) for o in new]))
    print("HITS", hits, "target ExecState", g.exec_state(TGT), flush=True)
    try:
        g.close_panel(TGT); os.remove(TGT); print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
