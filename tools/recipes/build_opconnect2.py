"""build_opconnect2.py — OpConnect2_v0.vi: wire a TOP-LEVEL source terminal into a sink terminal that lives in ANY
diagram of the target (top level or a loop's), by indices — the sub-diagram-capable Connect Wire.
  sink   : Traverse "Diagram"[index] -> TMSC -> Nodes[][index 2] -> Terminals[][index 3]   (OpNetInfo_v1's ladder)
  source : VI -> Block Diagram (23C) -> Nodes[][index 4] -> Terminals[][index 5]           (OpCreateControl's ladder)
  Terminal.Connect Wire (6349C03) on the sink with Wire Source = source. LabVIEW creates the loop tunnel itself
  when the sink is inside a structure (Connect Wire crosses borders); flip it with set_index_mode afterwards.
Base: copy of OpNetInfo_v1 (creator neutralised by its error-in control). Zero GUI (spec §31).

Run (bgrun --max-min 15): tools/recipes/build_opconnect2.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpNetInfo_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpConnect2_v0.vi")
g._run.__defaults__ = (6.0, 60.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def idx(cls, uid):
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def last_node():
    return g.count(OP, "Node") - 1


def main():
    g._lv = None
    if os.path.exists(OP):
        try:
            g.close_panel(OP)
        except Exception:
            pass
    shutil.copyfile(SRC, OP)
    g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    print("base ExecState", g.exec_state(OP), "wires", g.count(OP, "Wire"), flush=True)
    ovr = [o for o in g.report(OP, "Function") if o["pos"][0] < 300][0]              # Open VI Reference
    ias = g.report(OP, "IndexArray")
    ia_t = max(ias, key=lambda o: o["pos"][0] if o["pos"][1] < 350 else -1)         # IA_t at (1150,280): the sink Terminal element
    print("Open VI Ref", ovr, "IA_t", ia_t, flush=True)

    p1 = step("PN VI.Block Diagram (source side)", "+1", lambda: g.build_property(OP, "VI Server:VI", [("23C", False)], (420, 560)))
    u1 = p1[0]["uid"]
    step("OpenVIRef.vi reference -> PN1 (branch)", "accepted", lambda: g.wire(OP, "Function", idx("Function", ovr["uid"]), "vi reference", "Property", idx("Property", u1), "reference", branch=True))
    p2 = step("PN Diagram.Nodes[]", "+1", lambda: g.build_property(OP, "VI Server:Diagram", [("6375809", False)], (560, 560)))
    u2 = p2[0]["uid"]
    step("PN1.Diagram -> PN2", "+1", lambda: g.wire(OP, "Property", idx("Property", u1), "Diagram", "Property", idx("Property", u2), "reference"))
    ia4 = step("IA source node", "+1", lambda: g.build_index_array(OP, (700, 560)))
    u4 = ia4[0]["uid"]
    step("Nodes[] -> IA4.array", "+1", lambda: g.wire(OP, "Property", idx("Property", u2), "Nodes[]", "IndexArray", idx("IndexArray", u4), "array"))
    r = step("control index 4", "label 'index 4'", lambda: g.create_control(OP, last_node(), 2))
    if not r or r[1] != "index 4":
        print("STOP index 4:", r, flush=True); return 2
    p3 = step("PN Node.Terminals[] (source)", "+1", lambda: g.build_property(OP, "VI Server:Node", [("6359000", False)], (850, 560)))
    u3 = p3[0]["uid"]
    step("IA4.element -> PN3", "+1", lambda: g.wire(OP, "IndexArray", idx("IndexArray", u4), "element", "Property", idx("Property", u3), "reference"))
    ia5 = step("IA source terminal", "+1", lambda: g.build_index_array(OP, (1000, 560)))
    u5 = ia5[0]["uid"]
    step("Terms[] -> IA5.array", "+1", lambda: g.wire(OP, "Property", idx("Property", u3), "Terms[]", "IndexArray", idx("IndexArray", u5), "array"))
    r = step("control index 5", "label 'index 5'", lambda: g.create_control(OP, last_node(), 2))
    if not r or r[1] != "index 5":
        print("STOP index 5:", r, flush=True); return 3

    inv = step("build_invoke Terminal.Connect Wire", "+1 Invoke", lambda: g.build_invoke(OP, "VI Server:Terminal", "6349C03", (1300, 560)))
    ui = inv[0]["uid"]
    step("IA_t.element -> Connect Wire.reference (sink; branch)", "accepted", lambda: g.wire(OP, "IndexArray", idx("IndexArray", ia_t["uid"]), "element", "Invoke", idx("Invoke", ui), "reference", branch=True))
    step("IA5.element -> Wire Source", "+1", lambda: g.wire(OP, "IndexArray", idx("IndexArray", u5), "element", "Invoke", idx("Invoke", ui), "Wire Source"))
    ce = [o for o in g.report(OP, "SubVI") if o["pos"][0] >= 1500]
    if ce:
        step("Connect Wire.error out -> Clear Errors (branch into the existing sink is illegal; drop a new one)", "+1",
             lambda: (g.drop_subvi(OP, r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb\Clear Errors.vi", 0, (1500, 620)),
                      g.wire(OP, "Invoke", idx("Invoke", ui), "error out", "SubVI", len(g.report(OP, "SubVI")) - 1 if False else [i for i, o in enumerate(g.report(OP, "SubVI")) if o["pos"] == (1500, 620)][0], "error in (no error)")))
    es = g.exec_state(OP)
    print("\nassembled wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - not saving", flush=True); return 5
    print("saved", g.save(OP), flush=True)
    print("FP:", [(i, l, ind) for i, l, ind in g.fp_labels(OP)], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
