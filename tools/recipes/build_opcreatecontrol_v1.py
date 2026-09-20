"""build_opcreatecontrol_v1.py — OpCreateControl_v1.vi = OpCreateControl_v0 + the created control's LABEL reported
on the op's front panel: Invoke 'Create Control' output (Control ref) -> PN Control.Label (6332005) -> PN
Text.Text (632D800) -> indicator (made by OpCreateIndicator_v0 on the op itself; expected label 'Text').
Zero GUI (spec §26).

Run through the deadline runner (bgrun --max-min 8) as tools/recipes/build_opcreatecontrol_v1.py [--no-test]

Steps:
  1. copy OpCreateControl_v0 -> OpCreateControl_v1 (ExecState 1)
  2. build_property Control.Label at (850,450); wire Invoke 'Create Control' -> reference
  3. build_property Text.Text at (950,450); wire PN4 'Label' -> reference  -> ExecState 1
  4. indicator on PN5's 'Text' output: OpCreateIndicator_v0 on the op, node = count(Node)-1 (PN5 is the newest),
     terminal t swept 0..5 until a new ControlTerminal appears AND GetControlValue('Text') works
  5. ExecState 1 -> COM save; test on a scratch GUIBENCH copy: node 11 (IA534) terminals 2, 0, 1 -> the op's
     'Text' indicator reports the label of each created control (print it)
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpCreateControl_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpCreateControl_v1.vi")
OP_CI = os.path.join(g.CLAUDEDEV, "OpCreateIndicator_v0.vi")
TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_cc1_target.vi")
g._run.__defaults__ = (6.0, 45.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def idx(cls, uid):
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def create_indicator(target, node_index, term):
    before = g.uids(target, "ControlTerminal")
    vi = g.op(OP_CI)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue("index", node_index); vi.SetControlValue("index 2", term)
    try:
        g._run(vi)
    except RuntimeError as e:
        if "modal dialog" not in str(e):
            raise
    return g.new_since(target, "ControlTerminal", before)


def text_readable():
    try:
        g.op(OP).GetControlValue("Text"); return True
    except Exception:
        return False


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
    print("baseline Wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)
    ui = g.report(OP, "Invoke")[0]["uid"]

    pn4 = step("2 build_property Control.Label", "+1 Property", lambda: g.build_property(OP, "VI Server:Control", [("6332005", False)], (850, 450)))
    if not pn4:
        return 2
    u4 = pn4[0]["uid"]
    step("2a Invoke 'Create Control' -> PN4.reference", "Wire +1", lambda: g.wire(OP, "Invoke", idx("Invoke", ui), "Create Control", "Property", idx("Property", u4), "reference"))
    pn5 = step("3 build_property Text.Text", "+1 Property", lambda: g.build_property(OP, "VI Server:Text", [("632D800", False)], (950, 450)))
    if not pn5:
        return 3
    u5 = pn5[0]["uid"]
    step("3a PN4.Label -> PN5.reference", "Wire +1", lambda: g.wire(OP, "Property", idx("Property", u4), "Label", "Property", idx("Property", u5), "reference"))
    print("   ExecState", g.exec_state(OP), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: broken after PNs", flush=True); return 4

    n = g.count(OP, "Node")
    hit = None
    forced = [int(a.split("=")[1]) for a in sys.argv if a.startswith("--text-term=")]
    order = forced if forced else list(range(6))
    strays = 0
    for t in order:
        new = create_indicator(OP, n - 1, t)
        ok = text_readable()
        labels = []
        for nm in ("Text", "reference", "reference out", "error in (no error)", "error out", "error in", "Label", "Text 2"):
            try:
                g.op(OP).GetControlValue(nm); labels.append(nm)
            except Exception:
                pass
        print(f"   PN5 terminal {t}: new {[(o['uid'], o['pos']) for o in new]} 'Text' readable={ok} labels={labels} ExecState {g.exec_state(OP)}", flush=True)
        if new and ok:
            hit = t; break
        if new:
            strays += 1
    if hit is None:
        print("STOP: no 'Text' indicator created on PN5", flush=True); return 5
    if strays:
        print(f"DISCOVERY: 'Text' output is terminal {hit}; {strays} stray indicator(s) were made - NOT saving. Rerun with --text-term={hit}", flush=True); return 7
    es = g.exec_state(OP)
    print("assembled Wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 6
    step("5 COM save", "size > 0", lambda: g.save(OP))
    if "--no-test" in sys.argv:
        return 0

    shutil.copyfile(TGT_SRC, TGT); g.open_panel(TGT); time.sleep(0.8)
    vi = g.op(OP)
    vi.SetControlValue("vi path", TGT); vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    for t in (2, 0, 1):
        before = g.uids(TGT, "ControlTerminal")
        vi.SetControlValue("index", 11); vi.SetControlValue("index 2", t)
        try:
            g._run(vi)
        except Exception as e:
            print(f"   run {str(e)[:60]}", flush=True)
        new = g.new_since(TGT, "ControlTerminal", before)
        print(f"   IA534 terminal {t}: new {[(o['uid'], o['pos']) for o in new]} label reported = {vi.GetControlValue('Text')!r}", flush=True)
    try:
        g.close_panel(TGT); os.remove(TGT); print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
