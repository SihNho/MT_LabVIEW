"""build_opctrlvalue.py - OpCtrlValue_v0.vi: read a front-panel control's VALUE through a Control reference.

This is step 1 of the UI-thread measurement (gate G1 of docs/restructure-plan-4.6.md), and it is deliberately the
smallest possible step so a failure is cheap.

WHY IT MATTERS. Reading `ASI_adjust focus-subvi.vi` showed the frame loop's only unconditional per-frame cost besides
the tracking kernel is **two `Value` property nodes** (uids 46 and 108). A `Value` property node always executes in the
**UI thread**, so its latency is not a constant - it queues behind whatever else the UI thread is doing, panel redraws
included. That is a concrete mechanism for the user's report that turning the image display on destabilises frames. But
nobody has measured the size: at ~50 us per read it is a footnote, at ~2 ms it is a third of the 6.00 ms budget at
150 Hz and it becomes the main target of the whole restructuring.

WHY THIS DONOR. `OpFPLabels_v0.vi` already contains, verified by reading its diagram:

    Property(VI -> `Panel`) -> Property(Panel -> `Controls[]`) -> Index Array -> Property(Control -> `Label`,
    `Indicator`) -> Property(Text -> `Text`)

so a **Control reference already exists at runtime** partway down that chain. Wiring a control reference into a
property node by script has never been done in this project and was listed as the unproven step; this route avoids it
entirely, because the reference is already there. Only the property read off it changes, `Label` -> `Value`.

`Control.Value` returns a **variant**; wiring it to a Variant indicator lets ActiveX marshal it to Python with no
`Variant To Data` node - the same trick planned for OpConstValue_v0, and the reason no new primitive is needed.

WHAT THIS IS NOT. One call through this op is dominated by COM round-trip cost, so it does **not** by itself give a
per-read figure. It is the building block: the timing harness puts the read inside a LabVIEW loop so that N reads cost
one COM call. Building that loop is step 2, and it only makes sense once this step works.

  py tools/bgrun.py --max-min 20 --log tools/bench/build_opctrlvalue.log -- py -u tools/recipes/build_opctrlvalue.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpCtrlValue_v0.vi")
PROBE = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")     # a VI with known controls, used as the read target
g._run.__defaults__ = (6.0, 60.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn()
        print(f"   observed: {obs}", flush=True)
        STEPS.append((name, True))
        return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True)
        STEPS.append((name, False))
        return None


def main():
    g._lv = None
    # never touch the target through VI Server before overwriting it (the "changed on disk / corrupt VI" modal)
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.open_panel(OP)                       # a target loaded only via GetVIReference declines every edit SILENTLY
    time.sleep(0.8)

    before = step("1 donor inventory", "4 Property nodes, 1 IndexArray, ExecState 1",
                  lambda: ({c: g.count(OP, c) for c in ("Property", "IndexArray", "Node", "Wire")},
                           g.exec_state(OP)))

    nodes = step("2 locate the Control property node (the one reading Label + Indicator)",
                 "one node whose terminals include 'Label' and 'Indicator'",
                 lambda: [(i, uid, [nm for _, nm, _ in terms if nm])
                          for i, (uid, lbl, terms) in g.net_map(OP, diagram_index=0, max_nodes=40,
                                                                max_terms=16)[0].items()])
    if nodes:
        for i, uid, names in nodes:
            if "Label" in names and "Indicator" in names:
                print(f"   -> target node index {i}, uid {uid}, terminals {names}", flush=True)

    # The donor's chain is confirmed: Property(uid 112 `Panel`) -> Property(113 `Controls[]`) -> IndexArray(308)
    # -> Property(114 `Label`,`Indicator`) -> Property(115 `Text`). uid 114 is the node sitting on a **Control
    # reference**, which is the reference this measurement needs and which nothing in the fleet could otherwise
    # produce. Swapping the property it reads is therefore the whole job.
    #
    # No op re-points an existing property node's property (build_property CREATES one), so this is delete + build +
    # rewire. The two downstream nodes (115 `Text`, and the Clear Errors pair) are collateral: `Text.Text` only makes
    # sense on a Label reference, so it goes too.
    def idx(cls, uid):
        return [o["uid"] for o in g.report(OP, cls)].index(uid)

    pos114 = next((o["pos"] for o in g.report(OP, "Property") if o["uid"] == 114), (520, 300))
    step("3 delete the Text property node (uid 115) - meaningless without a Label reference",
         "Property 4 -> 3",
         lambda: (g.delete_object(OP, "Property", idx("Property", 115)), g.count(OP, "Property"))[1])
    step("4 delete the Label/Indicator property node (uid 114)", "Property 3 -> 2",
         lambda: (g.delete_object(OP, "Property", idx("Property", 114)), g.count(OP, "Property"))[1])
    step("5 clean up the wires those deletions orphaned", "no error",
         lambda: g.remove_bad_wires(OP))
    # build_property takes (property_unique_id, is_write) pairs and the FULL class string - not a bare name.
    # Control.Value = 633200D, already registered in docs/vi-server-ids.json; read, so is_write=False.
    pn = step("6 build Property('VI Server:Control', [Control.Value read]) where uid 114 was", "Property 2 -> 3",
              lambda: g.build_property(OP, "VI Server:Control", [("633200D", False)], pos114))
    new_i = step("6b index of the new Property node", "the last one",
                 lambda: g.count(OP, "Property") - 1)
    step("7 wire IndexArray.element -> the new node's `reference`", "Wire count +1",
         lambda: g.wire(OP, "IndexArray", idx("IndexArray", 308), "element",
                        "Property", new_i, "reference"))
    # wire_indicators only BRANCHES onto indicators that already exist; the donor's were deleted with their nodes,
    # so the Value output needs a NEW indicator - that is create_indicator. Two traps here, both already paid for
    # elsewhere in this project: create_indicator indexes **Nodes[]**, which is a different ordering from the
    # Property-class index used above, and the terminal index must be READ rather than guessed.
    def value_terminal():
        nodes, _ = g.net_map(OP, diagram_index=0, max_nodes=40, max_terms=16)
        for n, (uid, lbl, terms) in nodes.items():
            names = [nm for _, nm, _ in terms if nm]
            if "Value" in names and "reference" in names:
                t = next(t for t, nm, _ in terms if nm == "Value")
                print(f"   new node is Nodes[{n}] uid {uid}, `Value` is terminal {t}, terminals {names}", flush=True)
                return n, t
        raise RuntimeError("no node with both `reference` and `Value` terminals - the property did not take")

    nt = step("8a locate the new node in Nodes[] order and find its `Value` terminal",
              "one node carrying both `reference` and `Value`", value_terminal)
    if nt:
        step("8b create an indicator on `Value` so ActiveX marshals the variant to Python",
             "a new front-panel indicator appears",
             lambda: g.create_indicator(OP, nt[0], nt[1]))
    st = step("9 save", "ExecState 1",
              lambda: (g.save(OP), g.exec_state(OP))[1])

    print("\nsteps:", STEPS, flush=True)
    print("final ExecState:", st, flush=True)
    print("counts:", {c: g.count(OP, c) for c in ("Property", "IndexArray", "Node", "Wire")}, flush=True)
    return 0 if st == 1 else 1


if __name__ == "__main__":
    sys.exit(main())
