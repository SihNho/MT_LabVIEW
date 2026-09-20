"""build_opbuildcase_v1b.py - stage 2 of OpBuildCase_v1: feed the creator's REFNUM inputs from control NAMES.

Stage 1 (build_opbuildcase_v1.py) put `Get Controls.vi` on the diagram with a `Control Names` control, fed by the VI.Block
Diagram property node.  Its `Control Terminals` output is the array of terminal refnums Python cannot make.

Stage 2 rewires the creator:
  * the `Inputs` refnum-array control (useless over COM) is deleted; `Control Terminals` of a SECOND Get Controls node
    (`Control Names 2` = the input control names) goes straight into the creator's `Inputs`
  * the `Selector` refnum control is deleted; an Index Array on the FIRST Get Controls' `Control Terminals` gives the single
    terminal refnum for the creator's `Selector`
Result: py drives it with plain strings -> build_case(target, location, frames, selector_name, input_names).
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opbuildcase_v1b.log -- py -u tools/recipes/build_opbuildcase_v1b.py
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
GETCTL = os.path.join(EM, "Get Controls.vi")
OP = os.path.join(g.CLAUDEDEV, "OpBuildCase_v1.vi"); OP_IA = os.path.join(g.CLAUDEDEV, "OpBuildIA_v0.vi")
g._run.__defaults__ = (6.0, 60.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); STEPS.append((name, True)); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); STEPS.append((name, False)); return None


def main():
    g._lv = None
    g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    print("op: nodes", g.count(OP, "Node"), "SubVIs", g.count(OP, "SubVI"), "wires", g.count(OP, "Wire"),
          "ExecState", g.exec_state(OP), flush=True)
    print("fp:", [l for _, l, _ in g.fp_labels(OP)], flush=True)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        for o in g.new_since(OP, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(OP, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(OP, "Invoke", ids.index(o["uid"]))

    def sub_i(uid):
        return [o["uid"] for o in g.report(OP, "SubVI")].index(uid)

    subs = g.report(OP, "SubVI")
    print("SubVIs:", [(i, o["uid"], o["pos"]) for i, o in enumerate(subs)], flush=True)
    creator = max(subs, key=lambda o: o["pos"][0])                          # Create Case Structure.vi, dropped rightmost
    gc1 = min(subs, key=lambda o: abs(o["pos"][0] - (creator["pos"][0] - 260)) + abs(o["pos"][1] - (creator["pos"][1] + 180)))
    print("creator:", creator["uid"], creator["pos"], "| Get Controls #1:", gc1["uid"], gc1["pos"], flush=True)
    props = g.report(OP, "Property"); pn = props[0] if props else None
    # 1. drop Get Controls #2 (for the input tunnels)
    def drop(path, pos):
        purge(); before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, 0, pos)
        new = [o for o in g.report(OP, "SubVI") if o["uid"] not in before]; assert len(new) == 1
        return new[0]["uid"]
    gc2 = step("drop Get Controls #2", "+1 SubVI", lambda: drop(GETCTL, (gc1["pos"][0], gc1["pos"][1] + 160)))
    if gc2 is None:
        return 3
    if pn is not None:
        step("PN.Diagram -> GC2.'Diagram in' (branch)", "accepted",
             lambda: g.wire(OP, "Property", 0, "Diagram", "SubVI", sub_i(gc2), "Diagram in", branch=True))
    n_gc2 = g.count(OP, "Node") - 1
    lab2 = step("control on GC2.'Control Names'", "label", lambda: _ctl(OP, n_gc2, "Control Names", purge))
    # 2. free the creator's refnum inputs: delete the Selector / Inputs controls (their wires go with them)
    for name in ("Inputs", "Selector"):
        step(f"delete the refnum control {name!r}", "gone", lambda name=name: g.delete_by_label(OP, name, allow_broken=True))
    purge(); g.remove_bad_wires_scripted(OP)
    print("   after deleting the refnum controls: wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)
    # 3. GC2.'Control Terminals' -> creator.'Inputs'   (array of terminal refnums, exactly what the creator wants)
    step("GC2.'Control Terminals' -> creator.'Inputs'", "+1 wire",
         lambda: g.wire(OP, "SubVI", sub_i(gc2), "Control Terminals", "SubVI", sub_i(creator["uid"]), "Inputs"))
    # 4. Index Array on GC1.'Control Terminals' -> creator.'Selector'
    terms = g.report(OP, "Terminal")
    owned = [(i, o) for i, o in enumerate(terms) if o.get("owner") in (gc1["uid"], str(gc1["uid"]))]
    print("   Terminals owned by GC1:", [(i, o["uid"], o["pos"]) for i, o in owned][:12], flush=True)
    made = None
    for i, o in owned:
        vi = g.op(OP_IA); vi.SetControlValue("vi path", OP); vi.SetControlValue("Class Name", "Terminal")
        vi.SetControlValue("index", i); vi.SetControlValue("location (0, 0)", [gc1["pos"][0] + 150, gc1["pos"][1] - 60])
        before = g.uids(OP, "IndexArray")
        try:
            g._run(vi)
        except Exception as e:
            print(f"   IA from Terminal[{i}]: EXC {str(e)[:120]}", flush=True); purge(); continue
        purge(); new = g.new_since(OP, "IndexArray", before)
        if not new:
            continue
        ia = new[0]["uid"]; ia_i = [x["uid"] for x in g.report(OP, "IndexArray")].index(ia)
        try:
            g.wire(OP, "IndexArray", ia_i, "element", "SubVI", sub_i(creator["uid"]), "Selector")
            made = (i, ia); print(f"   IA from Terminal[{i}] -> Selector: OK (ExecState {g.exec_state(OP)})", flush=True); break
        except Exception as e:
            print(f"   IA from Terminal[{i}] -> Selector: {str(e)[:120]}", flush=True)
            ids = [x["uid"] for x in g.report(OP, "IndexArray")]
            if ia in ids:
                g.delete_object(OP, "IndexArray", ids.index(ia))
            g.remove_bad_wires_scripted(OP)
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("\nassembled: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", es,
          "\nfp:", [l for _, l, _ in g.fp_labels(OP)], "\nIndex Array:", made, "\nsteps failed:", [n for n, ok in STEPS if not ok], flush=True)
    if es != 1 or made is None:
        print("STOP: not saving", flush=True); return 5
    print("saved", g.save(OP), flush=True)
    return 0


def _ctl(OP, n, wanted, purge, max_terms=14):
    for t in range(max_terms):
        w0 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n, t); purge()
        if new and lab and lab.lower().startswith(wanted.lower()) and g.count(OP, "Wire") > w0:
            return lab
        if new:
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
            g.remove_bad_wires_scripted(OP)
    return None


if __name__ == "__main__":
    sys.exit(main())
