"""build_opnetinfo.py — OpNetInfo_v1.vi: headless connectivity reader. Inputs: `index` (Traverse "Diagram" index
= which diagram, top level or a loop's), `index 2` (node in that diagram's Nodes[] order), `index 3` (terminal in
Node.Terminals[] order). Outputs: `Style` / `Text` (node type name / label), `Name` (terminal name), `UID`
(connected wire's UID, 0 when unwired), `Is Broken?`. Python groups terminals by wire UID -> net list.
Chain (all script, spec §30): OpBuildPN_v0 skeleton (Traverse Diagram -> IA308 -> TMSC -> Diagram) ->
PN Diagram.Nodes[] -> IA_n[index 2] -> PN Node[Terminals[]] -> IA_t[index 3] -> PN Terminal[Name, Connected Wire]
-> PN Wire[UID, Is Broken?] -> Clear Errors; PN Node[Label, Style] <- IA_n.element (branch) -> PN Text.Text.

Run (bgrun --max-min 15): tools/recipes/build_opnetinfo.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpBuildInvoke_v0.vi")   # OpBuildPN copies hang Traverse (spec §30); Invoke-lineage copies traverse fine
OP = os.path.join(g.CLAUDEDEV, "OpNetInfo_v1.vi")
CE = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb\Clear Errors.vi"
g._run.__defaults__ = (6.0, 120.0)


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


def readable(name):
    try:
        g.op(OP).GetControlValue(name); return True
    except Exception:
        return False


def make_indicator(node_index, wanted, terms=(4, 5, 6, 3, 2, 1, 0)):
    for t in terms:
        wb = g.uids(OP, "Wire")
        new = g.create_indicator(OP, node_index, t)
        if not new:
            continue
        if readable(wanted):
            return t
        ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
        g.delete_object(OP, "ControlTerminal", ct.index(new[0]["uid"]))
        for u in g.uids(OP, "Wire") - wb:
            ws = [o["uid"] for o in g.report(OP, "Wire")]
            if u in ws:
                g.delete_object(OP, "Wire", ws.index(u))
        g.remove_bad_wires_scripted(OP)
    raise RuntimeError(f"no output {wanted!r} on Nodes[{node_index}]")


def main():
    g._lv = None
    if os.path.exists(OP):
        try:
            g.close_panel(OP)
        except Exception:
            pass
    shutil.copyfile(SRC, OP)
    # load the copy through the reporter (Open VI Reference inside LabVIEW) BEFORE OpenFrontPanel: on this lineage
    # OpenFrontPanel on a not-yet-loaded copy hung 180 s twice (04:5x, 05:0x) while report-then-open took 0.1 s
    subs = g.report(OP, "SubVI"); fns = g.report(OP, "Function")
    print("copy loaded via reporter: SubVIs", [(o["uid"], o["pos"]) for o in subs], flush=True)
    g.open_panel(OP); time.sleep(1.0)
    ci = max(range(len(subs)), key=lambda i: subs[i]["pos"][0])
    tmsc = max(fns, key=lambda o: o["pos"][0])
    # 05:2x: deleting the lvlib creator node hangs LabVIEW tonight (spec §30) -> keep it, neutralise it: a control on
    # its 'error in (no error)' terminal, set TRUE by every caller (erdosmiller VIs pass errors through untouched).
    # discovery on a throwaway copy: which (node, terminal) is the creator's 'error in (no error)'?
    D = os.path.join(g.CLAUDEDEV, "SCRATCH_disc.vi"); shutil.copyfile(SRC, D); g.report(D, "SubVI"); g.open_panel(D); time.sleep(0.5)
    found = None
    for n in range(g.count(D, "Node")):
        for t in range(14):
            try:
                new, label = g.create_control(D, n, t)
            except Exception:
                new, label = [], None
            if not new:
                continue
            print(f"   disc Nodes[{n}] t{t} -> {label!r}", flush=True)
            if label and label.startswith("error in"):
                found = (n, t); break
            ct = [o["uid"] for o in g.report(D, "ControlTerminal")]
            g.delete_object(D, "ControlTerminal", ct.index(new[0]["uid"])); g.remove_bad_wires_scripted(D)
        if found:
            break
    try:
        g.close_panel(D); os.remove(D)
    except Exception:
        pass
    if not found:
        print("STOP: creator error-in terminal not found", flush=True); return 1
    new, label = g.create_control(OP, found[0], found[1])
    print(f"   creator = Nodes[{found[0]}] terminal {found[1]}: control {label!r} on the real op", flush=True)
    if not (new and label and label.startswith("error in")):
        print("STOP: control not created on the real op", flush=True); return 1
    ci_node = found[0]
    g.op(OP).SetControlValue("error in (no error)", (True, 1, "neutralised creator"))
    print("skeleton ExecState", g.exec_state(OP), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: skeleton broken", flush=True); return 1
    ti = lambda: idx("Function", tmsc["uid"])

    pnN = step("PN Diagram.Nodes[]", "+1", lambda: g.build_property(OP, "VI Server:Diagram", [("6375809", False)], (760, 280)))
    uN = pnN[0]["uid"]
    step("TMSC -> PN_N.reference", "accepted", lambda: g.wire(OP, "Function", ti(), "specific class reference", "Property", idx("Property", uN), "reference", branch=True))
    iaN = step("IA_n", "+1", lambda: g.build_index_array(OP, (900, 280)))
    uIN = iaN[0]["uid"]
    step("Nodes[] -> IA_n.array", "+1", lambda: g.wire(OP, "Property", idx("Property", uN), "Nodes[]", "IndexArray", idx("IndexArray", uIN), "array"))
    r = step("control index 2 on IA_n.index", "label 'index 2'", lambda: g.create_control(OP, last_node(), 2))
    if not r or r[1] != "index 2":
        print("STOP: index 2 control", r, flush=True); return 2

    pnT = step("PN Node.Terminals[]", "+1", lambda: g.build_property(OP, "VI Server:Node", [("6359000", False)], (1000, 280)))
    uT = pnT[0]["uid"]
    step("IA_n.element -> PN_T.reference", "+1", lambda: g.wire(OP, "IndexArray", idx("IndexArray", uIN), "element", "Property", idx("Property", uT), "reference"))
    iaT = step("IA_t", "+1", lambda: g.build_index_array(OP, (1150, 280)))
    uIT = iaT[0]["uid"]
    step("Terms[] -> IA_t.array", "+1", lambda: g.wire(OP, "Property", idx("Property", uT), "Terms[]", "IndexArray", idx("IndexArray", uIT), "array"))
    r = step("control index 3 on IA_t.index", "label 'index 3'", lambda: g.create_control(OP, last_node(), 2))
    if not r or r[1] != "index 3":
        print("STOP: index 3 control", r, flush=True); return 3

    # node identity WITHOUT Node.Label/Style (they crash LabVIEW on TMSC/class-constant VIs, spec §30): GObject.UID
    pnS = step("PN Node [UID]", "+1", lambda: g.build_property(OP, "VI Server:Node", [("632A813", False)], (1000, 420)))
    uS = pnS[0]["uid"]
    step("IA_n.element -> PN_S.reference (branch)", "accepted", lambda: g.wire(OP, "IndexArray", idx("IndexArray", uIN), "element", "Property", idx("Property", uS), "reference", branch=True))
    nS = last_node()
    step("indicator UID (node)", "readable", lambda: make_indicator(nS, "UID"))

    pnTm = step("PN Terminal [Name, Connected Wire]", "+1", lambda: g.build_property(OP, "VI Server:Terminal", [("634A004", False), ("634A000", False)], (1300, 280)))
    uTm = pnTm[0]["uid"]
    step("IA_t.element -> PN_Tm.reference", "+1", lambda: g.wire(OP, "IndexArray", idx("IndexArray", uIT), "element", "Property", idx("Property", uTm), "reference"))
    nTm = last_node()
    step("indicator Name", "readable", lambda: make_indicator(nTm, "Name"))
    pnW = step("PN Wire [UID, Is Broken?]", "+1", lambda: g.build_property(OP, "VI Server:Wire", [("632A813", False), ("6371004", False)], (1450, 280)))
    uW = pnW[0]["uid"]

    def cw():
        for term in ("Connected Wire", "Wire", "Conn Wire"):
            try:
                return term, g.wire(OP, "Property", idx("Property", uTm), term, "Property", idx("Property", uW), "reference")
            except Exception as e:
                print(f"   {term!r}: {str(e)[:70]}", flush=True)
        return None
    if not step("PN_Tm.Connected Wire -> PN_W.reference", "one name", cw):
        return 4
    step("PN_Tm.error out -> PN_W.error in", "+1", lambda: g.wire(OP, "Property", idx("Property", uTm), "error out", "Property", idx("Property", uW), "error in (no error)"))
    nW = last_node()
    step("indicator UID 2 (wire)", "readable", lambda: make_indicator(nW, "UID 2"))
    step("indicator Is Broken?", "readable", lambda: make_indicator(nW, "Is Broken?"))
    s0 = g.uids(OP, "SubVI"); g.drop_subvi(OP, CE, 0, (1600, 280))
    uCE = next(o["uid"] for o in g.report(OP, "SubVI") if o["uid"] not in s0)
    step("PN_W.error out -> Clear Errors", "+1", lambda: g.wire(OP, "Property", idx("Property", uW), "error out", "SubVI", idx("SubVI", uCE), "error in (no error)"))
    g.remove_bad_wires_scripted(OP)
    es = g.exec_state(OP)
    print("\nassembled wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - not saving", flush=True); return 5
    print("saved", g.save(OP), flush=True)
    # self-test on OpMove_v0: diagram 0, node 0, terminals 0..3
    vi = g.op(OP); vi.SetControlValue("vi path", os.path.join(g.CLAUDEDEV, "OpMove_v0.vi")); vi.SetControlValue("Class Name", "Diagram"); vi.SetControlValue("index", 0)
    for n in range(3):
        for t in range(4):
            vi.SetControlValue("index 2", n); vi.SetControlValue("index 3", t)
            try:
                g._run(vi)
            except RuntimeError as e:
                print(f"   n={n} t={t}: {str(e)[:40]}", flush=True); break
            print(f"   n={n} t={t}: node uid={vi.GetControlValue('UID')} term={vi.GetControlValue('Name')!r} wire={vi.GetControlValue('UID 2')} broken={vi.GetControlValue('Is Broken?')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
