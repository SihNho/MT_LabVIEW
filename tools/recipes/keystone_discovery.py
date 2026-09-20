"""keystone_discovery.py — discovery for docs/keystone-op-spec.md "Build plan v2", on a scratch copy.

Run ONLY through the deadline runner:
  py tools/bgrun.py --max-min 15 --log tools/bench/keystone_discovery.log -- py -u tools/recipes/keystone_discovery.py [--keep]

Predictions are printed BEFORE each step; the observation follows. Scratch: claudeDev\SCRATCH_keystone.vi
(copy of OpWire_v1.vi). No deletion step: plan v2 keeps Wire Inputs in place and neutralises it by
running with an empty `Names` array (D6 tests that it then does nothing).
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
CREATOR = os.path.join(EM, "Create Property Node.vi")
SRC = os.path.join(g.CLAUDEDEV, "OpWire_v1.vi")
SCR = os.path.join(g.CLAUDEDEV, "SCRATCH_keystone.vi")
g._run.__defaults__ = (6.0, 60.0)


def counts(t):
    return {c: len(g.report(t, c)) for c in ("SubVI", "Wire", "ControlTerminal", "IndexArray")}


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn()
        print(f"   observed: {obs}", flush=True)
        return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True)
        return None


def main():
    keep = "--keep" in sys.argv
    g._lv = None
    # a stale scratch may still be loaded from an earlier (killed) run: close it before overwriting
    if os.path.exists(SCR):
        step("close stale scratch", "closed or not loaded", lambda: g.close_panel(SCR))
        time.sleep(0.5)
    shutil.copyfile(SRC, SCR)
    g.open_panel(SCR); time.sleep(1.0)
    # H5: after a programmatic panel open, click the window's title bar so LabVIEW's UI loop is
    # released before the next COM Run (release confirmed 20:45 today).
    import lvclick as c
    try:
        L, T, R, B = c.rect("SCRATCH_keystone.vi Front Panel")
        c.act("click", X=min(L + 300, R - 120), Y=T + 10); time.sleep(0.4)
    except Exception as e:
        print("title click skipped:", str(e)[:80], flush=True)
    c0 = counts(SCR); print("baseline", c0, "ExecState", g.exec_state(SCR), flush=True)
    subvi_before = g.uids(SCR, "SubVI")

    step("D1 drop_subvi(Create Property Node.vi)", "+1 SubVI, ExecState 0 (required inputs unwired)",
         lambda: (g.drop_subvi(SCR, CREATOR, 0, (875, 620)), counts(SCR), g.exec_state(SCR)))
    new_subvi = g.new_since(SCR, "SubVI", subvi_before)
    print("   creator uid/pos:", [(o["uid"], o["pos"]) for o in new_subvi], flush=True)
    subs = g.report(SCR, "SubVI")
    ci = next((i for i, o in enumerate(subs) if o["uid"] in {n["uid"] for n in new_subvi}), None)
    ias = g.report(SCR, "IndexArray")
    i327 = next((i for i, o in enumerate(ias) if o["uid"] == 327), None)
    i308 = next((i for i, o in enumerate(ias) if o["uid"] == 308), None)
    gi = next((i for i, o in enumerate(subs) if o["pos"] == (725, 281)), None)   # Get Outputs
    print("   indices: creator", ci, "IA327", i327, "IA308", i308, "GetOutputs", gi, flush=True)

    step("D3a IndexArray327.element -> creator 'Diagram in' (branch)", "connected: Wire +1 or branch accepted",
         lambda: g.wire(SCR, "IndexArray", i327, "element", "SubVI", ci, "Diagram in", branch=True))
    step("D3b IndexArray308.element -> creator 'reference' (branch)", "connected",
         lambda: g.wire(SCR, "IndexArray", i308, "element", "SubVI", ci, "reference", branch=True))

    def d3d():
        for nm in ("error in (no error)", "error in"):
            try:
                return nm, g.wire(SCR, "SubVI", gi, "error out", "SubVI", ci, nm, branch=True)
            except Exception as e:
                print(f"   {nm!r}: {str(e)[:120]}", flush=True)
        return None
    step("D3d GetOutputs.error out -> creator error in (branch)", "connected with one of the two names", d3d)
    print("   counts now", counts(SCR), "ExecState", g.exec_state(SCR), flush=True)

    step("save (gui_save path, allow_broken)", "file mtime moves", lambda: g.save(SCR, allow_broken=True))

    step("D2 copy_into(creator, 'Properties')", "+1 ControlTerminal (array of cluster) on the scratch",
         lambda: (g.copy_into(CREATOR, "Properties", SCR), (g.revert(SCR), None)[1], counts(SCR)))
    g.open_panel(SCR); time.sleep(0.8)
    subs = g.report(SCR, "SubVI")
    ci = next((i for i, o in enumerate(subs) if o["uid"] in {n["uid"] for n in new_subvi}), None)
    step("D3c control 'Properties' -> creator 'Properties'", "Wire +1 (datatype accepted)",
         lambda: g.wire_control(SCR, ["Properties"], "SubVI", ci, ["Properties"]))
    print("\nfinal", counts(SCR), "ExecState", g.exec_state(SCR), flush=True)
    step("save final", "file mtime moves", lambda: g.save(SCR, allow_broken=True))
    if not keep:
        try:
            g.close_panel(SCR)
        except Exception as e:
            print("close_panel:", str(e)[:100])
        try:
            os.remove(SCR); print("scratch deleted", flush=True)
        except Exception as e:
            print("scratch not deleted:", e, flush=True)


if __name__ == "__main__":
    main()
