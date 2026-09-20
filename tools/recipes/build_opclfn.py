"""build_opclfn.py - OpCLFNBuild_v0.vi: create and configure a Call Library Function Node on a target VI entirely by script,
using NI's import-wizard library (resource\\importtools\\sharedlib\\VI\\Block Diagram\\Call Library Node\\...) - plan and peer
review in docs/gpu-backend.md ("Plan: scripted CLFN configuration", archive/peer/2026-09-09-clfn-build-op-plan.md).

Op front panel (all plain data, settable over COM):
  vi path (target) | location (0, 0) | library path | function name | calling convention (0 = C) | reentrant (bool) |
  flat params (binary string: the flattened Parameter Info array, composed in Python) | apply params (bool)
Outputs: flat params out (Flatten of the node's Parameter Info AFTER the set, or of the fresh node when apply=false),
  prototype (string, CallLibrary.Prototype 636D000), n terms (I32 from Parameter Terminals), error out.

Ladder inside the op (base OpBuildIA_v0: Open VI Ref -> PN VI.Block Diagram; creator + Index Array chain removed):
  PN.Diagram -> NI Create.vi (diagram, position) -> Library Path.vi (Set) -> Function Name.vi (Set) -> Calling Convention.vi (Set)
  -> Reentrant.vi (Set) -> Parameter Info.vi (Get) -> [Unflatten (binary string = flat params, type = Get output) ->
  Parameter Info.vi (Set)] -> Parameter Info.vi (Get) -> Flatten -> indicator ; Invoke CallLibrary.Prototype -> indicator ;
  Parameter Terminals.vi -> Array Size -> indicator.
Every NI attribute VI: 'CallLib Refnum' in / 'CallLib Refnum out', 'error in (no error)' / 'error out', 'operation' ring
(Get = 0, Set = 1 per the recovered strings).  Wiring by NAME (g.wire / wire_control); creators via OpBuildFlatten_v0 /
OpBuildUnflatten_v0 / OpBuildIA_v0 / build_invoke; junk Invokes purged; ONE COM client.
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opclfn.log -- py -u tools/recipes/build_opclfn.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

NI = r"C:\Program Files\National Instruments\LabVIEW 2026\resource\importtools\sharedlib\VI\Block Diagram\Call Library Node"
CREATE = os.path.join(NI, "Method", "Create.vi"); ATTR = lambda n: os.path.join(NI, "Attribute", n + ".vi")
SRC = os.path.join(g.CLAUDEDEV, "OpBuildIA_v0.vi"); OP = os.path.join(g.CLAUDEDEV, "OpCLFNBuild_v0.vi")
g._run.__defaults__ = (6.0, 60.0)
STEPS = []
RANK = {}                                                          # SubVI uid -> Nodes[] index (creation order; node_rank() is WRONG in general)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); STEPS.append((name, True)); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); STEPS.append((name, False)); return None


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        for o in g.new_since(OP, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(OP, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(OP, "Invoke", ids.index(o["uid"]))

    def sub_i(uid):
        return [o["uid"] for o in g.report(OP, "SubVI")].index(uid)

    def drop(path, pos):
        purge()                                                        # junk Invokes are appended after; purge BEFORE the drop so ranks stay stable
        before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, 0, pos)
        new = [o for o in g.report(OP, "SubVI") if o["uid"] not in before]; assert len(new) == 1, f"drop {os.path.basename(path)}: {len(new)}"
        RANK[new[0]["uid"]] = g.count(OP, "Node") - 1                   # Nodes[] = creation order: the node just dropped is last
        return new[0]["uid"]
    subs = g.report(OP, "SubVI"); props = g.report(OP, "Property")
    # 1. remove the Index Array creator (900,640) and the Traverse/IA chain is left as is (harmless, unwired outputs)
    ci = next(i for i, o in enumerate(subs) if o["pos"] == (900, 640)); g.delete_object(OP, "SubVI", ci); g.remove_bad_wires_scripted(OP)
    pn = min(props, key=lambda o: abs(o["pos"][0] - 700) + abs(o["pos"][1] - 380)); pi = lambda: [o["uid"] for o in g.report(OP, "Property")].index(pn["uid"])
    # 2. NI chain: Create -> Library Path -> Function Name -> Calling Convention -> Reentrant -> Parameter Info (Get)
    y = 640; x = 900
    u_create = step("drop Create.vi", "+1", lambda: drop(CREATE, (x, y)))
    step("PN.Diagram -> Create.diagram", "+1", lambda: g.wire(OP, "Property", pi(), "Diagram", "SubVI", sub_i(u_create), "diagram"))
    step("location -> Create.position/next to", "+1", lambda: g.wire_control(OP, ["location (0, 0)"], "SubVI", sub_i(u_create), ["position/next to"]))
    chain = [("Library Path", "path"), ("Function Name", "function name"), ("Calling Convention", "calling convention"), ("Reentrant", "reentrant")]
    prev = u_create; xx = x
    for name, ctrl_term in chain:
        xx += 160; u = step(f"drop {name}.vi", "+1", lambda name=name, xx=xx: drop(ATTR(name), (xx, y)))
        step(f"{prev_name(prev, u_create)}.CallLib Refnum out -> {name}.CallLib Refnum", "+1", lambda u=u, prev=prev: g.wire(OP, "SubVI", sub_i(prev), "CallLib Refnum out", "SubVI", sub_i(u), "CallLib Refnum"))
        step(f"error chain -> {name}", "+1", lambda u=u, prev=prev: g.wire(OP, "SubVI", sub_i(prev), "error out", "SubVI", sub_i(u), "error in (no error)"))
        step(f"control -> {name}.{ctrl_term}", "+1 control", lambda u=u, ctrl_term=ctrl_term: control_by_label(u, ctrl_term))
        step(f"control -> {name}.operation (Set)", "+1 control", lambda u=u: control_by_label(u, "operation"))
        prev = u
    # Parameter Info Get, Flatten -> indicator, Unflatten -> Parameter Info Set (gated later by the caller: apply params = leave flat params empty to skip)
    xx += 160; u_get = step("drop Parameter Info.vi (Get)", "+1", lambda: drop(ATTR("Parameter Info"), (xx, y)))
    step("prev -> Get.CallLib Refnum", "+1", lambda: g.wire(OP, "SubVI", sub_i(prev), "CallLib Refnum out", "SubVI", sub_i(u_get), "CallLib Refnum"))
    step("error -> Get", "+1", lambda: g.wire(OP, "SubVI", sub_i(prev), "error out", "SubVI", sub_i(u_get), "error in (no error)"))
    # 3. sample of the fresh node's Parameter Info: Get -> Flatten -> indicator
    u_fl1 = step("OpBuildFlatten: Flatten #1", "+1 FlattenString", lambda: creator_node(OP_FLAT, "FlattenString", (xx + 160, y - 160)))
    step("Get.parameter info out -> Flatten1.anything", "+1", lambda: g.wire(OP, "SubVI", sub_i(u_get), "parameter info out", "FlattenString", cls_i("FlattenString", u_fl1), "anything"))
    ind1 = step("indicator on Flatten1.data string", "label", lambda: indicator_by_label(u_fl1, "data string"))
    # 4. Unflatten (binary string control, type = Get output branch) -> Parameter Info Set
    u_uf = step("OpBuildUnflatten: Unflatten", "+1 FlattenUnflattenString", lambda: creator_node(OP_UNFLAT, "FlattenUnflattenString", (xx + 160, y + 160)))
    step("Get.parameter info out -> Unflatten.type (branch)", "accepted", lambda: g.wire(OP, "SubVI", sub_i(u_get), "parameter info out", "FlattenUnflattenString", cls_i("FlattenUnflattenString", u_uf), "type", branch=True))
    step("control -> Unflatten.binary string", "control", lambda: control_by_label(u_uf, "binary string"))
    step("Get.error out -> Unflatten.error in", "+1", lambda: g.wire(OP, "SubVI", sub_i(u_get), "error out", "FlattenUnflattenString", cls_i("FlattenUnflattenString", u_uf), "error in"))
    xx += 320; u_set = step("drop Parameter Info.vi (Set)", "+1", lambda: drop(ATTR("Parameter Info"), (xx, y)))
    step("Get.CallLib Refnum out -> Set.CallLib Refnum", "+1", lambda: g.wire(OP, "SubVI", sub_i(u_get), "CallLib Refnum out", "SubVI", sub_i(u_set), "CallLib Refnum"))
    step("Unflatten.value -> Set.parameter info", "+1", lambda: g.wire(OP, "FlattenUnflattenString", cls_i("FlattenUnflattenString", u_uf), "value", "SubVI", sub_i(u_set), "parameter info"))
    step("Unflatten.error out -> Set.error in", "+1", lambda: g.wire(OP, "FlattenUnflattenString", cls_i("FlattenUnflattenString", u_uf), "error out", "SubVI", sub_i(u_set), "error in (no error)"))
    step("control -> Set.operation", "control", lambda: control_by_label(u_set, "operation"))
    # 5. read back: Get2 -> Flatten2 -> indicator ; Prototype invoke -> indicator ; Parameter Terminals -> indicator
    xx += 160; u_get2 = step("drop Parameter Info.vi (Get2)", "+1", lambda: drop(ATTR("Parameter Info"), (xx, y)))
    step("Set -> Get2 refnum", "+1", lambda: g.wire(OP, "SubVI", sub_i(u_set), "CallLib Refnum out", "SubVI", sub_i(u_get2), "CallLib Refnum"))
    step("Set -> Get2 error", "+1", lambda: g.wire(OP, "SubVI", sub_i(u_set), "error out", "SubVI", sub_i(u_get2), "error in (no error)"))
    u_fl2 = step("OpBuildFlatten: Flatten #2", "+1", lambda: creator_node(OP_FLAT, "FlattenString", (xx + 160, y - 160)))
    step("Get2.parameter info out -> Flatten2.anything", "+1", lambda: g.wire(OP, "SubVI", sub_i(u_get2), "parameter info out", "FlattenString", cls_i("FlattenString", u_fl2), "anything"))
    ind2 = step("indicator on Flatten2.data string", "label", lambda: indicator_by_label(u_fl2, "data string"))
    indp = None
    inv = step("build_invoke CallLibrary.Prototype (636D000)", "+1 Invoke", lambda: g.build_invoke(OP, "VI Server:CallLibrary", "636D000", (xx + 160, y + 160)))
    if inv:
        ui = inv[0]["uid"]; RANK[ui] = g.count(OP, "Node") - 1
        step("Get2.CallLib Refnum out -> Prototype.reference", "+1", lambda: g.wire(OP, "SubVI", sub_i(u_get2), "CallLib Refnum out", "Invoke", cls_i("Invoke", ui), "reference"))
        indp = step("indicator on Prototype output", "label", lambda: indicator_by_label(ui, "Prototype"))
    xx += 320; u_terms = step("drop Parameter Terminals.vi", "+1", lambda: drop(ATTR("Parameter Terminals"), (xx, y)))
    step("Get2 -> Terminals refnum", "+1", lambda: g.wire(OP, "SubVI", sub_i(u_get2), "CallLib Refnum out", "SubVI", sub_i(u_terms), "CallLib Refnum"))
    step("Get2 -> Terminals error", "+1", lambda: g.wire(OP, "SubVI", sub_i(u_get2), "error out", "SubVI", sub_i(u_terms), "error in (no error)"))
    indt = step("indicator on Terminals.Terms[]", "label", lambda: indicator_by_label(u_terms, "Terms"))
    inde = step("indicator on Terminals.error out", "label", lambda: indicator_by_label(u_terms, "error out"))
    print("\nINDICATORS:", {"flat in": ind1, "flat out": ind2, "prototype": indp, "terms": indt, "error": inde}, flush=True)
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("\nassembled Wires", g.count(OP, "Wire"), "ExecState", es, "steps", STEPS, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 6
    print("saved", g.save(OP), flush=True); return 0


def prev_name(uid, u_create):
    return "Create" if uid == u_create else f"node{uid}"


def control_by_label(uid, wanted, max_terms=12):
    """create a control on the terminal of SubVI `uid` whose auto-label starts with `wanted` (probe t = 0.. ; wrong ones are
    deleted; each probe leaves one junk Invoke, purged by the caller).  Returns the control label or None."""
    n = RANK[uid]
    for t in range(max_terms):
        w0 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n, t)
        if new and lab and lab.lower().startswith(wanted.lower()) and g.count(OP, "Wire") > w0:
            return lab
        if new:
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
            g.remove_bad_wires_scripted(OP)
    return None


OP_FLAT = os.path.join(g.CLAUDEDEV, "OpBuildFlatten_v0.vi"); OP_UNFLAT = os.path.join(g.CLAUDEDEV, "OpBuildUnflatten_v0.vi")


def creator_node(op_path, cls, location):
    """run a creator op (OpBuildFlatten_v0 / OpBuildUnflatten_v0) on OP; returns the new node's uid; ranks it"""
    inv_before = g.uids(OP, "Invoke"); before = g.uids(OP, cls)
    vi = g.op(op_path); vi.SetControlValue("vi path", OP); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0); vi.SetControlValue("location (0, 0)", list(location))
    g._run(vi)
    for o in g.new_since(OP, "Invoke", inv_before):                                   # the op's junk Invoke on OP
        ids = [x["uid"] for x in g.report(OP, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(OP, "Invoke", ids.index(o["uid"]))
    new = g.new_since(OP, cls, before); assert len(new) == 1, f"creator {os.path.basename(op_path)}: {len(new)} new {cls}"
    RANK[new[0]["uid"]] = g.count(OP, "Node") - 1
    return new[0]["uid"]


def cls_i(cls, uid):
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def indicator_by_label(uid, wanted, max_terms=12):
    """create an indicator on the OUTPUT terminal of node `uid` whose auto-label starts with `wanted`; returns the label"""
    n = RANK[uid]
    for t in range(max_terms):
        fp0 = {l for _, l, _ in g.fp_labels(OP)}; w0 = g.count(OP, "Wire")
        new = g.create_indicator(OP, n, t); labs = [l for _, l, _ in g.fp_labels(OP) if l not in fp0]
        if new and labs and labs[-1].lower().startswith(wanted.lower()) and g.count(OP, "Wire") > w0:
            return labs[-1]
        if new:
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
            g.remove_bad_wires_scripted(OP)
    return None


if __name__ == "__main__":
    sys.exit(main())
