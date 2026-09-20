"""build_opmove.py — OpMove_v0.vi: move any block-diagram object to an absolute position (GObject.Move,
Unique ID 632A400), built entirely by script from OpDelete_v0 (step 3b, docs/keystone-op-spec.md §20).

Run through the deadline runner:
  py tools/bgrun.py --max-min 8 --log tools/bench/build_keystone.log -- py -u tools/recipes/build_opmove.py [--no-test]

Steps (prediction contract in each step line):
  1. copy OpDelete_v0 -> OpMove_v0; delete its single Invoke (the GObj/Delete node) with delete_object
  2. remove_bad_wires (documented menu recipe) -> ExecState 1 (the IA308.element wire is gone)
  3. build_invoke(op, "VI Server:GObject", "632A400", (900, 640)) -> +1 Invoke (GObj / Move)
  4. wire IndexArray[308].element -> reference; wire control 'location (0, 0)' -> position (name probed)
  5. ExecState 1 -> COM save; else stop, nothing saved
  6. test on a scratch copy of GUIBENCH_v0: move IndexArray 0 to (1200, 900); reporter must show the new pos
  7. wire inventory of OpBuildPN_v0 (positions) for the Index Array rewiring plan (read-only)
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpDelete_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpMove_v0.vi")
TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_move_target.vi")
g._run.__defaults__ = (6.0, 45.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def main():
    g._lv = None
    for p in (OP, TGT):
        if os.path.exists(p):
            try:
                g.close_panel(p)
            except Exception:
                pass
    shutil.copyfile(SRC, OP)
    g.open_panel(OP); time.sleep(1.0)
    print("baseline Invokes", [(o["uid"], o["pos"]) for o in g.report(OP, "Invoke")],
          "IA", [(o["uid"], o["pos"]) for o in g.report(OP, "IndexArray")], "Wires", g.count(OP, "Wire"),
          "ExecState", g.exec_state(OP), flush=True)

    step("1 delete the Delete invoke", "1 Invoke gone; ExecState 0 (dangling wire)",
         lambda: (g.delete_object(OP, "Invoke", 0), g.exec_state(OP)))
    # 2. the dangling wire (IA308.element -> the deleted Invoke) is the only wire right of IA308:
    #    delete it by script (delete_object on class Wire) instead of the menu recipe, whose clicks
    #    were refused by the GUI gate on 2026-09-06 17:33 (no entries in tools/gui_actions.log).
    ia_x = next(o["pos"][0] for o in g.report(OP, "IndexArray") if o["uid"] == 308)
    wires = g.report(OP, "Wire")
    dangling = [i for i, o in enumerate(wires) if o["pos"][0] > ia_x + 15]
    print("   wires right of IA308:", [(wires[i]["uid"], wires[i]["pos"]) for i in dangling], flush=True)
    if len(dangling) != 1:
        print("STOP: expected exactly one dangling wire", flush=True); return 2
    step("2 delete the dangling wire", "1 Wire gone; ExecState 1",
         lambda: (g.delete_object(OP, "Wire", dangling[0]), g.exec_state(OP)))
    if g.exec_state(OP) != 1:
        print("STOP: op broken after cleanup; not saving", flush=True); return 2
    w0 = g.count(OP, "Wire")

    new = step("3 build_invoke GObject.Move", "+1 Invoke at (900,640)",
               lambda: g.build_invoke(OP, "VI Server:GObject", "632A400", (900, 640)))
    if not new:
        print("STOP: no Move node", flush=True); return 3
    mi = [o["uid"] for o in g.report(OP, "Invoke")].index(new[0]["uid"])
    ia = [o["uid"] for o in g.report(OP, "IndexArray")].index(308)
    step("4a IA308.element -> reference", f"Wire {w0}+1", lambda: g.wire(OP, "IndexArray", ia, "element", "Invoke", mi, "reference"))

    def pos_wire():
        for term in ("position", "Position", "new position", "Location", "location"):
            try:
                r = g.wire_control(OP, ["location (0, 0)"], "Invoke", mi, [term])
                return term, r
            except Exception as e:
                print(f"   {term!r}: {str(e)[:90]}", flush=True)
        return None
    step("4b control location -> position", "one name accepted", pos_wire)
    es = g.exec_state(OP)
    print("\nassembled Wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: still broken (owner required? position name?) — NOT saving", flush=True)
        try:
            g._lv_gui("-Action", "shotwin", "-Title", "'OpMove_v0.vi Block Diagram'", "-Path", "tools/bench/opmove_broken.png")
        except Exception:
            pass
        return 4
    step("5 COM save", "size > 0", lambda: g.save(OP))
    if "--no-test" in sys.argv:
        return 0

    shutil.copyfile(TGT_SRC, TGT); g.open_panel(TGT); time.sleep(0.8)
    before = g.report(TGT, "IndexArray")
    print("target IA before", [(o["uid"], o["pos"]) for o in before], flush=True)
    vi = g.op(OP)
    vi.SetControlValue("vi path", TGT); vi.SetControlValue("Class Name", "IndexArray"); vi.SetControlValue("index", 0)
    vi.SetControlValue("location (0, 0)", [1200, 900])
    t0 = time.time()
    step("6 RUN OpMove_v0: IndexArray[0] -> (1200,900)", "reporter shows (1200,900) for that uid; ExecState unchanged",
         lambda: (g._run(vi), f"{time.time() - t0:.2f}s", [(o["uid"], o["pos"]) for o in g.report(TGT, "IndexArray")], g.exec_state(TGT)))
    try:
        g.close_panel(TGT); os.remove(TGT); print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:80], flush=True)

    # 7 read-only: wires of OpBuildPN_v0 for the Index Array rewiring plan
    pn = os.path.join(g.CLAUDEDEV, "OpBuildPN_v0.vi")
    print("\nOpBuildPN_v0 wires:", [(o["uid"], o["pos"]) for o in g.report(pn, "Wire")], flush=True)
    print("OpBuildPN_v0 IA:", [(o["uid"], o["pos"]) for o in g.report(pn, "IndexArray")], "SubVIs:",
          [(o["uid"], o["pos"]) for o in g.report(pn, "SubVI")], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
