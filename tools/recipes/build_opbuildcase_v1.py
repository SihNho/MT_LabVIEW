"""build_opbuildcase_v1.py - OpBuildCase_v1.vi: a Case Structure that Python can actually drive.

Why v0 is not enough (measured 2026-09-09, docs/NAMES.md): erdosmiller `Create Case Structure.vi` takes `Selector` (a terminal
refnum) and `Inputs` (an array of terminal refnums), and COM cannot produce a refnum — so v0's controls stay empty, the creator
calls Connect Wire with an invalid reference and every run raises an error-1055 modal dialog. The Case Structure is created, but
unattended runs are blocked and no selector or input tunnel is wired.

v1 applies the fleet's standing answer to exactly this problem (OpWireCtl): take the terminals as NAMES and resolve them to
refnums INSIDE the op.

  controls (all plain data, settable over COM):
    vi path | location (0, 0) | frames (I32) | selector control name (string) | input control names (string array)
  diagram:
    Open VI Reference -> PN VI.Block Diagram ─┬─> Get Controls.vi (`Control Names` = selector name + input names)
                                             └─> Create Case Structure.vi  (Diagram in, location,
                                                   Selector  <- Index Array(Control Terminals, 0),
                                                   Inputs    <- Array Subset(Control Terminals, 1..),
                                                   Frames)
    creator error out -> indicator (no dialog)

Built from OpBuildCase_v0 (which already has the creator + Diagram/location wiring) by adding the Get Controls chain.
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opbuildcase_v1.log -- py -u tools/recipes/build_opbuildcase_v1.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
GETCTL = os.path.join(EM, "Get Controls.vi"); IA = os.path.join(EM, "Create Index Array.vi")
SRC = os.path.join(g.CLAUDEDEV, "OpBuildCase_v0.vi"); OP = os.path.join(g.CLAUDEDEV, "OpBuildCase_v1.vi")
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
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    print("copy of v0: nodes", g.count(OP, "Node"), "SubVIs", g.count(OP, "SubVI"), "wires", g.count(OP, "Wire"),
          "ExecState", g.exec_state(OP), flush=True)
    print("front panel:", [l for _, l, _ in g.fp_labels(OP)], flush=True)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        for o in g.new_since(OP, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(OP, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(OP, "Invoke", ids.index(o["uid"]))

    def sub_i(uid):
        return [o["uid"] for o in g.report(OP, "SubVI")].index(uid)
    # locate the creator (the Create Case Structure.vi node) and the VI.Block Diagram property node
    subs = g.report(OP, "SubVI"); props = g.report(OP, "Property")
    print("SubVIs:", [(i, o["uid"], o["pos"]) for i, o in enumerate(subs)], flush=True)
    print("Property nodes:", [(o["uid"], o["pos"]) for o in props], flush=True)
    creator = max(subs, key=lambda o: o["pos"][0])                          # dropped last, rightmost
    print("creator (rightmost SubVI):", creator["uid"], creator["pos"], flush=True)
    # drop Get Controls.vi and wire the diagram into it
    uG = step("drop Get Controls.vi", "+1 SubVI", lambda: _drop(OP, GETCTL, (creator["pos"][0] - 260, creator["pos"][1] + 180), purge))
    if uG is None:
        return 3
    pn = min(props, key=lambda o: abs(o["pos"][0] - 700) + abs(o["pos"][1] - 380)) if props else None
    if pn is not None:
        step("PN.Diagram -> Get Controls.'Diagram in' (branch)", "accepted",
             lambda: g.wire(OP, "Property", [o["uid"] for o in g.report(OP, "Property")].index(pn["uid"]), "Diagram",
                            "SubVI", sub_i(uG), "Diagram in", branch=True))
    step("control 'Control Names' on Get Controls", "control",
         lambda: _ctl(OP, uG, "Control Names", purge))
    print("\nfront panel now:", [l for _, l, _ in g.fp_labels(OP)], flush=True)
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("assembled so far: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    print("steps failed:", [n for n, ok in STEPS if not ok], flush=True)
    print("\nNEXT (needs the Control Terminals -> Selector/Inputs wiring, which requires Index Array + Array Subset creators):",
          "\n  Get Controls.'Control Terminals' -> Index Array[0] -> creator.Selector",
          "\n  Get Controls.'Control Terminals' -> Array Subset[1..] -> creator.Inputs", flush=True)
    if es == 1:
        print("saved", g.save(OP), flush=True)
    else:
        print("NOT saved (ExecState != 1)", flush=True)
    return 0


def _drop(OP, path, pos, purge):
    purge(); before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, 0, pos)
    new = [o for o in g.report(OP, "SubVI") if o["uid"] not in before]; assert len(new) == 1, f"drop: {len(new)}"
    return new[0]["uid"]


def _ctl(OP, uid, wanted, purge, max_terms=14):
    n = g.count(OP, "Node") - 1
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
