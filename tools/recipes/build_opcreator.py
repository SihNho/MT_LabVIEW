"""build_opcreator.py - generic op builder for an erdosmiller node CREATOR: Op<Name>_v0.vi places the creator's node on a
target's top-level diagram at 'location (0, 0)'.  Generalises build_opbuildba.py (2026-09-09): copy OpBuildIA_v0, swap the
creator SubVI, wire PN VI.Block Diagram -> 'Diagram in' and the location control, then give every remaining REQUIRED input a
front-panel control (probe terminals until ExecState == 1), purge junk Invokes, save, and test on a scratch target.
  py tools/bgrun.py --max-min 12 --log tools/bench/build_op_<name>.log -- py -u tools/recipes/build_opcreator.py \
        --creator "Create Unflatten from String.vi" --op OpBuildUnflatten_v0 [--max-terms 12] [--no-test]
The creator's inputs that get controls are printed; the Python wrapper is `gscript.build_creator(op_path, target, location,
**controls)`.  ONE COM client at a time.
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
SRC = os.path.join(g.CLAUDEDEV, "OpBuildIA_v0.vi"); TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
g._run.__defaults__ = (6.0, 45.0)


def arg(name, default=None):
    if f"--{name}" in sys.argv:
        i = sys.argv.index(f"--{name}"); return sys.argv[i + 1] if i + 1 < len(sys.argv) else True
    return default


def main():
    creator = os.path.join(EM, arg("creator")); OP = os.path.join(g.CLAUDEDEV, arg("op") + ".vi"); TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_" + arg("op") + "_target.vi")
    max_terms = int(arg("max-terms", 12))
    g._lv = None
    for p in (OP, TGT):
        if os.path.exists(p):
            os.remove(p)
    shutil.copyfile(SRC, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        for o in g.new_since(OP, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(OP, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(OP, "Invoke", ids.index(o["uid"]))
    subs = g.report(OP, "SubVI"); props = g.report(OP, "Property")
    ci = next(i for i, o in enumerate(subs) if o["pos"] == (900, 640)); cx, cy = subs[ci]["pos"]
    g.delete_object(OP, "SubVI", ci); g.remove_bad_wires_scripted(OP)
    sub0 = g.uids(OP, "SubVI"); g.drop_subvi(OP, creator, 0, (cx, cy))
    subs = g.report(OP, "SubVI"); ni = next((i for i, o in enumerate(subs) if o["uid"] not in sub0), None)
    if ni is None:
        print("STOP: creator not dropped", flush=True); return 3
    pi = [o["uid"] for o in g.report(OP, "Property")].index(min(props, key=lambda o: abs(o["pos"][0] - 700) + abs(o["pos"][1] - 380))["uid"])
    w0 = g.count(OP, "Wire")
    try:
        g.wire(OP, "Property", pi, "Diagram", "SubVI", ni, "Diagram in"); print("Diagram in wired", flush=True)
    except Exception as e:
        print("Diagram in:", str(e)[:120], flush=True)
    try:
        g.wire_control(OP, ["location (0, 0)"], "SubVI", ni, ["location (0, 0)"]); print("location wired", flush=True)
    except Exception as e:
        print("location:", str(e)[:120], flush=True)
    n_cre = g.count(OP, "Node") - 1                                   # Nodes[] = creation order; the creator was dropped last
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP); controls = []
    for t in range(0, max_terms):
        if es == 1:
            break
        w1 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n_cre, t)
        if new and lab and g.count(OP, "Wire") > w1:
            purge(); es = g.exec_state(OP); controls.append((t, lab)); print(f"   t{t}: control {lab!r} -> ExecState {es}", flush=True)
            continue
        if new:                                                        # an OUTPUT got an unwired control: remove it
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
            g.remove_bad_wires_scripted(OP); purge()
        print(f"   t{t}: {lab!r} (no input control)", flush=True)
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("\nassembled Wires", g.count(OP, "Wire"), "(base", w0, ") Invokes", g.count(OP, "Invoke"), "ExecState", es, "controls", controls, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 6
    print("saved", g.save(OP), flush=True)
    if arg("no-test"):
        return 0
    shutil.copyfile(TGT_SRC, TGT); g.report(TGT, "SubVI"); g.open_panel(TGT); time.sleep(0.8)
    before = g.uids(TGT, "Node"); tinv0 = g.uids(TGT, "Invoke")
    vi = g.op(OP); vi.SetControlValue("vi path", TGT); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0); vi.SetControlValue("location (0, 0)", [1300, 700])
    try:
        g._run(vi)
    except Exception as e:
        print("test run:", str(e)[:200], flush=True)
    junk = {o["uid"] for o in g.new_since(TGT, "Invoke", tinv0)}
    print("test: new nodes on scratch:", [(o["uid"], o["class"], o["pos"]) for o in g.new_since(TGT, "Node", before) if o["uid"] not in junk], flush=True)
    try:
        g.close_panel(TGT); os.remove(TGT); print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
