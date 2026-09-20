"""build_opclfnparams.py - OpCLFNParams_v0.vi: read AND set the import wizard's `Parameter Info` functional global
(VI\\Block Diagram\\Attribute\\Parameter Info.vi) through FLATTENED data, because COM cannot set an array of clusters.
Why (2026-09-09): NI Method\\Create.vi applies that global to the node it creates; with the global EMPTY LabVIEW dies
(ACCESS_VIOLATION at NULL, minidump d8556cd8/70426c46) as soon as Function Name is valid - variants A/B/C/E all crashed,
D (Path only -> error 1077 before that point) survived.  So the global must hold a valid parameter list BEFORE Create.vi.

Diagram (flat, no error chain between the FGVs - they have none):
  FGV A (Get, default op) --parameters info out--> Flatten To String -> indicators `data string`, `type string`
                          \\-(branch)-> Unflatten From String.type ; control `binary string` -> Unflatten.binary string
  Unflatten.value -> FGV B.`parameters info` ; control `operation` -> FGV B.operation (0 Get = no-op, 1 Set)
  Unflatten.error out -> indicator (keeps the auto-error dialog away when `binary string` is empty)
Run 1 (binary string empty, operation 0): `type string` (I16[] type descriptor) + `data string` of the EMPTY array = the
layout sample.  Run 2 (binary string = Python-composed bytes, operation 1): the global now holds our parameter list.
  py tools/bgrun.py --max-min 12 --log tools/bench/build_opclfnparams.log -- py -u tools/recipes/build_opclfnparams.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

BD = r"C:\Program Files\National Instruments\LabVIEW 2026\resource\importtools\sharedlib\VI\Block Diagram"
FGV = os.path.join(BD, "Attribute", "Parameter Info.vi")
SRC = os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi"); OP = os.path.join(g.CLAUDEDEV, "OpCLFNParams_v0.vi")
OP_FLAT = os.path.join(g.CLAUDEDEV, "OpBuildFlatten_v0.vi"); OP_UNFLAT = os.path.join(g.CLAUDEDEV, "OpBuildUnflatten_v0.vi")
g._run.__defaults__ = (6.0, 45.0)
RANK = {}
STEPS = []


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

    def cls_i(cls, uid):
        return [o["uid"] for o in g.report(OP, cls)].index(uid)

    def drop(path, pos):
        purge(); before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, 0, pos)
        new = [o for o in g.report(OP, "SubVI") if o["uid"] not in before]; assert len(new) == 1, f"drop: {len(new)}"
        RANK[new[0]["uid"]] = g.count(OP, "Node") - 1
        return new[0]["uid"]

    def creator_node(op_path, cls, location):
        purge(); before = g.uids(OP, cls)
        vi = g.op(op_path); vi.SetControlValue("vi path", OP); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0); vi.SetControlValue("location (0, 0)", list(location))
        g._run(vi); purge()
        new = g.new_since(OP, cls, before); assert len(new) == 1, f"creator {os.path.basename(op_path)}: {len(new)} new {cls}"
        RANK[new[0]["uid"]] = g.count(OP, "Node") - 1
        return new[0]["uid"]

    def del_terms(new):
        ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
        for o in new:
            if o["uid"] in ct:
                g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
        g.remove_bad_wires_scripted(OP)

    def control_by_label(uid, wanted, max_terms=16):
        n = RANK[uid]
        for t in range(max_terms):
            w0 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n, t); purge()
            if new and lab and lab.lower().startswith(wanted.lower()) and g.count(OP, "Wire") > w0:
                return lab
            if new:
                del_terms(new)
        return None

    def indicator_by_label(uid, wanted, max_terms=16, keep=True):
        """indicator on the OUTPUT terminal whose auto-label CONTAINS `wanted`; returns the label (= terminal name)"""
        n = RANK[uid]
        for t in range(max_terms):
            fp0 = {l for _, l, _ in g.fp_labels(OP)}; w0 = g.count(OP, "Wire")
            new = g.create_indicator(OP, n, t); purge(); labs = [l for _, l, _ in g.fp_labels(OP) if l not in fp0]
            if new and labs and wanted.lower() in labs[-1].lower() and g.count(OP, "Wire") > w0:
                if not keep:
                    del_terms(new)
                return labs[-1]
            if new:
                del_terms(new)
        return None

    # 0. clear the base
    while g.count(OP, "Node"):
        try:
            g.delete_object(OP, "Node", 0)
        except RuntimeError as e:
            if "expected 1 object gone" not in str(e):
                raise
            break
    g.remove_bad_wires_scripted(OP)
    while g.count(OP, "ControlTerminal"):
        g.delete_object(OP, "ControlTerminal", 0)
    g.remove_bad_wires_scripted(OP); purge()
    print("base cleared: nodes", g.count(OP, "Node"), "ExecState", g.exec_state(OP), flush=True)
    # 1. FGV A (Get) and its output name
    ua = step("drop Parameter Info.vi (A, Get)", "+1 SubVI", lambda: drop(FGV, (300, 320)))
    out_name = step("A output terminal name (probe indicator, then delete it)", "label containing 'info'", lambda: indicator_by_label(ua, "info", keep=False))
    if not out_name:
        print("STOP: FGV output not found", flush=True); return 5
    # 2. Flatten
    ufl = step("OpBuildFlatten: Flatten", "+1 FlattenString", lambda: creator_node(OP_FLAT, "FlattenString", (700, 200)))
    step(f"A.{out_name} -> Flatten.anything", "+1 wire", lambda: g.wire(OP, "SubVI", cls_i("SubVI", ua), out_name, "FlattenString", cls_i("FlattenString", ufl), "anything"))
    ind_d = step("indicator Flatten.data string", "label", lambda: indicator_by_label(ufl, "data string"))
    ind_t = step("indicator Flatten.type string", "label", lambda: indicator_by_label(ufl, "type string"))
    # 3. Unflatten
    uuf = step("OpBuildUnflatten: Unflatten", "+1 FlattenUnflattenString", lambda: creator_node(OP_UNFLAT, "FlattenUnflattenString", (700, 480)))
    step(f"A.{out_name} -> Unflatten.type (branch)", "accepted", lambda: g.wire(OP, "SubVI", cls_i("SubVI", ua), out_name, "FlattenUnflattenString", cls_i("FlattenUnflattenString", uuf), "type", branch=True))
    ctl_bin = step("control Unflatten.binary string", "control", lambda: control_by_label(uuf, "binary string"))
    ind_e = step("indicator Unflatten.error out", "label", lambda: indicator_by_label(uuf, "error out"))
    # 4. FGV B (Set)
    ub = step("drop Parameter Info.vi (B, Set)", "+1 SubVI", lambda: drop(FGV, (1100, 480)))
    step("Unflatten.value -> B.parameters info", "+1 wire", lambda: g.wire(OP, "FlattenUnflattenString", cls_i("FlattenUnflattenString", uuf), "value", "SubVI", cls_i("SubVI", ub), "parameters info"))
    ctl_op = step("control B.operation", "control", lambda: control_by_label(ub, "operation"))
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    labels = {"out_name": out_name, "data string": ind_d, "type string": ind_t, "binary string": ctl_bin, "error out": ind_e, "operation": ctl_op}
    print("\nassembled: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", es, "LABELS", labels, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 6
    print("saved", g.save(OP), flush=True)
    json.dump(labels, open(os.path.join(os.path.dirname(HERE), "bench", "opclfnparams_labels.json"), "w"), indent=1)
    # 5. run 1: layout sample of the EMPTY global
    vi = g.op(OP); vi.SetControlValue(ctl_bin, ""); vi.SetControlValue(ctl_op, 0)
    try:
        g._run(vi)
    except Exception as e:
        print("run1:", str(e)[:200], flush=True)
    for name in (ind_d, ind_t, ind_e):
        try:
            v = vi.GetControlValue(name)
            if isinstance(v, str) and name == ind_d:
                v = v.encode("latin-1").hex()
            print(f"{name} = {repr(v)[:1200]}", flush=True)
        except Exception as e:
            print(name, "EXC", str(e)[:120], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
