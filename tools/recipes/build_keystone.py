"""build_keystone.py — build OpBuildPN_v0.vi (docs/keystone-op-spec.md, Build plan v2) in one batch.

Run ONLY through the deadline runner:
  py tools/bgrun.py --max-min 20 --log tools/bench/build_keystone.log -- py -u tools/recipes/build_keystone.py [--no-test]

Order is chosen so the VI is NEVER saved while broken (scripted edits do not dirty the VI, so the
editor's Ctrl+S is a no-op and COM SaveInstrument blocks on a broken VI — 2026-09-05):
  1. copy OpWire_v1 -> OpBuildPN_v0            (non-broken)
  2. copy_into 'Properties' control from Create Property Node.vi   (control only: non-broken, COM save)
  3. drop the creator, wire Diagram in / reference / Properties / error in / error out
  4. ExecState must be 1 -> COM save. If 0: report and stop (no gui_save).
  5. functional test on a scratch copy of OpFP_v0: ref class 'Property' index 0 -> +1 Property node.
Prediction contract printed before each step.
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402
import lvclick as c  # noqa: E402

EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
CREATOR = os.path.join(EM, "Create Property Node.vi")
SRC = os.path.join(g.CLAUDEDEV, "OpWire_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpBuildPN_v0.vi")
FPT_SRC = os.path.join(g.CLAUDEDEV, "OpFP_v0.vi")
FPT = os.path.join(g.CLAUDEDEV, "SCRATCH_buildpn_target.vi")
g._run.__defaults__ = (6.0, 60.0)


def counts(t):
    return {k: len(g.report(t, k)) for k in ("SubVI", "Wire", "ControlTerminal", "IndexArray", "Property")}


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def title_click(title):
    try:
        L, T, R, B = c.rect(title)
        c.act("click", X=min(L + 300, R - 120), Y=T + 10); time.sleep(0.4)
    except Exception as e:
        print("   title click skipped:", str(e)[:80], flush=True)


def open_released(path):
    g.open_panel(path); time.sleep(1.0)
    title_click(os.path.basename(path) + " Front Panel")


def main():
    g._lv = None
    for p in (OP, FPT):
        if os.path.exists(p):
            try:
                g.close_panel(p)
            except Exception:
                pass
    shutil.copyfile(SRC, OP)
    open_released(OP)
    print("baseline", counts(OP), "ExecState", g.exec_state(OP), flush=True)

    # 2. the array-of-cluster control, while the VI is still healthy
    ct0 = g.uids(OP, "ControlTerminal")
    step("copy_into(creator, 'Properties')", "+1 ControlTerminal; file replaced; ExecState stays 1",
         lambda: (g.copy_into(CREATOR, "Properties", OP), (g.revert(OP), None)[1]))
    open_released(OP)
    new_ct = g.new_since(OP, "ControlTerminal", ct0)
    print("   new control terminals:", [(o["uid"], o["pos"]) for o in new_ct], "ExecState", g.exec_state(OP), flush=True)
    if not new_ct:
        print("STOP: Properties control not copied", flush=True); return 2

    # 3. creator + wires
    sub0 = g.uids(OP, "SubVI")
    step("drop_subvi(creator)", "+1 SubVI, ExecState 0", lambda: (g.drop_subvi(OP, CREATOR, 0, (875, 620)), g.exec_state(OP)))
    subs = g.report(OP, "SubVI")
    ci = next((i for i, o in enumerate(subs) if o["uid"] not in sub0), None)
    gi = next((i for i, o in enumerate(subs) if o["pos"] == (725, 281)), None)      # Get Outputs
    sinks = [i for i, o in enumerate(subs) if o["pos"] in ((980, 470), (980, 540))]   # Clear Errors x2
    ias = g.report(OP, "IndexArray")
    i327 = next(i for i, o in enumerate(ias) if o["uid"] == 327)
    i308 = next(i for i, o in enumerate(ias) if o["uid"] == 308)
    print("   indices creator", ci, "GetOutputs", gi, "sinks", sinks, flush=True)
    step("IA327.element -> Diagram in", "branch accepted", lambda: g.wire(OP, "IndexArray", i327, "element", "SubVI", ci, "Diagram in", branch=True))
    step("IA308.element -> reference", "branch accepted", lambda: g.wire(OP, "IndexArray", i308, "element", "SubVI", ci, "reference", branch=True))
    step("GetOutputs.error out -> error in (no error)", "branch accepted", lambda: g.wire(OP, "SubVI", gi, "error out", "SubVI", ci, "error in (no error)", branch=True))
    step("control Properties -> Properties", "Wire +1", lambda: g.wire_control(OP, ["Properties"], "SubVI", ci, ["Properties"]))
    for si in sinks:
        r = step(f"creator error out -> sink {si}", "Wire +1 or branch", lambda si=si: g.wire(OP, "SubVI", ci, "error out", "SubVI", si, "error in (no error)", branch=True))
        if r is not None:
            break
    es = g.exec_state(OP)
    print("\nassembled", counts(OP), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: VI still broken - an input is missing (check location / reference typing); NOT saving", flush=True)
        return 3
    step("COM save", "size > 0", lambda: g.save(OP))

    if "--no-test" in sys.argv:
        return 0
    # 5. functional test: make a Property node on a scratch copy of OpFP_v0 by referencing ITS Property node
    shutil.copyfile(FPT_SRC, FPT)
    open_released(FPT)
    before = g.uids(FPT, "Property")
    vi = g.op(OP)
    vi.SetControlValue("vi path", FPT)
    vi.SetControlValue("Class Name", "Property"); vi.SetControlValue("index", 0)
    vi.SetControlValue("Names", [])                                   # neutralise Wire Inputs
    vi.SetControlValue("Class Name 2", "Diagram"); vi.SetControlValue("index 2", 0)
    vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Properties", g.cluster_array([("Position", False)]))
    step("RUN OpBuildPN_v0 on scratch OpFP copy", "error out clean; +1 Property on the scratch",
         lambda: (g._run(vi), g._err(vi), [(o["uid"], o["pos"]) for o in g.new_since(FPT, "Property", before)]))
    try:
        g.close_panel(FPT); os.remove(FPT); print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
